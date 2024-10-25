import tkinter as tk
import threading
import time
import random
from pynput import keyboard
from pynput.mouse import Button, Controller
import platform
import winreg

# Initialize the main app window
app = tk.Tk()
app.title("GPT-Clicker")
app.geometry("400x300")

# Global variables
clicking_left = [False]
clicking_right = [False]
mouse = Controller()
left_key_binding = keyboard.KeyCode.from_char('r')
right_key_binding = keyboard.KeyCode.from_char('f')
left_key_listener_active = False
right_key_listener_active = False

# Detect dark mode for Windows 10/11
def is_dark_mode():
    if platform.system() == "Windows":
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
            key = winreg.OpenKey(registry, key_path)
            is_dark = winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 0
            winreg.CloseKey(key)
            return is_dark
        except:
            return False
    return False

# Apply theme colors
if is_dark_mode():
    bg_color, fg_color, btn_color, entry_bg_color, entry_fg_color = '#1e1e1e', '#f0f0f0', '#333333', '#333333', '#ffffff'
else:
    bg_color, fg_color, btn_color, entry_bg_color, entry_fg_color = '#ffffff', '#000000', '#cccccc', '#f0f0f0', '#000000'
app.configure(bg=bg_color)

# Validation function to allow only numeric input
def validate_numeric_input(new_value):
    return new_value.isdigit() or new_value == ""

validate_cmd = (app.register(validate_numeric_input), '%P')

# Rounded Entry Class with Numeric Validation and Enter Key Binding to Remove Focus
class RoundedEntry(tk.Canvas):
    def __init__(self, parent, width=100, height=30, radius=15):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg_color)
        self.radius = radius
        self.entry = tk.Entry(
            self, 
            relief="flat", 
            justify="center", 
            bg=entry_bg_color, 
            fg=entry_fg_color, 
            insertbackground=entry_fg_color,
            validate="key",
            validatecommand=validate_cmd
        )
        self.create_oval(0, 0, radius * 2, radius * 2, fill=entry_bg_color, outline="")
        self.create_oval(width - radius * 2, 0, width, radius * 2, fill=entry_bg_color, outline="")
        self.create_rectangle(radius, 0, width - radius, height, fill=entry_bg_color, outline="")
        self.entry.place(x=radius, y=5, width=width - 2 * radius, height=height - 10)
        
        # Bind the Enter key to remove focus
        self.entry.bind("<Return>", lambda e: parent.focus())

    def get(self):
        return self.entry.get()

    def delete(self, start, end):
        self.entry.delete(start, end)

    def insert(self, index, value):
        self.entry.insert(index, value)

# Rounded Button Class
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=130, height=40, radius=20, bg=btn_color, fg=fg_color):
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.command = command
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.draw_button(text)
        self.bind("<Button-1>", lambda e: self.command())
    
    def draw_button(self, text):
        self.create_oval(0, 0, self.radius * 2, self.radius * 2, fill=self.bg, outline="")
        self.create_oval(self.winfo_reqwidth() - self.radius * 2, 0, self.winfo_reqwidth(), self.radius * 2, fill=self.bg, outline="")
        self.create_rectangle(self.radius, 0, self.winfo_reqwidth() - self.radius, self.winfo_reqheight(), fill=self.bg, outline="")
        self.create_text(self.winfo_reqwidth() / 2, self.winfo_reqheight() / 2, text=text, fill=self.fg, font=('Helvetica', 10, 'bold'))

# Functions to start and stop clicking
def start_clicking(clicking_type, min_cps, max_cps, button):
    def click_loop():
        while clicking_type[0]:
            current_cps = random.uniform(min_cps, max_cps)
            interval = 1.0 / current_cps
            mouse.click(button)
            time.sleep(interval)
    threading.Thread(target=click_loop).start()

def toggle_clicking(clicking_type, min_entry, max_entry, button):
    try:
        min_cps = float(min_entry.get())
        max_cps = float(max_entry.get())
    except ValueError:
        min_cps, max_cps = 10, 15
        min_entry.delete(0, tk.END)
        min_entry.insert(0, "10")
        max_entry.delete(0, tk.END)
        max_entry.insert(0, "15")
    if clicking_type[0]:
        clicking_type[0] = False
    else:
        clicking_type[0] = True
        start_clicking(clicking_type, min_cps, max_cps, button)

# Functions to set new key bindings
def set_left_key_binding():
    global left_key_listener_active
    left_key_listener_active = True
    left_status_label.config(text="Press any key for Left Click Binding...")

def set_right_key_binding():
    global right_key_listener_active
    right_key_listener_active = True
    right_status_label.config(text="Press any key for Right Click Binding...")

# Key binding listener function
def on_press(key):
    global left_key_binding, right_key_binding, left_key_listener_active, right_key_listener_active
    if left_key_listener_active:
        left_key_binding = key
        left_key_listener_active = False
        left_status_label.config(text=f"Left Click key binding set to: '{key.char if hasattr(key, 'char') else key}'")
    elif right_key_listener_active:
        right_key_binding = key
        right_key_listener_active = False
        right_status_label.config(text=f"Right Click key binding set to: '{key.char if hasattr(key, 'char') else key}'")
    elif key == left_key_binding:
        toggle_clicking(clicking_left, left_min_cps_entry, left_max_cps_entry, Button.left)
    elif key == right_key_binding:
        toggle_clicking(clicking_right, right_min_cps_entry, right_max_cps_entry, Button.right)

listener = keyboard.Listener(on_press=on_press)
listener.start()

# Rounded entry fields for CPS with numeric validation and Enter key binding
left_min_cps_entry = RoundedEntry(app, width=100, height=30)
left_min_cps_entry.insert(0, "10")
left_min_cps_entry.grid(column=1, row=0, padx=10, pady=5)

left_max_cps_entry = RoundedEntry(app, width=100, height=30)
left_max_cps_entry.insert(0, "15")
left_max_cps_entry.grid(column=1, row=1, padx=10, pady=5)

right_min_cps_entry = RoundedEntry(app, width=100, height=30)
right_min_cps_entry.insert(0, "10")
right_min_cps_entry.grid(column=1, row=2, padx=10, pady=5)

right_max_cps_entry = RoundedEntry(app, width=100, height=30)
right_max_cps_entry.insert(0, "15")
right_max_cps_entry.grid(column=1, row=3, padx=10, pady=5)

# Rounded buttons for setting key binds
left_key_bind_button = RoundedButton(app, text="Set Left Key Bind", command=set_left_key_binding)
left_key_bind_button.grid(column=1, row=4, padx=10, pady=10)

right_key_bind_button = RoundedButton(app, text="Set Right Key Bind", command=set_right_key_binding)
right_key_bind_button.grid(column=1, row=5, padx=10, pady=10)

# Labels for current key bindings
left_status_label = tk.Label(app, text=f"Left Click key binding: '{left_key_binding.char}'", bg=bg_color, fg=fg_color, font=('Helvetica', 10, 'bold'))
left_status_label.grid(column=0, row=4, padx=10, pady=5, sticky="W")

right_status_label = tk.Label(app, text=f"Right Click key binding: '{right_key_binding.char}'", bg=bg_color, fg=fg_color, font=('Helvetica', 10, 'bold'))
right_status_label.grid(column=0, row=5, padx=10, pady=5, sticky="W")

# CPS Labels
left_min_cps_label = tk.Label(app, text="Left Click Min CPS:", bg=bg_color, fg=fg_color, font=('Helvetica', 10, 'bold'))
left_min_cps_label.grid(column=0, row=0, padx=10, pady=5, sticky="W")

left_max_cps_label = tk.Label(app, text="Left Click Max CPS:", bg=bg_color, fg=fg_color, font=('Helvetica', 10, 'bold'))
left_max_cps_label.grid(column=0, row=1, padx=10, pady=5, sticky="W")

right_min_cps_label = tk.Label(app, text="Right Click Min CPS:", bg=bg_color, fg=fg_color, font=('Helvetica', 10, 'bold'))
right_min_cps_label.grid(column=0, row=2, padx=10, pady=5, sticky="W")

right_max_cps_label = tk.Label(app, text="Right Click Max CPS:", bg=bg_color, fg=fg_color, font=('Helvetica', 10, 'bold'))
right_max_cps_label.grid(column=0, row=3, padx=10, pady=5, sticky="W")

app.mainloop()
