import sys
import os
from datetime import datetime
import time
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "dashboard.log")

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=1_000_000,  # 1MB
    backupCount=3        # keep 3 old logs
)

stream_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[file_handler, stream_handler]
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAVESHARE_LIB = os.path.join(BASE_DIR, "lib")

sys.path.append(WAVESHARE_LIB)

from waveshare_epd import epd7in5h

import renderer
import api

logger = logging.getLogger(__name__)

def setup():
    epd = epd7in5h.EPD()
    epd.init()
    epd.Clear()
    time.sleep(1)
    
    api.clear_all()
    api.refresh_all()
    
    return epd

def sleep_until_next_minute(offset_seconds=0):
    now = datetime.now()
    seconds = now.second + now.microsecond / 1_000_000

    # sleep until (60 - offset)
    sleep_time = 60 - seconds - offset_seconds

    if sleep_time < 0:
        sleep_time += 60  # handle wrap-around

    time.sleep(sleep_time)
    
def handle_keyboard_interupt(epd):
    epd.Clear()
    epd.sleep()
    logger.info("Display Slept")
    exit
    
def test_render():
    data = api.return_data()
    image = renderer.render_dashboard(data)
    image.save("dashboard.png")

def test_display():
    epd = setup()
    data = api.return_data()
    image = renderer.render_dashboard(data)
    epd.display(epd.getbuffer(image))

if __name__ == "__main__":
    epd = setup()
    logger.info("Dashboard Started")

    while True:
        try:
            sleep_until_next_minute()
            
            now = datetime.now()

            if now.minute == 0:
                api.cache["weather"].get(force_refresh=True)

            api.refresh_all()
            data = api.return_data()       
            image = renderer.render_dashboard(data)
            epd.display(epd.getbuffer(image))
        except KeyboardInterrupt as e:
            logger.warning("Detected Keyboard Interrupt")
            handle_keyboard_interupt(epd)