import sys
import os
import requests
import tempfile
import subprocess
from PyQt6.QtWidgets import QMessageBox, QProgressDialog, QApplication
from PyQt6.QtCore import Qt

# --- Configuration ---
# IMPORTANT: Replace with your actual GitHub username and repository name.
GITHUB_REPO_OWNER = "tnicko1"
GITHUB_REPO_NAME = "Retail-Operations-Suite"
# This is the filename of the installer you will upload to GitHub releases.
RELEASE_ASSET_NAME = "Retail-Operations-Suite-Installer.exe"
# The current version of the application. This must be updated for each new release.
CURRENT_VERSION = "1.0.0"


def get_latest_release_info():
    """
    Fetches the latest release information from the GitHub repository.
    Returns the JSON response from the API.
    """
    api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest release info: {e}")
        return None


def compare_versions(current_version, latest_version_tag):
    """
    Compares two version strings (e.g., "1.0.0" vs "v1.0.1").
    Returns True if the latest version is newer, False otherwise.
    """
    # Strip the 'v' prefix from the tag if it exists
    if latest_version_tag.startswith('v'):
        latest_version_tag = latest_version_tag[1:]

    # Split versions into parts and convert to integers
    current_parts = list(map(int, current_version.split('.')))
    latest_parts = list(map(int, latest_version_tag.split('.')))

    # Compare parts
    return latest_parts > current_parts


def check_for_updates(parent_window):
    """
    Checks for updates and prompts the user if a new version is available.
    """
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
    """
    Downloads the installer from the release assets and runs it.
    """
    assets = release_info.get("assets", [])
    download_url = None
    for asset in assets:
        if asset.get("name") == RELEASE_ASSET_NAME:
            download_url = asset.get("browser_download_url")
            break

    if not download_url:
        QMessageBox.critical(parent_window, "Error", "Could not find the installer file in the latest release.")
        return

    try:
        # Download the file with a progress dialog
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, RELEASE_ASSET_NAME)

        progress = QProgressDialog("Downloading update...", "Cancel", 0, total_size, parent_window)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        bytes_downloaded = 0
        with open(installer_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if progress.wasCanceled():
                    return
                f.write(chunk)
                bytes_downloaded += len(chunk)
                progress.setValue(bytes_downloaded)

        progress.setValue(total_size)
        print(f"Installer downloaded to: {installer_path}")

        # Run the installer and exit the current application
        subprocess.Popen([installer_path])
        print("Launching installer and exiting application...")
        QApplication.quit()

    except requests.exceptions.RequestException as e:
        QMessageBox.critical(parent_window, "Download Error", f"Failed to download the update: {e}")
    except Exception as e:
        QMessageBox.critical(parent_window, "Installation Error", f"An unexpected error occurred: {e}")
