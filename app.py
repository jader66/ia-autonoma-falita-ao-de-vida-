import os
import re
import subprocess
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    from voice import VoiceListener
except Exception:
    VoiceListener = None

from command_engine import CommandEngine
try:
    from version import APP_VERSION
except Exception:
    APP_VERSION = "1.7.0"
try:
    from updater import check_and_update
except Exception:
    check_and_update = None


class AssistantApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Assistente v{APP_VERSION}")
        self.root.geometry("980x680")
        self.root.minsize(760, 520)
        self.root.configure(bg="#0d1117")
        self.voice = None
        self.listening = False
        self.last_search_results = []
        self.context = {}
        self.engine = CommandEngine(self)

        self.tts = None
        if pyttsx3:
            try:
                self.tts = pyttsx3.init()
                self.tts.setProperty("rate", 175)
            except Exception:
                pass

        self._build_ui()
        self.write_message(
            "Assistente",
            f"Olá! Estou pronto. Versão {APP_VERSION}. Você pode falar comigo naturalmente ou usar o teclado."
        )
        if check_and_update:
            self.root.after(1500, self.start_update_check)

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#0d1117")
        header.pack(fill="x", padx=28, pady=(24, 12))
        tk.Label(
            header, text="ASSISTENTE", font=("Segoe UI", 22, "bold"),
            fg="white", bg="#0d1117"
        ).pack(side="left")
        self.status = tk.Label(
            header, text="● ONLINE", font=("Segoe UI", 9, "bold"),
            fg="#65d18a", bg="#0d1117"
        )
        self.status.pack(side="right")

        body = tk.Frame(self.root, bg="#111820")
        body.pack(fill="both", expand=True, padx=28, pady=8)
        self.chat = tk.Text(
            body, wrap="word", state="disabled", bg="#111820",
            fg="#e6edf3", insertbackground="white", relief="flat",
            bd=0, padx=20, pady=20, font=("Segoe UI", 11)
        )
        self.chat.pack(fill="both", expand=True)

        bottom = tk.Frame(self.root, bg="#0d1117")
        bottom.pack(fill="x", padx=28, pady=(12, 24))
        self.entry = tk.Entry(
            bottom, bg="#161b22", fg="white",
            insertbackground="white", relief="flat",
            font=("Segoe UI", 12)
        )
        self.entry.pack(
            side="left", fill="x", expand=True, ipady=12, padx=(0, 8)
        )
        self.entry.bind("<Return>", lambda _: self.send())

        tk.Button(
            bottom, text="🎙", command=self.toggle_voice, bg="#30363d",
            fg="white", activebackground="#484f58", relief="flat",
            padx=14, pady=9, font=("Segoe UI", 11, "bold"),
            cursor="hand2"
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            bottom, text="ENVIAR", command=self.send, bg="#238636",
            fg="white", activebackground="#2ea043", relief="flat",
            padx=20, pady=10, font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        ).pack(side="right")
        self.entry.focus_set()

    def write_message(self, author, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{author}\n", "author")
        self.chat.insert("end", f"{text}\n\n")
        self.chat.tag_configure(
            "author", foreground="#65d18a",
            font=("Segoe UI", 10, "bold")
        )
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def speak(self, text):
        if not self.tts:
            return
        threading.Thread(
            target=self._speak_worker, args=(text,), daemon=True
        ).start()

    def _speak_worker(self, text):
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception:
            pass

    def send(self):
        command = self.entry.get().strip()
        if command:
            self.process(command)

    def process(self, command):
        self.entry.delete(0, "end")
        self.write_message("Você", command)
        response = self.engine.execute(command)
        self.write_message("Assistente", response)
        self.speak(response)

    def start_update_check(self):
        if not check_and_update:
            return
        check_and_update(
            on_status=lambda status: self.root.after(0, lambda: self.status.config(text="● " + status.upper())),
            on_ready=lambda latest: self.root.after(0, self.finish_update),
        )

    def finish_update(self):
        self.write_message("Assistente", "Atualização baixada. Reiniciando para instalar...")
        self.root.after(1200, self.root.destroy)

    def toggle_voice(self):
        if not VoiceListener:
            self.write_message(
                "Assistente",
                "O módulo de voz não está disponível. Instale as dependências."
            )
            return
        if self.listening:
            self.listening = False
            self.status.config(text="● ONLINE", fg="#65d18a")
            if self.voice:
                self.voice.stop()
            return
        self.listening = True
        self.status.config(text="● ESCUTANDO", fg="#58a6ff")
        self.voice = VoiceListener(
            self.on_voice_command, self.on_voice_status
        )
        self.voice.start()

    def on_voice_status(self, text):
        self.root.after(0, lambda: self.status.config(text=text))

    def on_voice_command(self, command):
        self.root.after(0, lambda: self.process(command))

    def open_target(self, target):
        aliases = {
            "calculadora": "calc.exe",
            "calc": "calc.exe",
            "bloco de notas": "notepad.exe",
            "notepad": "notepad.exe",
            "explorador": "explorer.exe",
            "explorador de arquivos": "explorer.exe",
            "gerenciador de tarefas": "taskmgr.exe",
            "paint": "mspaint.exe",
            "terminal": "wt.exe",
            "prompt de comando": "cmd.exe",
        }
        key = target.lower().strip()

        if key in aliases:
            try:
                subprocess.Popen(aliases[key])
                return f"Abrindo {target}."
            except Exception as exc:
                return f"Não consegui abrir {target}: {exc}"

        folders = self._folder_aliases()
        if key in folders:
            return self.open_folder(folders[key], target)

        sites = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://github.com",
            "whatsapp": "https://web.whatsapp.com",
        }
        if key in sites:
            webbrowser.open(sites[key])
            return f"Abrindo {target}."

        if re.match(r"^https?://", target, re.I):
            webbrowser.open(target)
            return f"Abrindo {target}."

        candidate = Path(target).expanduser()
        if candidate.exists():
            try:
                os.startfile(str(candidate))
                return f"Abrindo {target}."
            except Exception as exc:
                return f"Não consegui abrir {target}: {exc}"

        return f"Ainda não tenho o aplicativo '{target}' cadastrado."

    @staticmethod
    def _folder_aliases():
        home = Path.home()
        return {
            "area de trabalho": home / "Desktop",
            "desktop": home / "Desktop",
            "downloads": home / "Downloads",
            "pasta downloads": home / "Downloads",
            "documentos": home / "Documents",
            "meus documentos": home / "Documents",
            "imagens": home / "Pictures",
            "fotos": home / "Pictures",
            "videos": home / "Videos",
            "vídeos": home / "Videos",
            "musicas": home / "Music",
            "músicas": home / "Music",
        }

    def open_folder(self, folder, label=None):
        folder = Path(folder).expanduser()
        if not folder.exists():
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                return f"Não consegui acessar a pasta: {exc}"
        try:
            os.startfile(str(folder))
            return f"Abrindo {label or folder.name}."
        except Exception as exc:
            return f"Não consegui abrir a pasta: {exc}"

    def close_target(self, target):
        processes = {
            "calculadora": ["CalculatorApp.exe", "Calculator.exe"],
            "calc": ["CalculatorApp.exe", "Calculator.exe"],
            "bloco de notas": ["notepad.exe"],
            "notepad": ["notepad.exe"],
            "paint": ["mspaint.exe"],
            "gerenciador de tarefas": ["Taskmgr.exe"],
            "terminal": ["WindowsTerminal.exe", "wt.exe"],
            "prompt de comando": ["cmd.exe"],
        }
        key = target.lower().strip()
        names = processes.get(key)
        if not names:
            return (
                f"Não vou fechar '{target}' automaticamente porque não tenho "
                "um processo seguro cadastrado para ele."
            )

        closed = False
        errors = []
        for name in names:
            result = subprocess.run(
                ["taskkill", "/IM", name, "/T", "/F"],
                capture_output=True,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if result.returncode == 0:
                closed = True
            elif result.stderr:
                errors.append(result.stderr.strip())

        if closed:
            return f"Fechei {target}."
        return f"Não encontrei {target} aberto."

    def search_files(self, query):
        query = str(query).strip()
        if not query:
            return "Diga o nome do arquivo ou pasta que você quer procurar."

        roots = [
            Path.home() / "Desktop",
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path.home() / "Pictures",
            Path.home() / "Videos",
            Path.home() / "Music",
        ]
        query_lower = query.lower()
        results = []
        seen = set()

        for root in roots:
            if not root.exists():
                continue
            try:
                for path in root.rglob("*"):
                    if len(results) >= 8:
                        break
                    try:
                        if query_lower in path.name.lower():
                            key = str(path).lower()
                            if key not in seen:
                                seen.add(key)
                                results.append(path)
                    except (OSError, PermissionError):
                        continue
            except (OSError, PermissionError):
                continue
            if len(results) >= 8:
                break

        self.last_search_results = results

        if not results:
            return f"Não encontrei '{query}' nas pastas principais do usuário."

        lines = [f"Encontrei {len(results)} resultado(s):"]
        for path in results:
            lines.append(f"• {path}")
        return "\n".join(lines)

    def create_folder(self, name):
        name = str(name).strip().strip('"')
        name = re.sub(r'[<>:"/\\|?*]', "", name).strip()
        if not name:
            return "Diga o nome da pasta que você quer criar."

        folder = Path.home() / "Desktop" / name
        if folder.exists():
            return f"A pasta '{name}' já existe na Área de Trabalho."
        try:
            folder.mkdir(parents=True, exist_ok=False)
            return f"Criei a pasta '{name}' na Área de Trabalho."
        except Exception as exc:
            return f"Não consegui criar a pasta: {exc}"

    def create_reminder(self, raw):
        match = re.search(
            r"(?:em|daqui a)\s+(\d+)\s*(minutos?|horas?)",
            raw.lower()
        )
        if not match:
            return "Use, por exemplo: criar lembrete em 10 minutos de testar o sistema."
        amount = int(match.group(1))
        unit = match.group(2)
        seconds = amount * 60 if unit.startswith("min") else amount * 3600
        task = re.split(
            r"(?:minutos?|horas?)", raw, flags=re.I, maxsplit=1
        )[-1]
        task = re.sub(
            r"^\s*(?:de|para)\s*", "", task, flags=re.I
        ).strip() or "verificar o lembrete"
        self.root.after(
            seconds * 1000, lambda: self.reminder_alert(task)
        )
        when = datetime.now() + timedelta(seconds=seconds)
        return f"Lembrete criado para {when.strftime('%H:%M')}: {task}."

    def reminder_alert(self, task):
        messagebox.showinfo("Lembrete", task)
        self.write_message("Assistente", f"Lembrete: {task}")
        self.speak(f"Lembrete: {task}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    AssistantApp().run()
