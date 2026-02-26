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

Use `.env` for local secrets/config:

```env
ELEVENLABS_API_KEY=your_api_key_here
ELEVENLABS_VOICE_ID=nPczCjzI2devNBz1zQrb
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
```

A starter `.env` is included. Fill in the API key value.

Default voice ID is Brian:
- `nPczCjzI2devNBz1zQrb`

## Run

```bash
python tts_app.py
```

## Notes
- `Speak` currently plays audio directly only for local (`pyttsx3`) mode.
- ElevenLabs mode currently generates MP3 via **Save to File**.
