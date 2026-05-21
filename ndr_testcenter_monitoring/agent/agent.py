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


def get_windows_install_date():
    if platform.system().lower() != "windows":
        return None

    try:
        import winreg

        registry_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            install_timestamp, _ = winreg.QueryValueEx(key, "InstallDate")
        return datetime.fromtimestamp(int(install_timestamp)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def get_windows_version_info():
    if platform.system().lower() != "windows":
        return platform.platform()

    try:
        import winreg

        registry_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            product_name, _ = winreg.QueryValueEx(key, "ProductName")
            display_version, _ = winreg.QueryValueEx(key, "DisplayVersion")
            current_build, _ = winreg.QueryValueEx(key, "CurrentBuild")
            try:
                ubr, _ = winreg.QueryValueEx(key, "UBR")
                build = f"{current_build}.{ubr}"
            except FileNotFoundError:
                build = str(current_build)

        return f"{product_name} {display_version} Build {build}"
    except Exception:
        return platform.platform()


def collect_system_info():
    return {
        "hostname": socket.gethostname(),
        "power_status": "online",
        "usage_status": "busy",
        "windows_version": get_windows_version_info(),
        "reinstalled_at": get_windows_install_date(),
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
