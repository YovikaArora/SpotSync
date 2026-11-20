import argparse
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import paho.mqtt.client as mqtt


CONFIG_PATH = Path(__file__).with_name("config.json")
PARKING_TOPIC = "spotsync/parking/{slot_id}/occupancy"

# Person 1 confirmed that B2-A4 must remain OUT_OF_SERVICE.
# SENSOR_007 must not be included in simulator publishing.
DISABLED_SENSOR_IDS = {"SENSOR_007"}
DISABLED_SLOT_IDS = {"B2-A4"}


def load_config():
    """Load simulator settings and sensor mappings."""
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def current_timestamp():
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def generate_sensor_reading(sensor_id, slot_id, status):
    """Generate a valid reading for a parking sensor."""
    if status == "occupied":
        distance_cm = round(random.uniform(3.0, 15.0), 2)
    else:
        distance_cm = round(random.uniform(30.0, 100.0), 2)

    return {
        "sensor_id": sensor_id,
        "slot_id": slot_id,
        "status": status,
        "distance_cm": distance_cm,
        "timestamp": current_timestamp(),
    }


def generate_entrance_event(sensor_id):
    """Generate an entrance or exit event without a parking slot."""
    return {
        "sensor_id": sensor_id,
        "status": random.choice(["entry_detected", "exit_detected"]),
        "distance_cm": round(random.uniform(5.0, 30.0), 2),
        "timestamp": current_timestamp(),
    }


def publish_message(client, topic, payload, qos):
    """Publish a JSON payload to the MQTT broker."""
    info = client.publish(
        topic,
        json.dumps(payload),
        qos=qos,
    )

    info.wait_for_publish(timeout=5)

    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"Publish failed: {topic}")
        return False

    if not info.is_published():
        print(f"Publish timed out: {topic}")
        return False

    return True


def run_cycle(parking_slots, entrance_sensor, parking_states, client=None, qos=1):
    """Generate one cycle. Without a client, only preview messages offline."""
    print("\n--- Simulation cycle ---")

    for slot in parking_slots:
        sensor_id = slot["sensor_id"]
        slot_id = slot["slot_id"]

        if sensor_id in DISABLED_SENSOR_IDS or slot_id in DISABLED_SLOT_IDS:
            print(f"SKIPPED {sensor_id} -> {slot_id}: OUT_OF_SERVICE")
            continue

        if random.random() < 0.10:
            current_state = parking_states[sensor_id]
            parking_states[sensor_id] = (
                "available" if current_state == "occupied" else "occupied"
            )

        status = parking_states[sensor_id]
        reading = generate_sensor_reading(sensor_id, slot_id, status)
        topic = PARKING_TOPIC.format(slot_id=slot_id)

        if client is None:
            print(f"DRY RUN {topic}")
            print(json.dumps(reading))
        elif publish_message(client, topic, reading, qos):
            print(f"PUBLISHED {sensor_id} -> {slot_id}: {status}")

        if client is not None:
            time.sleep(0.2)

    if random.random() < 0.30:
        sensor_id = entrance_sensor["sensor_id"]
        topic = entrance_sensor["topic"]
        event = generate_entrance_event(sensor_id)

        if client is None:
            print(f"DRY RUN {topic}")
            print(json.dumps(event))
        elif publish_message(client, topic, event, qos):
            print(f"PUBLISHED {sensor_id}: {event['status']}")

    print("Reading cycle completed.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="SpotSync Person 5 sensor simulator"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Connect to MQTT and publish messages. Requires prior team approval.",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Repeat cycles continuously. Requires --publish.",
    )
    args = parser.parse_args(argv)

    if args.continuous and not args.publish:
        parser.error("--continuous requires --publish")

    config = load_config()
    interval = config["simulation_interval_seconds"]
    mqtt_config = config["mqtt"]
    qos = mqtt_config["qos"]

    parking_slots = config["parking_lot"]["slots"]
    entrance_sensor = config["entrance_sensor"]

    active_slots = [
        slot for slot in parking_slots
        if slot["sensor_id"] not in DISABLED_SENSOR_IDS
        and slot["slot_id"] not in DISABLED_SLOT_IDS
    ]

    parking_states = {
        slot["sensor_id"]: random.choice(["occupied", "available"])
        for slot in active_slots
    }

    print("SpotSync Person 5 Sensor Simulator")
    print("----------------------------------")
    print(f"Configured parking sensors: {len(parking_slots)}")
    print(f"Active simulator parking sensors: {len(active_slots)}")
    print(f"Entrance sensor: {entrance_sensor['sensor_id']}")
    print("SENSOR_007 / B2-A4: DISABLED (OUT_OF_SERVICE)")
    print(f"Simulation interval: {interval} seconds")

    if not args.publish:
        print("\nOFFLINE DRY-RUN MODE")
        print("No MQTT connection will be opened.")
        run_cycle(
            active_slots,
            entrance_sensor,
            parking_states,
        )
        print("\nDry run finished. No messages were published.")
        return

    broker = os.getenv("SPOTSYNC_MQTT_BROKER", mqtt_config["broker"])
    port = int(os.getenv("SPOTSYNC_MQTT_PORT", mqtt_config["port"]))

    print("\nLIVE MQTT MODE REQUESTED.")
    print("Do not use this mode until Person 1 and Person 2 approve testing.")
    print(f"Broker: {broker}:{port}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    loop_started = False

    try:
        client.connect(broker, port, 60)
        client.loop_start()
        loop_started = True

        cycle = 0
        while True:
            cycle += 1
            print(f"\nCycle {cycle}")

            run_cycle(
                active_slots,
                entrance_sensor,
                parking_states,
                client=client,
                qos=qos,
            )

            if not args.continuous:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\nSensor simulator stopped.")

    except (OSError, ValueError, KeyError) as error:
        print(f"\nSimulator configuration or connection error: {error}")

    finally:
        if loop_started:
            client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
