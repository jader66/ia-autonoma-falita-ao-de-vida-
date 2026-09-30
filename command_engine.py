import re
import subprocess
import webbrowser
from datetime import datetime


class CommandEngine:
    """Motor central de comandos naturais da interface única."""

    def __init__(self, app):
        self.app = app

    def execute(self, raw):
        text = self.normalize(raw)

        if not text:
            return "Não recebi nenhum comando."

        if self._matches(text, ["sair", "encerrar", "fechar assistente", "fechar o assistente"]):
            self.app.root.after(300, self.app.root.destroy)
            return "Tudo bem. Vou encerrar."

        if self._is_time_request(text):
            return f"Agora são {datetime.now().strftime('%H:%M')}."

        if self._contains_any(text, ["ajuda", "o que você faz", "o que voce faz", "suas funções", "suas funcoes"]):
            return (
                "Posso abrir programas e sites, pesquisar na internet, controlar funções "
                "do Windows, criar lembretes e responder por voz. Tudo continua na mesma tela."
            )

        if self._is_lock_request(text):
            try:
                subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
                return "Computador bloqueado."
            except Exception as exc:
                return f"Não consegui bloquear o computador: {exc}"

        if self._is_windows_settings_request(text):
            try:
                subprocess.Popen("start ms-settings:", shell=True)
                return "Abrindo as configurações do Windows."
            except Exception as exc:
                return f"Não consegui abrir as configurações: {exc}"

        if "lembrete" in text or "me lembre" in text or "me avise" in text:
            return self.app.create_reminder(raw)

        if self._contains_any(text, [
            "pesquisar", "pesquisa", "buscar", "busque", "procure",
            "pesquisa na internet", "procura na internet", "google"
        ]):
            query = self.extract_search_query(text)
            if query:
                webbrowser.open(
                    "https://www.google.com/search?q=" + query.replace(" ", "+")
                )
                return f"Pesquisando por {query}."
            return "O que você quer que eu pesquise?"

        if self._contains_any(text, [
            "abrir", "abre", "abra", "iniciar", "inicie",
            "inicia", "executar", "execute", "rodar", "roda"
        ]):
            target = self.extract_target(
                text,
                ["abrir", "abre", "abra", "iniciar", "inicie",
                 "inicia", "executar", "execute", "rodar", "roda"]
            )
            target = self.clean_target(target)
            if target:
                return self.app.open_target(target)
            return "Qual programa ou site você quer que eu abra?"

        return (
            "Entendi o comando, mas ainda não tenho uma ação para essa solicitação. "
            "A próxima evolução será adicionar novas ações ao mesmo motor, sem criar outra tela."
        )

    @staticmethod
    def normalize(text):
        text = str(text).lower().strip()
        text = text.replace("á", "a").replace("à", "a").replace("ã", "a")
        text = text.replace("â", "a").replace("é", "e").replace("ê", "e")
        text = text.replace("í", "i").replace("ó", "o").replace("ô", "o")
        text = text.replace("õ", "o").replace("ú", "u").replace("ç", "c")
        text = re.sub(r"[!?.,;:]+", " ", text)
        return re.sub(r"\s+", " ", text)

    @staticmethod
    def _contains_any(text, words):
        return any(word in text for word in words)

    @staticmethod
    def _matches(text, words):
        return text in words

    @staticmethod
    def _is_time_request(text):
        return (
            "que horas" in text
            or "que hora" in text
            or "horas sao" in text
            or text in {"hora", "horas"}
        )

    @staticmethod
    def _is_lock_request(text):
        return (
            ("bloque" in text or "trave" in text)
            and ("computador" in text or "pc" in text)
        )

    @staticmethod
    def _is_windows_settings_request(text):
        return (
            "configuracoes do windows" in text
            or "configuracao do windows" in text
            or "configuracoes windows" in text
            or "configuracao windows" in text
            or "abrir configuracoes" in text
        )

    @staticmethod
    def extract_target(text, triggers):
        for trigger in sorted(triggers, key=len, reverse=True):
            pattern = rf"\b{re.escape(trigger)}\b\s*(.*)"
            match = re.search(pattern, text)
            if match and match.group(1).strip():
                return match.group(1).strip()
        return None

    @staticmethod
    def clean_target(target):
        if not target:
            return None
        target = re.sub(
            r"^(o|a|os|as|um|uma|meu|minha|meu|por favor)\s+",
            "",
            target,
            flags=re.I,
        )
        target = re.sub(
            r"\s+(por favor|pra mim|para mim)$",
            "",
            target,
            flags=re.I,
        )
        return target.strip()

    @staticmethod
    def extract_search_query(text):
        query = text

        prefixes = [
            "pesquisa na internet",
            "procura na internet",
            "pesquisar na internet",
            "pesquise na internet",
            "pesquisar",
            "pesquisa",
            "buscar",
            "busque",
            "procure",
            "google",
        ]

        for prefix in sorted(prefixes, key=len, reverse=True):
            query = re.sub(rf"\b{re.escape(prefix)}\b", "", query, count=1)
            if query != text:
                break

        query = re.sub(r"^\s*(sobre|por|para)\s+", "", query)
        query = re.sub(r"\s+(por favor|pra mim|para mim)$", "", query)
        return query.strip()
