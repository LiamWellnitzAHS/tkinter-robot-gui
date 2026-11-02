from flask import Flask, jsonify, request
import time
from PCA9685 import PCA9685

app = Flask(__name__)


class Robot:
    def __init__(self):
        # Waveshare motor driver pin assignments
        self.PWMA = 0
        self.AIN1 = 2
        self.AIN2 = 1
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

        # Initialize the PWM controller at I2C address 0x40
        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(50)

        # Tracks whether the robot's power system is enabled
        self.powered_on = False

    def stop(self):
        # Set motor speeds to zero and disable the motor driver pins
        self.pwm.setDutycycle(self.PWMA, 0)
        self.pwm.setLevel(self.AIN1, 0)
        self.pwm.setLevel(self.AIN2, 0)

        self.pwm.setDutycycle(self.PWMB, 0)
        self.pwm.setLevel(self.BIN1, 0)
        self.pwm.setLevel(self.BIN2, 0)

    def toggle_power(self):
        # Switch the robot's power state
        self.powered_on = not self.powered_on

        # Stop the motors when the robot is switched off
        if not self.powered_on:
            self.stop()

        print(f"-> Robot Power System: {'ON' if self.powered_on else 'OFF'}")

        return self.powered_on

    def movefwd(self, speed=45):
        # Drive both motors forward, compensating for the left motor
        print(f"Moving Forward at speed {speed}")
        self.pwm.setDutycycle(self.PWMA, speed + 5)
        self.pwm.setLevel(self.AIN1, 0)
        self.pwm.setLevel(self.AIN2, 1)
        self.pwm.setDutycycle(self.PWMB, speed)
        self.pwm.setLevel(self.BIN1, 0)
        self.pwm.setLevel(self.BIN2, 1)

    def movebackward(self, speed=45):
        # Drive both motors backward, compensating for the right motor
        print(f"Moving Backward at speed {speed}")
        
        self.pwm.setDutycycle(self.PWMA, speed)
        self.pwm.setLevel(self.AIN1, 1)
        self.pwm.setLevel(self.AIN2, 0)

        self.pwm.setDutycycle(self.PWMB, speed + 7)
        self.pwm.setLevel(self.BIN1, 1)
        self.pwm.setLevel(self.BIN2, 0)

    def turn(self, direction, speed=45):
        # Turn by driving the two motors in opposite directions
        if direction == "right":
            print(f"Turning Right at speed {speed}")

            # Left motor forward, right motor backward
            self.pwm.setDutycycle(self.PWMA, speed)
            self.pwm.setLevel(self.AIN1, 0)
            self.pwm.setLevel(self.AIN2, 1)

            self.pwm.setDutycycle(self.PWMB, speed)
            self.pwm.setLevel(self.BIN1, 1)
            self.pwm.setLevel(self.BIN2, 0)

        elif direction == "left":
            print(f"Turning Left at speed {speed}")

            # Left motor backward, right motor forward
            self.pwm.setDutycycle(self.PWMA, speed)
            self.pwm.setLevel(self.AIN1, 1)
            self.pwm.setLevel(self.AIN2, 0)

            self.pwm.setDutycycle(self.PWMB, speed)
            self.pwm.setLevel(self.BIN1, 0)
            self.pwm.setLevel(self.BIN2, 1)

        else:
            # Reject directions other than left or right
            raise ValueError("Direction must be 'left' or 'right'")

    def turnleft(self, speed=45):
        # Turn left by calling turn() with the direction "left"
        self.turn("left", speed)

    def turnright(self, speed=45):
        # Turn right by calling turn() with the direction "right"
        self.turn("right", speed)

    def execute(self, command, payload=None):
        # Handle commands received from the Flask API
        payload = payload or {}

        # Handle the power toggle separately
        if command == "play":
            return {
                "status": "executed",
                "robot_powered_on": self.toggle_power()
            }

        # Ignore movement commands when the robot is switched off
        if not self.powered_on and command in ["up", "down", "left", "right"]:
            return {
                "status": "ignored",
                "reason": "Robot system is off. Use 'play' to turn on."
            }, 400

        # Read the requested speed, defaulting to 50
        speed = payload.get("speed", 50)

        # Dispatch the command to the appropriate method
        if command == "up":
            self.movefwd(speed)

        elif command == "down":
            self.movebackward(speed)

        elif command == "left":
            self.turnleft(speed)

        elif command == "right":
            self.turnright(speed)

        elif command == "pause":
            print("Executing Emergency Stop")
            self.stop()

        else:
            # Return an error for commands the API does not recognize
            return {
                "status": "error",
                "reason": "Unknown command"
            }, 400

        # Report the result of the command
        return {
            "status": "executed",
            "command": command,
            "robot_powered_on": self.powered_on
        }


# Create one Robot instance for the Flask application
robot = Robot()


@app.route("/action/<command>", methods=["POST"])
def handle_action(command):
    # Read the JSON request body, using an empty dictionary if absent
    payload = request.get_json() or {}

    # Execute the requested command and retrieve its response
    result = robot.execute(command, payload)

    # Some commands return both a response and an HTTP status code
    if isinstance(result, tuple):
        response, status_code = result
        return jsonify(response), status_code

    return jsonify(result)


if __name__ == "__main__":
    # Make the Flask server accessible to other devices on the network
    app.run(host="0.0.0.0", port=5001)
