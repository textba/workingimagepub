import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import pyttsx3


class TTSApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Nate's Bot - Text to Speech")
        self.root.geometry("700x450")

        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty("voices")

        self._build_ui()
        self._load_voices()

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="Text to Speech", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w", pady=(0, 10))

        text_label = ttk.Label(container, text="Enter text:")
        text_label.pack(anchor="w")

        self.text_box = tk.Text(container, height=12, wrap="word")
        self.text_box.pack(fill="both", expand=True, pady=(6, 10))

        controls = ttk.Frame(container)
        controls.pack(fill="x", pady=(0, 8))

        ttk.Label(controls, text="Voice:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(controls, textvariable=self.voice_var, state="readonly", width=40)
        self.voice_combo.grid(row=0, column=1, sticky="w", padx=(0, 12))

        ttk.Label(controls, text="Rate:").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self.rate_var = tk.IntVar(value=180)
        self.rate_spin = ttk.Spinbox(controls, from_=80, to=300, textvariable=self.rate_var, width=7)
        self.rate_spin.grid(row=0, column=3, sticky="w", padx=(0, 12))

        ttk.Label(controls, text="Volume:").grid(row=0, column=4, sticky="w", padx=(0, 6))
        self.volume_var = tk.DoubleVar(value=1.0)
        self.volume_spin = ttk.Spinbox(controls, from_=0.0, to=1.0, increment=0.1, textvariable=self.volume_var, width=7)
        self.volume_spin.grid(row=0, column=5, sticky="w")

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

    def _load_voices(self):
        if not self.voices:
            self.voice_combo["values"] = ["Default"]
            self.voice_combo.current(0)
            return

        voice_names = []
        for v in self.voices:
            label = f"{v.name} ({v.id})"
            voice_names.append(label)

        self.voice_combo["values"] = voice_names
        self.voice_combo.current(0)

    def _apply_settings(self):
        selected_index = self.voice_combo.current()
        if selected_index >= 0 and selected_index < len(self.voices):
            self.engine.setProperty("voice", self.voices[selected_index].id)

        self.engine.setProperty("rate", int(self.rate_var.get()))

        volume = float(self.volume_var.get())
        volume = max(0.0, min(1.0, volume))
        self.engine.setProperty("volume", volume)

    def _get_text(self) -> str:
        return self.text_box.get("1.0", "end").strip()

    def _run_in_thread(self, func):
        threading.Thread(target=func, daemon=True).start()

    def speak(self):
        text = self._get_text()
        if not text:
            messagebox.showwarning("No text", "Please enter some text first.")
            return

        def _job():
            try:
                self.status_var.set("Speaking...")
                self._apply_settings()
                self.engine.say(text)
                self.engine.runAndWait()
                self.status_var.set("Done")
            except Exception as e:
                self.status_var.set("Error")
                messagebox.showerror("TTS Error", str(e))

        self._run_in_thread(_job)

    def save_to_file(self):
        text = self._get_text()
        if not text:
            messagebox.showwarning("No text", "Please enter some text first.")
            return

        path = filedialog.asksaveasfilename(
            title="Save speech audio",
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav"), ("All files", "*.*")],
        )
        if not path:
            return

        def _job():
            try:
                self.status_var.set("Saving audio...")
                self._apply_settings()
                self.engine.save_to_file(text, path)
                self.engine.runAndWait()
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
