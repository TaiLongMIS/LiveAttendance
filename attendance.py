import cv2
from src.config import *
import time
from typing import Union
cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

def detect_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

def dummy_function(frame):
    print("Yes I'm working. \n")
    return frame

def process_frame(cap = cap,
                  rtsp_url : Union[str, int] = None, 
                  interval : float = 1.0, 
                  additional_function = dummy_function):
    if rtsp_url is None:
        print('No RTSP link was provided, default webcam is loaded.')
    else:
        print(f'Connecting to RTSP . . .')
        cap = cv2.VideoCapture(rtsp_url)
    
    last_time = time.time()
    print(cap.isOpened())
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            current_time = time.time()
            if current_time - last_time >= interval:
                num_of_faces = len(detect_face(frame))
                last_time = current_time 
                if num_of_faces >= 1:
                    additional_function(frame)
        else:
            print("Error: Could not read frame")
            break
    cap.release()
    
if __name__ == "__main__":
    # cap = cv2.VideoCapture(0)
    process_frame(rtsp_url=0)