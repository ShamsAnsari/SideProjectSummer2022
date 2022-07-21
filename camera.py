import base64
from queue import Queue
import cv2
import numpy as np
import requests

IP = "143.198.96.83"
PORT = "8000"
TOKEN = "HUGO"


def run():
    video_capture = cv2.VideoCapture(0)

    flag = True
    while True:
        if flag:
            _, frame = video_capture.read()
            send(frame)
        flag = not flag
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


def send(frame):
    url = f"http://{IP}:{PORT}/receive_frame"
    img_str = cv2.imencode('.jpg', frame)[1].tostring()
    # img_str = base64.b64encode(cv2.imencode('.jpg', frame))

    headers = {"content-length": str(len(img_str)), "Authorization": TOKEN}
    data = img_str
    response = requests.post(url, data=data, headers=headers)




if __name__ == '__main__':
    run()
