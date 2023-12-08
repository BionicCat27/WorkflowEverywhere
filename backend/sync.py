import json
import os
import shutil
import threading
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

CONFIG_FILE_NAME = "./config.json"
INTELLIJ_TARGET = ""
VSCODE_KEYBINDINGS_PATH = os.path.expanduser("~/Library/Application Support/Code/User")
VSCODE_TARGET_FILENAME = "keybindings.json"
VSCODE_BACKUP_FILENAME = "keybindings_backup.json"
VSCODE_TARGET_FILEPATH = f"{VSCODE_KEYBINDINGS_PATH}/{VSCODE_TARGET_FILENAME}"
VSCODE_BACKUP_FILEPATH = f"{VSCODE_KEYBINDINGS_PATH}/{VSCODE_BACKUP_FILENAME}"

EXPECTED_SHORTCUT_KEYS = ['name', 'vscode', 'intellij', 'key', 'when']

def checkBackups():
    if not os.path.exists(VSCODE_BACKUP_FILEPATH):
        shutil.copyfile(VSCODE_TARGET_FILEPATH, VSCODE_BACKUP_FILEPATH)

@app.route("/shortcuts", methods = ['PUT', 'GET'])
def shortcuts():
    checkBackups()
    if request.method == "PUT":
        with open(CONFIG_FILE_NAME, "w") as configFile:
            json.dump(request.get_json(), configFile, indent=2)
        updateShortcutFiles()
        return "Config Successfully Updated", 200
    elif request.method == "GET":
        config = getCurrentConfig()
        return jsonify(config), 200

@app.route("/shortcuts/add", methods=['POST'])
def addShortcut():
    checkBackups()
    config = getCurrentConfig()
    request_shortcut = request.get_json()
    new_shortcut ={}
    missing_keys = getMissingKeys(request_shortcut)
    if len(missing_keys) > 0:
        return f"Must contain following keys: {missing_keys}", 400
    new_shortcut = {expected_key: request_shortcut[expected_key] for expected_key in EXPECTED_SHORTCUT_KEYS}
    config.append(new_shortcut)
    with open(CONFIG_FILE_NAME, "w") as configFile:
        json.dump(config, configFile, indent=2)
    updateShortcutFiles()
    return "Shortcut successfully added", 200

@app.route('/loadbackups', methods = ['POST'])
def loadBackups():
    checkBackups()
    shutil.copyfile(VSCODE_BACKUP_FILEPATH, VSCODE_TARGET_FILEPATH)
    os.remove(VSCODE_BACKUP_FILEPATH)
    return "Loaded backups", 200

@app.route("/healthcheck", methods = ['GET'])
def healthcheck():
    checkBackups()
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

def updateShortcutFiles():
    config = getCurrentConfig()
    for shortcut in config:
        missing_keys = getMissingKeys(shortcut)        
        if len(missing_keys) == 0:
            clearVSCodeShortcuts()
            addVSCodeShortcut(shortcut)
            # addIntellijShortcut(shortcut)

def clearVSCodeShortcuts():
    with open(VSCODE_TARGET_FILEPATH, "w") as vscodeFile:
        vscodeFile.write("[]")

def addVSCodeShortcut(shortcut):
    if not os.path.exists(VSCODE_KEYBINDINGS_PATH):
        print("Failure.")
        return
    with open(VSCODE_TARGET_FILEPATH, "a+") as vscodeFile:
        vscodeFile.seek(0)
        lines = vscodeFile.readlines()
        commentLine = ""
        vscodeConfig = lines
        if '//' in lines[0]:
            commentLine = lines[0]
            vscodeConfig = lines[1:]
        configString = ""
        for line in vscodeConfig:
            configString += str(line)
        vscodeConfig = json.loads(configString)
        new_shortcut = {}
        new_shortcut['workflowEverywhereName'] = shortcut['name']
        new_shortcut['key'] = shortcut['key']
        new_shortcut['command'] = shortcut['vscode']
        new_shortcut['when'] = shortcut['when']
        vscodeConfig.append(new_shortcut)
        vscodeFile.seek(0)
        vscodeFile.truncate(0)
        if commentLine != "":
            vscodeFile.write(commentLine)
        json.dump(vscodeConfig, vscodeFile, indent=4)

def getMissingKeys(shortcut):
    missing_keys = []
    missing_keys = [key for key in EXPECTED_SHORTCUT_KEYS if key not in shortcut]
    return missing_keys

if __name__ == '__main__':
    app.run(debug=True)