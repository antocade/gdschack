import cv2 
import serial

profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +'haarcascade_profileface.xml')

def detect(gray, frame): 
    # detect side profile and draw rectangle around it
    profile = profile_cascade.detectMultiScale(gray, 1.3, 5)
    for(x,y,w,h) in profile:
        cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (255, 0, 0), 2) 

    return frame 

video_capture = cv2.VideoCapture(0) 
while video_capture.isOpened(): 
   # Captures video_capture frame by frame 
    _, frame = video_capture.read()  
  
    # To capture image in monochrome                     
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   
      
    # # calls the detect() function     
    canvas = detect(gray, frame)    
  
    # Displays the result on camera feed                      
    cv2.imshow('Video', canvas)  
  
    # The control breaks once q key is pressed                         
    if cv2.waitKey(1) & 0xff == ord('q'):                
        break
  
# Release the capture once all the processing is done. 
video_capture.release()                                  
cv2.destroyAllWindows() 


