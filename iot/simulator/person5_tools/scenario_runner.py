#!/usr/bin/env python3
"""
Additive SpotSync MQTT scenario publisher for Person 5 integration testing.

Reads the existing ../config.json and publishes contract-shaped test messages.
Use only against a development/test broker and coordinate database-affecting
scenarios with the backend/database owners first.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE.parent / "config.json"
PARKING_STATUSES = {
    "occupied", "available", "fault", "blocked",
    "sensor_offline", "unexpected_occupancy",
}
ENTRANCE_STATUSES = {
    "entry_detected", "exit_detected", "fault", "sensor_offline",
}


def timestamp(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(seconds=offset_seconds)).isoformat()


def load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_parking_payload(sensor_id: str, slot_id: str, status: str,
                          stale_seconds: int = 0) -> dict[str, Any]:
    if status not in PARKING_STATUSES:
        raise ValueError(f"Unsupported parking status: {status}")
    distance = round(random.uniform(3, 15), 2) if status == "occupied" else round(random.uniform(30, 100), 2)
    return {
        "sensor_id": sensor_id,
        "slot_id": slot_id,
        "status": status,
        "distance_cm": distance,
        "timestamp": timestamp(stale_seconds),
    }


def build_entrance_payload(sensor_id: str, status: str) -> dict[str, Any]:
    if status not in ENTRANCE_STATUSES:
        raise ValueError(f"Unsupported entrance status: {status}")
    return {
        "sensor_id": sensor_id,
        "status": status,
        "distance_cm": round(random.uniform(5, 30), 2),
        "timestamp": timestamp(),
    }


def choose_sensor(config: dict[str, Any], sensor_id: str | None) -> tuple[str, str | None, str]:
    parking = config["parking_lot"]["slots"]
    entrance = config["entrance_sensor"]
    if sensor_id == entrance["sensor_id"]:
        return entrance["sensor_id"], None, entrance["topic"]
    if sensor_id:
        for slot in parking:
            if slot["sensor_id"] == sensor_id:
                return sensor_id, slot["slot_id"], f"spotsync/parking/{slot['slot_id']}/occupancy"
        raise ValueError(f"Sensor ID not found in config: {sensor_id}")
    first = parking[0]
    return first["sensor_id"], first["slot_id"], f"spotsync/parking/{first['slot_id']}/occupancy"


def scenario_messages(sensor_id: str, slot_id: str | None, scenario: str,
                      count: int,
                      entrance_topic: str = "spotsync/sensors/SENSOR_008/events"
                      ) -> list[tuple[str, dict[str, Any] | None]]:
    if slot_id is None:
        if scenario not in {"entrance", "entrance-fault", "entrance-offline"}:
            raise ValueError("SENSOR_008 supports entrance, entrance-fault, or entrance-offline scenarios.")
        status = {
            "entrance": "entry_detected",
            "entrance-fault": "fault",
            "entrance-offline": "sensor_offline",
        }[scenario]
        return [
            (entrance_topic, build_entrance_payload(sensor_id, status))
            for _ in range(count)
        ]

    topic = f"spotsync/parking/{slot_id}/occupancy"
    if scenario == "missing":
        return [(topic, None) for _ in range(count)]
    if scenario == "flap":
        statuses = ["occupied", "available"] * ((count + 1) // 2)
        return [
            (topic, build_parking_payload(sensor_id, slot_id, statuses[i]))
            for i in range(count)
        ]
    if scenario == "stale":
        return [
            (topic, build_parking_payload(
                sensor_id, slot_id, "occupied", stale_seconds=3600
            ))
            for _ in range(count)
        ]
    if scenario == "invalid":
        payload = build_parking_payload(sensor_id, slot_id, "occupied")
        payload.pop("distance_cm")
        return [(topic, payload) for _ in range(count)]

    status = {
        "occupied": "occupied",
        "available": "available",
        "fault": "fault",
        "blocked": "blocked",
        "offline": "sensor_offline",
        "unexpected": "unexpected_occupancy",
    }[scenario]
    return [
        (topic, build_parking_payload(sensor_id, slot_id, status))
        for _ in range(count)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish SpotSync sensor test scenarios.")
    parser.add_argument("--sensor-id", help="Sensor ID from config; defaults to SENSOR_001.")
    parser.add_argument("--scenario", required=True,
        choices=["occupied", "available", "fault", "blocked", "offline",
                 "unexpected", "flap", "stale", "invalid", "missing",
                 "entrance", "entrance-fault", "entrance-offline"])
    parser.add_argument("--count", type=int, default=3, help="Number of messages (default: 3).")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between messages.")
    parser.add_argument("--publish", action="store_true", help="Explicitly connect to MQTT and publish messages. Default is dry-run.")
    args = parser.parse_args()

    if args.count < 1 or args.interval < 0:
        parser.error("--count must be >= 1 and --interval must be >= 0")

    config = load_config()
    sensor_id, slot_id, topic = choose_sensor(config, args.sensor_id)
    messages = scenario_messages(
        sensor_id, slot_id, args.scenario, args.count,
        entrance_topic=topic,
    )

    broker = os.getenv("SPOTSYNC_MQTT_BROKER", config["mqtt"]["broker"])
    port = int(os.getenv("SPOTSYNC_MQTT_PORT", config["mqtt"]["port"]))
    qos = int(config["mqtt"].get("qos", 1))

    if args.scenario == "missing":
        print("MISSING-MESSAGE SCENARIO: intentionally publishing nothing.")
        return 0

    if not args.publish:
        print("DRY RUN: no MQTT connection or messages published.")
        for msg_topic, payload in messages:
            print(f"TOPIC: {msg_topic}")
            print(json.dumps(payload, indent=2))
        return 0

    if args.publish and (sensor_id == "SENSOR_007" or slot_id == "B2-A4"):
        parser.error("Live publishing to SENSOR_007 / B2-A4 is blocked while the space is OUT_OF_SERVICE.")

    if mqtt is None:
        print("Missing dependency: install paho-mqtt in the project's active environment.", file=sys.stderr)
        return 2

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    try:
        client.connect(broker, port, 60)
        client.loop_start()
        for index, (msg_topic, payload) in enumerate(messages, start=1):
            client.publish(msg_topic, json.dumps(payload), qos=qos).wait_for_publish(timeout=5)
            print(f"[{index}/{len(messages)}] published {msg_topic}: {payload['status']}")
            if index < len(messages):
                time.sleep(args.interval)
    except Exception as exc:
        print(f"MQTT scenario failed: {exc}", file=sys.stderr)
        return 1
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
