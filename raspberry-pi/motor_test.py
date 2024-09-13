import RPi.GPIO as GPIO
import time

# Pin definitions for motors
left_motor_in1 = 4
left_motor_in2 = 23
right_motor_in3 = 24
right_motor_in4 = 25

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable warnings about pins already in use
GPIO.setup(left_motor_in1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(left_motor_in2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(right_motor_in3, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(right_motor_in4, GPIO.OUT, initial=GPIO.LOW)

def move_left_forward_right_backward():

    GPIO.output(left_motor_in1, GPIO.HIGH)
    GPIO.output(left_motor_in2, GPIO.LOW)
    GPIO.output(right_motor_in3, GPIO.HIGH)
    GPIO.output(right_motor_in4, GPIO.LOW)
    print("Left motor forward, Right motor forward...")

def move_left_backward_right_forward():
    """Move left motor backward and right motor forward."""
    GPIO.output(left_motor_in1, GPIO.LOW)
    GPIO.output(left_motor_in2, GPIO.HIGH)
    GPIO.output(right_motor_in3, GPIO.HIGH)
    GPIO.output(right_motor_in4, GPIO.LOW)
    print("Left motor backward, Right motor forward...")

def stop_movement():
    """Stop both motors."""
    GPIO.output(left_motor_in1, GPIO.LOW)
    GPIO.output(left_motor_in2, GPIO.LOW)
    GPIO.output(right_motor_in3, GPIO.LOW)
    GPIO.output(right_motor_in4, GPIO.LOW)
    print("Stopping motors...")

# Test opposite movements
move_left_forward_right_backward()
time.sleep(5)  # Run for 5 seconds
stop_movement()

time.sleep(2)  # Wait for 2 seconds

move_left_backward_right_forward()
time.sleep(5)  # Run for 5 seconds
stop_movement()

# Clean up GPIO
GPIO.cleanup()
