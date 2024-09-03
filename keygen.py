import secrets
import os

# Define the path where the token will be stored
token_file_path = 'token.txt'

def generate_and_store_token():
    # Generate a secure token
    token = secrets.token_hex(16)  # Generates a 32-character hex token
    
    # Store the token in a file
    with open(token_file_path, 'w') as token_file:
        token_file.write(token)
    
    print(f"Token generated and stored in {token_file_path}")

if __name__ == "__main__":
    # Check if token file already exists
    if os.path.exists(token_file_path):
        print(f"Token file already exists at {token_file_path}.")
    else:
        generate_and_store_token()
