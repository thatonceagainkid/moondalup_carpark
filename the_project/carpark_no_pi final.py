"""
Fresh no_pi.py with full config auto-detection and error feedback.
Uses your existing:
    - management.py
    - sensors.py
    - display.py   (for read_temperature)
"""

import tkinter as tk
import time
import os
from pathlib import Path

from carpark_manager import CarparkManagement
from carpark_sensors import EntrySensor, ExitSensor
from carpark_display import read_temperature

def write_log_to_file(message, filename="carpark_log.txt"):
    """Append a log message to a text file, guaranteed to create it."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    # ALWAYS save in same folder as no_pi.py
    log_path = Path(__file__).parent / filename

    with open(log_path, "a") as f:
        f.write(f"{timestamp}  {message}\n")

    print(f"[LOG SAVED] {log_path}")
# ---------------- CONFIG AUTO-DETECTION ---------------- #

def load_carpark_manager():
    possible_files = ["moondalup_carpark\\the_project\\moondalup.json", "config.json", "settings.json"]
    for f in possible_files:
        if Path(f).exists():
            print(f"[INFO] Using config file: {f}")
            return CarparkManagement.from_config_file(f)

    print("[ERROR] No config file found.")
    print("Files in folder:", os.listdir("."))
    raise FileNotFoundError("No config found")


# ---------------- DATA PROVIDER ---------------- #

class GUIDataProvider:
    def __init__(self, manager, weather_file="weather.json"):
        self.manager = manager
        self.temperature = read_temperature(weather_file) or 22

    @property
    def available_spaces(self):
        return self.manager.available_spaces()

    @property
    def current_time(self):
        return time.localtime()

    def update_temperature(self, temp):
        self.temperature = temp


# ---------------- SENSOR BRIDGE ---------------- #

class GUISensorConnector:
    def __init__(self, manager, provider, update_display, update_log, update_parked):
        self.manager = manager
        self.provider = provider          # ← STORE PROVIDER HERE
        self.update_display = update_display
        self.update_log = update_log
        self.update_parked = update_parked

        # Use your existing sensors.py
        self.entry = EntrySensor(callback=manager.handle_entry)
        self.exit = ExitSensor(callback=manager.handle_exit)

    def incoming_car(self, plate):
        self.entry.detect(plate)               
        message = f"[IN]  {plate}"
        self.update_log(message)               
        write_log_to_file(message)             

    def outgoing_car(self, plate):
        self.exit.detect(plate)                
        message = f"[OUT] {plate}"
        self.update_log(message)               
        write_log_to_file(message)             

    def _refresh(self, log_message):
        self.update_display()
        self.update_log(log_message)
        self.update_parked()


# ---------------- DISPLAY WINDOW ---------------- #

class CarParkDisplay:
    fields = ['Available bays', 'Temperature', 'Time']

    def __init__(self, root, provider: GUIDataProvider):
        self.provider = provider

        self.win = tk.Toplevel(root)
        self.win.title("Moondalup Carpark")
        self.win.geometry("600x250")

        self.labels = {}
        for i, field in enumerate(self.fields):
            tk.Label(self.win, text=field + ":", font=('Arial', 20)).grid(row=i, column=0, sticky=tk.E)
            label = tk.Label(self.win, text="---", font=('Arial', 20))
            label.grid(row=i, column=1, sticky=tk.W)
            self.labels[field] = label

        self.refresh()

    def refresh(self):
        self.labels['Available bays'].config(text=self.provider.available_spaces)
        self.labels['Temperature'].config(text=f"{self.provider.temperature:.1f}℃")
        self.labels['Time'].config(text=time.strftime("%H:%M:%S", self.provider.current_time))
        self.win.after(1000, self.refresh)


# ---------------- CONTROL WINDOW ---------------- #

class ControlWindow:
    def __init__(self, root, connector: GUISensorConnector):
        self.connector = connector

        win = tk.Toplevel(root)
        win.title("Simulated Sensors")
        win.geometry("600x250")

        self.plate_var = tk.StringVar()
        tk.Label(win, text="License Plate:", font=('Arial', 16)).grid(row=0, column=0)
        tk.Entry(win, textvariable=self.plate_var, font=('Arial', 16)).grid(row=0, column=1)

        tk.Button(win, text="Incoming 🚘", font=('Arial', 18),
                  command=lambda: connector.incoming_car(self.plate_var.get())
        ).grid(row=1, columnspan=2, pady=10)

        tk.Button(win, text="Outgoing 🚘", font=('Arial', 18),
                  command=lambda: connector.outgoing_car(self.plate_var.get())
        ).grid(row=2, columnspan=2, pady=5)

        self.temp_var = tk.StringVar()
        tk.Label(win, text="Temperature °C:", font=('Arial', 16)).grid(row=3, column=0)
        tk.Entry(win, textvariable=self.temp_var, font=('Arial', 16)).grid(row=3, column=1)
        self.temp_var.trace_add("write", self.temp_change)

    def temp_change(self, *_):
        try:
            temp = float(self.temp_var.get())
            self.connector.provider.update_temperature(temp)
            self.connector.update_display()
        except ValueError:
            pass


# ---------------- LOG WINDOW ---------------- #

class LogWindow:
    def __init__(self, root):
        win = tk.Toplevel(root)
        win.title("Live Log")
        win.geometry("400x300")

        self.box = tk.Text(win, state='disabled')
        self.box.pack(fill=tk.BOTH, expand=True)

    def write(self, msg):
        self.box.config(state='normal')
        self.box.insert(tk.END, msg + "\n")
        self.box.config(state='disabled')

        # ALSO WRITE TO FILE
        write_log_to_file(msg)   # ← NEW

# ---------------- ACTIVE CARS WINDOW ---------------- #

class ParkedCarsWindow:
    def __init__(self, root, manager):
        self.manager = manager

        win = tk.Toplevel(root)
        win.title("Currently Parked Cars")
        win.geometry("400x300")

        self.listbox = tk.Listbox(win, font=('Arial', 16))
        self.listbox.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for car in self.manager.get_active_cars():
            self.listbox.insert(tk.END, car.license_plate)


# ---------------- APP START ---------------- #

def start_gui():
    manager = load_carpark_manager()
    provider = GUIDataProvider(manager)

    root = tk.Tk()
    root.withdraw()

    display = CarParkDisplay(root, provider)
    log_win = LogWindow(root)
    parked_win = ParkedCarsWindow(root, manager)

    connector = GUISensorConnector(
        manager,
        provider,             
        update_display=display.refresh,
        update_log=log_win.write,
        update_parked=parked_win.refresh
    )

    control = ControlWindow(root, connector)

    root.mainloop()


if __name__ == "__main__":
    start_gui()