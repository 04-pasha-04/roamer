from flask import Flask, Response, request, abort, jsonify
import subprocess
import logging
import os
import requests
import threading
import time
from googleapiclient.discovery import build
from collections import deque
import redis

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube RTMP URL
YOUTUBE_URL = 'rtmp://a.rtmp.youtube.com/live2/fsw6-csp7-495j-vfm2-04ag'  # Replace with your YouTube RTMP URL
api_key = 'AIzaSyBAnFtogm4M7MhjqeubJpbAAWtUcVho6Q8'
broadcast_id = 'GwI0dayAyOQ'

# Path to the token file
token_file_path = 'token.txt'

# FFmpeg processes
current_ffmpeg_process = None

# Stream status
is_live_stream_active = False

# Build YouTube service
youtube = build('youtube', 'v3', developerKey=api_key)

# Command queue
command_queue = deque()

# Redis configuration
redis_host = 'localhost'  # Replace with your Redis host if different
redis_port = 6379  # Replace with your Redis port if different
redis_db = 0  # Redis database index

# Initialize Redis connection
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# Redis key for processed message IDs
processed_message_ids_key = 'processed_message_ids'

def load_secret_token():
    if not os.path.exists(token_file_path):
        raise FileNotFoundError(f"Token file not found at {token_file_path}. Please generate a token first.")

    with open(token_file_path, 'r') as token_file:
        return token_file.read().strip()

def start_main_ffmpeg_stream():
    global current_ffmpeg_process, is_live_stream_active
    if current_ffmpeg_process:
        current_ffmpeg_process.terminate()
    current_ffmpeg_process = subprocess.Popen([
        'ffmpeg',
        '-i', 'pipe:0',  # Input from pipe
        '-vf', 'drawtext=text=%{localtime}:x=10:y=10:fontsize=24:fontcolor=white',  # Draw time overlay
        '-c:v', 'libx264',  # Use H.264 codec for video
        '-preset', 'ultrafast',  # Use ultrafast preset for low latency
        '-tune', 'zerolatency',  # Tune for zero latency
        '-c:a', 'aac',      # Use AAC for audio
        '-f', 'flv',        # Output format for RTMP
        YOUTUBE_URL         # YouTube RTMP URL
    ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    is_live_stream_active = True

def start_fallback_ffmpeg_stream():
    global current_ffmpeg_process, is_live_stream_active
    if current_ffmpeg_process and current_ffmpeg_process.poll() is None:
        logger.info("Fallback stream is already running.")
        return
    logger.info("Starting fallback stream.")
    current_ffmpeg_process = subprocess.Popen([
        'ffmpeg',
        '-re',  # Read input at native frame rate
        '-f', 'lavfi', '-i', 'color=size=1920x1080:rate=30:color=black',
        '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-vf', "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='Reconnecting video stream...'",
        '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency',
        '-c:a', 'aac',
        '-ar', '44100', '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-f', 'flv',
        YOUTUBE_URL
    ])
    is_live_stream_active = False

def monitor_stream():
    global is_live_stream_active, current_ffmpeg_process
    while True:
        if not is_live_stream_active and (current_ffmpeg_process is None or current_ffmpeg_process.poll() is not None):
            logger.info("No active stream detected. Starting fallback stream.")
            start_fallback_ffmpeg_stream()
        time.sleep(5)  # Check every 5 seconds

# Start the monitoring thread
monitor_thread = threading.Thread(target=monitor_stream, daemon=True)
monitor_thread.start()

@app.route('/live', methods=['POST'])
def live():
    # Load the secret token from the file
    secret_token = load_secret_token()

    # Check the token in the request headers
    token = request.headers.get('Authorization')
    if token != f"Bearer {secret_token}":
        logger.warning("Unauthorized access attempt")
        abort(403, description="Forbidden: Invalid token")

    logger.info("Received RTMP stream")

    start_main_ffmpeg_stream()

    def generate():
        global is_live_stream_active
        try:
            while True:
                chunk = request.stream.read(1024)
                if not chunk:
                    break
                current_ffmpeg_process.stdin.write(chunk)
                current_ffmpeg_process.stdin.flush()
        finally:
            logger.info("RTMP stream ended")
            is_live_stream_active = False
            if current_ffmpeg_process:
                current_ffmpeg_process.stdin.close()
                current_ffmpeg_process.wait()

    return Response(generate(), content_type='video/x-flv')


@app.route('/get_command', methods=['GET'])
def get_command():
    # Fetch new messages from YouTube
    fetch_live_chat_messages()

    if command_queue:
        command = command_queue.popleft()  # Pop the command from the queue
        return jsonify({"command": command}), 200
    else:
        return jsonify({"message": "No commands available"}), 204


def get_live_broadcast_snippet(api_key, broadcast_id):
    url = "https://www.googleapis.com/youtube/v3/liveBroadcasts"

    # Define the parameters for the request
    params = {
        'id': broadcast_id,
        'part': 'snippet',
        'key': api_key
    }

    # Make the API request
    response = requests.get(url, params=params)

    # Raise an error if the request was unsuccessful
    response.raise_for_status()

    # Parse the JSON response
    return response.json()

def get_live_chat_id(api_key, broadcast_id):
    try:
        response = youtube.videos().list(
            part='liveStreamingDetails',
            id=broadcast_id
        ).execute()

        if 'items' not in response or not response['items']:
            logger.error("No items found in the response. The broadcast ID might be incorrect.")
            return None

        live_stream_details = response['items'][0].get('liveStreamingDetails')
        if not live_stream_details:
            logger.error("Live streaming details are not available for this broadcast ID.")
            return None

        live_chat_id = live_stream_details.get('activeLiveChatId')
        if not live_chat_id:
            logger.error("Live chat ID is not available. The stream might not be live or live chat is disabled.")
        return live_chat_id

    except Exception as e:
        logger.error(f"An error occurred while retrieving the live chat ID: {e}")
        return None

def fetch_live_chat_messages():
    global command_queue

    try:
        # Fetch the live chat ID
        live_chat_id = get_live_chat_id(api_key, broadcast_id)
        if not live_chat_id:
            logger.error("Live chat ID is not available.")
            return

        # Fetch live chat messages
        response = youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part='snippet',
            maxResults=200
        ).execute()

        for item in response['items']:
            message_id = item['id']  # Unique ID for each message
            message_text = item['snippet']['displayMessage'].lower()

            # Process the message if it contains a command and hasn't been processed yet
            if message_id not in redis_client.smembers(processed_message_ids_key) and any(
                    command in message_text for command in ['forward', 'left', 'right', 'back']):
                command_queue.append(message_text)
                redis_client.sadd(processed_message_ids_key, message_id)

    except Exception as e:
        logger.error(f"An error occurred while fetching live chat messages: {e}")


if __name__ == "__main__":
    # Start the fallback stream immediately
    start_fallback_ffmpeg_stream()
    app.run(host='0.0.0.0', port=5000)
