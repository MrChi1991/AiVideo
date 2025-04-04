import pika
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
from storage.minio_client import MinIOClient
from prometheus_client import Counter

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
minio_client = MinIOClient()
REQUESTS_TOTAL = Counter('scriptwriter_requests_total', 'Total Requests to Scriptwriter')

def callback(ch, method, properties, body):
    REQUESTS_TOTAL.inc()
    task = json.loads(body)
    if 'task_id' not in task:
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return
    prompt = task['data'].get('prompt', 'Write a short script about an animated cat adventure')
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        script = response.choices[0].message.content
        
        script_id = f"scripts/{task['task_id']}.txt"
        minio_client.upload_string("script-bucket", script_id, script)
        
        ch.basic_publish(exchange='', routing_key='quality_check', body=json.dumps({
            'task': 'validate_script',
            'data': {'script_id': script_id},
            'previous_step': 'scriptwriting',
            'next_step': 'storyboarding'
        }))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error in scriptwriting: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def main():
    connection = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', retry_delay=5))
        channel = connection.channel()
        channel.queue_declare(queue='scriptwriting')
        channel.basic_consume(queue='scriptwriting', on_message_callback=callback)
        print('Scriptwriter started')
        channel.start_consuming()
    except Exception as e:
        print(f"Không thể khởi động Scriptwriter: {e}")
    finally:
        if connection and not connection.is_closed:
            connection.close()

if __name__ == '__main__':
    main()
