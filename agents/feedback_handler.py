from flask import Flask, request, jsonify
import json
import os
from prometheus_client import Counter

app = Flask(__name__)
REQUESTS_TOTAL = Counter('feedback_handler_requests_total', 'Total Requests to Feedback Handler')

@app.route('/feedback', methods=['POST'])
def handle_feedback():
    REQUESTS_TOTAL.inc()
    feedback = request.get_json()
    
    try:
        with open('feedback_db.json', 'a') as f:
            f.write(json.dumps(feedback) + '\n')
        
        return jsonify({'status': 'success'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
