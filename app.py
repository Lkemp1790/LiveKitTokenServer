from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt, os, time

app = Flask(__name__)
CORS(app)

LIVEKIT_API_KEY = os.getenv('LIVEKIT_API_KEY')        # required
LIVEKIT_API_SECRET = os.getenv('LIVEKIT_API_SECRET')  # required
LIVEKIT_WS_URL = os.getenv('LIVEKIT_WS_URL', 'wss://mochai-j3b8jbmd.livekit.cloud')

def generate_token(room_name: str, identity: str) -> str:
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return None
    now = int(time.time())
    payload = {
        'iss': LIVEKIT_API_KEY,          # API key ID
        'sub': identity,                 # participant identity
        'exp': now + 3600,
        'nbf': now,
        # LiveKit video grant
        'video': {
            'room': room_name,
            'roomJoin': True,
            'canPublish': True,
            'canSubscribe': True,
            'canPublishData': True,
        },
        # Optional nice-to-haves
        'name': identity,
        'metadata': '',
    }
    return jwt.encode(payload, LIVEKIT_API_SECRET, algorithm='HS256')

@app.route('/token', methods=['GET'])
def get_token():
    room_name = request.args.get('roomName', 'agent-room')
    identity = request.args.get('participantName', 'unity-client')
    token = generate_token(room_name, identity)
    if not token:
        return jsonify({'error': 'Failed to generate token'}), 500
    return jsonify({
        'serverUrl': LIVEKIT_WS_URL,          # exact Cloud URL
        'participantToken': token,            # field name client accepts
        'roomName': room_name,
        'participantName': identity,
    })
