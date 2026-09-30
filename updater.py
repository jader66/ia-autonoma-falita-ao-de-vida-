import json
import os
import re
import subprocess
import tempfile
import threading
import urllib.request
from pathlib import Path

REPO = "jader66/ia-autonoma-falita-ao-de-vida-"
LATEST_API = f"https://api.github.com/repos/{REPO}/releases/latest"
INSTALLER_URL = f"https://github.com/{REPO}/releases/latest/download/Assistente-Setup.exe"


def _version_tuple(value):
    nums = re.findall(r"\d+", str(value))
    return tuple(int(x) for x in nums[:4]) or (0,)


def get_current_build():
    try:
        from version import APP_BUILD
        return int(APP_BUILD)
    except Exception:
        return 0


def check_latest():
    request = urllib.request.Request(
        LATEST_API,
        headers={"User-Agent": "Assistente-Updater/1.0"},
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        data = json.loads(response.read().decode("utf-8"))

    tag = data.get("tag_name", "")
    match = re.search(r"build[.-]?(\d+)", tag, re.I)
    if not match:
        return None

    return {
        "tag": tag,
        "build": int(match.group(1)),
        "version": tag.lstrip("v").split("-")[0],
    }


def update_available():
    latest = check_latest()
    if not latest:
        return None
    if latest["build"] <= get_current_build():
        return None
    return latest


def download_installer(progress=None):
    target = Path(tempfile.gettempdir()) / "Assistente-Setup-update.exe"
    request = urllib.request.Request(
        INSTALLER_URL,
        headers={"User-Agent": "Assistente-Updater/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response, open(target, "wb") as output:
        total = int(response.headers.get("Content-Length", "0"))
        done = 0
        while True:
            chunk = response.read(1024 * 256)
            if not chunk:
                break
            output.write(chunk)
            done += len(chunk)
            if progress and total:
                progress(done / total)
    return target


def install_update(installer_path):
    subprocess.Popen(
        [str(installer_path), "/SILENT", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS"],
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def check_and_update(on_status=None, on_ready=None):
    def worker():
        try:
            latest = update_available()
            if not latest:
                return

            if on_status:
                on_status(f"Atualização {latest['version']} encontrada. Baixando...")

            installer = download_installer(
                lambda p: on_status(f"Baixando atualização: {int(p * 100)}%")
                if on_status else None
            )

            if on_ready:
                on_ready(latest)

            install_update(installer)
        except Exception:
            # Atualização automática nunca deve impedir o Assistente de abrir.
            return

    threading.Thread(target=worker, daemon=True).start()
