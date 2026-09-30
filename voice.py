"""Camada de voz da V1.

Esta camada não usa PyAudio. Ela foi separada do aplicativo principal para
que o sistema possa evoluir para ativação por palavra-chave sem acoplar
o núcleo da interface ao microfone.
"""

import json
import os
import queue
import zipfile
import urllib.request


MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"
MODEL_DIR = os.path.join("models", "vosk-model-small-pt-0.3")


def model_available():
    return os.path.isdir(MODEL_DIR)


def download_model():
    os.makedirs("models", exist_ok=True)
    archive = os.path.join("models", "vosk-model-small-pt-0.3.zip")
    urllib.request.urlretrieve(MODEL_URL, archive)
    with zipfile.ZipFile(archive, "r") as zf:
        zf.extractall("models")
    os.remove(archive)
    return model_available()


def recognize_once(seconds=6):
    try:
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer
    except ImportError:
        return None

    if not model_available():
        return None

    model = Model(MODEL_DIR)
    recognizer = KaldiRecognizer(model, 16000)
    audio = queue.Queue()

    def callback(indata, frames, time, status):
        audio.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback,
    ):
        for _ in range(max(1, int(seconds * 2))):
            data = audio.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text") or None

    result = json.loads(recognizer.FinalResult())
    return result.get("text") or None
