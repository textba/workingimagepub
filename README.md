# Text-to-Speech Python App

Simple desktop TTS app using `tkinter` + `pyttsx3`.

## Features
- Type/paste text
- Choose installed voice
- Adjust speaking rate + volume
- Speak out loud
- Save generated speech to `.wav`

## Setup

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```bash
python tts_app.py
```

## Notes
- Uses your system's installed voices.
- On some systems, saving to file may take a few seconds.
