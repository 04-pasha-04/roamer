import secrets
import os
import json

# Load configuration from JSON file
config_file_path = 'server/config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)


def generate_and_store_token():
    # Generate a secure token
    token = secrets.token_hex(16)  # Generates a 32-character hex token
    
    # Store the token in a file
    with open(config_file_path, 'w') as token_:
        token_.write(token)
    
    print(f"Token generated and stored in {config_file_path}")

if __name__ == "__main__":
    # Check if token file already exists
    if os.path.exists(config_file_path):
        print(f"Token file already exists at {config_file_path}.")
    else:
        generate_and_store_token()
