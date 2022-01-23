# ===== CONFIG =====

HEART_EMOTION_BUTTON = 'num4'
HELLO_EMOTION_BUTTON = 'num6'
DISABLE_SAR_INTERACTION = False
WINDOW_NAME = 'Super Animal Royale'
NO_COORDS = (0, 150)
YES_COORDS = (-100, 120)
TIMINGS = [0.04, 0.04, 0.07]

# ==================

from enum import Enum
from time import sleep
from typing import Tuple

try:
    from pyautogui import move, keyDown, keyUp, press
except ImportError:
    print('Cannot import pyautogui')
    print('Please install that library to allow script interact with SAR o^o')
    if not DISABLE_SAR_INTERACTION:
        exit(1)
    else:
        def move(x, y): pass
        def press(_): pass
        def keyDown(_): pass
        def keyUp(_): pass


try:
    from win32gui import GetWindowText, GetForegroundWindow
    WIN32GUI_INSTALLED = True
except ImportError:
    print('win32gui library is not installed')
    print('That library is used to check if SAR window is foreground')
    print('Script will work without that library, but it will work in any window')
    print('Recommend you to install that dependency for more comfortable using ^w^')
    WIN32GUI_INSTALLED = False
    def GetWindowText(_): return 'Super Animal Royale'
    def GetForegroundWindow(): return None


class SARCommand(Enum):
    Hello = 'hello'
    Heart = '<3'
    Yes = 'yes'
    No = 'no'


def execute_in_sar(command: SARCommand) -> bool:
    """
    Interacts with the game, executing selected comand
    :param command: Action, what to do in the game
    :return: successful
    """
    if GetWindowText(GetForegroundWindow()) != WINDOW_NAME:
        return False
    if command == SARCommand.Hello:
        press(HELLO_EMOTION_BUTTON)
    elif command == SARCommand.Heart:
        press(HEART_EMOTION_BUTTON)
    elif command in [SARCommand.Yes, SARCommand.No]:
        coords: Tuple[int, int] = YES_COORDS if command == SARCommand.Yes else NO_COORDS
        keyDown('z')
        sleep(TIMINGS[0])
        move(*coords)
        sleep(TIMINGS[1])
        keyUp('z')
        sleep(TIMINGS[2])
        coords = (-coords[0], -coords[1])
        move(*coords)
    else:
        raise Exception('Command is not supported')
    return True
