import json
from pathlib import Path
from typing import Optional

def read_temperature(weather_file: str) -> Optional[float]:
    p = Path(weather_file)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        # assume key "temperature_c"
        return data.get("temperature_c")
    except Exception:
        return None

def render_summary(center, weather_file: str):
    temp = read_temperature(weather_file)
    print("="*40)
    print(f"{center.name} — Capacity {center.total_spaces()} — Available {center.available_spaces()}")
    if temp is not None:
        print(f"Current temperature: {temp} °C")
    else:
        print("Temperature: N/A")
    print(f"Cars parked: {len(center.get_active_cars())}")
    print("="*40)