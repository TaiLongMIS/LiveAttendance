import cv2
import requests
from sqlalchemy import create_engine, text
from fastapi import HTTPException
import pandas as pd
from datetime import datetime, date
from src.config import *
import json
import io
import os

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class DataBaseOperation():
    def __init__(self):
        engine = create_engine(DB_CONNECTION_STRING)
        self.connection = engine.connect()

    @staticmethod
    def _detect_face(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces
    
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
        if image is not None:
            files = {"image": (image.filename, image.file, image.content_type)}
        else:
            raise Exception("No image found for the registration process")

        response = requests.post(FR_REGISTRATION_API, data=data, files=files)

        if response.status_code == 200 or 201:
            return {"message": "Registration successful", "status_code": 201}
        else:
            return {"message": "Registration unsucessful", "status_code": 500}

    def _process_single_response(self, content):
        if isinstance(content, dict):
            print(content)
            staff_id = content["ID"]
            current_date = date.today().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                query = text(f"""
                            SELECT * FROM [User]
                            WHERE StaffID = {staff_id}

                            """)
                result = self.connection.execute(query).fetchone()
                if result is None:
                    return "Person is not registered"
            except:
                print("User information cannot be retrieved")

            try:
                query = text(f"""
                        SELECT id FROM AttendanceReport
                        WHERE StaffID = {staff_id} AND [Date] = '{current_date}'
                    """)
                result = self.connection.execute(query).fetchone()
            except:
                print("Filtering from `User` table unsuccessfull")

            if result:
                try:
                    update_query = text(f"""
                                        UPDATE Attendance.dbo.AttendanceReport
                                        SET CheckOut = '{current_time}'
                                        WHERE StaffID = {staff_id} AND [DATE] = '{current_date}'
                                """)
                    
                    self.connection.execute(update_query)
                    self.connection.commit()
                    self.yamaha_data(staff_id)
                except:
                    return "Attendance report couldn't be updated"
            else:
                try:
                    insert_query = text(f"""
                                        INSERT INTO Attendance.dbo.AttendanceReport (Date, CheckIn, CheckOut, StaffID)
                                        VALUES ('{current_date}', '{current_time}', '{current_time}', {staff_id})
                                """)
                    self.connection.execute(insert_query)
                    self.connection.commit()
                    
                    return {"message": "Check-in and checkout time recorded", "staff_id": staff_id, "checkin": current_time, "checkout": current_time}
                except:
                    return "First check in report creation failed"
        else:
            pass

    def _send_match_request(self, image):
        match_result = None
        faces = DataBaseOperation._detect_face(image)
        if len(faces) == 0:
            return "No face found"
        _, image = cv2.imencode(".png", image)
        image_bytes = image.tobytes()
        files = {"image": ("frame.png", image_bytes, "image/png")}

        # response = requests.post(f'{FR_MATCH_API}', files=files)
        try:
            response = requests.post(f'{FR_MULTI_MATCH_API}', files=files)
            if (response.ok):
                contents = eval(response.content.decode("ascii"))
                if isinstance(contents, list):
                    for content in contents:
                        match_result = self._process_single_response(content)
                elif isinstance(contents, dict):
                    match_result = self._process_single_response(contents)
                else:
                    print(f"matching response should be either `list` or `dict`") 

                # print(match_result)
                return match_result
            else:
                print(f"Response: {response.content}")
            
            
        except:
            print(f"Invalid URL: {FR_MULTI_MATCH_API}")
        
    def query_checkout(self, date: datetime, output_size: int)->list:
        try:
            query = text(f"""
                            SELECT TOP {output_size} * FROM Attendance.dbo.AttendanceReport
                            WHERE [Date] = '{date}'
                            ORDER BY CheckOut DESC
                        """)
            results = self.connection.execute(query).fetchall()
            
            checkout_results = zip(*list(map(lambda x: x[-2:], results)))
            checkout_time, ids = list(checkout_results)
            df = pd.DataFrame(columns=["staff_id", "checkout_time"]) 
            df["staff_id"] = ids
            df["checkout_time"] = checkout_time

            return df.to_dict(orient="records")
        
        except Exception as e:
            return e
        
    def yamaha_data(self, staff_id):
        print(f"Yamaha data method")
        params = {
            "staff_id": staff_id,
        }
        fr_get_image = requests.get(FR_GET_IMAGE_API, params=params)
        if fr_get_image.status_code == 200:
            byte_image = io.BytesIO(fr_get_image.content)
            data = {"customer_id": staff_id}
            files = {"image_url": ("rendered_image.png", byte_image, "image/png")}
            yamaha_response = requests.post(YAMAHA_API, files=files, data=data)
            print(f"yamaha_response: {yamaha_response.content}")
            print("########   ######")
        else:
            print(f"no image found in database for staff_id: {staff_id}")
            




