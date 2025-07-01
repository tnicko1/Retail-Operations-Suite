# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# This section lists all the data files (assets, fonts, etc.)
# that need to be included with your application.
# Format: ('source_path_on_disk', 'destination_folder_in_bundle')
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
    ('utils.py', '.'),
    ('fonts', 'fonts')
]

# This section explicitly lists libraries that PyInstaller might miss.
hiddenimports = [
    'pyrebase',
    'requests',
    'bs4',
    'pytz',
    'google.auth',
    'google.auth.transport.requests',
    'pycryptodome',
    'PyQt6.sip',
    'PyQt6.QtNetwork',
    'PyQt6.QtPrintSupport',
]

a = Analysis(
    ['main.py'],  # The main entry point of your application
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Retail Operations Suite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep True for debugging. We need to see the error.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/program/logo-no-flair.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Retail Operations Suite',
)
