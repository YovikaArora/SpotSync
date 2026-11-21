#!/usr/bin/env python3
"""Read-only validation of the official SpotSync simulator mapping and topics."""
import json
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "config.json"
EXPECTED = {
    "SENSOR_001": "B1-A1",
    "SENSOR_002": "B1-A2",
    "SENSOR_003": "B1-A3",
    "SENSOR_004": "B2-A1",
    "SENSOR_005": "B2-A2",
    "SENSOR_006": "B2-A3",
    "SENSOR_007": "B2-A4",
}


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    slots = config["parking_lot"]["slots"]
    actual = {item["sensor_id"]: item["slot_id"] for item in slots}
    assert actual == EXPECTED, f"Mapping mismatch.\nExpected: {EXPECTED}\nActual: {actual}"
    assert len(slots) == 7, f"Expected 7 parking sensors, found {len(slots)}"
    entrance = config["entrance_sensor"]
    assert entrance["sensor_id"] == "SENSOR_008"
    assert entrance["topic"] == "spotsync/sensors/SENSOR_008/events"
    print("PASS: seven official parking sensor mappings")
    print("PASS: SENSOR_008 entrance topic and separate role")
    print("PASS: simulator config is valid")


if __name__ == "__main__":
    main()
