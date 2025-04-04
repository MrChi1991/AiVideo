from flask import Flask, request, jsonify
import bpy
from storage.minio_client import MinIOClient
import os
from prometheus_client import Counter

app = Flask(__name__)
minio_client = MinIOClient()
REQUESTS_TOTAL = Counter('animator_requests_total', 'Total Requests to Animator')

@app.route('/process', methods=['POST'])
def animate():
    REQUESTS_TOTAL.inc()
    data = request.get_json()
    design_paths = data.get('design_paths', [])
    
    try:
        # Clear existing scene
        bpy.ops.wm.read_factory_settings(use_empty=True)
        
        # Load each design as a plane
        for i, path in enumerate(design_paths):
            local_path = minio_client.download_file("design-bucket", path, f"temp_design_{i}.png")
            bpy.ops.import_image.to_plane(files=[{"name": os.path.basename(local_path)}], directory=os.path.dirname(local_path))
            obj = bpy.context.object
            obj.location = (i*2, 0, 0)  # Space out objects
            
            # Add simple animation: move forward
            obj.keyframe_insert(data_path="location", frame=1)
            obj.location.x += 5
            obj.keyframe_insert(data_path="location", frame=120)
        
        # Render animation
        bpy.context.scene.render.filepath = f"animations/{data['task_id']}.mp4"
        bpy.ops.render.render(animation=True)
        
        # Upload to MinIO
        minio_client.upload_file("animation-bucket", f"animations/{data['task_id']}.mp4", bpy.context.scene.render.filepath)
        
        return jsonify({
            'status': 'success',
            'animation_path': f"animations/{data['task_id']}.mp4",
            'next_step': 'soundmastering'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
