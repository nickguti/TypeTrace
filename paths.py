"""Risoluzione dei percorsi di risorse e dati.

Sotto PyInstaller --onefile la cartella del modulo e' la directory temporanea
_MEIxxxx, creata all'avvio e cancellata all'uscita: tutto cio' che vi viene
scritto sparisce a ogni chiusura. Le risorse di sola lettura vanno quindi
lette dal bundle, mentre database, impostazioni e log vanno in %APPDATA%.
"""

import os
import shutil
import sys

APP_NAME = "TypeTrace"


def is_frozen():
    """True quando l'app gira come eseguibile PyInstaller."""
    return getattr(sys, "frozen", False)


def bundle_dir():
    """Cartella delle risorse di sola lettura (lang.json, icon.ico)."""
    if is_frozen():
        return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(filename):
    """Percorso di una risorsa inclusa nel bundle."""
    return os.path.join(bundle_dir(), filename)


def data_dir():
    """Cartella scrivibile e persistente per i dati dell'utente.

    TYPETRACE_DATA_DIR ha la precedenza: serve ai test e a chi vuole tenere
    i dati accanto all'eseguibile su una chiavetta.
    """
    override = os.environ.get("TYPETRACE_DATA_DIR")
    if override:
        try:
            os.makedirs(override, exist_ok=True)
            return override
        except Exception:
            pass

    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, APP_NAME)
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        # Ultimo fallback: accanto al codice, come nelle versioni precedenti
        return os.path.dirname(os.path.abspath(__file__))
    return path


def data_path(filename):
    """Percorso di un file di dati persistente."""
    return os.path.join(data_dir(), filename)


def migrate_legacy_file(filename):
    """Recupera una volta sola un file scritto dalle versioni precedenti.

    Le versioni fino alla 3.1.5 salvavano accanto al codice sorgente. Se il file
    nuovo non esiste ancora ma quello vecchio si', lo si copia per non perdere
    lo storico dell'utente. Restituisce sempre il percorso nuovo.
    """
    target = data_path(filename)
    if os.path.exists(target):
        return target

    legacy = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if os.path.exists(legacy) and os.path.abspath(legacy) != os.path.abspath(target):
        try:
            shutil.copy2(legacy, target)
        except Exception:
            pass
    return target
