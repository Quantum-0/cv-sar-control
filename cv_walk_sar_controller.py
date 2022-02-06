from datetime import datetime
import math

import cv2
import mediapipe as mp
import numpy as np
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

av_angle = 90
av_angle_2 = 90
av_angle_3 = 90
cur = -1
dir = {0: 's', 1: 'd', 2: 'a', 3: 'w'}
go = 0
last_jump = datetime.now()
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.2,
    min_tracking_confidence=0.2, max_num_hands=1) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    a = np.double(image)
    b = a * 0
    image = np.uint8(b)
    if results.multi_hand_landmarks:
      # print(results.multi_handedness)
      for hand_landmarks in results.multi_hand_landmarks:
        for idx, lm in enumerate(hand_landmarks.landmark):
            if idx == 8:
                target = (lm.x, lm.y)
            elif idx == 6:
                source = (lm.x, lm.y)
            elif idx == 12:
                target_2 = (lm.x, lm.y)
            elif idx == 10:
                source_2 = (lm.x, lm.y)
            elif idx == 4:
                target_3 = (lm.x, lm.y)
            elif idx == 2:
                source_3 = (lm.x, lm.y)
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
        angle = math.degrees(math.atan2(target[0] - source[0], target[1] - source[1]))
        angle_2 = math.degrees(math.atan2(target_2[0] - source_2[0], target_2[1] - source_2[1]))
        angle_3 = math.degrees(math.atan2(target_3[0] - source_3[0], target_3[1] - source_3[1]))
        a = angle - av_angle
        if a > 180:
            a -= 360
        elif a < -180:
            a += 360
        av_angle += a / 3
        if av_angle > 180:
            av_angle -= 360
        elif av_angle < -180:
            av_angle += 360
        a = angle_2 - av_angle_2
        if a > 180:
            a -= 360
        elif a < -180:
            a += 360
        av_angle_2 += a / 3
        if av_angle_2 > 180:
            av_angle_2 -= 360
        elif av_angle_2 < -180:
            av_angle_2 += 360
        a = angle_3 - av_angle_3
        if a > 180:
            a -= 360
        elif a < -180:
            a += 360
        av_angle_3 += a / 3
        if av_angle_3 > 180:
            av_angle_3 -= 360
        elif av_angle_3 < -180:
            av_angle_3 += 360

        a = angle - angle_3
        if a > 180:
            a -= 360
        elif a < -180:
            a += 360
        print(a)
        jumping = abs(a) > 55

        prev_cur = cur
        # if 45 > av_angle > -45:
        #     cur = 0
        #     print('Down')
        # elif -45 > av_angle > -135:
        #     cur = 1
        #     print('Right')
        # elif 45 < av_angle < 135:
        #     cur = 2
        #     print('Left')
        # else:
        #     cur = 3
        #     print('Up')
        if av_angle < -135 or av_angle > 135:
            if av_angle_2 < -135 or av_angle_2 > 135:
                cur = 3
            else:
                cur = 0
        elif -45 > av_angle > -135:
            if -45 > av_angle_2 > -135:
                cur = 1
            else:
                cur = 2
        if prev_cur != cur:
            if prev_cur != -1:
                pyautogui.keyUp(dir[prev_cur])
            pyautogui.keyDown(dir[cur])
        if jumping:
            if (datetime.now() - last_jump).total_seconds() > 0.5:
                last_jump = datetime.now()
                pyautogui.press('space')
                print('Jump!')
        go = 1
    else:
        if go > 0:
            go -= 0.2
        else:
            if cur != -1:
                pyautogui.keyUp(dir[cur])
            prev_cur = -1
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()