import os
from PIL import Image, ImageDraw, ImageFont

BOX_COORDINATES = {
    "weather": [(10, 10), (790, 130)],
    "time": [(10, 140), (540, 340)],
    "calendar": [(550, 140), (790, 470)],
    "room_info": [(10, 350), (270, 470)],
    "system_info": [(280, 350), (540, 470)],
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTER_PATH = os.path.join(BASE_DIR, "assets", "fonts", "inter.ttf")

TIME_FONT_SIZE = 128
HEADER_FONT_LARGE_SIZE = 48
HEADER_FONT_MEDIUM_SIZE = 32
HEADER_FONT_SMALL_SIZE = 24
BODY_FONT_LARGE_SIZE = 18
BODY_FONT_MEDIUM_SIZE = 14
BODY_FONT_SMALL_SIZE = 10

TIME_FONT = ImageFont.truetype(INTER_PATH, TIME_FONT_SIZE)
HEADER_FONT_LARGE = ImageFont.truetype(INTER_PATH, HEADER_FONT_LARGE_SIZE)
HEADER_FONT_MEDIUM = ImageFont.truetype(INTER_PATH, HEADER_FONT_MEDIUM_SIZE)
HEADER_FONT_SMALL = ImageFont.truetype(INTER_PATH, HEADER_FONT_SMALL_SIZE)
BODY_FONT_LARGE = ImageFont.truetype(INTER_PATH, BODY_FONT_LARGE_SIZE)
BODY_FONT_MEDIUM = ImageFont.truetype(INTER_PATH, BODY_FONT_MEDIUM_SIZE)
BODY_FONT_SMALL = ImageFont.truetype(INTER_PATH, BODY_FONT_SMALL_SIZE)

BOX_BORDER_WEIGHT = 2
BOX_BORDER_RADIUS = 8

BOX_PADDING = 10

def get_box_origin(box_name):
    return BOX_COORDINATES[box_name][0][0], BOX_COORDINATES[box_name][0][1], BOX_COORDINATES[box_name][1][0], BOX_COORDINATES[box_name][1][1]

def draw_weather_box(draw):
    x1, y1, x2, y2 = get_box_origin("weather")
    draw.rounded_rectangle(BOX_COORDINATES["weather"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING), "Weather:", font=HEADER_FONT_MEDIUM, fill="black")
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING + HEADER_FONT_MEDIUM_SIZE + BOX_PADDING), "Sunny, 25°C", font=BODY_FONT_MEDIUM, fill="black")

def draw_time_box(draw):
    x1, y1, x2, y2 = get_box_origin("time")
    draw.rounded_rectangle(BOX_COORDINATES["time"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text(((int(x2) - int(x1)) // 2 + int(x1), (int(y2) - int(y1)) // 2 + int(y1)), "14:00", anchor="mm", font=TIME_FONT, fill="black")

def draw_calendar_box(draw):
    x1, y1, x2, y2 = get_box_origin("calendar")
    draw.rounded_rectangle(BOX_COORDINATES["calendar"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING), "Calendar: Meeting at 3 PM", font=HEADER_FONT_MEDIUM, fill="black")

def draw_room_info_box(draw):
    x1, y1, x2, y2 = get_box_origin("room_info")
    draw.rounded_rectangle(BOX_COORDINATES["room_info"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING), "Room Info: Conference Room A", font=HEADER_FONT_SMALL, fill="black")

def draw_system_info_box(draw):
    x1, y1, x2, y2 = get_box_origin("system_info")
    draw.rounded_rectangle(BOX_COORDINATES["system_info"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING), "System Info: CPU 30%, RAM 40%", font=HEADER_FONT_SMALL, fill="black")

def render_dashboard():
    image = Image.new("RGB", (800, 480), "white")
    draw = ImageDraw.Draw(image)
    draw_weather_box(draw)
    draw_time_box(draw)
    draw_calendar_box(draw)
    draw_room_info_box(draw)
    draw_system_info_box(draw)
    return image

image = render_dashboard()

image.save(os.path.join(BASE_DIR, "images", "output.png"))