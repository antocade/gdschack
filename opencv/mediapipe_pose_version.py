import cv2
import time
import math as m
import mediapipe as mp

import socketio
import eventlet

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

def findAngle(x1, y1, x2, y2):
    theta = m.acos( (y2 -y1)*(-y1) / (m.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ) * y1) )
    degree = int(180/m.pi)*theta
    return degree

# init the global variables

def run_posture_analysis():

    # Font type.
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Colors.
    blue = (255, 127, 0)
    red = (50, 50, 255)
    green = (127, 255, 0)
    dark_blue = (127, 20, 0)
    light_green = (127, 233, 100)
    yellow = (0, 255, 255)
    pink = (255, 0, 255)

    # hold the index of the specific landmarks I want
    LEFT_EAR = 7
    LEFT_SHOULDER = 11

    EVIL_POSTURE_THRESHOLD = 40.0 

    frame_num = 0
    
    # Initialize mediapipe pose class.
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    video_capture = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
    while video_capture.isOpened(): 

        success, frame = video_capture.read()

        h, w = frame.shape[:2] 

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Process the image and detect poses
        results = pose.process(image)
        
        # Convert back to BGR for rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw the pose annotations on the image
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            l_shoulder_x = int(results.pose_landmarks.landmark[LEFT_SHOULDER].x * w)
            l_shoulder_y = int(results.pose_landmarks.landmark[LEFT_SHOULDER].y * h)

            l_ear_x = int(results.pose_landmarks.landmark[LEFT_EAR].x * w)
            l_ear_y = int(results.pose_landmarks.landmark[LEFT_EAR].y * h)

            posture_angle = findAngle(l_shoulder_x, l_shoulder_y, l_ear_x , l_ear_y)

            if (posture_angle > EVIL_POSTURE_THRESHOLD):
                colour = red
            else:
                colour = green

            score = 100 - (((posture_angle - 10.0) / (90.0 - 10.0)) * 100 ) 

            angle_text_string = "Angle: " + str(posture_angle) + " Score: " + str(score)

            cv2.line(image, (l_shoulder_x, l_shoulder_y), (l_ear_x , l_ear_y), colour, 4)
            cv2.putText(image, angle_text_string, (10, 30), font, 0.9, colour, 2)
            
            frame_num = frame_num + 1
            if (frame_num % 10 == 0):
                sio.emit('postureScore', score)
                print(score)
                eventlet.sleep(0.02)
                frame_num = 0

        
        # Displays the result on camera feed                      
        cv2.imshow('Video', image)  
    
        # The control breaks once q key is pressed                         
        if cv2.waitKey(1) & 0xff == ord('q'):                
            break

    video_capture.release()                                  
    cv2.destroyAllWindows() 

eventlet.spawn(run_posture_analysis)
eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8468)), app)