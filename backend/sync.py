import json
import os
import threading
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

CONFIG_FILE_NAME = "./config.json"

@app.route("/shortcuts", methods = ['PUT', 'GET'])
def shortcuts():
    if request.method == "PUT":
        with open(CONFIG_FILE_NAME, "w") as configFile:
            json.dump(request.get_json(), configFile, indent=2)
        return "Config Successfully Updated", 200
    elif request.method == "GET":
        config = getCurrentConfig()
        return jsonify(config), 200

@app.route("/shortcuts/add", methods=['POST'])
def addShortcut():
    config = getCurrentConfig()
    new_shortcut = json.dumps(request.get_json())
    config.append({
        "name": "",
        "vscode": "",
        "intellij": "",
    })
    with open(CONFIG_FILE_NAME, "w") as configFile:
        configFile.write(config)
    return "Shortcut successfully added", 200

@app.route("/healthcheck", methods = ['GET'])
def healthcheck():
    return "", 200

def getCurrentConfig():
    mode = "r"
    if not os.path.exists(CONFIG_FILE_NAME):
        mode = "w"
    with open(CONFIG_FILE_NAME, mode) as configFile:
        raw_config = configFile.read()
        if raw_config == "" or raw_config == None:
            raw_config = []
        else:
            raw_config = json.loads(raw_config)
        return raw_config

if __name__ == '__main__':
    app.run(debug=True)