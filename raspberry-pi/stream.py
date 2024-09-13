import subprocess
import time
import os

# Path to the token file
token_file_path = 'token.txt'

def load_secret_token():
    if not os.path.exists(token_file_path):
        raise FileNotFoundError(f"Token file not found at {token_file_path}. Please generate a token first.")

    with open(token_file_path, 'r') as token_file:
        return token_file.read().strip()

def stream_to_server():
    # Load the secret token from the file
    secret_token = load_secret_token()

    # Command to capture video and stream to the server
    command = (
        'libcamera-vid '
        '--inline '
        '--nopreview '
        '-t 0 '
        '--width 640 '
        '--height 480 '
        '--framerate 15 '
        '--codec h264 '
        '-o - | '
        'ffmpeg '
        '-f lavfi '
        '-i anullsrc=channel_layout=stereo:sample_rate=44100 '
        '-thread_queue_size 1024 '
        '-use_wallclock_as_timestamps 1 '
        '-i pipe:0 '
        '-c:v copy '
        '-c:a aac '
        '-preset fast '
        '-strict experimental '
        '-f flv '
        f'-headers "Authorization: Bearer {secret_token}" '  # Add token here
        'http://192.168.0.80:5000/live'  # Replace with your server's IP address
    )

    while True:
        try:
            # Run the command
            process = subprocess.run(command, shell=True)

            # If the process exits with a non-zero code, log and restart
            if process.returncode != 0:
                print(f"Stream crashed with return code {process.returncode}. Restarting in 5 seconds...")
                time.sleep(5)  # Wait before restarting

        except Exception as e:
            print(f"An error occurred: {e}. Restarting in 5 seconds...")
            time.sleep(5)  # Wait before restarting

if __name__ == "__main__":
    stream_to_server()
