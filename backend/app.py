# import cv2
# import base64
# import numpy as np
# import os
# import time
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from detect import process_image

# app = Flask(__name__)
# CORS(app, supports_credentials=True)

# # ✅ Define the directory for storing recorded videos
# VIDEO_DIR = r"F:\BE_Project\Final Year Project 2025\VIdeo_Integrated_Github\Model integrated - Copy\BE_ML_Model\backend\recorded_videos"
# os.makedirs(VIDEO_DIR, exist_ok=True)

# video_writer = None
# is_recording = False
# output_video_path = None

# @app.route('/stream', methods=['POST'])
# def stream():
#     global video_writer, is_recording

#     try:
#         data = request.json
#         image_data = data['image'].split(",")[1]  
#         image_bytes = base64.b64decode(image_data)

#         # Convert bytes to NumPy array and then to OpenCV format
#         nparr = np.frombuffer(image_bytes, np.uint8)
#         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         if frame is None:
#             raise ValueError("Decoded frame is None. Check base64 encoding.")

#         # Process the frame
#         processed_image_base64, defects = process_image(frame)

#         # Save the frame to video if recording
#         if is_recording and video_writer is not None:
#             video_writer.write(frame)

#         return jsonify({"processed_image": processed_image_base64, "defects": defects})

#     except Exception as e:
#         print("Error processing frame:", e)
#         return jsonify({"error": str(e)}), 500

# @app.route('/start_recording', methods=['POST'])
# def start_recording():
#     global video_writer, is_recording, output_video_path

#     timestamp = time.strftime("%Y%m%d-%H%M%S")
#     output_video_path = os.path.join(VIDEO_DIR, f"output_{timestamp}.avi")

#     # ✅ Define video codec and create VideoWriter
#     fourcc = cv2.VideoWriter_fourcc(*'XVID')
#     video_writer = cv2.VideoWriter(output_video_path, fourcc, 10, (640, 480))

#     if not video_writer.isOpened():
#         return jsonify({"error": "Failed to start video recording"}), 500

#     is_recording = True
#     return jsonify({"message": "Recording started", "video_path": output_video_path})

# @app.route('/stop_recording', methods=['POST'])
# def stop_recording():
#     global video_writer, is_recording

#     if video_writer is not None:
#         video_writer.release()
#         video_writer = None

#     is_recording = False
#     return jsonify({"message": "Recording stopped", "video_path": output_video_path})

# # ✅ New Route to List Recorded Videos
# @app.route('/get_videos', methods=['GET'])
# def get_videos():
#     try:
#         video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".avi")]
#         video_list = [{"filename": f, "url": f"http://localhost:5000/videos/{f}"} for f in video_files]

#         return jsonify({"videos": video_list})

#     except Exception as e:
#         print("Error listing videos:", e)
#         return jsonify({"error": str(e)}), 500

# # ✅ Serve Video Files
# @app.route('/videos/<filename>', methods=['GET'])
# def get_video(filename):
#     return send_from_directory(VIDEO_DIR, filename)

# if __name__ == '__main__':
#     app.run(debug=True)

import cv2
import base64
import numpy as np
import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from detect import process_image
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Flask app setup
app = Flask(__name__)
CORS(app, supports_credentials=True)

# ✅ Define directory for storing recorded videos
VIDEO_DIR = os.getenv("VIDEO_DIR", "recorded_videos")  # Use relative path for portability
os.makedirs(VIDEO_DIR, exist_ok=True)

video_writer = None
is_recording = False
output_video_path = None

@app.route('/stream', methods=['POST'])
def stream():
    global video_writer, is_recording

    try:
        data = request.json
        image_data = data['image'].split(",")[1]  
        image_bytes = base64.b64decode(image_data)

        # Convert bytes to NumPy array and then to OpenCV format
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise ValueError("Decoded frame is None. Check base64 encoding.")

        # Process the frame
        processed_image_base64, defects = process_image(frame)

        # Save the frame to video if recording
        if is_recording and video_writer is not None:
            video_writer.write(frame)

        return jsonify({"processed_image": processed_image_base64, "defects": defects})

    except Exception as e:
        print("Error processing frame:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global video_writer, is_recording, output_video_path

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_video_path = os.path.join(VIDEO_DIR, f"output_{timestamp}.mp4")  # ✅ Use MP4 format

    # ✅ Use 'mp4v' codec for better browser compatibility
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, 10, (640, 480))

    if not video_writer.isOpened():
        return jsonify({"error": "Failed to start video recording"}), 500

    is_recording = True
    return jsonify({"message": "Recording started", "video_path": output_video_path})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global video_writer, is_recording

    if video_writer is not None:
        video_writer.release()
        video_writer = None

    is_recording = False
    return jsonify({"message": "Recording stopped", "video_path": output_video_path})

# ✅ List Recorded Videos
@app.route('/get_videos', methods=['GET'])
def get_videos():
    try:
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")]
        video_list = [{"filename": f, "url": f"/videos/{f}"} for f in video_files]  # ✅ Remove hardcoded backend URL

        return jsonify({"videos": video_list})

    except Exception as e:
        print("Error listing videos:", e)
        return jsonify({"error": str(e)}), 500

# ✅ Serve Video Files
@app.route('/videos/<filename>', methods=['GET'])
def get_video(filename):
    return send_from_directory(VIDEO_DIR, filename, mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("DEBUG", "False").lower() == "true")

