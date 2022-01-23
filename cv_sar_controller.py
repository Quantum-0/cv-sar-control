#!/usr/bin/env python3

# Copyright (c) Quantum0 2022

# ===== CONFIG =====

# CV Config
min_detection_confidence_face = 0.5
min_tracking_confidence_face = 0.5
min_detection_confidence_hand = 0.5
min_tracking_confidence_hand = 0.5
# Detecting Config
threshold_close_center = 0.6
threshold_yes = 3.5
centification_coeficient = (0.05, 0.01)
x_amplitude_decrease_coeficient = 0.99
time_to_say_no = 0.85
shake_times_to_say_no = 4
min_amplitude_to_say_no = 2
sleep_after_detection = 0.5
max_time_to_lower_head_to_say_yes = 0.225
max_time_to_raise_head_to_say_yes = 0.5
exponential_smoothing_for_mouth = 0.02
mouth_width_change_for_heart = (0.5, 0.87, 1.02, 1.45)  # width min/max and height min/max

# ==================

from datetime import datetime, timedelta
from time import sleep
import numpy as np
import cv2
import mediapipe as mp
from sar_adapter import SARCommand, execute_in_sar


# Create meshes
face_mesh = mp.solutions.face_mesh.FaceMesh(
    min_detection_confidence=min_detection_confidence_face,
    min_tracking_confidence=min_tracking_confidence_face
)
hands_mesh = mp.solutions.hands.Hands(
    min_detection_confidence=min_detection_confidence_hand,
    min_tracking_confidence=min_tracking_confidence_hand
)
cap = cv2.VideoCapture(0)

center_x = 0
center_y = 0
zero_intersections_x = []
sign_x = True
is_down = False
max_left = 0
max_right = 0
was_at_center_yes = datetime.now()
was_down_time = datetime.now()
mouth_w = 50
mouth_h = 10
averange_mw = 50
averange_mh = 10
is_hand = False


while cap.isOpened():
    success, image = cap.read()

    # Flip the image horizontally for a later selfie-view display
    # Also convert the color space from BGR to RGB
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # To improve performance
    image.flags.writeable = False

    # Get the result
    results = face_mesh.process(image)

    # To improve performance
    image.flags.writeable = True

    # Convert the color space from RGB to BGR
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    img_h, img_w, img_c = image.shape
    face_3d = []
    face_2d = []

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for idx, lm in enumerate(face_landmarks.landmark):
                if idx == 33 or idx == 263 or idx == 1 or idx == 61 or idx == 291 or idx == 199 or idx == 78 or idx == 308 or idx == 11 or idx == 16:
                    if idx == 1:
                        nose_2d = (lm.x * img_w, lm.y * img_h)
                        nose_3d = (lm.x * img_w, lm.y * img_h, lm.z * 8000)
                    elif idx == 78:
                        mouth_left = (lm.x * img_w, lm.y * img_h)
                    elif idx == 308:
                        mouth_right = (lm.x * img_w, lm.y * img_h)
                    elif idx == 11:
                        mouth_up = (lm.x * img_w, lm.y * img_h)
                    elif idx == 16:
                        mouth_down = (lm.x * img_w, lm.y * img_h)

                    x, y = int(lm.x * img_w), int(lm.y * img_h)

                    # Get the 2D Coordinates
                    face_2d.append([x, y])

                    # Get the 3D Coordinates
                    face_3d.append([x, y, lm.z])

                    # Convert it to the NumPy array
            face_2d = np.array(face_2d, dtype=np.float64)

            # Convert it to the NumPy array
            face_3d = np.array(face_3d, dtype=np.float64)

            # The camera matrix
            focal_length = 1 * img_w

            cam_matrix = np.array([[focal_length, 0, img_h / 2],
                                   [0, focal_length, img_w / 2],
                                   [0, 0, 1]])

            # The Distance Matrix
            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            # Solve PnP
            success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

            # Get rotational matrix
            rmat, jac = cv2.Rodrigues(rot_vec)

            # Get angles
            angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

            # Get the y rotation degree
            x = angles[1] * 360
            y = angles[0] * 360

            center_x = x * centification_coeficient[0] + center_x * (1-centification_coeficient[0])
            center_y = y * centification_coeficient[1] + center_y * (1-centification_coeficient[1])

            # Centered coords
            x = x - center_x
            y = y - center_y
            if x > 0:
                max_right = max(x, max_right)
            else:
                max_left = max(-x, max_left)
            max_left *= x_amplitude_decrease_coeficient
            max_right *= x_amplitude_decrease_coeficient

            # NO handler
            if (x > threshold_close_center and sign_x is False) or (x < -threshold_close_center and sign_x is True):
                sign_x = x > 0
                zero_intersections_x.append(datetime.now())
                zero_intersections_x = [x for x in zero_intersections_x if x > (datetime.now() - timedelta(seconds=time_to_say_no))]
                if len(zero_intersections_x) >= shake_times_to_say_no and max_left + max_right > min_amplitude_to_say_no:
                    print('NO')
                    execute_in_sar(SARCommand.No)
                    sleep(sleep_after_detection)
                    zero_intersections_x.clear()
                    max_left = 0
                    max_right = 0

            # YES handler
            if is_down and y > - threshold_close_center:
                t1 = was_down_time - was_at_center_yes
                t2 = datetime.now() - was_down_time
                # print(t1, t2)
                if t1.total_seconds() < max_time_to_lower_head_to_say_yes \
                        and t2.total_seconds() < max_time_to_raise_head_to_say_yes:
                    print('YES')
                    execute_in_sar(SARCommand.Yes)
                    sleep(sleep_after_detection)
                is_down = False
                was_at_center_yes = datetime.now()
            elif not is_down and y < - threshold_yes:
                was_down_time = datetime.now()
                is_down = True
            elif y > - threshold_close_center:
                was_at_center_yes = datetime.now()

            # <3 handler
            mouth_w = np.linalg.norm(np.array(mouth_left)-np.array(mouth_right))
            mouth_h = np.linalg.norm(np.array(mouth_up)-np.array(mouth_down))
            # print(mouth_w, mouth_h)
            averange_mw = mouth_w * exponential_smoothing_for_mouth + averange_mw * (1-exponential_smoothing_for_mouth)
            averange_mh = mouth_h * exponential_smoothing_for_mouth + averange_mh * (1-exponential_smoothing_for_mouth)
            if mouth_width_change_for_heart[0] < (mouth_w / averange_mw) < mouth_width_change_for_heart[1]\
                    and mouth_width_change_for_heart[2] < (mouth_h / averange_mh) < mouth_width_change_for_heart[3]:
                print('<3')
                execute_in_sar(SARCommand.Heart)
                sleep(sleep_after_detection)

        # Try find hand
        hands_res = hands_mesh.process(image)
        if hands_res.multi_handedness:
            if not is_hand:
                print('Hewwo')
                execute_in_sar(SARCommand.Hello)
                sleep(sleep_after_detection)
                is_hand = True
        else:
            is_hand = False

        # Display the nose direction
        nose_3d_projection, jacobian = cv2.projectPoints(nose_3d, rot_vec, trans_vec, cam_matrix, dist_matrix)

        p1 = (int(nose_2d[0]), int(nose_2d[1]))
        p2 = (int(nose_3d_projection[0][0][0]), int(nose_3d_projection[0][0][1]))

        cv2.line(image, p1, p2, (255, 0, 0), 2)
        cv2.line(image, (int(mouth_left[0]), int(mouth_left[1])), (int(mouth_right[0]), int(mouth_right[1])),
                 (0, 0, 255), 2)
        cv2.line(image, (int(mouth_up[0]), int(mouth_up[1])), (int(mouth_down[0]), int(mouth_down[1])),
                 (0, 0, 255), 2)

        # Add the text on the image
        # cv2.putText(image, text, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Head Pose Estimation', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
