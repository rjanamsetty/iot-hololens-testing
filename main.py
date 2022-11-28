import csv
import os
import sys
import time

import cv2
import numpy as np
from flask import Flask, request

import frame_handler
from lifx import Lifx

app = Flask(__name__)
lifx = Lifx()


def eink(version):
    os.system("./eink.sh img/{}{}.bmp".format(app.config.get('image'), version))


@app.route("/")
def index():
    image = app.config.get('image')
    eink(75)
    return "Server up and running with {}".format(image), 200


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
        return "0", 200
    except:
        return "0", 200


@app.route('/store', methods=['PUT'])
def store():
    to_store = request.data.decode('UTF-8').split(',')
    print(to_store)
    f = open('hololens.csv', 'a')
    writer = csv.writer(f)
    writer.writerow(to_store)
    return "Success", 200


@app.route('/light/toggle', methods=['POST'])
def toggle():
    try:
        state = lifx.toggle()
        return state, 200
    except:
        return 'Bad Gateway', 502


@app.route('/light/on', methods=['POST'])
def on():
    try:
        lifx.on()
        return 'on', 200
    except:
        return 'Bad Gateway', 502


@app.route('/light/off', methods=['POST'])
def off():
    try:
        lifx.off()
        return 'off', 200
    except:
        return 'Bad Gateway', 502


@app.route('/light/brightness', methods=['POST'])
def brightness():
    try:
        value = request.args.get('value', default=0, type=int)
        if value < 0 or value > 65535:
            return 'Invalid Brightness', 400
        else:
            lifx.set_brightness(value)
            return 'ok', 200
    except:
        return 'Bad Gateway', 502


@app.route('/light/power')
def get_power():
    try:
        return lifx.power_state(), 200
    except:
        return 'Bad Gateway', 502


@app.route('/eink/size', methods=['POST'])
def size():
    try:
        value = request.args.get('value', default=0, type=int)
        if value == 25 or value == 50 or value == 75:
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
        if value == 0 or value == 30 or value == 60:
            eink(75 if value == 0 else value)
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
    app.run(host="192.168.1.33", port=8080, debug=True)
