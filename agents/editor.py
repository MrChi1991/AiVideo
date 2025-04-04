from flask import Flask, request, jsonify
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from storage.minio_client import MinIOClient
from prometheus_client import Counter

app = Flask(__name__)
minio_client = MinIOClient()
REQUESTS_TOTAL = Counter('editor_requests_total', 'Total Requests to Editor')

@app.route('/process', methods=['POST'])
def edit_video():
    REQUESTS_TOTAL.inc()
    data = request.get_json()
    video_paths = data.get('video_paths', [])
    audio_path = data.get('audio_path')
    
    try:
        # Download videos and audio
        videos = [VideoFileClip(minio_client.download_file("animation-bucket", path, f"temp_{i}.mp4")) 
                 for i, path in enumerate(video_paths)]
        audio = AudioFileClip(minio_client.download_file("audio-bucket", audio_path, "temp_audio.mp3"))
        
        # Concatenate videos and set audio
        final_video = concatenate_videoclips(videos)
        final_video = final_video.set_audio(audio)
        
        # Save and upload
        output_path = f"edited_videos/{data['task_id']}.mp4"
        final_video.write_videofile(output_path, codec="libx264")
        minio_client.upload_file("video-bucket", output_path, output_path)
        
        return jsonify({
            'status': 'success',
            'output_path': output_path,
            'next_step': 'polishing'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
