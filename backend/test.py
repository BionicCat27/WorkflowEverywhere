import json
import time
import requests

HOST = "http://127.0.0.1:5000"

def test():
    print("Doing healthcheck")
    result = requests.get(f"{HOST}/healthcheck")
    assert result.status_code == 200

    print("Clearing config")
    result = requests.put(f"{HOST}/shortcuts", json=[])
    assert result.status_code == 200
    
    print("Doing GET shortcuts")
    result = requests.get(f"{HOST}/shortcuts")
    content = result.content
    if content != "":
        content = json.loads(content)
    assert result.status_code == 200
    assert content == []

    print("Doing PUT shortcuts")
    data = [
        {
            "test": "test"
        }
    ]
    result = requests.put(f"{HOST}/shortcuts", json=data)
    assert result.status_code == 200
    result = requests.get(f"{HOST}/shortcuts")
    assert result.status_code == 200
    content = json.loads(result.content)
    assert content == data

    print("Doing POST shortcut")
    data = {
        "test2": "test"
    }
    result = requests.post(f"{HOST}/shortcuts/add", json=data)
    assert result.status_code == 400

    print("Clearing config")
    result = requests.put(f"{HOST}/shortcuts", json=[])
    assert result.status_code == 200
    
    data = {
        "name": "Open command picker",
        "intellij": "",
        "key": "shift+cmd+p",
        "vscode": "workbench.action.showCommands",
        "when": "editorTextFocus && !editorReadonly"
    }
    result = requests.post(f"{HOST}/shortcuts/add", json=data)
    assert result.status_code == 200
    result = requests.get(f"{HOST}/shortcuts")
    assert result.status_code == 200
    content = json.loads(result.content)
    assert len(content) == 1

    print("Waiting for testing time")
    time.sleep(10)
    print("Loading backups")
    result = requests.post(f"{HOST}/loadbackups")
    assert result.status_code == 200
    
    print("Finished tests")

if __name__ == "__main__":
    test()