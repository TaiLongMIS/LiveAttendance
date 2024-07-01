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
    uvicorn.run(app, host="0.0.0.0", port=8000)