from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64
import requests
import os

# === Configuration ===
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
# =====================

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/send-photo', methods=['POST'])
def send_photo():
    temp_path = None
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'status': 'error', 'msg': 'No image field'}), 400

        image_data = data['image']
        if ',' in image_data:
            header, image_base64 = image_data.split(',', 1)
        else:
            image_base64 = image_data
        img_bytes = base64.b64decode(image_base64)

        temp_path = f'temp_{os.getpid()}.jpg'
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)
        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(temp_path, 'rb') as photo:
            resp = requests.post(
                send_url, 
                data={'chat_id': CHAT_ID}, 
                files={'photo': photo},
                timeout=30
            )

        resp_json = resp.json()
        
        if not resp_json.get('ok'):
            return jsonify({'status': 'error', 'telegram_response': resp_json}), 500

        return jsonify({'status': 'ok', 'telegram_response': resp_json})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500
        
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)