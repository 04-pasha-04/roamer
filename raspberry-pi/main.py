import threading
import time
import requests  # To poll the get_command endpoint
from motor_control import MotorControl  # Import motor control
import stream  # Import the streaming control

# Pin definitions for motors (adjust these pins as per your setup)
left_motor_in1 = 4
left_motor_in2 = 23
right_motor_in3 = 24
right_motor_in4 = 25

# Create the MotorControl object
motor = MotorControl(left_motor_in1, left_motor_in2, right_motor_in3, right_motor_in4)

def run_streaming():
    """Function to start video streaming."""
    stream.stream_to_server()

def poll_get_command():
    """Function to poll the get_command endpoint every 5 seconds."""
    url = "http://192.168.0.80:5000/get_command"  # Replace with your actual endpoint
    while True:
        try:
            # Make a GET request to the get_command endpoint
            response = requests.get(url)

            if response.status_code == 200:
                # Process the command from the response
                command = response.json().get("command", None)  # Assuming the response is JSON

                if command:
                    print(f"Received command: {command}")
                    # Add motor actions based on the command
                    if command == "forward":
                        motor.move_forward_step(1)  # Move forward for 1 second
                    elif command == "backward":
                        motor.move_backward_step(1)  # Move backward for 1 second
                    elif command == "left":
                        motor.rotate_left_step(0.5)  # Rotate left
                    elif command == "right":
                        motor.rotate_right_step(0.5)  # Rotate right
                    else:
                        print(f"Unknown command: {command}")

            else:
                print(f"Failed to get command: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error polling get_command endpoint: {e}")

        time.sleep(5)  # Wait 5 seconds before polling again

if __name__ == "__main__":
    # Create two threads: one for motor control and one for streaming
    stream_thread = threading.Thread(target=run_streaming)
    poll_thread = threading.Thread(target=poll_get_command)

    # Start both threads
    stream_thread.start()
    poll_thread.start()

    # Wait for both threads to finish
    stream_thread.join()
    poll_thread.join()
