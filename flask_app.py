import base64
import os
import time
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from moviepy import AudioFileClip, VideoClip, ImageClip
from gtts import gTTS
from dotenv import load_dotenv

from tts_backend import synthesize
from youtube_uploader import upload_video
from drive_uploader import upload_to_drive
from tiktok_uploader import upload_video_to_tiktok

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "nPczCjzI2devNBz1zQrb")

YOUTUBE_UPLOAD_ENABLED = os.getenv("YOUTUBE_UPLOAD_ENABLED", "false").lower() == "true"
DRIVE_UPLOAD_ENABLED = os.getenv("DRIVE_UPLOAD_ENABLED", "false").lower() == "true"


def generate_elevenlabs_audio(text, output_path, voice_id=DEFAULT_VOICE_ID):
    if not ELEVENLABS_API_KEY:
        return False
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    r = requests.post(url, json=payload, headers=headers, timeout=90)
    if r.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(r.content)
        return True
    return False


def generate_openai_audio(text, output_path):
    if not OPENAI_API_KEY:
        return False
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "tts-1-hd", "input": text, "voice": "onyx"}
    r = requests.post(url, json=payload, headers=headers, timeout=90)
    if r.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(r.content)
        return True
    return False


def decode_intro_image(intro_image_data: str, timestamp: int):
    if not intro_image_data:
        return None
    try:
        encoded = intro_image_data.split(",", 1)[1] if "," in intro_image_data else intro_image_data
        image_bytes = base64.b64decode(encoded)
        out_path = os.path.join(app.static_folder, f"intro_{timestamp}.png")
        with open(out_path, "wb") as f:
            f.write(image_bytes)
        return out_path
    except Exception:
        return None


def choose_font_size_from_word_count(raw_text: str) -> int:
    words = max(1, len((raw_text or "").split()))
    min_words, max_words = 1, 12000
    max_size, min_size = 40.0, 10.0
    clamped = max(min_words, min(max_words, words))
    ratio = (clamped - min_words) / (max_words - min_words)
    size = max_size + ratio * (min_size - max_size)
    return int(round(size * 0.6))


def make_text_frame(t, total_duration, raw_text, size, font):
    img = Image.new("RGB", size, color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    words = (raw_text or "").split()
    if not words:
        return np.array(img)

    progress = min(1.0, max(0.0, t / total_duration if total_duration else 0))
    word_index = int(progress * len(words))

    margin = 40
    width = size[0] - (margin * 2)
    line_height = max(18, int((font.size if hasattr(font, "size") else 16) * 1.45))

    lines, line_words = [], []
    current = []
    for w in words:
        test = " ".join(current + [w])
        if draw.textlength(test, font=font) <= width:
            current.append(w)
        else:
            lines.append(" ".join(current))
            line_words.append(len(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
        line_words.append(len(current))

    y = 30
    consumed = 0
    for i, line in enumerate(lines[: int(size[1] / line_height) - 1]):
        count = line_words[i]
        active = consumed <= word_index < consumed + count
        color = (230, 245, 255) if active else (160, 160, 160)
        if active:
            w = draw.textlength(line, font=font)
            draw.rectangle([margin - 6, y - 2, margin + w + 6, y + line_height - 2], fill=(45, 65, 95))
        draw.text((margin, y), line, font=font, fill=color)
        y += line_height
        consumed += count

    return np.array(img)


@app.get('/')
def home():
    return send_from_directory('.', 'index.html')


@app.post('/api/tts')
def api_tts():
    data = request.get_json(silent=True) or {}
    try:
        output_file = synthesize(text=data.get('text', ''), provider=data.get('provider', 'pyttsx3'), voice_id=data.get('voice'))
        return jsonify({'ok': True, 'output_file': output_file, 'url': f"/{output_file}"})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.post('/api/generate-video')
def api_generate_video():
    data = request.json or {}
    text = (data.get('text') or '')[:72000]
    voice_id = data.get('voiceId', DEFAULT_VOICE_ID)
    intro_image_data = data.get('introImageData')

    if not text.strip():
        return jsonify({'error': 'No text provided'}), 400

    format_map = {
        'portrait_tiktok': (720, 1280),
        'landscape_720p': (1280, 720),
        'square_instagram': (720, 720),
    }
    requested = data.get('formats', ['portrait_tiktok'])
    selected = [(f, *format_map[f]) for f in requested if f in format_map] or [('portrait_tiktok', 720, 1280)]

    ts = int(time.time())
    audio_path = f"audio_{ts}.mp3"

    clean = text.replace('\n', ' ')
    ok = generate_elevenlabs_audio(clean, audio_path, voice_id)
    if not ok:
        ok = generate_openai_audio(clean, audio_path)
    if not ok:
        gTTS(text=clean, lang='en').save(audio_path)

    intro_path = decode_intro_image(intro_image_data, ts)

    audio = AudioFileClip(audio_path)
    duration = audio.duration
    font_size = choose_font_size_from_word_count(text)
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except Exception:
        font = ImageFont.load_default()

    outputs = []
    for name, w, h in selected:
        filename = f"{name}_{ts}.mp4"
        out = os.path.join(app.static_folder, filename)

        if intro_path:
            src = Image.open(intro_path).convert('RGB')
            fitted = ImageOps.fit(src, (w, h), method=Image.Resampling.LANCZOS)
            intro_fit = os.path.join(app.static_folder, f"intro_{name}_{ts}.png")
            fitted.save(intro_fit)
            clip = ImageClip(intro_fit, duration=duration).with_audio(audio)
        else:
            clip = VideoClip(lambda t: make_text_frame(t, duration, text, (w, h), font), duration=duration).with_audio(audio)

        clip.write_videofile(out, fps=8, codec='libx264', audio_codec='aac', preset='ultrafast', logger=None)
        outputs.append({'type': name, 'url': f'/{filename}', 'filename': filename})

    audio.close()
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return jsonify({'videos': outputs})


@app.post('/api/upload-video')
def api_upload_video():
    data = request.json or {}
    filename = data.get('filename', '')
    targets = data.get('targets', [])
    title = (data.get('title') or 'Text to Video').strip()
    description = (data.get('description') or '').strip()

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    file_path = os.path.join(app.static_folder, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Video file not found'}), 404

    results = {}
    if 'drive' in targets and DRIVE_UPLOAD_ENABLED:
        try:
            url, _ = upload_to_drive(file_path=file_path, title=filename, description=description)
            results['driveUrl'] = url
        except Exception as e:
            results['driveError'] = str(e)

    if 'youtube' in targets and YOUTUBE_UPLOAD_ENABLED:
        try:
            url, _ = upload_video(file_path=file_path, title=title, description=description)
            results['youtubeUrl'] = url
        except Exception as e:
            results['youtubeError'] = str(e)

    if 'tiktok' in targets:
        try:
            results['tiktokStatus'] = upload_video_to_tiktok(file_path, title=title, description=description).get('status', 'unknown')
        except Exception as e:
            results['tiktokError'] = str(e)

    return jsonify(results)


@app.get('/outputs/<path:filename>')
def outputs(filename):
    return send_from_directory('outputs', filename)


@app.get('/api/version')
def api_version():
    return jsonify({'version': 'v4-style upgrade', 'name': 'pythonspeechtotextfeb25'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
