from src.vision_utils import live_feed
import cv2
from src.config import *
from src.db_utils import DataBaseOperation
import multiprocessing

db_operation = DataBaseOperation()
# cap = cv2.VideoCapture(RTSP_LINKS[0])



if __name__ == "__main__":
    processes = []
    lock = multiprocessing.Lock()
    for rtsp_link in RTSP_LINKS:
        process = multiprocessing.Process(target=live_feed, args=(rtsp_link,))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()

    # live_feed(cap, db_operation._send_match_request)