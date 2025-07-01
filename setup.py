# This script uses PyInstaller to build the application.
# To run it, use the command: pyinstaller --noconfirm setup.spec

import PyInstaller.__main__
import os

# --- Application Information ---
APP_NAME = "Retail Operations Suite"
APP_VERSION = "1.0.0" # Make sure this matches the version in updater.py and main.py
MAIN_SCRIPT = "main.py"
ICON_PATH = "assets/program/logo-no-flair.ico"

# --- Files and Directories to Include ---
# This tells PyInstaller what to bundle with your .exe
# Format: list of tuples, ('source_path', 'destination_in_bundle')
datas = [
    ('assets', 'assets'),
    ('config.json', '.'),
    ('translations.py', '.'),
    ('data_handler.py', '.'),
    ('price_generator.py', '.'),
    ('a4_layout_generator.py', '.'),
    ('firebase_handler.py', '.'),
    ('auth_ui.py', '.'),
    ('app.py', '.'),
    ('updater.py', '.'),
    ('fonts', 'fonts') # Make sure to include the fonts directory
]

# --- Hidden Imports ---
# Sometimes PyInstaller can't find all the necessary libraries,
# especially if they are used indirectly. We list them here.
hidden_imports = [
    'pyrebase',
    'requests',
    'bs4',
    'pytz'
]

# --- Generate the .spec file content ---
# A .spec file is the main configuration file for PyInstaller.
# We are generating it dynamically here.
spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=[],
    datas={datas},
    hiddenimports={hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,         # Set to False for GUI applications
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{ICON_PATH}',
)

# This creates a single folder with everything inside
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}'
)
"""

# Write the spec file
spec_file_name = "setup.spec"
with open(spec_file_name, "w") as f:
    f.write(spec_content)

print(f"Generated {spec_file_name}. Now running PyInstaller...")

# --- Run PyInstaller ---
PyInstaller.__main__.run([
    '--noconfirm', # Overwrite previous builds without asking
    spec_file_name
])

print("PyInstaller build complete.")
print(f"You can find the output in the 'dist/{APP_NAME}' folder.")
print("Remember to ZIP this folder for distribution.")

