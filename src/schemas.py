from pydantic import BaseModel
from fastapi import File, UploadFile
from typing import Optional

class UserProfile(BaseModel):
    name: str
    staff_id: int
    department: str
    designation: str
