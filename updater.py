import requests
import sys
import subprocess
import os
import tempfile
from PyQt5.QtWidgets import QMessageBox
from version import VERSION

GITHUB_REPO = "PELMEN12337/museum-app"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def check_for_updates():
    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("tag_name", "").lstrip("v")
            if latest_version > VERSION:
                for asset in data.get("assets", []):
                    if asset["name"].startswith("museum_setup"):
                        return True, latest_version, asset["browser_download_url"]
    except Exception as e:
        print(f"Ошибка: {e}")
    return False, None, None


def download_and_install(download_url, parent_widget):
    try:
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "museum_setup_new.exe")

        # Скачивание с проверкой
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(installer_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Даём время на завершение старого процесса
        parent_widget.close()
        import time
        time.sleep(1)

        # Запускаем установщик с флагом, чтобы он не создавал окно консоли
        subprocess.Popen([installer_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit(0)
    except Exception as e:
        QMessageBox.critical(parent_widget, "Ошибка", f"Не удалось обновить: {e}")