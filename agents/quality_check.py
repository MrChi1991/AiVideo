from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np
from storage.minio_client import MinIOClient
from prometheus_client import Counter

app = Flask(__name__)
minio_client = MinIOClient()
model = tf.keras.models.load_model("ml_models/aqc_validator/model.h5")
REQUESTS_TOTAL = Counter('quality_check_requests_total', 'Total Requests to Quality Check')

@app.route('/validate', methods=['POST'])
def validate_output():
    REQUESTS_TOTAL.inc()
    data = request.get_json()
    task_type = data.get('task_type')
    output_path = data.get('output_path')
    
    try:
        if task_type == 'image':
            local_path = minio_client.download_file("storyboard-bucket", output_path, "temp_image.png")
            img = tf.keras.preprocessing.image.load_img(local_path, target_size=(224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)
            
            prediction = model.predict(img_array)
            if prediction[0][0] < 0.5:  # Threshold for quality
                return jsonify({'status': 'reject', 'reason': 'Low quality image'}), 400
        
        return jsonify({'status': 'approve', 'next_step': data.get('next_step', 'next')}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
