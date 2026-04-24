import sys
import os
from datetime import datetime
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAVESHARE_LIB = os.path.join(BASE_DIR, "lib")

sys.path.append(WAVESHARE_LIB)

from waveshare_epd import epd7in5h

import renderer
import api

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
            handle_keyboard_interupt(epd)