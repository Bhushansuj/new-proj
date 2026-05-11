import getpass
import os
import platform
import socket
import time
from datetime import datetime

import requests

API_URL = os.getenv("NDR_API_URL", "http://127.0.0.1:8000/agent/status")
API_TOKEN = os.getenv("NDR_AGENT_TOKEN", "ndr-agent-token")
INTERVAL_SECONDS = int(os.getenv("NDR_AGENT_INTERVAL", "60"))


def collect_system_info():
    return {
        "hostname": socket.gethostname(),
        "power_status": "online",
        "usage_status": "busy",
        "windows_version": platform.platform(),
        "last_user": getpass.getuser(),
        "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def send_status():
    data = collect_system_info()
    headers = {"X-API-Token": API_TOKEN}

    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        print(response.json())
    except Exception as error:
        print("Fehler beim Senden:", error)


if __name__ == "__main__":
    while True:
        send_status()
        time.sleep(INTERVAL_SECONDS)
