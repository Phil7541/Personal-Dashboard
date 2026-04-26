import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAVESHARE_LIB = os.path.join(BASE_DIR, "lib")

sys.path.append(WAVESHARE_LIB)

from waveshare_epd import epd7in5h

if __name__ == "__main__":
    epd = epd7in5h.EPD()
    epd.init()
    epd.Clear()
    time.sleep(1)
    epd.sleep()