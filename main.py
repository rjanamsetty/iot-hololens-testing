import csv
import os
import sys
import time

import cv2
import numpy as np
from flask import Flask, request

import frame_handler
import lifxhttp
from lifx import Lifx

app = Flask(__name__)
lifx = Lifx()
current = 0
valid_distance = [0, 1, 2, 3, 4, 5, 6, 7, 8]
valid_angles = [0, 15, 30, 45, 60, 75, 90]


def eink(version):
    os.system("./eink.sh img/{}{}.bmp".format(app.config.get('image'), version))


@app.route("/")
def index():
    image = app.config.get('image')
    eink(7)
    return "Server up and running with {}".format(image), 200


@app.route('/frame', methods=['PUT'])
def frame():
    global current
    start = time.time()
    ppm_arr = np.frombuffer(request.data, np.uint8)
    f = cv2.imdecode(ppm_arr, cv2.IMREAD_COLOR)

    # Perform feature extraction
    ref = cv2.imread(app.config.get('image') + '.png')
    ref_img = cv2.resize(ref, (200, 200))

    try:
        data = frame_handler.find_squares(f, ref_img)
        if data:
            data = [app.config.get('image'), current, start * 1000, time.time() * 1000] + data
            return ','.join([str(elem) for elem in data])
        return "0", 200
    except:
        return "0", 200


@app.route('/store', methods=['PUT'])
def store():
    to_store = request.data.decode('UTF-8').split(',')
    print(to_store)
    f = open(app.config.get('image') + '.csv', 'a')
    writer = csv.writer(f)
    writer.writerow(to_store)
    return "Success", 200


@app.route('/light/on', methods=['POST'])
def on():
    try:
        lifxhttp.changeBrightness(1)
        return 'on', 200
    except:
        return 'Bad Gateway', 502


@app.route('/light/off', methods=['POST'])
def off():
    try:
        lifxhttp.changeBrightness(0)
        return 'off', 200
    except:
        return 'Bad Gateway', 502


@app.route('/light/brightness', methods=['POST'])
def brightness():
    global current
    try:
        value = request.args.get('value', default=0, type=float)
        print(value)
        current = lifxhttp.changeBrightness(value)
        return 'ok', 200
    except:
        return 'Bad Gateway', 502


@app.route('/eink/size', methods=['POST'])
def size():
    try:
        value = request.args.get('value', default=0, type=int)
        if value in valid_distance:
            eink(value)
            return 'ok', 200
        else:
            return 'Invalid Size', 400
    except:
        return 'Bad Gateway', 502


@app.route('/eink/tilt', methods=['POST'])
def tilt():
    try:
        value = request.args.get('value', default=0, type=int)
        if value in valid_angles:
            eink(7 if value == 0 else 0 if value == 90 else value)
            return 'ok', 200
        else:
            return 'Invalid Tilt', 400
    except:
        return 'Bad Gateway', 502


@app.route('/eink/clear', methods=['POST'])
def clear():
    try:
        os.system("./eink.sh")
        return 'ok', 200
    except:
        return 'Bad Gateway', 502


if __name__ == "__main__":
    app.config['image'] = sys.argv[1]
    # app.run(host="192.168.0.13", port=8080, debug=True)
    # app.run(host="192.168.1.34", port=8080, debug=True)
    app.run(host="192.168.1.33", port=8080, debug=True)
    # app.run(port=8080, debug=True)
