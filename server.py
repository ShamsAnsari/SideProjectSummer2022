import argparse

from flask import Flask, redirect, url_for, request, render_template, Response, make_response, jsonify
from queue import Queue
from processor import *
import logging

app = Flask(__name__)

queue = Queue(100)
p = Processor()
log = logging.getLogger('werkzeug')
log.disabled = True

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


@app.route("/receive_frame", methods=["POST"])
def receive_frame():
    frame = request.data
    if not queue.full():
        frame = p.process(frame)
        queue.put(frame)

    response = make_response(
        jsonify(
            {"message": "ok"}
        ),
        200,
    )

    response.headers["Content-Type"] = "application/json"

    return response


def generate():
    while True:
        if not queue.empty():
            frame = queue.get()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(frame) + b'\r\n')






@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)

    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=False,
                    help="ip address of the device",default='143.198.96.83')
    ap.add_argument("-o", "--port", type=int, required=False, default='8000',
                    help="ephemeral port number of the server (1024 to 65535)")
    args = vars(ap.parse_args())
    app.run(host=args['ip'], port=args['port'])
