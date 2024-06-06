from src.vision_utils import live_feed
from src.attendance_system import DataBaseOperation
from src.schemas import UserProfile
from src.config import *
import cv2
from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional, Annotated
import uvicorn


app = FastAPI()
db_operation = DataBaseOperation()

cap = cv2.VideoCapture(0)

@app.post("/registration/")

async def person_registration(name: str = Form(...), 
                              staff_id: int = Form(...), 
                              department: str = Form(...), 
                              designation: str = Form(...),
                              image: Annotated[UploadFile, File(description="Image for registration")] = None):
    user_data = {
        "name": name,
        "staff_id": staff_id,
        "department": department,
        "designation": designation,
    }

    db_operation._person_registration(user_data, image)
    
# def additional_function_for_person_matching(image):
    

# def person_attendance():
    

if __name__ == "__main__":
    # send_request()
    # create_directories()
    # live_feed(cap, send_match_request)
    # engine = db_connect()
    # execute_query(connection)
    # print(engine)
    uvicorn.run(app, host="127.0.0.1", port=8000)
    print('hello')