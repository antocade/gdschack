import cv2
import time
import math as m
import mediapipe as mp
import socketio
import eventlet
from flask import Flask, Response
import threading
import serial

COM = 'COM3'
BAUD = 9600

ser = serial.Serial(COM, BAUD, timeout=.1)

sio = socketio.Server(cors_allowed_origins='*')
app_socket = socketio.WSGIApp(sio)
app_flask = Flask(__name__)

output_frame = None
lock = threading.Lock()

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

def findAngle(x1, y1, x2, y2):
    theta = m.acos((y2 - y1) * (-y1) / (m.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * y1))
    degree = int(180 / m.pi) * theta
    return degree

def generate_video():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue
            ret, buffer = cv2.imencode('.jpg', output_frame)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app_flask.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_posture_analysis():
    font = cv2.FONT_HERSHEY_SIMPLEX
    blue = (255, 127, 0)
    red = (50, 50, 255)
    green = (127, 255, 0)
    dark_blue = (127, 20, 0)
    light_green = (127, 233, 100)
    yellow = (0, 255, 255)
    pink = (255, 0, 255)
    LEFT_EAR = 7
    LEFT_SHOULDER = 11
    EVIL_POSTURE_THRESHOLD = 40.0
    frame_num = 0
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    video_capture = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    while video_capture.isOpened():
        success, frame = video_capture.read()
        h, w = frame.shape[:2]
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            l_shoulder_x = int(results.pose_landmarks.landmark[LEFT_SHOULDER].x * w)
            l_shoulder_y = int(results.pose_landmarks.landmark[LEFT_SHOULDER].y * h)
            l_ear_x = int(results.pose_landmarks.landmark[LEFT_EAR].x * w)
            l_ear_y = int(results.pose_landmarks.landmark[LEFT_EAR].y * h)
            posture_angle = findAngle(l_shoulder_x, l_shoulder_y, l_ear_x, l_ear_y)
            
            if posture_angle > EVIL_POSTURE_THRESHOLD:
                ser.write(1)
                colour = red
            else:
                colour = green
                ser.write(0)

            score = 100 - (((posture_angle - 10.0) / (90.0 - 10.0)) * 100)
            angle_text_string = "Angle: " + str(posture_angle) + " Score: " + str(score)

            cv2.line(image, (l_shoulder_x, l_shoulder_y), (l_ear_x, l_ear_y), colour, 4)
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, colour, 2)

            frame_num += 1
            if frame_num % 10 == 0:
                sio.emit('postureScore', score)
                print(score)
                eventlet.sleep(0.02)
                frame_num = 0

        global output_frame, lock
        with lock:
            output_frame = image.copy()

        cv2.imshow('Video', image)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

threading.Thread(target=lambda: app_flask.run(host='0.0.0.0', port=6864), daemon=True).start()
eventlet.spawn(run_posture_analysis)
eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8468)), app_socket)
