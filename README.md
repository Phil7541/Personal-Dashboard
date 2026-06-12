# E-Paper Personal Dashboard

A lightweight Raspberry Pi-powered dashboard designed for a 7.5" Waveshare e-paper display.
The project provides an always-on wall display for weather, calendar events, room sensor data, and system statistics while remaining low-power and distraction-free.

![Platform](https://img.shields.io/badge/platform-RaspberryPi-green)
![Language](https://img.shields.io/badge/language-Python-blue)

\

---

## Features

* Minute-synchronised clock rendering
* Weather forecast using Open-Meteo
* Google Calendar ICS integration
* ESP32-based room temperature and humidity monitoring
* Raspberry Pi system information display
* Per-source caching with fallback to last known valid data
* Runtime logging for debugging and monitoring
* Automatic refresh loop designed for e-paper displays
* Low-power, browser-free rendering pipeline using Pillow

---

## Screenshots

| Dashboard       | Calendar Layout |
| --------------- | --------------- |
| screenshot_here | screenshot_here |

*(Screenshots will be added once the final hardware enclosure is complete.)*

---

## Hardware

* Raspberry Pi Zero 2 W
* Waveshare 7.5" e-paper display (800×480)
* ESP32 sensor hub with SHT31 temperature/humidity sensor
* 3D-printed wall enclosure *(planned)*

The project was originally developed and tested on a Raspberry Pi 5 before being optimised for deployment on a Pi Zero 2 W.

---

## Tech Stack

### Software

* Python 3
* Pillow
* Requests
* Open-Meteo API
* iCalendar parsing
* psutil
* systemd

### Hardware / Embedded

* Raspberry Pi OS
* Waveshare e-paper driver library
* ESP32 sensor node
* SPI display interface

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/e-paper-dashboard.git
cd e-paper-dashboard
```

### 2. Create a virtual environment

```bash
python3 -m venv dashboard-env
source dashboard-env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create:

```text
src/envs/sensor_hub_ip.env
```

Example:

```env
SENSOR_HUB_IP=192.168.1.30
GOOGLE_CALENDAR_URLS=https://calendar-url-1,https://calendar-url-2
```

### 5. Run locally

```bash
python src/test.py
```

### 6. Start dashboard loop

```bash
python src/main.py
```

---

## Project Structure

```text
src/
├── main.py            # Main refresh/render loop
├── api.py             # Data fetching and caching
├── renderer.py        # Dashboard rendering logic
├── test.py            # Rendering/display testing
├── sleep.py           # Deep sleep if main fails to do so
├── logs/              # Runtime logs
│
assets/
├── fonts/
├── icons/
│
lib/
└── waveshare_epd/     # Display driver library
```

---

## Caching Strategy

Each data source is cached independently to reduce unnecessary API calls and improve reliability.

| Source       | Cache Duration |
| ------------ | -------------- |
| Weather      | 1 hour         |
| Calendar     | 15 minutes     |
| Room sensors | 5 minutes      |
| System info  | 1 minute       |

If a fetch fails, the dashboard continues using the previous valid data instead of crashing or displaying invalid values.

---

## Logging

Runtime logs are written to:

```text
src/logs/dashboard.log
```

The project is also designed to run as a `systemd` service, allowing logs to additionally be viewed using:

```bash
journalctl -u dashboard -f
```

---

## What I Learned

This project started as a relatively simple display experiment and gradually became a much larger exercise in building reliable long-running software for constrained hardware.

Some of the more interesting challenges included:

* Designing a rendering layout that worked well on an e-paper display
* Managing API failures without breaking the UI
* Handling calendar edge cases such as all-day and multi-day events
* Synchronising refresh timing with real-world clock updates
* Optimising performance for a Raspberry Pi Zero-class device
* Building a modular caching system instead of repeatedly querying external services

The project also helped improve my understanding of:

* Python application structure
* Hardware/software integration
* Long-running service reliability
* Practical UI layout logic without using a browser or frontend framework

---

## Future Improvements

* Centralised hub server for caching and logging
* Multi-device dashboard support
* Remote configuration interface
* OTA-style project updates
* Better offline indicators
* Additional sensor integrations
* Battery-backed graceful shutdown support
* Fully custom 3D-printed enclosure

---

## License

MIT License

---

## Notes

This is a personal project built primarily for learning and experimentation, with an emphasis on reliability, readability, and practical hardware integration rather than production-level scalability.

That said, it has been designed to run continuously on real hardware with minimal maintenance.
