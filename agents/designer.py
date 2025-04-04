from flask import Flask, request, jsonify
import requests
from storage.minio_client import MinIOClient
import io
from prometheus_client import Counter

app = Flask(__name__)
minio_client = MinIOClient()
DEEPAI_API_KEY = "your_deepai_key"  # Need to set in .env
REQUESTS_TOTAL = Counter('designer_requests_total', 'Total Requests to Designer')

@app.route('/process', methods=['POST'])
def design_assets():
    REQUESTS_TOTAL.inc()
    data = request.json
    prompts = data["prompts"]  # List of design prompts
    
    try:
        designs = []
        for prompt in prompts:
            response = requests.post(
                "[invalid url, do not cite]
                data={'text': prompt},
                headers={'api-key': DEEPAI_API_KEY}
            )
            image_url = response.json().get("output_url")
            # Download and upload to MinIO
            img_response = requests.get(image_url)
            upload_path = f"designs/{data['task_id']}/{prompt[:10]}.png"
            minio_client.upload_file("design-bucket", upload_path, io.BytesIO(img_response.content))
            designs.append(upload_path)
        
        return jsonify({
            "status": "success",
            "output": designs,
            "next_step": "animation"
        })
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
