import csv

from flask import Flask, request

import light_sensor

app = Flask(__name__)


@app.route("/")
def index():
    return "Light server up and running"


@app.route("/store", methods=['PUT'])
def store():
    data = request.data.decode("utf-8") + "\t" + light_sensor.get_lux()
    # open the TSV file in write mode
    with open("final.tsv", "w", newline="") as tsv_file:
        # create a TSV writer object
        writer = csv.writer(tsv_file, delimiter="\t")
        # write the string to the TSV file
        writer.writerow(data.split("\t"))


if __name__ == "__main__":
    app.run(host="192.168.1.6", port=8080, debug=True)
