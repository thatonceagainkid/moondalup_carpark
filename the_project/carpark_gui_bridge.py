from carpark_manager import CarparkManagement
from carpark_sensors import EntrySensor, ExitSensor
from carpark_display import read_temperature
import time

class GUIDataProvider:
    def __init__(self, manager: CarparkManagement, weather_file: str):
        self.manager = manager
        self.weather_file = weather_file
        self.temperature = read_temperature(weather_file) or 22  # fallback

    @property
    def available_spaces(self):
        return self.manager.available_spaces()

    @property
    def current_time(self):
        return time.localtime()

    def update_temperature(self, temp: float):
        self.temperature = temp  # receives temp from GUI
        

class GUISensorConnector:
    """Bridges GUI button events to your existing sensors"""
    def __init__(self, manager: CarparkManagement):
        self.manager = manager
        self.entry = EntrySensor(callback=self.manager.handle_entry)
        self.exit = ExitSensor(callback=self.manager.handle_exit)

    def incoming_car(self, plate: str):
        self.entry.detect(plate)

    def outgoing_car(self, plate: str):
        self.exit.detect(plate)