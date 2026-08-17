import cv2
import numpy as np

def detect_movement(frames):
    diffs = []

    for i in range(1, len(frames)):
        diff = cv2.absdiff(frames[i-1], frames[i])
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        score = np.sum(gray)
        diffs.append(score)

    avg_movement = np.mean(diffs)

    return avg_movement > 500000  # seuil à ajuster