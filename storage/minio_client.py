from minio import Minio
from dotenv import load_dotenv
import os
import io

load_dotenv()

class MinIOClient:
    def __init__(self):
        self.client = Minio(
            os.getenv('MINIO_ENDPOINT', 'localhost:9000'),
            access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('MINIO_SECRET_PASSWORD', 'minioadmin'),
            secure=False
        )

    def upload_string(self, bucket_name, object_name, content):
        try:
            self.client.put_object(bucket_name, object_name, io.BytesIO(content.encode()), len(content))
            return True
        except Exception as e:
            print(f"MinIO upload error: {e}")
            return False

    def upload_file(self, bucket_name, object_name, file_obj):
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
            self.client.put_object(bucket_name, object_name, file_obj, length=-1, part_size=10*1024*1024)
            return True
        except Exception as e:
            print(f"MinIO upload error: {e}")
            return False

    def download_file(self, bucket_name, object_name, local_path):
        try:
            self.client.fget_object(bucket_name, object_name, local_path)
            return local_path
        except Exception as e:
            print(f"MinIO download error: {e}")
            return None
