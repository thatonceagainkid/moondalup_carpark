"""
Simple CLI entry point to control and test the carpark system.
"""

import argparse
from pathlib import Path
from datetime import datetime
import sys

from carpark_manager import CarparkManagement
from carpark_sensors import EntrySensor, ExitSensor
import carpark_display

def main(config_path: str, weather_file: str):
    center = CarparkManagement.from_config_file(config_path)

    # Create sensors and wire them to the management center callbacks
    entry_sensor = EntrySensor(callback=lambda plate, model=None: center.handle_entry(plate, model))
    exit_sensor = ExitSensor(callback=lambda plate: center.handle_exit(plate))

    print(f"Loaded {center}")
    print("Commands:")
    print("  enter <plate> [model]    -- simulate a car entering")
    print("  exit <plate>             -- simulate a car exiting")
    print("  status                   -- show summary")
    print("  log                      -- dump event log")
    print("  save_log <path>          -- save event log to file")
    print("  simulate                 -- run a short simulated sequence")
    print("  quit / q                 -- exit")
    print("")

    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not cmd:
            continue

        parts = cmd.split()
        if parts[0] in ("quit", "q"):
            break

        if parts[0] == "enter":
            if len(parts) < 2:
                print("Usage: enter <plate> [model]")
                continue
            plate = parts[1]
            model = parts[2] if len(parts) >= 3 else None
            accepted = entry_sensor.detect(plate, model)
            # EntrySensor.detect returns None (callback handles business logic).
            # We'll show result using management center state:
            if plate in [c.license_plate for c in center.get_active_cars()]:
                print(f"Entered: {plate}")
            else:
                print(f"Entry rejected for {plate} (maybe full or duplicate).")

        elif parts[0] == "exit":
            if len(parts) < 2:
                print("Usage: exit <plate>")
                continue
            plate = parts[1]
            exit_sensor.detect(plate)
            # Check log to see if exit was processed
            # Quick check:
            if plate in [c.license_plate for c in center.get_active_cars()]:
                print(f"Exit not registered for {plate}.")
            else:
                print(f"Exit processed for {plate} (if it was inside).")

        elif parts[0] == "status":
            display.render_summary(center, weather_file)

        elif parts[0] == "log":
            for item in center.get_log():
                print(item)

        elif parts[0] == "save_log":
            if len(parts) < 2:
                print("Usage: save_log <path>")
                continue
            path = parts[1]
            center.save_log(path)
            print(f"Saved log to {path}")

        elif parts[0] == "simulate":
            # short built-in simulation
            sequence = [
                ("enter", "ABC123", "Toyota Camry"),
                ("enter", "XYZ789", "Mazda 3"),
                ("exit", "ABC123"),
                ("enter", "NEW001", "Tesla Model 3"),
                ("exit", "NOTIN"),
                ("enter", "ABC123", "Toyota Camry")
            ]
            for step in sequence:
                typ = step[0]
                if typ == "enter":
                    plate, model = step[1], step[2]
                    entry_sensor.detect(plate, model)
                    print(f"Simulated entry {plate} {model}")
                elif typ == "exit":
                    plate = step[1]
                    exit_sensor.detect(plate)
                    print(f"Simulated exit {plate}")
            print("Simulation finished.")
            display.render_summary(center, weather_file)

        else:
            print("Unknown command. Type 'status' or 'simulate' or 'quit'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Carpark CLI")
    parser.add_argument("--config", default="moondalup_carpark\\the_project\\moondalup.json", help="Locates moondalup.json")
    parser.add_argument("--weather", default="moondalup_carpark\\the_project\\weather.json", help="Path to weather.json")
    args = parser.parse_args()
    print("Looking for config file:", args.config)

    if not Path(args.config).exists():
        print(f"Config file {args.config} not found. Create one (see project README).")
        sys.exit(1)

    main(args.config, args.weather)