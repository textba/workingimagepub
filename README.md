# Text-to-Speech Python App

Simple desktop TTS app using `tkinter` with two providers:
- Local system voices via `pyttsx3`
- ElevenLabs API (Brian voice by default)

## Features
- Type/paste text
- Provider switch: `pyttsx3` or `elevenlabs`
- Local voice selector + rate + volume controls
- Save local speech to `.wav`
- Save ElevenLabs speech to `.mp3`

## Setup

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## ElevenLabs setup

1. Create an ElevenLabs API key.
2. Set it in environment (recommended):

```powershell
setx ELEVENLABS_API_KEY "your_api_key_here"
```

Then open a new terminal, or paste key in-app.

Default voice ID is set to Brian:
- `nPczCjzI2devNBz1zQrb`

## Run

```bash
python tts_app.py
```

## Notes
- `Speak` currently plays audio directly only for local (`pyttsx3`) mode.
- ElevenLabs mode currently generates MP3 via **Save to File**.
