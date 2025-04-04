from flask import Flask, request, jsonify
import subprocess
from storage.minio_client import MinIOClient
from prometheus_client import Counter

app = Flask(__name__)
minio_client = MinIOClient()
REQUESTS_TOTAL = Counter('polisher_requests_total', 'Total Requests to Polisher')

@app.route('/process', methods=['POST'])
def polish_video():
    REQUESTS_TOTAL.inc()
    data = request.get_json()
    video_path = data.get('video_path')
    
    try:
        # Download video
        local_path = minio_client.download_file("video-bucket", video_path, "temp_video.mp4")
        
        # Enhance with FFmpeg (upscale to 4K, improve quality)
        output_path = f"polished_videos/{data['task_id']}_4k.mp4"
        subprocess.run([
            "ffmpeg", "-i", local_path,
            "-vf", "scale=3840:2160",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            output_path
        ])
        
        # Upload polished video
        minio_client.upload_file("video-bucket", output_path, output_path)
        
        return jsonify({
            'status': 'success',
            'output_path': output_path,
            'next_step': 'distributing'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
