import sys
import os
import time
import requests
import psutil
from dotenv import load_dotenv
from icalendar import Calendar
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, "envs", "sensor_hub_ip.env")

load_dotenv(env_path)

SENSOR_HUB_IP = os.getenv("SENSOR_HUB_IP")

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
    import openmeteo_requests
    import requests_cache
    from retry_requests import retry
    from datetime import datetime, timezone

    # Setup API client
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

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

        if dt <= now:
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

def fetch_calendar_events():
    urls = os.getenv("GOOGLE_CALENDAR_URLS").split(",")

    now = datetime.now(timezone.utc)
    today = now.date()
    tomorrow = today + timedelta(days=1)

    today_events = []
    tomorrow_events = []

    for url in urls:
        response = requests.get(url.strip())
        cal = Calendar.from_ical(response.text)

        for component in cal.walk():
            if component.name != "VEVENT":
                continue

            start = component.get("dtstart").dt
            end = component.get("dtend").dt
            title = str(component.get("summary"))

            LOCAL_TZ = ZoneInfo("Europe/London")

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

    combined = today_events + tomorrow_events

    # Format
    formatted = []

    for event in combined[:5]:
        if event["all_day"]:
            formatted.append({
                "title": event["title"],
                "start": "All Day",
                "end": "",
                "all_day": True
            })
        else:
            start_local = event["start"].astimezone(LOCAL_TZ)
            end_local = event["end"].astimezone(LOCAL_TZ)

            formatted.append({
                "title": event["title"],
                "start": start_local.strftime("%H:%M"),
                "end": end_local.strftime("%H:%M"),
                "all_day": False
            })

    return formatted

def fetch_room_info():
    try:
        response = requests.get(f"http://{SENSOR_HUB_IP}/sht31", timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            "temperature": round(data.get("temperature", 0), 1),
            "humidity": round(data.get("humidity", 0), 1),
        }

    except requests.RequestException as e:
        print(f"[ESP32 ERROR] {e}")

        # fallback so your UI doesn't explode
        return {
            "temperature": None,
            "humidity": None,
        }

def fetch_system_info():
    # Implementation for fetching system information
    
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    cpu_temperature = round(psutil.sensors_temperatures()['cpu_thermal'][0].current, 2)
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = time.strftime("%H:%M", time.gmtime(uptime_seconds))
    ip_address = psutil.net_if_addrs()['wlan0'][0].address
    ip_address = ip_address.split(".")[-1]
    disk_usage = psutil.disk_usage('/').percent
    
    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "cpu_temperature": cpu_temperature,
        "uptime": uptime,
        "ip_address": ip_address,
        "disk_usage": disk_usage,
    }

def return_data():
    return {
        "weather": fetch_weather(),
        "calendar_events": fetch_calendar_events(),
        "room_info": fetch_room_info(),
        "system_info": fetch_system_info(),
    }
    
def return_weather():
    return fetch_weather()

def return_calendar_events():
    return fetch_calendar_events()

def return_room_info():
    return fetch_room_info()

def return_system_info():
    return fetch_system_info()

if __name__ == "__main__":
    data = return_data()
    print(data)