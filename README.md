# Computer Vision SAR Controller

## About
This script allows [Super Animal Royale](https://animalroyale.com/) player to control game with their head.
It uses your web-camera and computer vision for detecting your head and hand.

Available emotions and quick phrases:
- Yes (a nod of the head)
- No (head shaking)
- Heart/Kiss (make your lips like when you kissing)
- Hello (shake your hand in front of a camera)

In addition, there is a hardware solution, based on ESP8266 (with Arduino framework) and gyroscope sensor (ITG3200).
It can be placed on your headset for example. Microcontroller detects your head shaking with a gyroscope and sends
 information about it in your local Wi-Fi network to your computer, where another scripts handles UDP packets and
 interacts with SAR. This solution supports only "Yes" and "No" quick phrases.

## Files
- **cv_sar_controller.py** - Computer Vision controller for SAR (Main executable if you use camera)
- **hw_sar_controller.py** - UDP Handler for packets from microcontroller (Main executable if you use hardware solution)
- **esp_head_shaking_tracker.ino** - Arduino Sketch for ESP8266 with connected ITG3200 (Don't forget to set your Wi-Fi SSID and password)
- **sar_adapter.py** - Just a small module helps both main scripts to interact with game. Some kind of API, dunno.

## Dependencies & Requirements

### For CV Solution
- **Python 3.9+ interpreter**
- **win32gui**
- **opencv-python**
- **mediapipe**

### For HW Solution
- **Python 3.7+ interpreter**
- **win32gui**
- **ESP8266 Module**
- **ITG3200 Sensor**

## Install Instruction (for CV solution)

- Install [Python Interpreter](https://www.python.org/)
- Install requirements with PIP: `pip install mediapipe opencv-python pywin32`
- Run the script (cv_sar_controller.py) with the interpreter
- Open the game and have fun

## Demo

I hope I'll add some photos/videos later >w<

## Releases

I hope I'll found a way to compile it into executable EXE-file to simplify installing process >~<
