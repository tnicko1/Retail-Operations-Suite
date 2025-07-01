import sys
from cx_Freeze import setup, Executable

# --- Application Information ---
# This info will be displayed in the installer.
APP_NAME = "Retail Operations Suite"
APP_VERSION = "1.0.0" # Make sure this matches the version in updater.py
APP_AUTHOR = "Nikoloz Taturashvili"
APP_DESCRIPTION = "A comprehensive desktop application for managing retail price tags, inventory, and more."
ICON_PATH = "assets/program/logo-no-flair.ico"

# --- Build Configuration ---
# This tells cx_Freeze what to include in the build.

# List of packages to include. cx_Freeze often finds these automatically,
# but it's good to be explicit for packages it might miss.
packages = [
    "os", "sys", "re", "json", "requests", "pyrebase", "bs4",
    "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets", "PyQt6.QtPrintSupport"
]

# List of files and directories to include.
# This is crucial for your assets (fonts, images, icons).
include_files = [
    "assets/",        # Include the entire assets directory
    "config.json",    # The user's Firebase config file
    "translations.py",
    "data_handler.py",
    "price_generator.py",
    "a4_layout_generator.py",
    "firebase_handler.py",
    "auth_ui.py",
    "app.py",
    "updater.py"
]

build_exe_options = {
    "packages": packages,
    "include_files": include_files,
    "excludes": ["tkinter"],  # Exclude packages you don't need to reduce size
}

# --- Executable Configuration ---
# Defines the main entry point of your application.

# Set the base to "Win32GUI" to create a GUI application (no console window).
# For debugging, you can change this to None.
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        "main.py",                # Your main script
        base=base,
        target_name=f"{APP_NAME}.exe",
        icon=ICON_PATH,
    )
]

# --- MSI Installer Options ---
# Configures the metadata for the .msi installer.
bdist_msi_options = {
    "add_to_path": False,
    "initial_target_dir": f"%ProgramFiles%\\{APP_NAME}",
    "data": {
        "Shortcut": [
            (
                "DesktopShortcut",        # Shortcut
                "DesktopFolder",          # Directory
                APP_NAME,                 # Name
                "TARGETDIR",              # Component
                f"[TARGETDIR]{APP_NAME}.exe",# Target
                None,                     # Arguments
                None,                     # Description
                None,                     # Hotkey
                None,                     # Icon
                None,                     # IconIndex
                None,                     # ShowCmd
                'TARGETDIR'               # WkDir
            )
        ]
    }
}

# --- Setup ---
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=executables,
)
