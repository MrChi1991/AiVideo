from flask import Flask, request, jsonify
import requests
from storage.minio_client import MinIOClient
import io
from prometheus_client import Counter

app = Flask(__name__)
minio_client = MinIOClient()
FREESOUND_API_KEY = "your_freesound_key"  # Set in .env
REQUESTS_TOTAL = Counter('soundmaster_requests_total', 'Total Requests to Soundmaster')

@app.route('/process', methods=['POST'])
def create_soundtrack():
    REQUESTS_TOTAL.inc()
    data = request.get_json()
    script = data.get('script', 'cat meowing')
    
    try:
        # Search for sound on FreeSound
        search_url = f"https://freesound.org/apiv2/search/text/?query={script}&token={FREESOUND_API_KEY}"
        response = requests.get(search_url)
        sounds = response.json().get('results', [])
        
        if not sounds:
            return jsonify({'error': 'No sounds found'}), 404
        
        # Get first sound preview
        sound_id = sounds[0]['id']
        preview_url = sounds[0]['previews']['preview-hq-mp3']
        audio_response = requests.get(preview_url)
        
        # Upload to MinIO
        audio_id = f"audio/{data['task_id']}.mp3"
        minio_client.upload_file("audio-bucket", audio_id, io.BytesIO(audio_response.content))
        
        return jsonify({
            'status': 'success',
            'audio_path': audio_id,
            'next_step': 'editing'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
