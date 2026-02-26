from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from tts_backend import synthesize


class TTSRequest(BaseModel):
    text: str
    provider: str = 'pyttsx3'
    voice: str | None = None


app = FastAPI(title='Nate TTS API')
app.mount('/outputs', StaticFiles(directory='outputs'), name='outputs')


@app.get('/')
def home():
    return FileResponse('index.html')


@app.post('/api/tts')
def api_tts(payload: TTSRequest):
    try:
        output_file = synthesize(
            text=payload.text,
            provider=payload.provider,
            voice_id=payload.voice,
        )
        return {'ok': True, 'output_file': output_file, 'url': f'/{output_file}'}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
