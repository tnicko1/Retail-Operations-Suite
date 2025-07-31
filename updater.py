# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys
import os
import requests
import subprocess
import tempfile
from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt
from packaging.version import parse as parse_version

# --- CONFIGURATION ---
# The GitHub repository in the format 'owner/repo'
GITHUB_REPO = "tnicko1/Retail-Operations-Suite"


# The expected name of the MSI asset in the GitHub release.
# The installer created by setup.py will have a version in its name,
# so we just check for the .msi extension.

def check_for_updates(current_version_str):
    """
    Checks GitHub for the latest release of the application.

    Args:
        current_version_str (str): The current version of the running application.

    Returns:
        tuple: A tuple containing (latest_version_str, download_url) if an update is
               available and has an MSI asset, otherwise (None, None).
    """
    try:
        # Use the GitHub API to get information about the latest release
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (like 404, 500)

        latest_release = response.json()
        # The tag name (e.g., "v1.0.1") is used as the version identifier.
        # We strip the 'v' prefix for comparison.
        latest_version_str = latest_release.get("tag_name", "0.0.0").lstrip('v')

        # Use the 'packaging' library to safely compare semantic versions
        current_version = parse_version(current_version_str)
        latest_version = parse_version(latest_version_str)

        print(f"Current version: {current_version}, Latest version from GitHub: {latest_version}")

        # If the latest version on GitHub is greater than the current version
        if latest_version > current_version:
            assets = latest_release.get("assets", [])
            for asset in assets:
                # Find the .msi file in the release assets
                if asset.get("name").endswith(".msi"):
                    print(f"Update found: {latest_version_str}. Asset: {asset.get('name')}")
                    return latest_version_str, asset.get("browser_download_url")

            print("Update found, but no .msi asset was present in the latest release.")
            return None, None  # Update available, but no asset found

    except requests.exceptions.RequestException as e:
        # Handle network errors gracefully
        print(f"Could not check for updates due to a network error: {e}")
    except Exception as e:
        # Handle other potential errors (e.g., parsing JSON)
        print(f"An error occurred while checking for updates: {e}")

    return None, None


def download_and_install_update(download_url):
    """
    Downloads the MSI from the given URL, shows a progress dialog,
    and launches the installer.
    """
    if not download_url:
        QMessageBox.critical(None, "Update Error", "Could not get the download link for the update.")
        return

    try:
        # Start downloading the file
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        # Get the total file size for the progress bar
        total_size = int(response.headers.get('content-length', 0))
        temp_dir = tempfile.gettempdir()
        # Extract filename from URL to handle versioned installer names
        installer_name = download_url.split('/')[-1]
        installer_path = os.path.join(temp_dir, installer_name)

        # --- Progress Dialog ---
        progress_dialog = QProgressDialog("Downloading update...", "Cancel", 0, total_size)
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        progress_dialog.setWindowTitle("Updating")
        progress_dialog.show()

        downloaded_size = 0
        with open(installer_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if progress_dialog.wasCanceled():
                    print("Download cancelled by user.")
                    return
                f.write(chunk)
                downloaded_size += len(chunk)
                progress_dialog.setValue(downloaded_size)
                QApplication.processEvents()  # Keep the UI responsive

        progress_dialog.setValue(total_size)
        print(f"Downloaded installer to: {installer_path}")

        # --- Launch Installer ---
        QMessageBox.information(None, "Ready to Update",
                                "The update has been downloaded. The application will now close to run the installer.")

        # Use os.startfile to launch the MSI installer. This is the standard way on Windows.
        os.startfile(installer_path)

        # IMPORTANT: Exit the current application so the installer can replace files.
        sys.exit(0)

    except requests.exceptions.RequestException as e:
        QMessageBox.critical(None, "Download Error", f"Failed to download the update: {e}")
    except Exception as e:
        QMessageBox.critical(None, "Update Error", f"An error occurred during the update process: {e}")
