import os
import csv

RTSP_LINKS = ["rtsp://admin:admin1234@192.168.101.14:554"]
LOCAL_DB = "./local_db.csv"
DB_CONNECTION_STRING = "mssql+pyodbc://sa:dataport@192.168.100.128/Attendance?driver=ODBC+Driver+17+for+SQL+Server"
FR_REGISTRATION_API = "http://192.168.101.230:6969/api/v1/register"
FR_MATCH_API = "http://192.168.101.230:6969/api/v1/match"

def create_directories():
    if not os.path.exists(LOCAL_DB):
        with open(LOCAL_DB, "w+") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "ID", "Name", "Check In", "Check Out"])

# def db_connection():
