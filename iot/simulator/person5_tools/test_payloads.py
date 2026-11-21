"""Offline unit tests for Person 5 scenario payload construction."""
import unittest
from datetime import datetime, timedelta, timezone

from scenario_runner import (
    build_entrance_payload,
    build_parking_payload,
    scenario_messages,
)


class PayloadTests(unittest.TestCase):
    def test_parking_payload_contract(self):
        payload = build_parking_payload("SENSOR_001", "B1-A1", "occupied")
        self.assertEqual(
            set(payload),
            {"sensor_id", "slot_id", "status", "distance_cm", "timestamp"},
        )
        self.assertEqual(payload["slot_id"], "B1-A1")

    def test_entrance_payload_has_no_slot_id(self):
        payload = build_entrance_payload("SENSOR_008", "entry_detected")
        self.assertEqual(
            set(payload),
            {"sensor_id", "status", "distance_cm", "timestamp"},
        )
        self.assertNotIn("slot_id", payload)

    def test_entrance_scenario_uses_official_topic(self):
        topic, payload = scenario_messages(
            "SENSOR_008", None, "entrance", 1
        )[0]
        self.assertEqual(topic, "spotsync/sensors/SENSOR_008/events")
        self.assertEqual(payload["sensor_id"], "SENSOR_008")
        self.assertNotIn("slot_id", payload)

    def test_stale_scenario_generates_old_timestamp(self):
        _, payload = scenario_messages("SENSOR_001", "B1-A1", "stale", 1)[0]
        generated = datetime.fromisoformat(payload["timestamp"])
        age = datetime.now(timezone.utc) - generated
        self.assertGreaterEqual(age, timedelta(minutes=59))
        self.assertEqual(payload["status"], "occupied")

    def test_missing_scenario_publishes_nothing(self):
        topic, payload = scenario_messages(
            "SENSOR_001", "B1-A1", "missing", 1
        )[0]
        self.assertIsNone(payload)
        self.assertEqual(topic, "spotsync/parking/B1-A1/occupancy")


    def test_flap_scenario_alternates_occupancy(self):
        messages = scenario_messages(
            "SENSOR_001", "B1-A1", "flap", 4
        )
        statuses = [payload["status"] for _, payload in messages]
        self.assertEqual(
            statuses,
            ["occupied", "available", "occupied", "available"],
        )

    def test_fault_scenario_generates_fault_status(self):
        _, payload = scenario_messages(
            "SENSOR_001", "B1-A1", "fault", 1
        )[0]
        self.assertEqual(payload["status"], "fault")

    def test_offline_scenario_generates_sensor_offline_status(self):
        _, payload = scenario_messages(
            "SENSOR_001", "B1-A1", "offline", 1
        )[0]
        self.assertEqual(payload["status"], "sensor_offline")

    def test_invalid_scenario_omits_distance(self):
        _, payload = scenario_messages(
            "SENSOR_001", "B1-A1", "invalid", 1
        )[0]
        self.assertNotIn("distance_cm", payload)

    def test_entrance_fault_has_no_slot_id(self):
        topic, payload = scenario_messages(
            "SENSOR_008", None, "entrance-fault", 1
        )[0]
        self.assertEqual(topic, "spotsync/sensors/SENSOR_008/events")
        self.assertEqual(payload["status"], "fault")
        self.assertNotIn("slot_id", payload)

    def test_entrance_offline_has_no_slot_id(self):
        _, payload = scenario_messages(
            "SENSOR_008", None, "entrance-offline", 1
        )[0]
        self.assertEqual(payload["status"], "sensor_offline")
        self.assertNotIn("slot_id", payload)


if __name__ == "__main__":
    unittest.main()
