import os

RABBITMQ_CONFIG = {
    "host": os.getenv('RABBITMQ_HOST', 'localhost'),
    "port": int(os.getenv('RABBITMQ_PORT', 5672)),
    "credentials": {
        "username": os.getenv('RABBITMQ_USER', 'guest'),
        "password": os.getenv('RABBITMQ_PASSWORD', 'guest')
    }
}
