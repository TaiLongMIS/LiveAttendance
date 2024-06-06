import cv2
import requests
from sqlalchemy import URL, create_engine, text, insert, Table, DateTime
from fastapi import HTTPException
from datetime import datetime
from src.config import *




class DataBaseOperation():
    def __init__(self):
        engine = create_engine(DB_CONNECTION_STRING)
        self.connection = engine.connect()

    def _person_registration(self, user_data, image):
        
        name = user_data["name"]
        staff_id = user_data["staff_id"]
        department = user_data["department"]
        designation = user_data["designation"]

        if_exists_query = text(f"SELECT* FROM Attendance.dbo.[User] as u\
                                    WHERE u.StaffID = {staff_id}")
        
        result = self.connection.execute(if_exists_query)

        if result.first() is None:
            try:
                query = text(f"INSERT INTO [User](StaffID, Name, Department, Designation)\
                    VALUES ('{staff_id}', '{name}', '{department}', '{designation}')")
                self.connection.execute(query)
                self.connection.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error: Unable to write to the database")

        else:
            raise HTTPException(status_code=409, detail="User already registered against this staff ID")

        ## Preparing data for face recognition module

        data = {
            "id": staff_id,
            "name": name,
        }

        files = {}
        if image:
            files = {"image": (image.filename, image.file, image.content_type)}

        response = requests.post(FR_REGISTRATION_API, data=data, files=files)
        print(response)

        if response.status_code == 200:
            return {"message": "Registration successful", "status_code": 201}
        else:
            return {"message": "Registration unsucessful", "status_code": 500}

    def _person_match(self):
        pass


def send_match_request(image):
    _, image = cv2.imencode(".png", image)
    image_bytes = image.tobytes()
    files = {"image": ("frame.png", image_bytes, "image/png")}
    port = 6969
    response = requests.post(f'http://192.168.101.230:{port}/api/v1/match', files=files)
    content = response.content.decode("ascii")
    if isinstance(content, dict):
        id = content["ID"]
        name = content["NAME"]
    print(content)









def execute_query(connection):
    current_datetime = datetime.now()
    query = f"INSERT INTO [AttendanceReport](StaffID, Name, Department, Designation)\
        VALUES ('12345', 'Agdum Bagdum', 'Kingdom', 'Lord')"
    
    query = f"INSERT INTO [AttendanceReport](Date, CheckIn, Checkout, USER_ID)\
        VALUES ('{current_datetime}', '{current_datetime}', '{current_datetime}', '3')"
    
    staff_id = 31618
    user_query = text(f"SELECT ID FROM [User] WHERE StaffID = {staff_id}")
    user_id = connection.execute(user_query).first()[0]

    attendance_query = text("INSERT IGNORE INTO AttendanceReport (Date, CheckIn, Checkout, USER_ID)\
                            VALUES (:date, :checkin, :checkout, :user_id)")

    params = {
        "date": current_datetime,
        "checkin": current_datetime,
        "checkout": current_datetime,
        "user_id": user_id,
    }
    connection.execute(attendance_query, params)
    connection.commit()
