"""
Fresh no_pi.py with full config auto-detection and error feedback.
Uses your existing:
    - management.py
    - sensors.py
    - display.py   (for read_temperature)
"""

import tkinter as tk
import threading
import time
import os
from pathlib import Path

from carpark_manager import CarparkManagement
from carpark_sensors import EntrySensor, ExitSensor
from carpark_display import read_temperature   # Reuse your display.py function

# -----------------------------------------------------------
# AUTO-DETECT CONFIG FILE
# -----------------------------------------------------------

def load_carpark_manager():
    possible_files = [
        "moondalup_carpark\\the_project\\moondalup.json",        # Your preferred config name
        "config.json",           # Default from earlier
        "settings.json"          # Extra backup
    ]

    config_file = None
    for f in possible_files:
        if Path(f).exists():
            config_file = f
            break

    if config_file:
        print(f"[INFO] Using config file: {config_file}")
        return CarparkManagement.from_config_file(config_file)

    # If no config file found — show helpful message
    print("\n[ERROR] No config file found.")
    print("We looked for:", possible_files)
    print("\nFiles we did find in this folder:")
    print(os.listdir("."))
    print("\nMake sure a JSON config file exists, like:")
    print("  moondalup.json   OR  config.json\n")
    raise FileNotFoundError("No config file found.")

# -----------------------------------------------------------
# GUI Data Provider (for display window)
# -----------------------------------------------------------

class GUIDataProvider:
    def __init__(self, manager, weather_file="weather.json"):
        self.manager = manager
        self.temperature = read_temperature(weather_file) or 22.0
        self.weather_file = weather_file

    @property
    def available_spaces(self):
        return self.manager.available_spaces()

    @property
    def current_time(self):
        return time.localtime()

    # GUI can update this via text field:
    def update_temperature(self, temp: float):
        self.temperature = temp

# -----------------------------------------------------------
# GUI Sensor Connector (user button → real EntrySensor / ExitSensor)
# -----------------------------------------------------------

class GUISensorConnector:
    def __init__(self, manager):
        self.manager = manager
        # use your EXISTING sensors.py classes
        self.entry_sensor = EntrySensor(callback=self.manager.handle_entry)
        self.exit_sensor = ExitSensor(callback=self.manager.handle_exit)

    def incoming_car(self, plate: str):
        self.entry_sensor.detect(plate)

    def outgoing_car(self, plate: str):
        self.exit_sensor.detect(plate)

# -----------------------------------------------------------
# DISPLAY WINDOW
# -----------------------------------------------------------

class CarParkDisplay:
    fields = ['Available bays', 'Temperature', 'Time']

    def __init__(self, root, data_provider):
        self.data_provider = data_provider

        self.window = tk.Toplevel(root)
        self.window.title("Moondalup Carpark")
        self.window.geometry("600x300")

        # Labels to hold values
        self.labels = {}
        for i, field in enumerate(self.fields):
            tk.Label(self.window, text=field + ":", font=('Arial', 24)).grid(row=i, column=0, sticky=tk.E)
            self.labels[field] = tk.Label(self.window, text="---", font=('Arial', 24))
            self.labels[field].grid(row=i, column=1, sticky=tk.W)

        # Thread to update UI every second
        thread = threading.Thread(target=self._refresh_loop, daemon=True)
        thread.start()

    def _refresh_loop(self):
        while True:
            time.sleep(1)
            self.update_display()

    def update_display(self):
        self.labels['Available bays'].config(text=f"{self.data_provider.available_spaces}")
        self.labels['Temperature'].config(text=f"{self.data_provider.temperature:.1f}℃")
        self.labels['Time'].config(text=time.strftime("%H:%M:%S", self.data_provider.current_time))
        self.window.update()

# -----------------------------------------------------------
# CAR DETECTOR WINDOW (button sensor simulation)
# -----------------------------------------------------------

class CarDetectorWindow:
    def __init__(self, root, sensor_connector, data_provider):
        self.sensor_connector = sensor_connector
        self.data_provider = data_provider

        self.root = root
        self.root.title("Sensor Simulation")
        self.root.geometry("600x300")

        # License plate input
        self.plate_var = tk.StringVar()
        tk.Label(root, text="License Plate:", font=('Arial', 20)).grid(row=0, column=0)
        tk.Entry(root, textvariable=self.plate_var, font=('Arial', 20)).grid(row=0, column=1)

        # Buttons
        tk.Button(root, text="🚘 Incoming Car", font=('Arial', 20),
                  command=self.incoming_car).grid(row=1, columnspan=2, pady=10)
        tk.Button(root, text="Outgoing Car 🚘", font=('Arial', 20),
                  command=self.outgoing_car).grid(row=2, columnspan=2, pady=10)

        # Temperature entry
        self.temp_var = tk.StringVar()
        tk.Label(root, text="Temperature (°C):", font=('Arial', 20)).grid(row=3, column=0)
        tk.Entry(root, textvariable=self.temp_var, font=('Arial', 20)).grid(row=3, column=1)
        self.temp_var.trace_add("write", lambda *_: self._temp_changed())

    @property
    def current_plate(self):
        return self.plate_var.get()

    def incoming_car(self):
        self.sensor_connector.incoming_car(self.current_plate)

    def outgoing_car(self):
        self.sensor_connector.outgoing_car(self.current_plate)

    def _temp_changed(self):
        try:
            temp = float(self.temp_var.get())
            self.data_provider.update_temperature(temp)
        except ValueError:
            pass

# -----------------------------------------------------------
# RUN GUI APP
# -----------------------------------------------------------

def start_gui():
    manager = load_carpark_manager()
    provider = GUIDataProvider(manager)
    connector = GUISensorConnector(manager)

    root = tk.Tk()
    root.withdraw()  # Prevent empty window

    CarParkDisplay(root, provider)
    CarDetectorWindow(root, connector, provider)

    root.mainloop()

if __name__ == "__main__":
    start_gui()