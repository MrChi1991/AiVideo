from flask import Flask, request, jsonify
import pika
import json
from dotenv import load_dotenv
import os
from prometheus_client import Counter, generate_latest  # Thêm import

load_dotenv()
app = Flask(__name__)

REQUESTS_TOTAL = Counter('controller_requests_total', 'Total Requests to Controller')

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', retry_delay=5))
    channel = connection.channel()
except Exception as e:
    print(f"Không thể kết nối RabbitMQ: {e}")
    exit(1)

queues = ['scriptwriting', 'quality_check', 'storyboarding', 'designing', 'animating', 
          'soundmastering', 'editing', 'polishing', 'distributing']
for queue in queues:
    channel.queue_declare(queue=queue)

@app.route('/task', methods=['POST'])
def receive_task():
    REQUESTS_TOTAL.inc()
    data = request.get_json(silent=True)  # Thêm silent để tránh lỗi JSON
    if not data or 'type' not in data:
        return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
    task_type = data.get('type')
    task_data = data.get('data', {})

    if task_type == 'start':
        try:
            channel.basic_publish(exchange='', routing_key='scriptwriting',
                                body=json.dumps({'task': 'write_script', 'data': task_data}))
            return jsonify({'status': 'task_queued', 'next_step': 'scriptwriting'}), 200
        except Exception as e:
            return jsonify({'error': f'Không thể gửi task: {e}'}), 500
    return jsonify({'error': 'Invalid task type'}), 400

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('CONTROLLER_PORT', 5000)))  # Linh hoạt cổng qua .env
