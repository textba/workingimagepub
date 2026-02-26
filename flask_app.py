from flask import Flask, jsonify, request, send_from_directory

from tts_backend import synthesize

app = Flask(__name__, static_folder='.')


@app.get('/')
def home():
    return send_from_directory('.', 'index.html')


@app.post('/api/tts')
def api_tts():
    data = request.get_json(silent=True) or {}
    try:
        output_file = synthesize(
            text=data.get('text', ''),
            provider=data.get('provider', 'pyttsx3'),
            voice_id=data.get('voice'),
            api_key=data.get('apiKey'),
        )
        return jsonify({'ok': True, 'output_file': output_file, 'url': f"/{output_file}"})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.get('/outputs/<path:filename>')
def outputs(filename):
    return send_from_directory('outputs', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
