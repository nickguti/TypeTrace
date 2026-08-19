# -*- mode: python ; coding: utf-8 -*-
#
# Ricetta di build ufficiale. Va usata al posto della riga di comando:
# lang.json e l'icona devono finire dentro il bundle, altrimenti l'interfaccia
# mostra le chiavi di traduzione al posto dei testi.

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('lang.json', '.')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='TypeTrace',
    icon='icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
