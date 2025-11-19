"""
EntrySensor and ExitSensor are simple abstractions.
In production these would be replaced with code that listens to hardware events
(e.g., networked sensors, MQTT messages, GPIO interrupts, etc.).
"""

from typing import Callable

class EntrySensor:
    def __init__(self, callback: Callable[[str, str], None]):
        """
        callback: function(license_plate: str, model: str)
        """
        self.callback = callback

    def detect(self, license_plate: str, model: str = None):
        """Simulate detection of a car entering."""
        # In production, detection event handler calls callback with actual data.
        self.callback(license_plate, model)


class ExitSensor:
    def __init__(self, callback: Callable[[str], None]):
        """
        callback: function(license_plate: str)
        """
        self.callback = callback

    def detect(self, license_plate: str):
        """Simulate detection of a car exiting."""
        self.callback(license_plate)
