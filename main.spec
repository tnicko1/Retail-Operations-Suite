# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('C:\\Users\\Nikoloz\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\PyQt6\\Qt6\\bin\\*.dll', '.')],
    datas=[
        ('assets', 'assets'),
        ('fonts', 'fonts'),
        ('config.json', '.'),
        ('C:\\Users\\Nikoloz\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\pytz', 'pytz'),
        ('C:\\Users\\Nikoloz\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\PyQt6\\Qt6\\plugins\\styles', 'PyQt6\\Qt6\\plugins\\styles'),
        ('C:\\Users\\Nikoloz\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\certifi', 'certifi')
    ],
    hiddenimports=['PyQt6', 'PyQt6.sip', 'pytz'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/program/logo-no-flair.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Retail Operations Suite',
)
