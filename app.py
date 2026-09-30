import re
import subprocess
import threading
import webbrowser
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


class AssistantApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Assistente")
        self.root.geometry("980x680")
        self.root.minsize(760, 520)
        self.root.configure(bg="#0d1117")
        self.voice = None
        self.listening = False
        self.engine = CommandEngine(self)

        self.tts = None
        if pyttsx3:
            try:
                self.tts = pyttsx3.init()
                self.tts.setProperty("rate", 175)
            except Exception:
                pass

        self._build_ui()
        self.write_message("Assistente", "Olá! Estou pronto. Você pode falar comigo naturalmente ou usar o teclado.")

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#0d1117")
        header.pack(fill="x", padx=28, pady=(24, 12))
        tk.Label(header, text="ASSISTENTE", font=("Segoe UI", 22, "bold"),
                 fg="white", bg="#0d1117").pack(side="left")
        self.status = tk.Label(header, text="● ONLINE", font=("Segoe UI", 9, "bold"),
                               fg="#65d18a", bg="#0d1117")
        self.status.pack(side="right")

        body = tk.Frame(self.root, bg="#111820")
        body.pack(fill="both", expand=True, padx=28, pady=8)
        self.chat = tk.Text(body, wrap="word", state="disabled", bg="#111820",
                            fg="#e6edf3", insertbackground="white", relief="flat",
                            bd=0, padx=20, pady=20, font=("Segoe UI", 11))
        self.chat.pack(fill="both", expand=True)

        bottom = tk.Frame(self.root, bg="#0d1117")
        bottom.pack(fill="x", padx=28, pady=(12, 24))
        self.entry = tk.Entry(bottom, bg="#161b22", fg="white",
                              insertbackground="white", relief="flat",
                              font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 8))
        self.entry.bind("<Return>", lambda _: self.send())

        tk.Button(bottom, text="🎙", command=self.toggle_voice, bg="#30363d",
                  fg="white", activebackground="#484f58", relief="flat",
                  padx=14, pady=9, font=("Segoe UI", 11, "bold"),
                  cursor="hand2").pack(side="left", padx=(0, 8))
        tk.Button(bottom, text="ENVIAR", command=self.send, bg="#238636",
                  fg="white", activebackground="#2ea043", relief="flat",
                  padx=20, pady=10, font=("Segoe UI", 10, "bold"),
                  cursor="hand2").pack(side="right")
        self.entry.focus_set()

    def write_message(self, author, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{author}\n", "author")
        self.chat.insert("end", f"{text}\n\n")
        self.chat.tag_configure("author", foreground="#65d18a",
                                font=("Segoe UI", 10, "bold"))
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
        if command:
            self.process(command)

    def process(self, command):
        self.entry.delete(0, "end")
        self.write_message("Você", command)
        response = self.engine.execute(command)
        self.write_message("Assistente", response)
        self.speak(response)

    def toggle_voice(self):
        if not VoiceListener:
            self.write_message("Assistente", "O módulo de voz não está disponível. Instale as dependências.")
            return
        if self.listening:
            self.listening = False
            self.status.config(text="● ONLINE", fg="#65d18a")
            if self.voice:
                self.voice.stop()
            return
        self.listening = True
        self.status.config(text="● ESCUTANDO", fg="#58a6ff")
        self.voice = VoiceListener(self.on_voice_command, self.on_voice_status)
        self.voice.start()

    def on_voice_status(self, text):
        self.root.after(0, lambda: self.status.config(text=text))

    def on_voice_command(self, command):
        self.root.after(0, lambda: self.process(command))

    def open_target(self, target):
        aliases = {
            "calculadora": "calc.exe", "calc": "calc.exe",
            "bloco de notas": "notepad.exe", "notepad": "notepad.exe",
            "explorador": "explorer.exe", "explorador de arquivos": "explorer.exe",
            "gerenciador de tarefas": "taskmgr.exe", "paint": "mspaint.exe",
            "terminal": "wt.exe", "prompt de comando": "cmd.exe",
        }
        key = target.lower().strip()
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
            return "Use, por exemplo: criar lembrete em 10 minutos de testar o sistema."
        amount = int(match.group(1))
        unit = match.group(2)
        seconds = amount * 60 if unit.startswith("min") else amount * 3600
        task = re.split(r"(?:minutos?|horas?)", raw, flags=re.I, maxsplit=1)[-1]
        task = re.sub(r"^\s*(?:de|para)\s*", "", task, flags=re.I).strip() or "verificar o lembrete"
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
