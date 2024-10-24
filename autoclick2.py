import tkinter as tk
from tkinter import ttk
import threading
import time
import random
from pynput import keyboard
from pynput.mouse import Button, Controller

# Initialize the main app window with a dark theme
app = tk.Tk()
app.title("GPT-Clicker")  # Set the window title to GPT-Clicker
app.geometry("400x300")  # Set a fixed window size
app.configure(bg='#1e1e1e')  # Set modern dark background for the main window

# Global variables
clicking_left = False
clicking_right = False
mouse = Controller()  # Initialize mouse controller
left_key_binding = keyboard.KeyCode.from_char('r')  # Default left key binding to 'r'
right_key_binding = keyboard.KeyCode.from_char('f')  # Default right key binding to 'f'
left_key_listener_active = False  # Flag to indicate when capturing left key
right_key_listener_active = False  # Flag to indicate when capturing right key

# Function to remove focus from entry on Enter key press
def remove_focus(event):
    app.focus()  # Shift the focus back to the main window

# Validation function to allow only numeric input
def validate_numeric_input(new_value):
    if new_value == "" or new_value.isdigit() or (new_value.replace('.', '', 1).isdigit() and new_value.count('.') < 2):
        return True
    else:
        return False

# Register the validation function with Tkinter
validate_cmd = (app.register(validate_numeric_input), '%P')

# Function to start left-clicking
def start_left_clicking():
    global clicking_left
    clicking_left = True
    
    # Try to get the minimum and maximum CPS values for left click, handle errors and default if invalid
    try:
        left_min_cps = float(left_min_cps_entry.get())
        left_max_cps = float(left_max_cps_entry.get())
        if left_min_cps <= 0 or left_max_cps <= 0 or left_min_cps > left_max_cps:
            raise ValueError
    except ValueError:
        left_min_cps = 10  # Default minimum CPS
        left_max_cps = 15  # Default maximum CPS
        left_min_cps_entry.delete(0, tk.END)
        left_min_cps_entry.insert(0, "10")
        left_max_cps_entry.delete(0, tk.END)
        left_max_cps_entry.insert(0, "15")
    
    def left_click_loop():
        while clicking_left:
            current_cps = random.uniform(left_min_cps, left_max_cps)  # Randomize CPS for left click
            interval = 1.0 / current_cps  # Calculate time between each left click
            mouse.click(Button.left)  # Perform a left mouse click
            time.sleep(interval)  # Wait according to the randomized CPS
    
    # Run the left-clicking loop in a new thread
    threading.Thread(target=left_click_loop).start()

# Function to start right-clicking
def start_right_clicking():
    global clicking_right
    clicking_right = True
    
    # Try to get the minimum and maximum CPS values for right click, handle errors and default if invalid
    try:
        right_min_cps = float(right_min_cps_entry.get())
        right_max_cps = float(right_max_cps_entry.get())
        if right_min_cps <= 0 or right_max_cps <= 0 or right_min_cps > right_max_cps:
            raise ValueError
    except ValueError:
        right_min_cps = 10  # Default minimum CPS
        right_max_cps = 15  # Default maximum CPS
        right_min_cps_entry.delete(0, tk.END)
        right_min_cps_entry.insert(0, "10")
        right_max_cps_entry.delete(0, tk.END)
        right_max_cps_entry.insert(0, "15")
    
    def right_click_loop():
        while clicking_right:
            current_cps = random.uniform(right_min_cps, right_max_cps)  # Randomize CPS for right click
            interval = 1.0 / current_cps  # Calculate time between each right click
            mouse.click(Button.right)  # Perform a right mouse click
            time.sleep(interval)  # Wait according to the randomized CPS
    
    # Run the right-clicking loop in a new thread
    threading.Thread(target=right_click_loop).start()

# Function to stop left-clicking
def stop_left_clicking():
    global clicking_left
    clicking_left = False

# Function to stop right-clicking
def stop_right_clicking():
    global clicking_right
    clicking_right = False

# Function to toggle left-clicking based on key press
def toggle_left_clicking():
    if clicking_left:
        stop_left_clicking()
    else:
        start_left_clicking()

# Function to toggle right-clicking based on key press
def toggle_right_clicking():
    if clicking_right:
        stop_right_clicking()
    else:
        start_right_clicking()

# Hotkey listener for the custom key bindings
def on_press(key):
    global left_key_listener_active, right_key_listener_active, left_key_binding, right_key_binding

    # Capture left key binding
    if left_key_listener_active:
        if key == keyboard.Key.esc:  # If Esc is pressed, remove the key binding
            left_key_binding = None
            left_key_listener_active = False
            left_status_label.config(text="Left key binding cleared.")
        elif isinstance(key, keyboard.KeyCode):  # Capture other keys
            left_key_binding = key
            left_key_listener_active = False
            left_status_label.config(text=f"Left key binding set to: '{key.char}'")
        elif isinstance(key, keyboard.Key):
            left_key_binding = key
            left_key_listener_active = False
            left_status_label.config(text=f"Left key binding set to: '{key}'")

    # Capture right key binding
    elif right_key_listener_active:
        if key == keyboard.Key.esc:
            right_key_binding = None
            right_key_listener_active = False
            right_status_label.config(text="Right key binding cleared.")
        elif isinstance(key, keyboard.KeyCode):
            right_key_binding = key
            right_key_listener_active = False
            right_status_label.config(text=f"Right key binding set to: '{key.char}'")
        elif isinstance(key, keyboard.Key):
            right_key_binding = key
            right_key_listener_active = False
            right_status_label.config(text=f"Right key binding set to: '{key}'")
    
    # Toggle left-clicking when left key binding is pressed
    if left_key_binding is not None and key == left_key_binding:
        toggle_left_clicking()

    # Toggle right-clicking when right key binding is pressed
    if right_key_binding is not None and key == right_key_binding:
        toggle_right_clicking()

# Function to activate left key binding capture mode
def set_left_key_binding():
    global left_key_listener_active
    left_key_listener_active = True  # Activate left key binding capture
    left_status_label.config(text="Press any key for Left Click Binding (or Esc to clear)...")

# Function to activate right key binding capture mode
def set_right_key_binding():
    global right_key_listener_active
    right_key_listener_active = True  # Activate right key binding capture
    right_status_label.config(text="Press any key for Right Click Binding (or Esc to clear)...")

# Start a listener in a separate thread
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Dark theme colors
bg_color = '#1e1e1e'  # Very dark background
fg_color = '#f0f0f0'  # Light text color
btn_color = '#333333'  # Darker buttons for contrast
entry_bg_color = '#333333'  # Darker entry fields
entry_fg_color = '#ffffff'  # White text inside entry fields
font_style = ('Helvetica', 10, 'bold')  # Font for labels and buttons

# Helper function for styling widgets
def style_entry(entry):
    entry.configure(bg=entry_bg_color, fg=entry_fg_color, insertbackground=entry_fg_color)
    entry.bind("<Return>", remove_focus)  # Bind the Enter key to remove focus

def style_button(button):
    button.configure(bg=btn_color, fg=fg_color, font=font_style, relief='flat', padx=10, pady=5)

# Input fields for Left Click Minimum and Maximum CPS
left_min_cps_label = tk.Label(app, text="Left Click Min CPS:", bg=bg_color, fg=fg_color, font=font_style)
left_min_cps_label.grid(column=0, row=0, padx=10, pady=5, sticky="W")
left_min_cps_entry = tk.Entry(app, validate="key", validatecommand=validate_cmd)
style_entry(left_min_cps_entry)
left_min_cps_entry.grid(column=1, row=0, padx=10, pady=5)
left_min_cps_entry.insert(0, "10")

left_max_cps_label = tk.Label(app, text="Left Click Max CPS:", bg=bg_color, fg=fg_color, font=font_style)
left_max_cps_label.grid(column=0, row=1, padx=10, pady=5, sticky="W")
left_max_cps_entry = tk.Entry(app, validate="key", validatecommand=validate_cmd)
style_entry(left_max_cps_entry)
left_max_cps_entry.grid(column=1, row=1, padx=10, pady=5)
left_max_cps_entry.insert(0, "15")

# Input fields for Right Click Minimum and Maximum CPS
right_min_cps_label = tk.Label(app, text="Right Click Min CPS:", bg=bg_color, fg=fg_color, font=font_style)
right_min_cps_label.grid(column=0, row=2, padx=10, pady=5, sticky="W")
right_min_cps_entry = tk.Entry(app, validate="key", validatecommand=validate_cmd)
style_entry(right_min_cps_entry)
right_min_cps_entry.grid(column=1, row=2, padx=10, pady=5)
right_min_cps_entry.insert(0, "10")

right_max_cps_label = tk.Label(app, text="Right Click Max CPS:", bg=bg_color, fg=fg_color, font=font_style)
right_max_cps_label.grid(column=0, row=3, padx=10, pady=5, sticky="W")
right_max_cps_entry = tk.Entry(app, validate="key", validatecommand=validate_cmd)
style_entry(right_max_cps_entry)
right_max_cps_entry.grid(column=1, row=3, padx=10, pady=5)
right_max_cps_entry.insert(0, "15")

# Buttons for key binding and click control
left_key_bind_button = tk.Button(app, text="Set Left Key Bind", command=set_left_key_binding)
style_button(left_key_bind_button)
left_key_bind_button.grid(column=1, row=4, padx=10, pady=10)

right_key_bind_button = tk.Button(app, text="Set Right Key Bind", command=set_right_key_binding)
style_button(right_key_bind_button)
right_key_bind_button.grid(column=1, row=5, padx=10, pady=10)

# Status label to show the current left key binding
left_status_label = tk.Label(app, text="Left Click key binding set to: 'r'", bg=bg_color, fg=fg_color, font=font_style)
left_status_label.grid(column=0, row=4, padx=10, pady=5, sticky="W")

# Status label to show the current right key binding
right_status_label = tk.Label(app, text="Right Click key binding set to: 'f'", bg=bg_color, fg=fg_color, font=font_style)
right_status_label.grid(column=0, row=5, padx=10, pady=5, sticky="W")

# Start the GUI main loop
app.mainloop()
