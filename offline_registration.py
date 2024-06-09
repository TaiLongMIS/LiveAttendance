import cv2
from easygui import *
from src.vision_utils import capture_single_frame
from src.db_utils import DataBaseOperation
from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
import io

db_operation = DataBaseOperation()

def person_registration():
    """
    Performs the registration process for a person by capturing an image and 
    embedding that. This embedding is stored into the database against the 
    unique id of that person.

    """
    
    def gui_enter_box():
        enter_box_text = "Enter the following information"
        enter_box_title = "Registration for Attendance System"
        enter_box_input_list = ["Name", "StaffID", "Department", "Designation"]
        enter_box_default_list = ["Your Name", "420420", "MIS", "MLE"]

        inputs = multenterbox(enter_box_text, enter_box_title,
                            enter_box_input_list, enter_box_default_list)
        try:
            person_info = {enter_box_input_list[i]: inputs[i] for i in range(len(enter_box_input_list))}
            return person_info
        except:
            return
        
    person_info = gui_enter_box()


    if person_info is not None:
        name, staff_id, department, designation = person_info["Name"], person_info["StaffID"], person_info["Department"], person_info["Designation"]

        user_data = {
            "name": name,
            "staff_id": staff_id,
            "department": department,
            "designation": designation,
        }

        frame = capture_single_frame(cam_url=0, num_of_capture="single", return_image=True)
        _, image = cv2.imencode(".png", frame["image_array"])
        byte_io = io.BytesIO(image)
        byte_io.seek(0)
        upload_file = StarletteUploadFile(filename="image.png", file=byte_io)
        response = db_operation._person_registration(user_data, upload_file)

if __name__ == "__main__":
    person_registration()
