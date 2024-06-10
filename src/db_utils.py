import cv2
import requests
from sqlalchemy import create_engine, text
from fastapi import HTTPException
from datetime import datetime, date
from src.config import *

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

        if response.status_code == 200:
            return {"message": "Registration successful", "status_code": 201}
        else:
            return {"message": "Registration unsucessful", "status_code": 500}


    def _send_match_request(self, image):
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
                content = eval(response.content.decode("ascii"))
                print(f"Content: {content}")
                print(f"type: {type(content)}")
                if isinstance(content, dict):
                    staff_id = content["ID"]
                    current_date = date.today().strftime('%Y-%m-%d')
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    query = text(f"""
                            SELECT id FROM AttendanceReport
                            WHERE StaffID = {staff_id} AND [Date] = '{current_date}'
                        """)
                    result = self.connection.execute(query).fetchone()
                    print("Fetched the result")
                    if result:
                        update_query = text(f"""
                                            UPDATE Attendance.dbo.AttendanceReport
                                            SET CheckOut = '{current_time}'
                                            WHERE StaffID = {staff_id}
                                    """)
                        self.connection.execute(update_query)
                        self.connection.commit()
                    else:
                        insert_query = text(f"""
                                            INSERT INTO Attendance.dbo.AttendanceReport (Date, CheckIn, CheckOut, StaffID)
                                            VALUES ('{current_date}', '{current_time}', '{current_time}', {staff_id})
                                    """)
                        self.connection.execute(insert_query)
                        self.connection.commit()
                        
                        return {"message": "Check-in and checkout time recorded", "staff_id": staff_id, "checkin": current_time, "checkout": current_time}
                else:
                    pass
            else:
                pass
        except:
            print(f"Invalid URL: {FR_MULTI_MATCH_API}")


# class DBManager():
#     db_operation = None

#     @classmethod
#     def load_engine(cls):
#         cls.db_operation = DataBaseOperation()