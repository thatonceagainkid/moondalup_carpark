from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Car:
    license_plate: str
    model: Optional[str] = None
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None

    def mark_entry(self, when: Optional[datetime] = None):
        self.entry_time = when or datetime.now()

    def mark_exit(self, when: Optional[datetime] = None):
        self.exit_time = when or datetime.now()

    def __repr__(self):
        return f"Car(plate={self.license_plate}, model={self.model}, entry={self.entry_time}, exit={self.exit_time})"