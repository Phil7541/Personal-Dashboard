import os
from PIL import Image, ImageDraw, ImageFont
import time

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
HEADER_FONT_SIZE = 32
HEADER_FONT_SMALL_SIZE = 24
BODY_FONT_SIZE = 24

TIME_FONT = ImageFont.truetype(INTER_PATH, TIME_FONT_SIZE)
HEADER_FONT_LARGE = ImageFont.truetype(INTER_BOLD, HEADER_FONT_LARGE_SIZE)
HEADER_FONT_MEDIUM = ImageFont.truetype(INTER_SEMI_BOLD, HEADER_FONT_MEDIUM_SIZE)
HEADER_FONT = ImageFont.truetype(INTER_SEMI_BOLD, HEADER_FONT_SIZE)
HEADER_FONT_SMALL = ImageFont.truetype(INTER_SEMI_BOLD, HEADER_FONT_SMALL_SIZE)
BODY_FONT = ImageFont.truetype(INTER_SEMI_BOLD, BODY_FONT_SIZE)


BOX_BORDER_WEIGHT = 2
BOX_BORDER_RADIUS = 8

BOX_PADDING = 10
PADDING = 5

HUGE_ICON_SIZE = (100, 100)
LARGE_ICON_SIZE = (60, 60)
MEDIUM_ICON_SIZE = (30, 30)
SMALL_ICON_SIZE = (20, 20)

FORECAST_COLUMN_WIDTH = 90
CALENDAR_ITEM_HEIGHT = MEDIUM_ICON_SIZE[1] + PADDING + BODY_FONT_SIZE + PADDING

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

def draw_forecast_column(draw, image, x, y, time, weather, temp, rain_chance, rain_icon):
    weather_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "weather", f"{weather}.png"), SMALL_ICON_SIZE)
    draw.text((x, y), f"{time}", font=HEADER_FONT, fill="black")
    image.paste(weather_icon, (x , y + HEADER_FONT_SIZE + PADDING + PADDING), weather_icon)
    draw.text((x + SMALL_ICON_SIZE[0] + PADDING, y + HEADER_FONT_SIZE + PADDING), f"{temp}°", font=BODY_FONT, fill="black")
    image.paste(rain_icon, (x, y + HEADER_FONT_SIZE + PADDING + PADDING + PADDING + SMALL_ICON_SIZE[1] + PADDING), rain_icon)
    draw.text((x + SMALL_ICON_SIZE[0] + PADDING, y + HEADER_FONT_SIZE + PADDING + PADDING + SMALL_ICON_SIZE[1] + PADDING), f"{rain_chance}%", font=BODY_FONT, fill="black")

def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def draw_calendar_event(draw, image, x, y, max_width, name, start, end):
    calendar_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "calendar.png"), MEDIUM_ICON_SIZE)
    text_x = x + MEDIUM_ICON_SIZE[0] + PADDING
    text_width = max_width - MEDIUM_ICON_SIZE[0] - PADDING
    name_lines = wrap_text(draw, name, HEADER_FONT_SMALL, text_width)
    image.paste(calendar_icon, (x, y), calendar_icon)

    current_y = y
    for line in name_lines:
        draw.text((text_x, current_y), line, font=HEADER_FONT_SMALL, fill="black")
        current_y += HEADER_FONT_SMALL_SIZE + PADDING

    time_text = f"{start} - {end}"
    draw.text((text_x, current_y), time_text, font=BODY_FONT, fill="black")
    current_y += BODY_FONT_SIZE

    content_height = current_y - y
    total_height = max(content_height, MEDIUM_ICON_SIZE[1])

    return total_height

def draw_weather_box(draw, image):
    # Setup
    x1, y1, x2, y2 = get_box_origin("weather")
    weather_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "weather", "sun.png"), LARGE_ICON_SIZE)
    rain_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "weather", "rain.png"), SMALL_ICON_SIZE)
    text_left = x1 + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING
    
    # Draw Box
    draw.rounded_rectangle(BOX_COORDINATES["weather"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    
    # Draw Current Weather Content
    paste_icon(image, weather_icon, int(x1) + BOX_PADDING, int(y1) + BOX_PADDING)
    draw.text((int(x1) + BOX_PADDING, int(y2) - BOX_PADDING - HEADER_FONT_MEDIUM_SIZE), "25°", font=HEADER_FONT_MEDIUM, fill="black")
    bbox_max = draw.textbbox((text_left, int(y1) + BOX_PADDING), f"{MAX_TEMP}", font=BODY_FONT)
    bbox_min = draw.textbbox((text_left, int(y1) + BOX_PADDING + BODY_FONT_SIZE + PADDING), f"{MIN_TEMP}", font=BODY_FONT)
    draw.text((text_left, int(y1) + BOX_PADDING), f"{MAX_TEMP}°", font=BODY_FONT, fill="black")
    draw.line([(text_left, int(y1) + BOX_PADDING + BODY_FONT_SIZE + (PADDING // 2)), (max(bbox_max[2], bbox_min[2]), int(y1) + BOX_PADDING + BODY_FONT_SIZE + (PADDING // 2))], fill="black", width=BOX_BORDER_WEIGHT)
    draw.text((text_left, int(y1) + BOX_PADDING + BODY_FONT_SIZE + PADDING), f"{MIN_TEMP}°", font=BODY_FONT, fill="black")
    paste_icon(image, rain_icon, int(x1) + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING, int(y2)- BOX_PADDING - SMALL_ICON_SIZE[1])
    draw.text((text_left + SMALL_ICON_SIZE[0] + PADDING, int(y2) - BOX_PADDING - BODY_FONT_SIZE - PADDING), "60%", font=BODY_FONT, fill="black")
    
    # Draw Forecast Content
    draw_forecast_column(draw, image, int(x2) - (FORECAST_COLUMN_WIDTH * 5) - (PADDING * 8) - BOX_PADDING, int(y1) + BOX_PADDING, "15:00", "cloud", 24, 40, rain_icon)
    draw.line([(int(x2) - (FORECAST_COLUMN_WIDTH * 4) - (PADDING * 8) - BOX_PADDING, int(y1) + BOX_PADDING), (int(x2) - (FORECAST_COLUMN_WIDTH * 4) - (PADDING * 8) - BOX_PADDING, int(y2) - BOX_PADDING)], fill="black", width=BOX_BORDER_WEIGHT)
    draw_forecast_column(draw, image, int(x2) - (FORECAST_COLUMN_WIDTH * 4) - (PADDING * 6) - BOX_PADDING, int(y1) + BOX_PADDING, "16:00", "cloud", 24, 35, rain_icon)
    draw.line([(int(x2) - (FORECAST_COLUMN_WIDTH * 3) - (PADDING * 6) - BOX_PADDING, int(y1) + BOX_PADDING), (int(x2) - (FORECAST_COLUMN_WIDTH * 3) - (PADDING * 6) - BOX_PADDING, int(y2) - BOX_PADDING)], fill="black", width=BOX_BORDER_WEIGHT)
    draw_forecast_column(draw, image, int(x2) - (FORECAST_COLUMN_WIDTH * 3) - (PADDING * 4) - BOX_PADDING, int(y1) + BOX_PADDING, "17:00", "cloud-sun", 23, 30, rain_icon)
    draw.line([(int(x2) - (FORECAST_COLUMN_WIDTH * 2) - (PADDING * 4) - BOX_PADDING, int(y1) + BOX_PADDING), (int(x2) - (FORECAST_COLUMN_WIDTH * 2) - (PADDING * 4) - BOX_PADDING, int(y2) - BOX_PADDING)], fill="black", width=BOX_BORDER_WEIGHT)
    draw_forecast_column(draw, image, int(x2) - (FORECAST_COLUMN_WIDTH * 2) - (PADDING * 2) - BOX_PADDING, int(y1) + BOX_PADDING, "18:00", "cloud-sun", 21, 20, rain_icon)
    draw.line([(int(x2) - (FORECAST_COLUMN_WIDTH * 1) - (PADDING * 2) - BOX_PADDING, int(y1) + BOX_PADDING), (int(x2) - (FORECAST_COLUMN_WIDTH * 1) - (PADDING * 2) - BOX_PADDING, int(y2) - BOX_PADDING)], fill="black", width=BOX_BORDER_WEIGHT)
    draw_forecast_column(draw, image, int(x2) - (FORECAST_COLUMN_WIDTH * 1) - BOX_PADDING, int(y1) + BOX_PADDING, "19:00", "cloud-sun", 20, 0, rain_icon)


def draw_time_box(draw):
    x1, y1, x2, y2 = get_box_origin("time")
    current_time = time.strftime("%H:%M")
    draw.rounded_rectangle(BOX_COORDINATES["time"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    draw.text(((int(x2) - int(x1)) // 2 + int(x1), (int(y2) - int(y1)) // 2 + int(y1)), f"{current_time}", anchor="mm", font=TIME_FONT, fill="black")

def draw_calendar_box(draw, image):
    x1, y1, x2, y2 = get_box_origin("calendar")
    draw.rounded_rectangle(BOX_COORDINATES["calendar"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    
    content_x = x1 + BOX_PADDING
    content_y = y1 + BOX_PADDING
    content_width = (x2 - x1) - (BOX_PADDING * 2)
    content_height = (y2 - y1) - (BOX_PADDING * 2)
    current_y = content_y
    events = [
        ("Meeting with Bob about something quite long", "10:00", "11:00"),
        ("Lunch with Alice", "12:00", "13:00"),
        ("Project sync with team", "15:00", "16:30"),
        ("Dinner with Carol which might also be long text", "19:00", "20:00"),
        ("Another event that probably won't fit", "21:00", "22:00"),
    ]

    if events == []:
        calendar_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "calendar_big.png"), HUGE_ICON_SIZE)
        paste_icon(image, calendar_icon, (int(x1) + ((int(x2) - int(x1)) // 2) - (HUGE_ICON_SIZE[0] // 2)), (int(y1) + ((int(y2) - int(y1)) // 2) - (HUGE_ICON_SIZE[1] // 2)))
    else:
        for i, (name, start, end) in enumerate(events):
            remaining_height = (content_y + content_height) - current_y
            if remaining_height < MEDIUM_ICON_SIZE[1]:
                break

            used_height = draw_calendar_event(
                draw,
                image,
                content_x,
                current_y,
                content_width,
                name,
                start,
                end
            )
            current_y += used_height

            if i < len(events) - 1:
                next_name, next_start, next_end = events[i + 1]
                next_lines = wrap_text(draw, next_name, HEADER_FONT_SMALL, content_width - MEDIUM_ICON_SIZE[0] - PADDING)
                next_height = max(
                    (len(next_lines) * (HEADER_FONT_SMALL_SIZE + PADDING)) + BODY_FONT_SIZE,
                    MEDIUM_ICON_SIZE[1]
                )
                space_needed = PADDING + BOX_BORDER_WEIGHT + PADDING + next_height

                if current_y + space_needed <= (content_y + content_height):
                    # Enough space → draw divider
                    current_y += PADDING
                    draw.line(
                        [(content_x, current_y), (content_x + content_width, current_y)],
                        fill="black",
                        width=BOX_BORDER_WEIGHT
                    )
                    current_y += BOX_BORDER_WEIGHT + PADDING
                else:
                    break
    
    
def draw_room_info_box(draw, image):
    x1, y1, x2, y2 = get_box_origin("room_info")
    temperature_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "temperature.png"), MEDIUM_ICON_SIZE)
    humidity_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "humidity.png"), MEDIUM_ICON_SIZE)
    draw.rounded_rectangle(BOX_COORDINATES["room_info"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    paste_icon(image, temperature_icon, int(x1) + BOX_PADDING, int(y1) + BOX_PADDING)
    draw.text((int(x1) + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, int(y1) + BOX_PADDING), "22.1°", font=BODY_FONT, fill="black")
    paste_icon(image, humidity_icon, int(x1) + BOX_PADDING, int(y1) + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING)
    draw.text((int(x1) + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, int(y1) + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING), "45%", font=BODY_FONT, fill="black")

def draw_system_info_box(draw, image):
    x1, y1, x2, y2 = get_box_origin("system_info")
    BAR_WIDTH = 70
    cpu_fill_width = int((34 / 100) * BAR_WIDTH)
    memory_fill_width = int((68 / 100) * BAR_WIDTH)
    cpu_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "cpu.png"), MEDIUM_ICON_SIZE)
    memory_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "memory.png"), MEDIUM_ICON_SIZE)
    temperature_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "temperature.png"), MEDIUM_ICON_SIZE)
    clock_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "clock.png"), MEDIUM_ICON_SIZE)
    wifi_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "wifi.png"), MEDIUM_ICON_SIZE)
    disk_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "disk.png"), MEDIUM_ICON_SIZE)
    draw.rounded_rectangle(BOX_COORDINATES["system_info"], radius=BOX_BORDER_RADIUS, fill="white", outline="black", width=BOX_BORDER_WEIGHT)
    paste_icon(image, cpu_icon, x1 + BOX_PADDING, y1 + BOX_PADDING)
    draw.rounded_rectangle([(x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING), (x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING + BAR_WIDTH, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1])], radius=BOX_BORDER_RADIUS, outline="black", width=BOX_BORDER_WEIGHT)
    draw.rounded_rectangle([(x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING), (x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING + cpu_fill_width, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1])], radius=BOX_BORDER_RADIUS, fill="black")
    paste_icon(image, memory_icon, x1 + BOX_PADDING, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING)
    draw.rounded_rectangle([(x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING), (x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING + BAR_WIDTH, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + MEDIUM_ICON_SIZE[1] + PADDING)], radius=BOX_BORDER_RADIUS, outline="black", width=BOX_BORDER_WEIGHT)
    draw.rounded_rectangle([(x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING), (x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING + memory_fill_width, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + MEDIUM_ICON_SIZE[1] + PADDING)], radius=BOX_BORDER_RADIUS, fill="black")
    paste_icon(image, temperature_icon, x1 + BOX_PADDING, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING + MEDIUM_ICON_SIZE[1] + PADDING)
    draw.text((int(x1) + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, int(y1) + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING + MEDIUM_ICON_SIZE[1] + PADDING), "55°C", font=BODY_FONT, fill="black")
    paste_icon(image, clock_icon, x1 + ((x2 - x1) // 2), y1 + BOX_PADDING)
    draw.text((int(x1) + ((int(x2) - int(x1)) // 2) + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING), "37:42", font=BODY_FONT, fill="black")
    paste_icon(image, wifi_icon, x1 + ((x2 - x1) // 2), y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING)
    draw.text((int(x1) + ((int(x2) - int(x1)) // 2) + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING), "176", font=BODY_FONT, fill="black")
    paste_icon(image, disk_icon, x1 + ((x2 - x1) // 2), y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING + MEDIUM_ICON_SIZE[1] + PADDING)
    draw.text((int(x1) + ((int(x2) - int(x1)) // 2) + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING + MEDIUM_ICON_SIZE[1] + PADDING), "42%", font=BODY_FONT, fill="black")

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