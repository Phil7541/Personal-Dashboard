import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WAVESHARE_LIB = os.path.join(BASE_DIR, "lib")

sys.path.append(WAVESHARE_LIB)

import logging
from waveshare_epd import epd7in5h
import time


import renderer

epd = epd7in5h.EPD()

epd.init()
epd.Clear()
image = renderer.render_dashboard()

time.sleep(3)

epd.display(epd.getbuffer(image))
