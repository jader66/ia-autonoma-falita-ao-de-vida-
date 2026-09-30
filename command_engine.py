import re
import subprocess
import webbrowser
from datetime import datetime


class CommandEngine:
    """Motor central de comandos naturais e automações encadeadas."""

    ACTION_STARTS = (
        "abrir ", "abre ", "abra ", "iniciar ", "inicie ", "inicia ",
        "executar ", "execute ", "rodar ", "roda ", "feche ", "fechar ",
        "fecha ", "encerre ", "encerra ", "procure ", "procura ",
        "encontre ", "encontra ", "pesquisar ", "pesquisa ", "buscar ",
        "busque ", "crie uma pasta ", "cria uma pasta ", "criar uma pasta ",
        "bloqueie ", "bloqueia ", "trave ",
    )

    def __init__(self, app):
        self.app = app

    def execute(self, raw):
        text = self.normalize(raw)
        if not text:
            return "Não recebi nenhum comando."

        commands = self.split_chained_commands(text)
        if len(commands) > 1:
            return self.execute_chain(commands)

        return self.execute_single(raw, text)

    def execute_chain(self, commands):
        results = []
        for index, command in enumerate(commands, 1):
            results.append(f"{index}. {self.execute_single(command, command)}")
        return f"Executando {len(commands)} ações:\n" + "\n".join(results)

    def execute_single(self, raw, text=None):
        text = text or self.normalize(raw)

        if self._matches(text, ["sair", "encerrar", "fechar assistente", "fechar o assistente"]):
            self.app.root.after(300, self.app.root.destroy)
            return "Tudo bem. Vou encerrar."

        if self._is_time_request(text):
            return f"Agora são {datetime.now().strftime('%H:%M')}."

        if self._contains_any(text, ["ajuda", "o que voce faz", "suas funcoes"]):
            return (
                "Posso abrir e fechar programas, abrir pastas, procurar arquivos, "
                "criar pastas, executar sequências de ações, pesquisar na internet, "
                "controlar funções do Windows, criar lembretes e responder por voz."
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
            name = self.extract_after_phrases(text, [
                "crie uma pasta chamada", "cria uma pasta chamada",
                "criar uma pasta chamada", "crie uma pasta",
                "cria uma pasta", "criar uma pasta"
            ])
            return self.app.create_folder(self.clean_target(name))

        if self._is_file_search_request(text):
            query = self.extract_after_phrases(text, [
                "procure o arquivo", "procure pelo arquivo",
                "procura o arquivo", "procura pelo arquivo",
                "encontre o arquivo", "encontre pelo arquivo",
                "encontra o arquivo", "encontra pelo arquivo",
                "procure", "procura", "encontre", "encontra"
            ])
            return self.app.search_files(self.clean_target(query))

        if self._is_close_request(text):
            target = self.extract_after_phrases(text, ["feche", "fechar", "fecha", "encerre", "encerra"])
            target = self.clean_target(target)
            return self.app.close_target(target) if target else "Qual programa você quer que eu feche?"

        if self._contains_any(text, [
            "abrir ", "abre ", "abra ", "iniciar ", "inicie ", "inicia ",
            "executar ", "execute ", "rodar ", "roda "
        ]):
            target = self.clean_target(self.extract_target(text, [
                "abrir", "abre", "abra", "iniciar", "inicie",
                "inicia", "executar", "execute", "rodar", "roda"
            ]))
            return self.app.open_target(target) if target else "Qual programa, site ou pasta você quer que eu abra?"

        if self._contains_any(text, [
            "pesquisar ", "pesquisa ", "buscar ", "busque ",
            "procure na internet", "pesquisa na internet", "google "
        ]):
            query = self.extract_search_query(text)
            if query:
                webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
                return f"Pesquisando por {query}."
            return "O que você quer que eu pesquise?"

        return "Entendi o comando, mas ainda não tenho uma ação para essa solicitação."

    @classmethod
    def split_chained_commands(cls, text):
        result = [text]
        for pattern in [
            r"\s+e\s+(?:depois|em seguida|entao)\s+",
            r"\s+(?:depois|em seguida|entao)\s+"
        ]:
            pieces = []
            for part in result:
                pieces.extend(re.split(pattern, part, flags=re.I))
            result = [p.strip() for p in pieces if p.strip()]

        final = []
        for part in result:
            chunks = re.split(r"\s+e\s+", part)
            if len(chunks) == 1:
                final.append(part)
                continue
            current = chunks[0].strip()
            for chunk in chunks[1:]:
                candidate = chunk.strip()
                if cls._looks_like_action(candidate):
                    final.append(current)
                    current = candidate
                else:
                    current += " e " + candidate
            if current:
                final.append(current)
        return final

    @classmethod
    def _looks_like_action(cls, text):
        return any(text.startswith(prefix) for prefix in cls.ACTION_STARTS)

    @staticmethod
    def normalize(text):
        text = str(text).lower().strip()
        text = text.translate(str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc"))
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
        return "que horas" in text or "que hora" in text or "horas sao" in text or text in {"hora", "horas"}

    @staticmethod
    def _is_lock_request(text):
        return ("bloque" in text or "trave" in text) and ("computador" in text or "pc" in text)

    @staticmethod
    def _is_windows_settings_request(text):
        return any(x in text for x in [
            "configuracoes do windows", "configuracao do windows",
            "configuracoes windows", "configuracao windows",
            "abrir configuracoes"
        ])

    @staticmethod
    def _is_close_request(text):
        return any(text.startswith(p + " ") or text == p for p in ["feche", "fechar", "fecha", "encerre", "encerra"])

    @staticmethod
    def _is_file_search_request(text):
        return (
            text.startswith(("procure arquivo", "procura arquivo", "procure o arquivo",
                             "procura o arquivo", "procure pelo arquivo", "procura pelo arquivo",
                             "encontre arquivo", "encontra arquivo", "encontre o arquivo",
                             "encontra o arquivo"))
            or ("no computador" in text and any(w in text for w in ["procure", "procura", "encontre", "encontra"]))
        )

    @staticmethod
    def _is_create_folder_request(text):
        return any(p in text for p in ["crie uma pasta", "cria uma pasta", "criar uma pasta"])

    @staticmethod
    def extract_target(text, triggers):
        for trigger in sorted(triggers, key=len, reverse=True):
            match = re.search(rf"\b{re.escape(trigger)}\b\s*(.*)", text)
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
        target = re.sub(r"^(o|a|os|as|um|uma|meu|minha|meus|minhas|por favor)\s+", "", target, flags=re.I)
        target = re.sub(r"\s+(por favor|pra mim|para mim)$", "", target, flags=re.I)
        return target.strip()

    @staticmethod
    def extract_search_query(text):
        query = text
        for prefix in [
            "pesquisa na internet", "procura na internet",
            "pesquisar na internet", "pesquise na internet",
            "pesquisar", "pesquisa", "buscar", "busque",
            "procure", "google"
        ]:
            new_query = re.sub(rf"\b{re.escape(prefix)}\b", "", query, count=1)
            if new_query != query:
                query = new_query
                break
        query = re.sub(r"^\s*(sobre|por|para)\s+", "", query)
        return re.sub(r"\s+(por favor|pra mim|para mim)$", "", query).strip()
