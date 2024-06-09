from src.vision_utils import live_feed
from src.db_utils import DataBaseOperation
from src.config import *
import cv2
from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional, Annotated
import uvicorn


app = FastAPI()

db_operation = DataBaseOperation()



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


    







# live_feed(cap)




if __name__ == "__main__":
    # send_request()
    # create_directories()
    
    
    
    # print(engine)
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # image = cv2.imread("4.png")
    # db_operation.send_match_request(image)