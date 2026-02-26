import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import pyttsx3
import requests


ELEVENLABS_DEFAULT_VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"


class TTSApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Nate's Bot - Text to Speech (v2)")
        self.root.geometry("820x520")

        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")

        self._build_ui()
        self._load_voices()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="Text to Speech v2", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        provider_row = ttk.Frame(container)
        provider_row.pack(fill="x", pady=(0, 8))

        ttk.Label(provider_row, text="Provider:").pack(side="left", padx=(0, 8))
        self.provider_var = tk.StringVar(value="pyttsx3")
        self.provider_combo = ttk.Combobox(
            provider_row,
            textvariable=self.provider_var,
            state="readonly",
            values=["pyttsx3", "elevenlabs"],
            width=16,
        )
        self.provider_combo.pack(side="left")
        self.provider_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_provider_fields())

        text_label = ttk.Label(container, text="Enter text:")
        text_label.pack(anchor="w")

        self.text_box = tk.Text(container, height=12, wrap="word")
        self.text_box.pack(fill="both", expand=True, pady=(6, 10))

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="x", pady=(0, 8))

        # pyttsx3 settings tab
        self.local_tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.local_tab, text="Local (pyttsx3)")

        ttk.Label(self.local_tab, text="Voice:").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(self.local_tab, textvariable=self.voice_var, state="readonly", width=55)
        self.voice_combo.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(self.local_tab, text="Rate:").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=4)
        self.rate_var = tk.IntVar(value=180)
        self.rate_spin = ttk.Spinbox(self.local_tab, from_=80, to=300, textvariable=self.rate_var, width=10)
        self.rate_spin.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(self.local_tab, text="Volume:").grid(row=2, column=0, sticky="w", padx=(0, 6), pady=4)
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_spin = ttk.Spinbox(self.local_tab, from_=0.0, to=1.0, increment=0.1, textvariable=self.volume_var, width=10)
        self.volume_spin.grid(row=2, column=1, sticky="w", pady=4)

        # elevenlabs tab
        self.eleven_tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.eleven_tab, text="ElevenLabs")

        ttk.Label(self.eleven_tab, text="API Key (or set ELEVENLABS_API_KEY):").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)
        self.api_key_var = tk.StringVar(value=os.getenv("ELEVENLABS_API_KEY", ""))
        self.api_key_entry = ttk.Entry(self.eleven_tab, textvariable=self.api_key_var, width=58, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(self.eleven_tab, text="Voice ID:").grid(row=1, column=0, sticky="w", padx=(0, 6), pady=4)
        self.voice_id_var = tk.StringVar(value=ELEVENLABS_DEFAULT_VOICE_ID)
        self.voice_id_entry = ttk.Entry(self.eleven_tab, textvariable=self.voice_id_var, width=40)
        self.voice_id_entry.grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(self.eleven_tab, text="Model ID:").grid(row=2, column=0, sticky="w", padx=(0, 6), pady=4)
        self.model_id_var = tk.StringVar(value=ELEVENLABS_MODEL_ID)
        self.model_id_entry = ttk.Entry(self.eleven_tab, textvariable=self.model_id_var, width=40)
        self.model_id_entry.grid(row=2, column=1, sticky="w", pady=4)

        hint = ttk.Label(
            self.eleven_tab,
            text="Tip: Click 'Save to File' to generate MP3 with ElevenLabs.",
            foreground="#555",
        )
        hint.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        buttons = ttk.Frame(container)
        buttons.pack(fill="x")

        self.speak_btn = ttk.Button(buttons, text="Speak", command=self.speak)
        self.speak_btn.pack(side="left")

        self.save_btn = ttk.Button(buttons, text="Save to File", command=self.save_to_file)
        self.save_btn.pack(side="left", padx=8)

        self.stop_btn = ttk.Button(buttons, text="Stop", command=self.stop)
        self.stop_btn.pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(container, textvariable=self.status_var, foreground="#555")
        status.pack(anchor="w", pady=(10, 0))

        self._refresh_provider_fields()

    def _load_voices(self):
        if not self.voices:
            self.voice_combo["values"] = ["Default"]
            self.voice_combo.current(0)
            return

        labels = [f"{v.name} ({v.id})" for v in self.voices]
        self.voice_combo["values"] = labels
        self.voice_combo.current(0)

    def _refresh_provider_fields(self):
        provider = self.provider_var.get()
        if provider == "pyttsx3":
            self.notebook.select(self.local_tab)
        else:
            self.notebook.select(self.eleven_tab)

    def _get_text(self) -> str:
        return self.text_box.get("1.0", "end").strip()

    def _run_in_thread(self, func):
        threading.Thread(target=func, daemon=True).start()

    def _apply_local_settings(self):
        idx = self.voice_combo.current()
        if 0 <= idx < len(self.voices):
            self.engine.setProperty("voice", self.voices[idx].id)
        self.engine.setProperty("rate", int(self.rate_var.get()))
        vol = max(0.0, min(1.0, float(self.volume_var.get())))
        self.engine.setProperty("volume", vol)

    def _elevenlabs_synthesize_to_file(self, text: str, out_path: str):
        api_key = self.api_key_var.get().strip() or os.getenv("ELEVENLABS_API_KEY", "")
        if not api_key:
            raise ValueError("Missing ElevenLabs API key. Set ELEVENLABS_API_KEY or enter key in app.")

        voice_id = self.voice_id_var.get().strip() or ELEVENLABS_DEFAULT_VOICE_ID
        model_id = self.model_id_var.get().strip() or ELEVENLABS_MODEL_ID

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code >= 400:
            raise RuntimeError(f"ElevenLabs error {response.status_code}: {response.text[:400]}")

        with open(out_path, "wb") as f:
            f.write(response.content)

    def speak(self):
        text = self._get_text()
        if not text:
            messagebox.showwarning("No text", "Please enter some text first.")
            return

        provider = self.provider_var.get()

        def _job():
            try:
                self.status_var.set("Speaking...")
                if provider == "pyttsx3":
                    self._apply_local_settings()
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.status_var.set("Done")
                else:
                    messagebox.showinfo(
                        "ElevenLabs",
                        "For ElevenLabs, use 'Save to File' to generate MP3.\n"
                        "(Playback can be added in next step.)",
                    )
                    self.status_var.set("Ready")
            except Exception as e:
                self.status_var.set("Error")
                messagebox.showerror("TTS Error", str(e))

        self._run_in_thread(_job)

    def save_to_file(self):
        text = self._get_text()
        if not text:
            messagebox.showwarning("No text", "Please enter some text first.")
            return

        provider = self.provider_var.get()
        ext = ".wav" if provider == "pyttsx3" else ".mp3"
        filetype = "WAV audio" if provider == "pyttsx3" else "MP3 audio"

        path = filedialog.asksaveasfilename(
            title="Save speech audio",
            defaultextension=ext,
            filetypes=[(filetype, f"*{ext}"), ("All files", "*.*")],
        )
        if not path:
            return

        def _job():
            try:
                self.status_var.set("Saving audio...")
                if provider == "pyttsx3":
                    self._apply_local_settings()
                    self.engine.save_to_file(text, path)
                    self.engine.runAndWait()
                else:
                    self._elevenlabs_synthesize_to_file(text, path)
                self.status_var.set(f"Saved: {path}")
            except Exception as e:
                self.status_var.set("Error")
                messagebox.showerror("Save Error", str(e))

        self._run_in_thread(_job)

    def stop(self):
        try:
            self.engine.stop()
            self.status_var.set("Stopped")
        except Exception as e:
            messagebox.showerror("Stop Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TTSApp(root)
    root.mainloop()
