import csv
import sys
import time

import cv2
import numpy as np
from flask import Flask, request

import frame_handler

app = Flask(__name__)


@app.route("/")
def index():
    return "Server up and running with {!r}".format(app.config.get('image'))


@app.route('/frame', methods=['PUT'])
def frame():
    start = time.time()
    ppm_arr = np.frombuffer(request.data, np.uint8)
    f = cv2.imdecode(ppm_arr, cv2.IMREAD_COLOR)

    # Perform feature extraction
    ref = cv2.imread(app.config.get('image') + '.png')
    ref_img = cv2.resize(ref, (200, 200))

    try:
        data = frame_handler.find_squares(f, ref_img)
        if data:
            data = [start * 1000, time.time() * 1000] + data
            return ','.join([str(elem) for elem in data])
        return "0"
    except:
        return "0"


@app.route('/store', methods=['PUT'])
def store():
    to_store = request.data.decode('UTF-8').split(',')
    print(to_store)
    f = open('hololens.csv', 'a')
    writer = csv.writer(f)
    writer.writerow(to_store)
    return "Success"


if __name__ == "__main__":
    app.config['image'] = sys.argv[1]
    # app.run(host="192.168.0.13", port=8080, debug=True)
    app.run(host="127.0.0.1", port=8080, debug=True)
