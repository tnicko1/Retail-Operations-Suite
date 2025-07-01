import sys
import os
import requests
import tempfile
import subprocess
import zipfile
import shutil
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# --- Configuration ---
GITHUB_REPO_OWNER = "YOUR_GITHUB_USERNAME"
GITHUB_REPO_NAME = "YOUR_REPOSITORY_NAME"
# This is now the ZIP file you will upload to GitHub releases.
RELEASE_ASSET_NAME = "Retail-Operations-Suite.zip"
# The name of the executable inside the zip file
EXECUTABLE_NAME = "Retail Operations Suite.exe"
CURRENT_VERSION = "1.0.0"


def get_latest_release_info():
    api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest release info: {e}")
        return None


def compare_versions(current_version, latest_version_tag):
    if latest_version_tag.startswith('v'):
        latest_version_tag = latest_version_tag[1:]
    current_parts = list(map(int, current_version.split('.')))
    latest_parts = list(map(int, latest_version_tag.split('.')))
    return latest_parts > current_parts


def check_for_updates(parent_window):
    print("Checking for updates...")
    release_info = get_latest_release_info()
    if not release_info:
        print("Could not retrieve release information.")
        return

    latest_version = release_info.get("tag_name")
    if not latest_version:
        print("Could not determine the latest version from release info.")
        return

    print(f"Current version: {CURRENT_VERSION}, Latest version on GitHub: {latest_version}")

    if compare_versions(CURRENT_VERSION, latest_version):
        release_notes = release_info.get("body", "No release notes provided.")
        reply = QMessageBox.information(
            parent_window,
            "Update Available",
            f"A new version ({latest_version}) is available!\n\n"
            f"<b>Release Notes:</b>\n{release_notes}\n\n"
            "Would you like to download and install it now? The application will restart.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            download_and_install_update(parent_window, release_info)
    else:
        print("Application is up to date.")


def download_and_install_update(parent_window, release_info):
    assets = release_info.get("assets", [])
    download_url = None
    for asset in assets:
        if asset.get("name") == RELEASE_ASSET_NAME:
            download_url = asset.get("browser_download_url")
            break

    if not download_url:
        QMessageBox.critical(parent_window, "Error", "Could not find the release ZIP file in the latest release.")
        return

    try:
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, RELEASE_ASSET_NAME)

        progress = QProgressDialog("Downloading update...", "Cancel", 0, total_size, parent_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        bytes_downloaded = 0
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if progress.wasCanceled():
                    return
                f.write(chunk)
                bytes_downloaded += len(chunk)
                progress.setValue(bytes_downloaded)
        progress.setValue(total_size)

        # --- Unzip and Replace Logic ---
        # Get the directory where the current application is running
        current_app_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
            __file__)

        # Unzip the new version to a temporary folder
        update_folder = os.path.join(temp_dir, "retail_suite_update")
        if os.path.exists(update_folder):
            shutil.rmtree(update_folder)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(update_folder)

        # The unzipped contents are inside a folder named after the app
        unzipped_content_path = os.path.join(update_folder, "Retail Operations Suite")

        # Create a simple updater script to run after this app closes
        updater_script_path = os.path.join(temp_dir, "run_update.bat")
        with open(updater_script_path, "w") as f:
            f.write(f'@echo off\n')
            f.write(f'echo Closing old application...\n')
            f.write(f'taskkill /F /IM "{os.path.basename(sys.executable)}"\n')  # Force close the old app
            f.write(f'echo Replacing files...\n')
            f.write(f'timeout /t 3 /nobreak > NUL\n')  # Wait for files to be unlocked
            f.write(
                f'robocopy "{unzipped_content_path}" "{current_app_path}" /E /MOVE /IS\n')  # Move new files over old
            f.write(f'echo Update complete. Launching new version...\n')
            f.write(f'start "" "{os.path.join(current_app_path, EXECUTABLE_NAME)}"\n')
            f.write(f'del "%~f0"\n')  # Delete this script after running

        # Launch the updater script and exit
        subprocess.Popen([updater_script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
        QApplication.quit()

    except Exception as e:
        QMessageBox.critical(parent_window, "Update Error", f"An unexpected error occurred: {e}")

