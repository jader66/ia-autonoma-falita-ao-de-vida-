import os
import re
import sys
import threading
import webbrowser
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

try:
    import pyttsx3
except Exception:
    pyttsx3 = None


class AssistantApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Assistente")
        self.root.geometry("980x680")
        self.root.minsize(760, 520)
        self.root.configure(bg="#0d1117")

        self.tts = None
        if pyttsx3:
            try:
                self.tts = pyttsx3.init()
                self.tts.setProperty("rate", 175)
            except Exception:
                self.tts = None

        self._build_ui()
        self.write_message("Assistente", "Olá! Estou pronto. Digite um comando para começar.")

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#0d1117")
        header.pack(fill="x", padx=28, pady=(24, 12))

        title = tk.Label(
            header,
            text="ASSISTENTE",
            font=("Segoe UI", 22, "bold"),
            fg="#ffffff",
            bg="#0d1117",
        )
        title.pack(anchor="w")

        status = tk.Label(
            header,
            text="● ONLINE  •  CENTRAL ÚNICA",
            font=("Segoe UI", 9, "bold"),
            fg="#65d18a",
            bg="#0d1117",
        )
        status.pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self.root, bg="#111820")
        body.pack(fill="both", expand=True, padx=28, pady=8)

        self.chat = tk.Text(
            body,
            wrap="word",
            state="disabled",
            bg="#111820",
            fg="#e6edf3",
            insertbackground="#ffffff",
            relief="flat",
            bd=0,
            padx=20,
            pady=20,
            font=("Segoe UI", 11),
        )
        self.chat.pack(fill="both", expand=True)

        bottom = tk.Frame(self.root, bg="#0d1117")
        bottom.pack(fill="x", padx=28, pady=(12, 24))

        self.entry = tk.Entry(
            bottom,
            bg="#161b22",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 12),
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 10))
        self.entry.bind("<Return>", lambda _: self.send())

        send = tk.Button(
            bottom,
            text="ENVIAR",
            command=self.send,
            bg="#238636",
            fg="white",
            activebackground="#2ea043",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        send.pack(side="right")

        self.entry.focus_set()

    def write_message(self, author, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{author}\n", "author")
        self.chat.insert("end", f"{text}\n\n")
        self.chat.tag_configure("author", foreground="#65d18a", font=("Segoe UI", 10, "bold"))
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def speak(self, text):
        if not self.tts:
            return
        threading.Thread(target=self._speak_worker, args=(text,), daemon=True).start()

    def _speak_worker(self, text):
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception:
            pass

    def send(self):
        command = self.entry.get().strip()
        if not command:
            return

        self.entry.delete(0, "end")
        self.write_message("Você", command)

        response = self.handle_command(command)
        self.write_message("Assistente", response)
        self.speak(response)

    def handle_command(self, raw):
        command = raw.lower().strip()

        if command in {"sair", "fechar assistente", "encerrar"}:
            self.root.after(500, self.root.destroy)
            return "Encerrando o assistente."

        if "que horas" in command or command == "horário":
            return f"Agora são {datetime.now().strftime('%H:%M')}."

        if command.startswith("abrir "):
            target = raw[6:].strip()
            return self.open_target(target)

        if "criar lembrete" in command or command.startswith("me lembre"):
            return self.create_reminder(raw)

        if command in {"ajuda", "help", "o que você faz"}:
            return (
                "Nesta V1 eu consigo abrir programas e sites, consultar o horário, "
                "criar lembretes simples e executar comandos básicos. "
                "A estrutura já está preparada para receber as próximas funções."
            )

        return (
            "Entendi o comando, mas essa função ainda está sendo adicionada. "
            "A partir das próximas fases, poderei executar tarefas mais complexas."
        )

    def open_target(self, target):
        aliases = {
            "calculadora": "calc.exe",
            "calc": "calc.exe",
            "bloco de notas": "notepad.exe",
            "notepad": "notepad.exe",
            "explorador": "explorer.exe",
            "explorador de arquivos": "explorer.exe",
        }

        key = target.lower()

        if key in aliases:
            try:
                subprocess.Popen(aliases[key])
                return f"Abrindo {target}."
            except Exception as exc:
                return f"Não consegui abrir {target}: {exc}"

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

        return f"Ainda não tenho o aplicativo '{target}' cadastrado."

    def create_reminder(self, raw):
        match = re.search(r"(?:em|daqui a)\s+(\d+)\s*(minutos?|horas?)", raw.lower())
        if not match:
            return "Diga o tempo, por exemplo: 'criar lembrete em 10 minutos de testar o sistema'."

        amount = int(match.group(1))
        unit = match.group(2)
        seconds = amount * 60 if unit.startswith("min") else amount * 3600

        task = re.split(r"(?:minutos?|horas?)", raw, flags=re.I, maxsplit=1)[-1]
        task = re.sub(r"^\s*(?:de|para)\s*", "", task, flags=re.I).strip()
        task = task or "verificar o lembrete"

        self.root.after(seconds * 1000, lambda: self.reminder_alert(task))
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
