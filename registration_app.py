from src.vision_utils import live_feed
from src.db_utils import DataBaseOperation
from src.config import *
from fastapi import FastAPI, File, UploadFile, Form
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from datetime import date
import uvicorn


app = FastAPI()

db_operation = DataBaseOperation()

class DateModel(BaseModel):
    date_field: date =  Field(..., description="Pick a date")


from datetime import datetime
import logging
import uuid
import time, os
from fastapi import Request

projcet_name = 'DUMMY_PROJECT_FACE_RECOG'

if not os.path.exists('API_REQUEST_LOGS'):
    os.mkdir('API_REQUEST_LOGS')
    
# Set up logging
logging.basicConfig(
    filename='API_REQUEST_LOGS/api_access.log',
    level=logging.INFO,
    format='%(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)

def generate_unique_id():
    # Combine current timestamp (in microseconds) with a UUID
    timestamp = int(time.time() * 1000000)
    random_string = str(uuid.uuid4()).replace('-', '')
    return f"{timestamp}-{random_string}"

@app.middleware("http")
async def log_requests(request: Request, call_next):
    unique_id = generate_unique_id()
    # Log the request
    logging.info(
        "ENDPOINT_REQUEST_FOUND: "
        "{"
        f"'Unique_ID': '{unique_id}', "
        f"'Project_Name': '{projcet_name}', "
        f"'Endpoint_Name': '{str(request.url.path)}', "
        f"'Client_IP': '{request.client.host}', "
        f"'Request_Time': '{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}'"
        "}"
    )
    
    # Call the next middleware or route handler
    response = await call_next(request)
    
    return response


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

    response = db_operation._person_registration(user_data, image)
    return response


@app.post("/checkout-report/")

async def checkout_report(input_date: DateModel, num_people: int = 5):
    # print(f"Date: {input_date.date_field}")
    result = db_operation.query_checkout(input_date.date_field, num_people)
    print(result)
    return result


# live_feed(cap)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6979)