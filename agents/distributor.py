from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from storage.minio_client import MinIOClient
import os
from dotenv import load_dotenv
from prometheus_client import Counter

load_dotenv()
app = Flask(__name__)
minio_client = MinIOClient()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
REQUESTS_TOTAL = Counter('distributor_requests_total', 'Total Requests to Distributor')

@app.route('/process', methods=['POST'])
def distribute_video():
    REQUESTS_TOTAL.inc()
    data = request.get_json()
    video_path = data.get('video_path')
    metadata = data.get('metadata', {
        'title': 'Generated Video',
        'description': 'Auto-generated animation',
        'tags': ['animation', 'AI']
    })
    
    try:
        # Download video
        local_path = minio_client.download_file("video-bucket", video_path, "final_video.mp4")
        
        # Upload to YouTube
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": metadata['title'],
                    "description": metadata['description'],
                    "tags": metadata['tags'],
                    "categoryId": "22"  # Entertainment
                },
                "status": {"privacyStatus": "public"}
            },
            media_body=local_path
        )
        response = request.execute()
        
        return jsonify({
            'status': 'success',
            'youtube_id': response['id'],
            'url': f"https://www.youtube.com/watch?v={response['id']}"
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)
