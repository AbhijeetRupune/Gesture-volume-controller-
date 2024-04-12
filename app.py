import os
import sys
import cv2
import mediapipe as mp
from math import hypot
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
from flask import Flask, Response
import webbrowser

app = Flask(__name__)

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands 
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volMin,volMax = volume.GetVolumeRange()[:2]

def gen():
    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        lmList = []
        if results.multi_hand_landmarks:
            for handlandmark in results.multi_hand_landmarks:
                for id, lm in enumerate(handlandmark.landmark):
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy]) 
                mpDraw.draw_landmarks(img, handlandmark, mpHands.HAND_CONNECTIONS)

        if lmList!= []:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]

            cv2.circle(img, (x1, y1), 4, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 4, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

            length = hypot(x2 - x1, y2 - y1)

            vol = np.interp(length, [15, 220], [volMin, volMax])
            print(vol, length)
            volume.SetMasterVolumeLevel(vol, None)

            # Hand range 15 - 220
            # Volume range -63.5 - 0.0

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000/')
    app.run(host='0.0.0.0', debug=True, threaded=True)