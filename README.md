# Nate's Bot - TTS + Video Creator

This repo now includes:
- Desktop TTS app (`tts_app.py`)
- Web UI + Flask API for TTS and video generation (`index.html`, `flask_app.py`)
- FastAPI TTS endpoint (`fastapi_app.py`)
- Multi-format text-to-video render with ElevenLabs/OpenAI/gTTS fallback
- Optional upload helpers for YouTube, Google Drive, TikTok

## Features ported from video-reader-v4 backup
- Text -> video generation
- Multi-format output:
  - `portrait_tiktok` (9:16)
  - `landscape_720p` (16:9)
  - `square_instagram` (1:1)
- Intro image upload and video rendering
- Voice selection (Adam/Antoni/Brian)
- Upload endpoint hooks for YouTube/Drive/TikTok
- Version endpoint: `/api/version`

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Environment (.env)

```env
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=nPczCjzI2devNBz1zQrb
ELEVENLABS_MODEL_ID=eleven_multilingual_v2
OPENAI_API_KEY=

YOUTUBE_UPLOAD_ENABLED=false
DRIVE_UPLOAD_ENABLED=false
```

## Run Flask app (recommended for video)

```powershell
python flask_app.py
```

Open: `http://127.0.0.1:5000`

## Run FastAPI app (TTS API)

```powershell
uvicorn fastapi_app:app --reload --port 8000
```

Open: `http://127.0.0.1:8000`
