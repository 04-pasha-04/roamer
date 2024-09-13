import RPi.GPIO as GPIO
import time

class MotorControl:
    def __init__(self, in1, in2, in3, in4):
        """Initialize the motor control with the given pin numbers."""
        self.in1 = in1  # Left motor IN1
        self.in2 = in2  # Left motor IN2
        self.in3 = in3  # Right motor IN3
        self.in4 = in4  # Right motor IN4

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.in2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.in3, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.in4, GPIO.OUT, initial=GPIO.LOW)

    # Function to control Motor 1 (Left Motor)
    def motor1_forward(self):
        print("Motor 1 (Left) Forward")
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)

    def motor1_backward(self):
        print("Motor 1 (Left) Backward")
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)

    def motor1_stop(self):
        print("Motor 1 (Left) Stop")
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)

    # Function to control Motor 2 (Right Motor)
    def motor2_forward(self):
        print("Motor 2 (Right) Forward")
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.LOW)

    def motor2_backward(self):
        print("Motor 2 (Right) Backward")
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.HIGH)

    def motor2_stop(self):
        print("Motor 2 (Right) Stop")
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

    # Incremental movement functions
    def move_forward_step(self, duration=0.5):
        """Move forward for a short duration (step forward)."""
        print("Moving forward...")
        self.motor1_forward()  # Left motor forward
        self.motor2_forward()  # Right motor forward
        time.sleep(duration)  # Move for a brief time
        self.stop_movement()
        print("Step forward complete")

    def move_backward_step(self, duration=0.5):
        """Move backward for a short duration (step backward)."""
        print("Moving backward...")
        self.motor1_backward()  # Left motor backward
        self.motor2_backward()  # Right motor backward
        time.sleep(duration)  # Move for a brief time
        self.stop_movement()
        print("Step backward complete")

    def rotate_left_step(self, duration=0.3):
        """Rotate left for a short duration."""
        print("Rotating left...")
        self.motor1_backward()  # Left motor backward
        self.motor2_forward()   # Right motor forward
        time.sleep(duration)  # Rotate for a brief time
        self.stop_movement()
        print("Rotate left step complete")

    def rotate_right_step(self, duration=0.3):
        """Rotate right for a short duration."""
        print("Rotating right...")
        self.motor1_forward()   # Left motor forward
        self.motor2_backward()  # Right motor backward
        time.sleep(duration)  # Rotate for a brief time
        self.stop_movement()
        print("Rotate right step complete")

    def stop_movement(self):
        """Stop both motors."""
        print("Stopping both motors...")
        self.motor1_stop()  # Stop left motor
        self.motor2_stop()  # Stop right motor
        print("Motors stopped")

    def cleanup(self):
        """Clean up GPIO pins when exiting."""
        GPIO.cleanup()
