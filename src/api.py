import sys
import os
import time
import requests
import openmeteo_requests
from retry_requests import retry
from dotenv import load_dotenv
from icalendar import Calendar
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo 
import psutil
import logging
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, "envs", "sensor_hub_ip.env")

load_dotenv(env_path)

SENSOR_HUB_IP = os.getenv("SENSOR_HUB_IP")
LOCAL_TZ = ZoneInfo("Europe/London")
SESSION = retry(requests.Session(), retries=5, backoff_factor=0.2)
                
class CacheItem:
    def __init__(self, fetch_func, ttl_seconds, is_valid_func=None):
        self.fetch_func = fetch_func
        self.ttl = ttl_seconds
        self.value = None
        self.last_updated = None
        self.is_valid = is_valid_func or (lambda x: x is not None)

    def get(self, force_refresh=False):
        now = time.time()

        expired = (
            self.value is None
            or self.last_updated is None
            or (now - self.last_updated) > self.ttl
        )

        if expired or force_refresh:
            try:
                new_value = self.fetch_func()

                if self.is_valid(new_value):
                    self.value = new_value
                    self.last_updated = now
                else:
                    logger.warning(f"{self.fetch_func.__name__}: Invalid data received, keeping old cache")

            except Exception as e:
                logger.error(f"{self.fetch_func.__name__}: Cache fetch failed: {e}")
                # keep old value

        return self.value
    
    def clear(self):
        self.value = None
        self.last_updated = None

def weather_code_to_icon(code):
    if code == 0:
        return "sun"
    elif code in [1, 2]:
        return "cloud-sun"
    elif code == 3:
        return "cloud"
    elif code in [45, 48]:
        return "fog"
    elif code in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:
        return "rain"
    elif code in [71, 73, 75, 77, 85, 86]:
        return "snow"
    elif code in [95, 96, 99]:
        return "thunderstorm"
    else:
        return "cloud"

def fetch_weather():


    try:
        openmeteo = openmeteo_requests.Client(session=SESSION)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 51.4136,
            "longitude": -0.7505,
            "daily": ["temperature_2m_max", "temperature_2m_min"],
            "hourly": ["temperature_2m", "precipitation_probability", "weather_code"],
            "current": ["temperature_2m", "precipitation_probability", "weather_code"],
            "timezone": "GMT",
            "forecast_days": 2,
        }

        response = openmeteo.weather_api(url, params=params)[0]

        # -------- Current --------
        current = response.Current()
        current_temp = round(current.Variables(0).Value())
        current_rain = round(current.Variables(1).Value())
        current_code = int(current.Variables(2).Value())

        # -------- Daily --------
        daily = response.Daily()
        max_temp = round(daily.Variables(0).ValuesAsNumpy()[0])
        min_temp = round(daily.Variables(1).ValuesAsNumpy()[0])

        # -------- Hourly --------
        hourly = response.Hourly()

        times = hourly.Time()
        interval = hourly.Interval()

        temps = hourly.Variables(0).ValuesAsNumpy()
        rain = hourly.Variables(1).ValuesAsNumpy()
        codes = hourly.Variables(2).ValuesAsNumpy()

        # Convert timestamps → datetime
        now = datetime.now(timezone.utc)

        forecast = []

        for i in range(len(temps)):
            dt = datetime.fromtimestamp(times + i * interval, tz=timezone.utc)

            now = datetime.now(timezone.utc)

            next_hour = (now.replace(minute=0, second=0, microsecond=0)
                        + timedelta(hours=1))

            if dt <= next_hour:
                continue  # skip past hours

            forecast.append({
                "time": dt.strftime("%H:%M"),
                "temp": round(temps[i]),
                "rain": round(rain[i]),
                "condition": weather_code_to_icon(int(codes[i]))
            })

            if len(forecast) == 5:
                break

        return {
            "current_temp": current_temp,
            "max_temp": max_temp,
            "min_temp": min_temp,
            "rain_chance": current_rain,
            "condition": weather_code_to_icon(current_code),
            "forecast": forecast
        }
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        return None

def fetch_calendar_events():
    urls = os.getenv("GOOGLE_CALENDAR_URLS").split(",")

    if not urls:
        logger.warning("No calendar URLs set")
        return []

    now = datetime.now(timezone.utc)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    today_events = []
    tomorrow_events = []

    try:
        for url in urls:
            response = requests.get(url.strip(), timeout=10)
            cal = Calendar.from_ical(response.text)

            for component in cal.walk():
                if component.name != "VEVENT":
                    continue

                dtstart = component.get("dtstart")
                dtend = component.get("dtend")

                if not dtstart or not dtend:
                    continue

                start = dtstart.dt
                end = dtend.dt
                title = str(component.get("summary"))

                is_all_day = False

                # --- START ---
                if isinstance(start, datetime):
                    if start.tzinfo is None:
                        start = start.replace(tzinfo=timezone.utc)
                    else:
                        start = start.astimezone(timezone.utc)
                else:
                    # all-day event
                    is_all_day = True
                    start = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)

                # --- END ---
                if isinstance(end, datetime):
                    if end.tzinfo is None:
                        end = end.replace(tzinfo=timezone.utc)
                    else:
                        end = end.astimezone(timezone.utc)
                else:
                    end = datetime.combine(end, datetime.min.time(), tzinfo=timezone.utc)

                # --- FIX ALL-DAY EVENTS ---
                if is_all_day:
                    # Google gives end as next-day midnight → subtract a tiny bit
                    end = end - timedelta(seconds=1)
        
                event_date = start.date()

                # --- TODAY (including ongoing multi-day events) ---
                if start.date() <= today <= end.date() and end > now:
                    today_events.append({
                        "title": title,
                        "start": start,
                        "end": end,
                        "all_day": is_all_day
                    })

                # --- TOMORROW ---
                elif start.date() <= tomorrow <= end.date():
                    tomorrow_events.append({
                        "title": title,
                        "start": start,
                        "end": end,
                        "all_day": is_all_day
                    })

        # Sort
        today_events.sort(key=lambda x: x["start"])
        tomorrow_events.sort(key=lambda x: x["start"])

        # Format
        formatted = []

        # --- TODAY ---
        for event in today_events:
            if event["all_day"]:
                formatted.append({
                    "title": event["title"],
                    "time": "All Day"
                })
            else:
                formatted.append({
                    "title": event["title"],
                    "time": f'{event["start"].astimezone(LOCAL_TZ).strftime("%H:%M")} - {event["end"].astimezone(LOCAL_TZ).strftime("%H:%M")}'
                })

        # --- DIVIDER ---
        if tomorrow_events and len(formatted) < 4:
            formatted.append({
                "divider": "Tomorrow"
            })

            # --- TOMORROW ---
            for event in tomorrow_events:
                if event["all_day"]:
                    formatted.append({
                        "title": event["title"],
                        "time": "All Day"
                    })
                else:
                    formatted.append({
                        "title": event["title"],
                        "time": f'{event["start"].astimezone(LOCAL_TZ).strftime("%H:%M")} - {event["end"].astimezone(LOCAL_TZ).strftime("%H:%M")}'
                    })

        return formatted[:5]
    except Exception as e:
        logger.error(f"Calendar fetch failed: {e}")
        return []

def fetch_room_info():
    try:
        response = requests.get(f"http://{SENSOR_HUB_IP}/sht31", timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "temperature": round(data.get("temperature", 0), 1),
            "humidity": round(data.get("humidity", 0), 1),
        }

    except requests.RequestException as e:
        logger.error(f"ESP32 request failed: {e}")
        return {
            "temperature": None,
            "humidity": None,
        }

def fetch_system_info():
    try:    
        cpu_usage = psutil.cpu_percent(interval=None)
        memory_usage = psutil.virtual_memory().percent
        
        temps = psutil.sensors_temperatures()
        cpu_temp = None
        if temps:
            for name in temps:
                if temps[name]:
                    cpu_temp = temps[name][0].current
                    break
        cpu_temperature = round(cpu_temp, 2) if cpu_temp else None
        
        uptime_seconds = time.time() - psutil.boot_time()
        uptime = time.strftime("%H:%M", time.gmtime(uptime_seconds))
        
        addrs = psutil.net_if_addrs()
        ip_address = None
        for iface in ["wlan0", "eth0"]:
            if iface in addrs:
                for addr in addrs[iface]:
                    if addr.family == 2:  # AF_INET
                        ip_address = addr.address
                        break
        ip_address = ip_address.split(".")[-1] if ip_address else "?"

        disk_usage = psutil.disk_usage('/').percent
        
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "cpu_temperature": cpu_temperature,
            "uptime": uptime,
            "ip_address": ip_address,
            "disk_usage": disk_usage,
        }
    except Exception as e:
        logger.error(f"System info fetch failed: {e}")
        return None
    
def valid_weather(data):
    return data and data.get("current_temp") is not None

def valid_calendar(data):
    return isinstance(data, list)  # empty list is fine

def valid_room(data):
    return data and data.get("temperature") is not None

def valid_system(data):
    return data and data.get("cpu_usage") is not None

cache = {
    "weather": CacheItem(fetch_weather, 3600, valid_weather),  # 1 hour
    "calendar_events": CacheItem(fetch_calendar_events, 900, valid_calendar),  # 15 minutes
    "room_info": CacheItem(fetch_room_info, 300, valid_room),  # 5 minutes
    "system_info": CacheItem(fetch_system_info, 60, valid_system),  # 1 minute
}

def refresh_all():
    for key, item in cache.items():
        item.get(force_refresh=True)
    
def clear_all():
    for key, item in cache.items():
        item.clear()

def return_data():
    return {
        "weather": cache["weather"].get(),
        "calendar_events": cache["calendar_events"].get(),
        "room_info": cache["room_info"].get(),
        "system_info": cache["system_info"].get(),
    }

if __name__ == "__main__":
    data = return_data()
    logger.debug(f"Fetched data: {data}")