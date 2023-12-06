import json
import requests

HOST = "http://127.0.0.1:5000"

def test():
    print("Doing healthcheck")
    result = requests.get(f"{HOST}/healthcheck")
    assert result.status_code == 200
    
    print("Doing GET shortcuts")
    result = requests.get(f"{HOST}/shortcuts")
    content = json.loads(result.content)
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
    content = json.loads(result.content)
    print(content)
    assert result.status_code == 200
    assert content == data
    
    

    
    print("Finished tests")

if __name__ == "__main__":
    test()