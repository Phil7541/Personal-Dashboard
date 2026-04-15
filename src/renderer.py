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
INTER_SEMI_BOLD = os.path.join(BASE_DIR, "assets", "fonts", "inter_semi_bold.ttf")
INTER_BOLD = os.path.join(BASE_DIR, "assets", "fonts", "inter_bold.ttf")

TIME_FONT_SIZE = 128
HEADER_FONT_LARGE_SIZE = 48
HEADER_FONT_MEDIUM_SIZE = 36
HEADER_FONT_SMALL_SIZE = 24
BODY_FONT_SIZE = 24

TIME_FONT = ImageFont.truetype(INTER_PATH, TIME_FONT_SIZE)
HEADER_FONT_LARGE = ImageFont.truetype(INTER_BOLD, HEADER_FONT_LARGE_SIZE)
HEADER_FONT_MEDIUM = ImageFont.truetype(INTER_SEMI_BOLD, HEADER_FONT_MEDIUM_SIZE)
HEADER_FONT_SMALL = ImageFont.truetype(INTER_SEMI_BOLD, HEADER_FONT_SMALL_SIZE)
BODY_FONT = ImageFont.truetype(INTER_SEMI_BOLD, BODY_FONT_SIZE)


BOX_BORDER_WEIGHT = 2
BOX_BORDER_RADIUS = 8

BOX_PADDING = 10

LARGE_ICON_SIZE = (60, 60)
MEDIUM_ICON_SIZE = (30, 30)
SMALL_ICON_SIZE = (20, 20)

MAX_TEMP = 26
MIN_TEMP = 18

def load_icon(path, size):
    icon = Image.open(path)

    if icon.mode != "RGBA":
        icon = icon.convert("RGBA")

    icon = icon.resize(size)

    return icon

def paste_icon(image, icon, x, y):
    image.paste(icon, (x, y), icon)

def get_box_origin(box_name):
    return BOX_COORDINATES[box_name][0][0], BOX_COORDINATES[box_name][0][1], BOX_COORDINATES[box_name][1][0], BOX_COORDINATES[box_name][1][1]

def draw_weather_box(draw, image):
    x1, y1, x2, y2 = get_box_origin("weather")
    weather_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "weather", "sun.png"), LARGE_ICON_SIZE)
    rain_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "weather", "rain.png"), SMALL_ICON_SIZE)
    draw.rounded_rectangle(BOX_COORDINATES["weather"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    paste_icon(image, weather_icon, int(x1) + BOX_PADDING, int(y1) + BOX_PADDING)
    draw.text((int(x1) + BOX_PADDING, int(y2) - BOX_PADDING - HEADER_FONT_MEDIUM_SIZE), "25°", font=HEADER_FONT_MEDIUM, fill="black")
    draw.text((int(x1) + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING, int(y1) + BOX_PADDING), f"{MAX_TEMP}°", font=BODY_FONT, fill="black")
    draw.line([(int(x1) + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING, int(y1) + BOX_PADDING + BODY_FONT_SIZE + (BOX_PADDING // 2)), (int(x1) + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING + (15 * (max(len(str(MAX_TEMP)), len(str(MIN_TEMP))))), int(y1) + BOX_PADDING + BODY_FONT_SIZE + (BOX_PADDING // 2))], fill="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING, int(y1) + BOX_PADDING + BODY_FONT_SIZE + 5), f"{MIN_TEMP}°", font=BODY_FONT, fill="black")
    paste_icon(image, rain_icon, int(x1) + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING, int(y2)- BOX_PADDING - SMALL_ICON_SIZE[1])
    draw.text((int(x1) + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING + SMALL_ICON_SIZE[0] + 5, int(y2) - BOX_PADDING - BODY_FONT_SIZE - 2), "60%", font=BODY_FONT, fill="black")

def draw_time_box(draw):
    x1, y1, x2, y2 = get_box_origin("time")
    draw.rounded_rectangle(BOX_COORDINATES["time"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text(((int(x2) - int(x1)) // 2 + int(x1), (int(y2) - int(y1)) // 2 + int(y1)), "14:00", anchor="mm", font=TIME_FONT, fill="black")

def draw_calendar_box(draw, image):
    x1, y1, x2, y2 = get_box_origin("calendar")
    draw.rounded_rectangle(BOX_COORDINATES["calendar"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING), "Calendar: Meeting at 3 PM", font=HEADER_FONT_MEDIUM, fill="black")

def draw_room_info_box(draw, image):
    x1, y1, x2, y2 = get_box_origin("room_info")
    draw.rounded_rectangle(BOX_COORDINATES["room_info"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING), "Room Info: Conference Room A", font=HEADER_FONT_SMALL, fill="black")

def draw_system_info_box(draw, image):
    x1, y1, x2, y2 = get_box_origin("system_info")
    draw.rounded_rectangle(BOX_COORDINATES["system_info"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text((int(x1) + BOX_PADDING, int(y1) + BOX_PADDING), "System Info: CPU 30%, RAM 40%", font=HEADER_FONT_SMALL, fill="black")

def render_dashboard():
    image = Image.new("RGB", (800, 480), "white")
    draw = ImageDraw.Draw(image)
    draw_weather_box(draw, image)
    draw_time_box(draw)
    draw_calendar_box(draw, image)
    draw_room_info_box(draw, image)
    draw_system_info_box(draw, image)
    return image

if __name__ == "__main__":
    image = render_dashboard()
    image.save(os.path.join(BASE_DIR, "images", "output.png"))