import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models import Car

class CarparkManagement:
    def __init__(self, capacity: int, name: str = "Carpark"):
        self.name = name
        self.capacity = capacity
        # cars currently inside, keyed by license_plate
        self._active_cars: Dict[str, Car] = {}
        # log of events (entry/exit)
        self._log: List[Dict] = []

    @classmethod
    def from_config_file(cls, config_path: str):
        p = Path(config_path)
        data = json.loads(p.read_text())
        return cls(capacity=data.get("capacity", 0), name=data.get("carpark_name", "Carpark"))

    def available_spaces(self) -> int:
        return max(0, self.capacity - len(self._active_cars))

    def total_spaces(self) -> int:
        return self.capacity

    def handle_entry(self, license_plate: str, model: Optional[str] = None, when: Optional[datetime] = None) -> bool:
        """
        Return True if entry accepted, False if carpark is full or duplicate.
        """
        when = when or datetime.now()
        if license_plate in self._active_cars:
            # duplicate entry (car already inside)
            self._log.append({"event": "entry_rejected_already_in", "plate": license_plate, "when": when.isoformat()})
            return False

        if len(self._active_cars) >= self.capacity:
            # full
            self._log.append({"event": "entry_rejected_full", "plate": license_plate, "when": when.isoformat()})
            return False

        car = Car(license_plate=license_plate, model=model)
        car.mark_entry(when)
        self._active_cars[license_plate] = car
        self._log.append({"event": "entry", "plate": license_plate, "model": model, "when": when.isoformat()})
        return True

    def handle_exit(self, license_plate: str, when: Optional[datetime] = None) -> bool:
        """
        Return True if exit processed, False if car not found.
        """
        when = when or datetime.now()
        car = self._active_cars.pop(license_plate, None)
        if car is None:
            self._log.append({"event": "exit_rejected_not_found", "plate": license_plate, "when": when.isoformat()})
            return False

        car.mark_exit(when)
        self._log.append({
            "event": "exit",
            "plate": license_plate,
            "model": car.model,
            "entry": car.entry_time.isoformat() if car.entry_time else None,
            "exit": car.exit_time.isoformat()
        })
        return True

    def get_active_cars(self):
        return list(self._active_cars.values())

    def get_log(self):
        return list(self._log)

    def save_log(self, path: str):
        Path(path).write_text(json.dumps(self._log, indent=2))

    def __repr__(self):
        return f"<CarparkManagement name={self.name} capacity={self.capacity} occupied={len(self._active_cars)}>"