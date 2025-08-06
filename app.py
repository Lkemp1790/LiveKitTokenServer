from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def generate_token(room_name, participant_identity):
    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')
    
    if not api_key or not api_secret:
        return None
    
    exp = datetime.now() + timedelta(hours=1)
    
    payload = {
        'iss': api_key,
        'sub': api_key,
        'jti': f'{participant_identity}-{datetime.now().timestamp()}',
        'exp': exp,
        'nbf': datetime.now(),
        'room': room_name,
        'participant': participant_identity,
        'video': {
            'room': room_name,
            'roomJoin': True,
            'canPublish': True,
            'canSubscribe': True,
            'canPublishData': True
        },
        'audio': {
            'room': room_name,
            'roomJoin': True,
            'canPublish': True,
            'canSubscribe': True
        }
    }
    
    return jwt.encode(payload, api_secret, algorithm='HS256')

@app.route('/token', methods=['GET'])
def get_token():
    room_name = request.args.get('roomName', 'agent-room')
    participant_identity = request.args.get('participantName', 'unity-client')
    
    token = generate_token(room_name, participant_identity)
    livekit_url = f"wss://{os.getenv('LIVEKIT_API_KEY', '')[-1]}.livekit.cloud"
    
    if not token:
        return jsonify({"error": "Failed to generate token"}), 500
    
    return jsonify({
        "serverUrl": livekit_url,
        "participantToken": token,
        "roomName": room_name,
        "participantName": participant_identity
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
