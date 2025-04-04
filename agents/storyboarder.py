from flask import Flask, request, jsonify
from diffusers import StableDiffusionPipeline
import torch
from storage.minio_client import MinIOClient
import io
import os
from prometheus_client import Counter

app = Flask(__name__)
minio_client = MinIOClient()
REQUESTS_TOTAL = Counter('storyboarder_requests_total', 'Total Requests to Storyboarder')

# Tải model chỉ khi cần
pipeline = None
if torch.cuda.is_available():
    pipeline = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16)
    pipeline = pipeline.to("cuda")
else:
    pipeline = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1", torch_dtype=torch.float32)  # Model nhẹ hơn cho CPU

@app.route('/process', methods=['POST'])
def generate_storyboard():
    REQUESTS_TOTAL.inc()
    data = request.get_json(silent=True)
    if not data or 'task_id' not in data:
        return jsonify({'error': 'Dữ liệu không hợp lệ hoặc thiếu task_id'}), 400
    script = data.get('script', 'A cat in a forest, sunny day')
    scenes = script.split('\n')

    try:
        storyboards = []
        for i, scene in enumerate(scenes[:5]):  # Giới hạn 5 scenes để tối ưu
            if scene.strip():
                image = pipeline(scene).images[0]
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                storyboard_id = f"storyboards/{data['task_id']}/scene_{i}.png"
                minio_client.upload_file("storyboard-bucket", storyboard_id, img_byte_arr)
                storyboards.append(storyboard_id)

        return jsonify({
            'status': 'success',
            'storyboards': storyboards,
            'next_step': 'designing'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('STORYBOARDER_PORT', 5002)))
