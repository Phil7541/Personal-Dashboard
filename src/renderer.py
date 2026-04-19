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


FORECAST_COLUMN_WIDTH = 100
CALENDAR_ITEM_HEIGHT = MEDIUM_ICON_SIZE[1] + PADDING + BODY_FONT_SIZE + PADDING


MAX_TEMP = 26
MIN_TEMP = 18


def load_icon(path, size):
    icon = Image.open(path)

    if icon.mode != "RGBA":
        icon = icon.convert("RGBA")

    return icon.resize(size)


def paste_icon(image, icon, x, y):
    image.paste(icon, (x, y), icon)


def get_box_origin(box_name):
    return (
        BOX_COORDINATES[box_name][0][0],
        BOX_COORDINATES[box_name][0][1],
        BOX_COORDINATES[box_name][1][0],
        BOX_COORDINATES[box_name][1][1],
    )


def draw_forecast_column(draw, image, x, y, time, weather, temp, rain_chance, rain_icon):
    weather_icon = load_icon(
        os.path.join(BASE_DIR, "assets", "icons", "weather", f"{weather}.png"),
        SMALL_ICON_SIZE,
    )

    icon_y = y + HEADER_FONT_SIZE + (PADDING * 2)
    rain_y = icon_y + SMALL_ICON_SIZE[1] + (PADDING * 2)

    draw.text((x, y), time, font=HEADER_FONT, fill="black")

    paste_icon(image, weather_icon, x, icon_y)
    draw.text(
        (x + SMALL_ICON_SIZE[0] + PADDING, icon_y - PADDING),
        f"{temp}°",
        font=BODY_FONT,
        fill="black",
    )

    paste_icon(image, rain_icon, x, (rain_y + PADDING))
    draw.text(
        (x + SMALL_ICON_SIZE[0] + PADDING, rain_y),
        f"{rain_chance}%",
        font=BODY_FONT,
        fill="black",
    )


def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)

        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def draw_calendar_event(draw, image, x, y, max_width, name, start, end, is_all_day=False):
    calendar_icon = load_icon(
        os.path.join(BASE_DIR, "assets", "icons", "calendar.png"),
        MEDIUM_ICON_SIZE,
    )

    text_x = x + MEDIUM_ICON_SIZE[0] + PADDING
    text_width = max_width - MEDIUM_ICON_SIZE[0] - PADDING

    name_lines = wrap_text(draw, name, HEADER_FONT_SMALL, text_width)

    paste_icon(image, calendar_icon, x, y)

    current_y = y

    for line in name_lines:
        draw.text((text_x, current_y), line, font=HEADER_FONT_SMALL, fill="black")
        current_y += HEADER_FONT_SMALL_SIZE + PADDING

    if is_all_day:
        draw.text((text_x, current_y), "All day", font=BODY_FONT, fill="black")
    else:
        draw.text((text_x, current_y), f"{start} - {end}", font=BODY_FONT, fill="black")
    current_y += BODY_FONT_SIZE + PADDING

    content_height = current_y - y
    return max(content_height, MEDIUM_ICON_SIZE[1])


def draw_weather_box(draw, image, data):
    x1, y1, x2, y2 = get_box_origin("weather")

    weather_icon = load_icon(
        os.path.join(BASE_DIR, "assets", "icons", "weather", f"{data['condition']}.png"),
        LARGE_ICON_SIZE,
    )

    rain_icon = load_icon(
        os.path.join(BASE_DIR, "assets", "icons", "weather", "rain.png"),
        SMALL_ICON_SIZE,
    )

    text_left = x1 + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING

    draw.rounded_rectangle(
        BOX_COORDINATES["weather"],
        radius=BOX_BORDER_RADIUS,
        fill="white",
        outline="black",
        width=BOX_BORDER_WEIGHT,
    )

    paste_icon(image, weather_icon, x1 + BOX_PADDING, y1 + BOX_PADDING)

    draw.text(
        (x1 + BOX_PADDING + (LARGE_ICON_SIZE[0] // 2), y2 - BOX_PADDING - HEADER_FONT_MEDIUM_SIZE),
        f"{data['current_temp']}°",
        anchor="ma",
        font=HEADER_FONT_MEDIUM,
        fill="black",
    )
    
    maxbbox = draw.textbbox((0, 0), f"{data['max_temp']}", font=BODY_FONT)
    minbbox = draw.textbbox((0, 0), f"{data['min_temp']}", font=BODY_FONT)

    draw.text((text_left, y1 + BOX_PADDING), f"{data['max_temp']}°", font=BODY_FONT, fill="black")

    draw.line(
        [
            (text_left, y1 + BOX_PADDING + BODY_FONT_SIZE + (PADDING // 2)),
            (text_left + max(maxbbox[2] - maxbbox[0], minbbox[2] - minbbox[0]), y1 + BOX_PADDING + BODY_FONT_SIZE + (PADDING // 2)),
        ],
        fill="black",
        width=BOX_BORDER_WEIGHT,
    )

    draw.text(
        (text_left, y1 + BOX_PADDING + BODY_FONT_SIZE + PADDING),
        f"{data['min_temp']}°",
        font=BODY_FONT,
        fill="black",
    )

    rain_x = x1 + BOX_PADDING + LARGE_ICON_SIZE[0] + BOX_PADDING
    rain_y = y2 - BOX_PADDING

    paste_icon(image, rain_icon, rain_x, rain_y - SMALL_ICON_SIZE[1])

    draw.text(
        (rain_x + SMALL_ICON_SIZE[0] + PADDING, rain_y - BODY_FONT_SIZE),
        f"{data['rain_chance']}%",
        font=BODY_FONT,
        fill="black",
    )

    base_x = x2 - BOX_PADDING

    hours = 0

    for i in data['forecast']:
        col_x = base_x - (FORECAST_COLUMN_WIDTH * (5 - hours)) - (PADDING * (2 * (4 - hours)))
        draw_forecast_column(draw, image, col_x, y1 + BOX_PADDING, i['time'], i['condition'], i['temp'], i['rain'], rain_icon)

        if hours < 4:
            line_x = base_x - (FORECAST_COLUMN_WIDTH * (4 - hours)) - (PADDING * (2 * (4 - hours)))
            draw.line(
                [(line_x, y1 + BOX_PADDING), (line_x, y2 - BOX_PADDING)],
                fill="black",
                width=BOX_BORDER_WEIGHT,
            )
        hours += 1


def draw_time_box(draw):
    x1, y1, x2, y2 = get_box_origin("time")

    draw.rounded_rectangle(
        BOX_COORDINATES["time"],
        radius=BOX_BORDER_RADIUS,
        fill="white",
        outline="black",
        width=BOX_BORDER_WEIGHT,
    )

    draw.text(
        ((x2 - x1) // 2 + x1, (y2 - y1) // 2 + y1),
        time.strftime("%H:%M"),
        anchor="mm",
        font=TIME_FONT,
        fill="black",
    )


def draw_calendar_box(draw, image, data):
    x1, y1, x2, y2 = get_box_origin("calendar")

    draw.rounded_rectangle(
        BOX_COORDINATES["calendar"],
        radius=BOX_BORDER_RADIUS,
        fill="white",
        outline="black",
        width=BOX_BORDER_WEIGHT,
    )

    content_x = x1 + BOX_PADDING
    content_y = y1 + BOX_PADDING
    content_width = (x2 - x1) - (BOX_PADDING * 2)
    content_height = (y2 - y1) - (BOX_PADDING * 2)

    current_y = content_y

    if not data:
        icon = load_icon(
            os.path.join(BASE_DIR, "assets", "icons", "calendar_big.png"),
            HUGE_ICON_SIZE,
        )

        paste_icon(
            image,
            icon,
            x1 + (x2 - x1) // 2 - HUGE_ICON_SIZE[0] // 2,
            y1 + (y2 - y1) // 2 - HUGE_ICON_SIZE[1] // 2,
        )
        return

    events = 0

    for i in data:
        remaining_height = (content_y + content_height) - current_y
        if remaining_height < MEDIUM_ICON_SIZE[1]:
            break
        
        used_height = draw_calendar_event(
            draw, image, content_x, current_y, content_width, i['title'], i['start'], i['end'], i['all_day']
        )

        current_y += used_height

        if events < len(data) - 1:
            next_name = data[events + 1]['title']

            next_lines = wrap_text(
                draw,
                next_name,
                HEADER_FONT_SMALL,
                content_width - MEDIUM_ICON_SIZE[0] - PADDING,
            )

            next_height = max(
                (len(next_lines) * (HEADER_FONT_SMALL_SIZE + PADDING)) + BODY_FONT_SIZE,
                MEDIUM_ICON_SIZE[1],
            )

            space_needed = PADDING + BOX_BORDER_WEIGHT + PADDING + next_height

            if current_y + space_needed <= (content_y + content_height):
                current_y += PADDING

                draw.line(
                    [(content_x, current_y), (content_x + content_width, current_y)],
                    fill="black",
                    width=BOX_BORDER_WEIGHT,
                )

                current_y += BOX_BORDER_WEIGHT + PADDING
            else:
                break
        events += 1


def draw_room_info_box(draw, image, data):
    x1, y1, x2, y2 = get_box_origin("room_info")

    temp_icon = load_icon(
        os.path.join(BASE_DIR, "assets", "icons", "system", "temperature.png"),
        MEDIUM_ICON_SIZE,
    )

    humidity_icon = load_icon(
        os.path.join(BASE_DIR, "assets", "icons", "system", "humidity.png"),
        MEDIUM_ICON_SIZE,
    )

    draw.rounded_rectangle(
        BOX_COORDINATES["room_info"],
        radius=BOX_BORDER_RADIUS,
        fill="white",
        outline="black",
        width=BOX_BORDER_WEIGHT,
    )

    if data['temperature'] is None or data['humidity'] is None:
        draw.text(
            ((x2 - x1) // 2 + x1, (y2 - y1) // 2 + y1),
            "No data",
            anchor="mm",
            font=HEADER_FONT,
            fill="black",
        )
        return
    else:
        paste_icon(image, temp_icon, x1 + BOX_PADDING, y1 + BOX_PADDING)
        draw.text(
            (x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING, y1 + BOX_PADDING),
            f"{data['temperature']:.1f}°",
            font=BODY_FONT,
            fill="black",
        )

        paste_icon(
            image,
            humidity_icon,
            x1 + BOX_PADDING,
            y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING,
        )

        draw.text(
            (
                x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING,
                y1 + BOX_PADDING + MEDIUM_ICON_SIZE[1] + PADDING,
            ),
            f"{data['humidity']}%",
            font=BODY_FONT,
            fill="black",
        )


def draw_system_info_box(draw, image, data):
    x1, y1, x2, y2 = get_box_origin("system_info")

    BAR_WIDTH = 70

    cpu_fill = int((data['cpu_usage'] / 100) * BAR_WIDTH)
    mem_fill = int((data['memory_usage'] / 100) * BAR_WIDTH)
    
    cpu_radius = min(BOX_BORDER_RADIUS, cpu_fill // 2)
    mem_radius = min(BOX_BORDER_RADIUS, mem_fill // 2)
    
    cpu_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "cpu.png"), MEDIUM_ICON_SIZE)
    mem_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "memory.png"), MEDIUM_ICON_SIZE)
    temp_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "temperature.png"), MEDIUM_ICON_SIZE)
    clock_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "clock.png"), MEDIUM_ICON_SIZE)
    wifi_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "wifi.png"), MEDIUM_ICON_SIZE)
    disk_icon = load_icon(os.path.join(BASE_DIR, "assets", "icons", "system", "disk.png"), MEDIUM_ICON_SIZE)

    draw.rounded_rectangle(
        BOX_COORDINATES["system_info"],
        radius=BOX_BORDER_RADIUS,
        fill="white",
        outline="black",
        width=BOX_BORDER_WEIGHT,
    )

    # CPU
    bar_x = x1 + BOX_PADDING + MEDIUM_ICON_SIZE[0] + PADDING
    bar_y = y1 + BOX_PADDING

    paste_icon(image, cpu_icon, x1 + BOX_PADDING, bar_y)

    draw.rounded_rectangle(
        [(bar_x, bar_y), (bar_x + BAR_WIDTH, bar_y + MEDIUM_ICON_SIZE[1])],
        radius=cpu_radius,
        outline="black",
        width=BOX_BORDER_WEIGHT,
    )

    draw.rounded_rectangle(
        [(bar_x, bar_y), (bar_x + cpu_fill, bar_y + MEDIUM_ICON_SIZE[1])],
        radius=cpu_radius,
        fill="black",
    )

    # Memory
    bar_y += MEDIUM_ICON_SIZE[1] + PADDING

    paste_icon(image, mem_icon, x1 + BOX_PADDING, bar_y)

    draw.rounded_rectangle(
        [(bar_x, bar_y), (bar_x + BAR_WIDTH, bar_y + MEDIUM_ICON_SIZE[1])],
        radius=mem_radius,
        outline="black",
        width=BOX_BORDER_WEIGHT,
    )

    draw.rounded_rectangle(
        [(bar_x, bar_y), (bar_x + mem_fill, bar_y + MEDIUM_ICON_SIZE[1])],
        radius=mem_radius,
        fill="black",
    )

    # Temperature
    bar_y += MEDIUM_ICON_SIZE[1] + PADDING

    paste_icon(image, temp_icon, x1 + BOX_PADDING, bar_y)

    draw.text(
        (bar_x, bar_y),
        f"{data['cpu_temperature']:.1f}°C",
        font=BODY_FONT,
        fill="black",
    )

    # Right column
    right_x = x1 + (x2 - x1) // 2
    right_y = y1 + BOX_PADDING

    paste_icon(image, clock_icon, right_x, right_y)
    draw.text((right_x + MEDIUM_ICON_SIZE[0] + PADDING, right_y), f"{data['uptime']}", font=BODY_FONT, fill="black")

    right_y += MEDIUM_ICON_SIZE[1] + PADDING

    paste_icon(image, wifi_icon, right_x, right_y)
    draw.text((right_x + MEDIUM_ICON_SIZE[0] + PADDING, right_y), f"{data['ip_address']}", font=BODY_FONT, fill="black")

    right_y += MEDIUM_ICON_SIZE[1] + PADDING

    paste_icon(image, disk_icon, right_x, right_y)
    draw.text((right_x + MEDIUM_ICON_SIZE[0] + PADDING, right_y), f"{data['disk_usage']}%", font=BODY_FONT, fill="black")


def render_dashboard(data):
    image = Image.new("RGB", (800, 480), "white")
    draw = ImageDraw.Draw(image)

    draw_weather_box(draw, image, data["weather"])
    draw_time_box(draw)
    draw_calendar_box(draw, image, data["calendar_events"])
    draw_room_info_box(draw, image, data["room_info"])
    draw_system_info_box(draw, image, data["system_info"])

    return image


if __name__ == "__main__":
    image = render_dashboard()
    image.save(os.path.join(BASE_DIR, "images", "output.png"))