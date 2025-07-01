# This script uses PyInstaller to build the application.
# To run it, use the command: python setup.py

import PyInstaller.__main__
import os

# --- Application Information ---
APP_NAME = "Retail Operations Suite"
APP_VERSION = "1.0.0" # Make sure this matches the version in updater.py and main.py
MAIN_SCRIPT = "main.py"
ICON_PATH = "assets/program/logo-no-flair.ico"

# --- Files and Directories to Include ---
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
    ('fonts', 'fonts')
]

# --- Hidden Imports ---
# Explicitly tell PyInstaller about libraries it might miss.
# This is often necessary for complex packages like Pyrebase.
hidden_imports = [
    'pyrebase',
    'requests',
    'bs4',
    'pytz',
    'google.auth',
    'google.auth.transport.requests',
    'pycryptodome'
]

# --- Generate the .spec file content ---
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
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Set to False for GUI applications
    icon='{ICON_PATH}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
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
    '--noconfirm',
    spec_file_name
])

print("PyInstaller build complete.")
print(f"The application is in the 'dist/{APP_NAME}' folder.")
