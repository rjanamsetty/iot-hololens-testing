import requests

import api

current = 0


def changeBrightness(brightness):
    global current
    url = "https://api.lifx.com/v1/lights/all/state"

    payload = {
        "duration": 0,
        "fast": False,
        "brightness": brightness
    }
    headers = {
        "accept": "text/plain",
        "content-type": "application/json",
        "Authorization": api.lifx_api,
    }

    value = requests.put(url, json=payload, headers=headers)
    if brightness == 0: current = current + 1
    return current


if __name__ == "__main__":
    changeBrightness(0.15)
