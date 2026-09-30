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

        if self._contains_any(text, ["ajuda", "o que voce faz", "suas funcoes"]):
            return (
                "Posso abrir e fechar programas, abrir pastas, procurar arquivos, "
                "criar pastas, pesquisar na internet, controlar funções do Windows, "
                "criar lembretes e responder por voz. Tudo continua na mesma tela."
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

        if self._is_create_folder_request(text):
            name = self.extract_after_phrases(
                text,
                [
                    "crie uma pasta chamada",
                    "cria uma pasta chamada",
                    "criar uma pasta chamada",
                    "crie uma pasta",
                    "cria uma pasta",
                    "criar uma pasta",
                ],
            )
            return self.app.create_folder(self.clean_target(name))

        if self._is_file_search_request(text):
            query = self.extract_after_phrases(
                text,
                [
                    "procure o arquivo",
                    "procure pelo arquivo",
                    "procura o arquivo",
                    "procura pelo arquivo",
                    "encontre o arquivo",
                    "encontre pelo arquivo",
                    "encontra o arquivo",
                    "encontra pelo arquivo",
                    "procure",
                    "procura",
                    "encontre",
                    "encontra",
                ],
            )
            query = self.clean_target(query)
            return self.app.search_files(query)

        if self._is_close_request(text):
            target = self.extract_after_phrases(
                text,
                ["feche", "fechar", "fecha", "encerre", "encerra"]
            )
            target = self.clean_target(target)
            if target:
                return self.app.close_target(target)
            return "Qual programa você quer que eu feche?"

        # Abrir vem antes de pesquisar para que "abrir o Google" abra o site.
        if self._contains_any(text, [
            "abrir", "abre", "abra", "iniciar", "inicie",
            "inicia", "executar", "execute", "rodar", "roda"
        ]):
            target = self.extract_target(
                text,
                [
                    "abrir", "abre", "abra", "iniciar", "inicie",
                    "inicia", "executar", "execute", "rodar", "roda"
                ]
            )
            target = self.clean_target(target)
            if target:
                return self.app.open_target(target)
            return "Qual programa, site ou pasta você quer que eu abra?"

        if self._contains_any(text, [
            "pesquisar", "pesquisa", "buscar", "busque", "procure",
            "procura na internet", "pesquisa na internet", "google"
        ]):
            query = self.extract_search_query(text)
            if query:
                webbrowser.open(
                    "https://www.google.com/search?q=" + query.replace(" ", "+")
                )
                return f"Pesquisando por {query}."
            return "O que você quer que eu pesquise?"

        return (
            "Entendi o comando, mas ainda não tenho uma ação para essa solicitação. "
            "A próxima evolução será adicionar novas ações ao mesmo motor, sem criar outra tela."
        )

    @staticmethod
    def normalize(text):
        text = str(text).lower().strip()
        replacements = str.maketrans(
            "áàãâéêíóôõúç",
            "aaaaeeiooouc"
        )
        text = text.translate(replacements)
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
    def _is_close_request(text):
        return any(
            text.startswith(prefix + " ")
            or text == prefix
            for prefix in ["feche", "fechar", "fecha", "encerre", "encerra"]
        )

    @staticmethod
    def _is_file_search_request(text):
        return (
            text.startswith("procure arquivo")
            or text.startswith("procura arquivo")
            or text.startswith("procure o arquivo")
            or text.startswith("procura o arquivo")
            or text.startswith("procure pelo arquivo")
            or text.startswith("procura pelo arquivo")
            or text.startswith("encontre arquivo")
            or text.startswith("encontra arquivo")
            or text.startswith("encontre o arquivo")
            or text.startswith("encontra o arquivo")
            or "no computador" in text and any(
                word in text for word in ["procure", "procura", "encontre", "encontra"]
            )
        )

    @staticmethod
    def _is_create_folder_request(text):
        return any(
            phrase in text
            for phrase in [
                "crie uma pasta",
                "cria uma pasta",
                "criar uma pasta",
            ]
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
    def extract_after_phrases(text, phrases):
        for phrase in sorted(phrases, key=len, reverse=True):
            if text.startswith(phrase):
                return text[len(phrase):].strip()
        for phrase in sorted(phrases, key=len, reverse=True):
            match = re.search(rf"\b{re.escape(phrase)}\b\s*(.*)", text)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def clean_target(target):
        if not target:
            return None
        target = re.sub(
            r"^(o|a|os|as|um|uma|meu|minha|meus|minhas|por favor)\s+",
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
            new_query = re.sub(
                rf"\b{re.escape(prefix)}\b", "", query, count=1
            )
            if new_query != query:
                query = new_query
                break
        query = re.sub(r"^\s*(sobre|por|para)\s+", "", query)
        query = re.sub(
            r"\s+(por favor|pra mim|para mim)$", "", query
        )
        return query.strip()
