# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Chemin du projet
project_root = Path(SPECPATH).parent
static_dir = project_root / "backend" / "static"

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Inclure les fichiers statiques
        (str(static_dir), "static"),
    ],
    hiddenimports=[
        # FastAPI et dépendances
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'fastapi',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'fastapi.middleware.gzip',
        'fastapi.middleware.httpsredirect',
        'fastapi.middleware.trustedhost',
        'pydantic',
        'pydantic_core',
        'pydantic.fields',
        'pydantic.main',
        'pydantic.types',
        'starlette',
        'starlette.applications',
        'starlette.middleware',
        'starlette.responses',
        'starlette.routing',
        
        # Zeroconf et réseau
        'zeroconf',
        'zeroconf._services',
        'zeroconf._handlers',
        'zeroconf._utils',
        'zeroconf._dns',
        'zeroconf._updates',
        'ifaddr',
        'netifaces',
        
        # QR Code et Pillow
        'qrcode',
        'qrcode.image',
        'qrcode.image.pil',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        
        # SQLite
        'sqlite3',
        
        # Autres dépendances
        'websockets',
        'python_dotenv',
        'typing_extensions',
        'annotated_types',
        'anyio',
        'click',
        'h11',
        'httptools',
        'pyyaml',
        'uvloop',
        'watchfiles',
        
        # Pour les fichiers statiques
        'aiofiles',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclure les modules inutiles pour réduire la taille
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GestionStock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console visible pour voir les logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Ajouter un fichier .ico si disponible
)