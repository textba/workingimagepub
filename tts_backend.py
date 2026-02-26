import os
from pathlib import Path
from uuid import uuid4

import pyttsx3
import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "nPczCjzI2devNBz1zQrb")  # Brian
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")


def synthesize(text: str, provider: str, voice_id: str | None = None, api_key: str | None = None) -> str:
    text = (text or "").strip()
    if not text:
        raise ValueError("text is required")

    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)

    provider = (provider or "pyttsx3").strip().lower()

    if provider == "pyttsx3":
        out_path = out_dir / f"{uuid4().hex}.wav"
        engine = pyttsx3.init()
        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
        return str(out_path).replace("\\", "/")

    if provider == "elevenlabs":
        key = (api_key or os.getenv("ELEVENLABS_API_KEY", "")).strip()
        if not key:
            raise ValueError("Missing ElevenLabs API key")

        voice = (voice_id or ELEVENLABS_DEFAULT_VOICE_ID).strip()
        out_path = out_dir / f"{uuid4().hex}.mp3"
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        headers = {
            "xi-api-key": key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": ELEVENLABS_MODEL_ID,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
        }

        res = requests.post(url, headers=headers, json=payload, timeout=90)
        if res.status_code >= 400:
            raise RuntimeError(f"ElevenLabs error {res.status_code}: {res.text[:300]}")

        out_path.write_bytes(res.content)
        return str(out_path).replace("\\", "/")

    raise ValueError("provider must be 'pyttsx3' or 'elevenlabs'")
