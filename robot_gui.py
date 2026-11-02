import time
import tkinter as tk
import requests

# Raspberry Pi settings
pi_ip = "192.168.240.129"
pi_url = "http://" + pi_ip + ":5001/action"
speed = 45


# Sends a command to the robot and writes the result in the user log
def send_command(action, message):
    try:
        response = requests.post(f"{pi_url}/{action}", json={"speed": speed}, timeout=2)
        result = response.json()
        code = response.status_code
        if result.get("status") == "executed":
            write_log(message + " (status code " + str(code) + ")")
        else:
            write_log("Robot refused: " + result.get("reason", "unknown") + " (status code " + str(code) + ")")
        return result
    except requests.exceptions.RequestException:
        write_log("ERROR: could not reach the robot")
        return None


# Adds a line with the time to the user log
def write_log(text):
    log_box.config(state="normal")
    log_box.insert("end", time.strftime("%H:%M:%S") + "  " + text + "\n")
    log_box.see("end")
    log_box.config(state="disabled")


# Button functions
def movefwd():
    send_command("up", "Moving forward")


def movebackward():
    send_command("down", "Moving backward")


def turnleft():
    send_command("left", "Turning left")


def turnright():
    send_command("right", "Turning right")


def stop():
    send_command("pause", "Stopped")


# The play button turns the robot's power on or off
def toggle_power():
    result = send_command("play", "Power toggled")
    if result and "robot_powered_on" in result:
        if result["robot_powered_on"]:
            write_log("Robot power is ON")
        else:
            write_log("Robot power is OFF")


root = tk.Tk()
root.title("4 Quadrant GUI")
root.geometry("1920x1080")

# Top left video stream quadrant
top_left_quad = tk.Frame(root, borderwidth=1, relief="solid")
top_left_quad.place(relx=0.0, rely=0.0, relwidth=0.5, relheight=0.5)

box1 = tk.Frame(top_left_quad, borderwidth=2, relief="solid")
box1.place(relx=0.5, rely=0.5, anchor="center")
tk.Label(box1, text="Video Stream 1 Placeholder").pack(padx=40, pady=40)

# Bottom left video stream quadrant
bottom_left_quad = tk.Frame(root, borderwidth=1, relief="solid")
bottom_left_quad.place(relx=0.0, rely=0.5, relwidth=0.5, relheight=0.5)

box2 = tk.Frame(bottom_left_quad, borderwidth=2, relief="solid")
box2.place(relx=0.5, rely=0.5, anchor="center")
tk.Label(box2, text="Video Stream 2 Placeholder").pack(padx=40, pady=40)

# Bottom right user log quadrant
bottom_right_quad = tk.Frame(root, borderwidth=1, relief="solid")
bottom_right_quad.place(relx=0.5, rely=0.5, relwidth=0.5, relheight=0.5)

tk.Label(bottom_right_quad, text="User Log").pack(pady=5)
log_box = tk.Text(bottom_right_quad, state="disabled")
log_box.pack(fill="both", expand=True, padx=10, pady=10)

# Top right controls quadrant
top_right_quad = tk.Frame(root, borderwidth=1, relief="solid")
top_right_quad.place(relx=0.5, rely=0.0, relwidth=0.5, relheight=0.5)

pad = tk.Frame(top_right_quad)
pad.place(relx=0.5, rely=0.5, anchor="center")

up_button = tk.Button(pad, text="^", command=movefwd)
down_button = tk.Button(pad, text="v", command=movebackward)
left_button = tk.Button(pad, text="<", command=turnleft)
right_button = tk.Button(pad, text=">", command=turnright)

buttons_frame = tk.Frame(pad)
tk.Button(buttons_frame, text="▶", command=toggle_power).pack(side="left")
tk.Button(buttons_frame, text="■", command=stop).pack(side="left")
up_button.grid(row=0, column=1)
left_button.grid(row=1, column=0)
buttons_frame.grid(row=1, column=1)
right_button.grid(row=1, column=2)
down_button.grid(row=2, column=1)

root.mainloop()
