"""Escuta contínua em português, sem PyAudio.

A palavra de ativação é configurável. Padrão: "assistente".
O modelo Vosk pode estar embutido no executável de arquivo único.
"""

import json
import os
import queue
import sys
import threading
import zipfile
import urllib.request

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"
MODEL_NAME = "vosk-model-small-pt-0.3"


def _base_dir():
    # PyInstaller --onefile extrai recursos para _MEIPASS.
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


MODEL_DIR = os.path.join(_base_dir(), "models", MODEL_NAME)


def model_available():
    return os.path.isdir(MODEL_DIR)


def download_model():
    # Usado somente quando o modelo não foi incluído na distribuição.
    target_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
    os.makedirs(target_root, exist_ok=True)
    archive = os.path.join(target_root, MODEL_NAME + ".zip")
    urllib.request.urlretrieve(MODEL_URL, archive)
    with zipfile.ZipFile(archive, "r") as zf:
        zf.extractall(target_root)
    os.remove(archive)
    return os.path.isdir(os.path.join(target_root, MODEL_NAME))


class VoiceListener:
    def __init__(self, on_command, on_status=None, wake_word="assistente"):
        self.on_command = on_command
        self.on_status = on_status or (lambda text: None)
        self.wake_word = wake_word.lower().strip()
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        try:
            import sounddevice as sd
            from vosk import Model, KaldiRecognizer
        except Exception:
            self.on_status("● VOZ INDISPONÍVEL")
            self.running = False
            return

        if not model_available():
            self.on_status("● BAIXANDO MODELO DE VOZ")
            try:
                download_model()
            except Exception:
                self.on_status("● MODELO NÃO DISPONÍVEL")
                self.running = False
                return

        try:
            model = Model(MODEL_DIR)
            recognizer = KaldiRecognizer(model, 16000)
            audio = queue.Queue()

            def callback(indata, frames, time, status):
                if self.running:
                    audio.put(bytes(indata))

            self.on_status("● ESCUTANDO: " + self.wake_word.upper())

            with sd.RawInputStream(
                samplerate=16000,
                blocksize=4000,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                while self.running:
                    data = audio.get()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = (result.get("text") or "").lower().strip()
                        if not text:
                            continue

                        if self.wake_word in text:
                            command = text.split(self.wake_word, 1)[1].strip()
                            if command:
                                self.on_status("● PROCESSANDO")
                                self.on_command(command)
                                self.on_status("● ESCUTANDO: " + self.wake_word.upper())
                            else:
                                self.on_status("● FALE O COMANDO")
        except Exception:
            self.on_status("● ERRO NO MICROFONE")
        finally:
            self.running = False
