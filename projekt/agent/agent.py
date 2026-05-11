import requests

# The exact URL for your local server
API_URL = "http://127.0.0.1:8000/update"

# The security token from your project's Security Concept
HEADERS = {
    "Authorization": "Bearer NDR-SECRET-TOKEN"
}

# Data representing one of your 35 physical test systems
data = {
    "hostname": "NDR-PH-01",
    "os_build": "22631",
    "status": "online",
    "is_virtual": False
}

def test_connection():
    try:
        response = requests.post(API_URL, json=data, headers=HEADERS)
        if response.status_code == 200:
            print("✅ Success! Data sent to NDR Backend.")
        else:
            print(f"❌ Failed! Server returned: {response.status_code}")
            print(f"Details: {response.text}")
    except Exception as e:
        print(f"❌ Error: Could not connect to server. Is Uvicorn running? \n{e}")

if __name__ == "__main__":
    test_connection()