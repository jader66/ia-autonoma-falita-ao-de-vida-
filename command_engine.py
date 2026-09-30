import os
import re
import subprocess
import webbrowser
from datetime import datetime


class CommandEngine:
    """Interpreta frases naturais sem exigir uma frase exata."""

    def __init__(self, app):
        self.app = app

    def execute(self, raw):
        text = self.normalize(raw)

        if self._matches(text, ["sair", "encerrar", "fechar assistente"]):
            self.app.root.after(300, self.app.root.destroy)
            return "Tudo bem. Vou encerrar."

        if "hora" in text or "horas" in text:
            return f"Agora são {datetime.now().strftime('%H:%M')}."

        if self._contains_any(text, ["abrir", "abre", "iniciar", "inicie", "executar"]):
            target = self.extract_target(text, ["abrir", "abre", "iniciar", "inicie", "executar"])
            if target:
                return self.app.open_target(target)

        if self._contains_any(text, ["pesquisar", "pesquisa", "buscar", "busque", "procure"]):
            query = self.extract_target(text, ["pesquisar", "pesquisa", "buscar", "busque", "procure"])
            if query:
                webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
                return f"Pesquisando por {query}."

        if "bloque" in text and "computador" in text:
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
            return "Computador bloqueado."

        if "configura" in text and "windows" in text:
            subprocess.Popen("start ms-settings:", shell=True)
            return "Abrindo as configurações do Windows."

        if "lembrete" in text or "me lembre" in text:
            return self.app.create_reminder(raw)

        if self._contains_any(text, ["ajuda", "o que você faz", "suas funções"]):
            return (
                "Posso controlar tarefas do Windows, abrir programas e sites, pesquisar, "
                "criar lembretes e responder por voz. Novas capacidades podem ser adicionadas "
                "ao mesmo motor sem criar novas telas."
            )

        return (
            "Entendi o que você disse, mas ainda não tenho uma ação cadastrada para isso. "
            "Essa frase já foi recebida pelo meu motor de comandos."
        )

    @staticmethod
    def normalize(text):
        text = text.lower().strip()
        text = re.sub(r"[!?.,;:]+", " ", text)
        return re.sub(r"\s+", " ", text)

    @staticmethod
    def _contains_any(text, words):
        return any(word in text for word in words)

    @staticmethod
    def _matches(text, words):
        return text in words

    @staticmethod
    def extract_target(text, triggers):
        for trigger in sorted(triggers, key=len, reverse=True):
            pattern = rf"\b{re.escape(trigger)}\b\s*(.*)"
            match = re.search(pattern, text)
            if match and match.group(1).strip():
                return match.group(1).strip()
        return None
