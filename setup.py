# Retail Operations Suite
# Copyright (C) 2025 Nikoloz Taturashvili (ნიკოლოზ ტატურაშვილი). All Rights Reserved.
#
# This file is part of the Retail Operations Suite.
# This software is proprietary and confidential.
#
# Unauthorized copying of this file, via any medium, is strictly prohibited.
# Proprietary and confidential.


import sys
from cx_Freeze import setup, Executable
import os

# --- Application Information ---
APP_NAME = "Retail Operations Suite"
# IMPORTANT: This version number MUST match the one in main.py
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "A suite of tools for managing retail operations, including price tag generation."
COMPANY_NAME = "Nikoloz Taturashvili" # This will be used as the Author/Publisher
# IMPORTANT: Generate a new GUID for this and paste it here.
# In PowerShell, run: [guid]::NewGuid()
UPGRADE_CODE = '{4281202f-2fdb-4d9a-a342-d833d8735e5b}'

# --- Base Executable ---
# base="Win32GUI" is used on Windows to create a GUI application (no console window)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# --- Icon path ---
# Define the path to the icon file once to reuse it
ICON_PATH = "assets/program/logo-no-flair.ico"

# --- Executable Definition ---
# This defines the main entry point of your application
executables = [
    Executable(
        "main.py",
        base=base,
        target_name=f"{APP_NAME}.exe",
        icon=ICON_PATH # Sets the icon for the .exe file
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
    "packages": [
        "os", "sys", "re", "json", "csv", "datetime", "traceback",
        "pyrebase", "bs4", "pytz", "requests", "PIL",
        "PyQt6",
        "packaging",
        "socks"
    ],
    "include_files": include_files,
    "excludes": ["tkinter"], # Exclude packages you don't need to reduce size
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
}

# --- MSI Shortcut Table ---
# This dictionary defines the shortcuts that the installer will create.
shortcut_table = [
    (
        "DesktopShortcut",        # Shortcut
        "DesktopFolder",          # Directory
        APP_NAME,                 # Name
        "TARGETDIR",              # Component
        "[TARGETDIR]" + f"{APP_NAME}.exe",# Target
        None,                     # Arguments
        APP_DESCRIPTION,          # Description
        None,                     # Hotkey
        None,                     # Icon
        None,                     # IconIndex
        None,                     # ShowCmd
        "TARGETDIR",              # WkDir
    ),
    (
        "ProgramMenuShortcut",     # Shortcut
        "ProgramMenuFolder",       # Directory
        APP_NAME,                  # Name
        "TARGETDIR",               # Component
        "[TARGETDIR]" + f"{APP_NAME}.exe", # Target
        None,                      # Arguments
        APP_DESCRIPTION,           # Description
        None,                      # Hotkey
        None,                      # Icon
        None,                      # IconIndex
        None,                      # ShowCmd
        "TARGETDIR",               # WkDir
    ),
]

# --- MSI Icon Table ---
# This tells the installer about the icon file to use in Add/Remove Programs.
icon_table = [
    ("ProductIcon", ICON_PATH) # The Id must be ProductIcon
]

# --- MSI Property Table ---
# This links the icon defined above to the installer's properties.
property_table = [
    ("ARPPRODUCTICON", "ProductIcon") # Sets the Add/Remove Programs icon
]


# --- MSI Specific Options ---
# Customize the properties of the generated MSI installer
bdist_msi_options = {
    "upgrade_code": UPGRADE_CODE,
    "add_to_path": False,
    "initial_target_dir": rf"[ProgramFilesFolder]\{COMPANY_NAME}\{APP_NAME}",
    "all_users": True, # Install for all users on the machine
    "license_file": "EULA.rtf",
    # Add all custom MSI tables to the 'data' dictionary
    "data": {
        "Shortcut": shortcut_table,
        "Icon": icon_table,
        "Property": property_table
    },
}

# --- Setup Function ---
# This function runs the build process with all the specified options
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=COMPANY_NAME, # This sets the "Publisher" field in Add/Remove Programs
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables
)
