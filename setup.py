import sys
from cx_Freeze import setup, Executable
import os

# --- Application Information ---
# Update these values for your application
APP_NAME = "Retail Operations Suite"
# IMPORTANT: This version number MUST match the one in main.py
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A suite of tools for managing retail operations, including price tag generation."
COMPANY_NAME = "Nikoloz Taturashvili"
# IMPORTANT: Generate a new GUID for this and paste it here.
# In PowerShell, run: [guid]::NewGuid()
UPGRADE_CODE = '{4281202f-2fdb-4d9a-a342-d833d8735e5b}'

# --- Base Executable ---
# base="Win32GUI" is used on Windows to create a GUI application (no console window)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# --- Executable Definition ---
# This defines the main entry point of your application
executables = [
    Executable(
        "main.py",
        base=base,
        target_name=f"{APP_NAME}.exe",
        icon="assets/program/logo-no-flair.ico" # Path to your application's .ico file
    )
]

# --- Files and Directories to Include in the Build ---
# This ensures all your assets, fonts, config files, and modules are included.
include_files = [
    'assets',
    'fonts',
    'config.json',
    'translations.py',
    'data_handler.py',
    'firebase_handler.py',
    'price_generator.py',
    'a4_layout_generator.py',
    'app.py',
    'auth_ui.py',
    'updater.py'
]

# --- Build Options for cx_Freeze ---
# Specify Python packages to include and other build settings
build_exe_options = {
    # Add any packages your project uses here
    "packages": [
        "os", "sys", "re", "json", "csv", "datetime", "traceback",
        "pyrebase", "bs4", "pytz", "requests", "PIL",
        "PyQt6", # Including the whole PyQt6 package is often safer
        "packaging" # Added for version parsing
    ],
    "include_files": include_files,
    "excludes": ["tkinter"], # Exclude packages you don't need to reduce size
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
}

# --- MSI Specific Options ---
# Customize the properties of the generated MSI installer
bdist_msi_options = {
    "upgrade_code": UPGRADE_CODE,
    "add_to_path": False,
    "initial_target_dir": rf"[ProgramFilesFolder]\{COMPANY_NAME}\{APP_NAME}",
    "all_users": True, # Install for all users on the machine
}

# --- Setup Function ---
# This function runs the build process with all the specified options
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables
)
