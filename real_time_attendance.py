from src.vision_utils import live_feed
import cv2
from src.config import *
from src.db_utils import DataBaseOperation

db_operation = DataBaseOperation()
cap = cv2.VideoCapture(0)



if __name__ == "__main__":
    live_feed(cap, db_operation._send_match_request)