import cv2
import os
import copy
import easygui
from datetime import datetime
from src.db_utils import DataBaseOperation


def capture_continuous_frames(save_dir, cam_url, init_count=0):
    """
    Capture several continuous frames from a video feed through a camera

    Parameters:
    -----------
    save_dir: str
        Output directory where the images will be saved
    cam_url: str
        RTSP link of ip cam
    
    """
    cap = cv2.VideoCapture(cam_url)

    if not os.path.isdir(save_dir):
        print("Provided save directory is not found. Creating a new directory for it...")
        os.makedirs(save_dir)
        print(f"Successfully created {save_dir}")
    
    count = init_count

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(os.path.join(save_dir, f"{count}.png"), frame)
            count += 1

            frame = cv2.putText(frame, f"Frame Count: {count}", org=(250, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.imshow("Live View", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    cv2.destroyAllWindows()
    cap.release()

def capture_single_frame(save_dir: str = None, cam_url=0, num_of_capture: str="multiple", return_image: bool = False, spoof_test=True):
    """
    Capture single frame from a video feed through a camera. Press esc to finish.

    Parameters:
    -----------
    save_dir: str
        Output directory where the images will be saved
    cam_url: str
        RTSP link of ip cam
    num_of_capture: str
        Defines whether a single image or multiple ones will be captured
    return_image: bool
        if `return_image` is true, then the captured image will be returned from this function. For this,
        `num_of_capture` must be `single`

    
    Returns:
    --------
    original_frame: Matlike Image
        Orignal frame captured when `num_of_images` is `single`
    
    """

    if num_of_capture not in ["multiple", "single"]:
        raise Exception("num_of_images can be either 'multiple' or 'single'")
    if num_of_capture == "multiple" and save_dir is None:
        easygui.msgbox("Multiple frames will be captured, but no output directory is defined")
    cap = cv2.VideoCapture(cam_url)
    
    if save_dir:
        if not os.path.isdir(save_dir):
            print("Provided save directory is not found. Creating a new directory for it...")
            os.makedirs(save_dir)
            print(f"Successfully created {save_dir}")
    
    count = 0
    payload = {"spoofing_result": False, "image_array": None}
    original_frame = None

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            key = cv2.waitKey(1)
            if key == 27:
                cv2.destroyAllWindows()
                cap.release()
                return payload
                # break
            elif key == 32:
                original_frame = copy.deepcopy(frame)
                # _, spoofing_result = spoofing_check(original_frame)
                spoofing_result = 1
                if spoofing_result != 1:    # If fake image, this will return back with executing rest of the function
                    return payload
                else:
                    payload["spoofing_result"] = True
                frame = cv2.putText(frame, f"Press Y to confirm, Press N to discard", org=(50, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1/2, color=(255, 255, 0), thickness=1, lineType=cv2.LINE_AA)
                cv2.imshow("Captured Image", frame)
                while(True):
                    confirm_key = cv2.waitKey(1)
                    if confirm_key == 89 or confirm_key == 121:
                        payload["image_array"] = original_frame
                        # label = easygui.enterbox("Label", "Enter a label for this image: ")
                        if save_dir:
                            label = easygui.enterbox("Label", "Enter a label for this image: ")
                            cv2.imwrite(os.path.join(save_dir, f"{label}.png"), original_frame)
                            # cv2.imwrite(save_dir, original_frame)
                        cv2.destroyWindow("Captured Image")
                        count += 1
                        break

                    elif confirm_key == 78 or confirm_key == 110:
                        cv2.destroyWindow("Captured Image")
                        break

            frame = cv2.putText(frame, f"Frame Count: {count}", org=(250, 50), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=1, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)
            cv2.imshow("Live View", frame)

            if num_of_capture == "single" and count == 1:
                break

            
    cv2.destroyAllWindows()
    cap.release()

    if return_image:
        assert num_of_capture == "single", "return_image must be 'single' to return the image"
        payload["image_array"] = original_frame
    return payload

def live_feed(cam_url):
    """
    Capture several continuous frames from a video feed through a camera

    Parameters:
    -----------
    cam_url: str
        RTSP link of ip cam
    
    """
    cap = cv2.VideoCapture(cam_url)
    db_operation = DataBaseOperation()
    elapsed_time = 0.
    count = 1
    while cap.isOpened():
        t1 = datetime.now()
        ret, frame = cap.read()
        if ret:
            try:
                frame = cv2.resize(frame, (640, 480))
                cv2.imshow("Live View", frame)
            except:
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        t2 = datetime.now()
        elapsed_time += (t2 - t1).total_seconds()
        if int(elapsed_time) == count:
            # return_message = additional_func(frame, lock)
            return_message = db_operation._send_match_request(frame)
            print(f"return message: {return_message}")
            

            # print(f"Elapsed {int(elapsed_time)} seconds")
            # print(return_message)
            count += 1
    
    cv2.destroyAllWindows()
    cap.release()
