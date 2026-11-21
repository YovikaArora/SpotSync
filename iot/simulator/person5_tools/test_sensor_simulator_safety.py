import contextlib
import io
import unittest
from unittest.mock import MagicMock, patch

from iot.simulator import sensor_simulator


class SensorSimulatorSafetyTests(unittest.TestCase):

    def test_default_run_does_not_create_mqtt_client(self):
        output = io.StringIO()

        with patch.object(sensor_simulator.mqtt, "Client") as mqtt_client, \
             contextlib.redirect_stdout(output):
            sensor_simulator.main([])

        mqtt_client.assert_not_called()
        self.assertIn("OFFLINE DRY-RUN MODE", output.getvalue())
        self.assertIn("No MQTT connection will be opened.", output.getvalue())
        self.assertIn("SENSOR_007 / B2-A4: DISABLED", output.getvalue())

    def test_publish_mode_excludes_b2_a4(self):
        output = io.StringIO()
        fake_client = MagicMock()
        fake_info = MagicMock()
        fake_info.rc = sensor_simulator.mqtt.MQTT_ERR_SUCCESS
        fake_info.is_published.return_value = True
        fake_client.publish.return_value = fake_info

        with patch.object(
            sensor_simulator.mqtt,
            "Client",
            return_value=fake_client,
        ), patch.object(sensor_simulator.random, "random", return_value=1.0), \
             patch.object(sensor_simulator.time, "sleep"), \
             contextlib.redirect_stdout(output):
            sensor_simulator.main(["--publish"])

        published_topics = [
            call.args[0]
            for call in fake_client.publish.call_args_list
        ]

        self.assertEqual(len(published_topics), 6)
        self.assertNotIn(
            "spotsync/parking/B2-A4/occupancy",
            published_topics,
        )
        self.assertTrue(
            all(topic.startswith("spotsync/parking/") for topic in published_topics)
        )

    def test_continuous_mode_requires_publish_flag(self):
        with patch.object(sensor_simulator.mqtt, "Client") as mqtt_client:
            with self.assertRaises(SystemExit):
                sensor_simulator.main(["--continuous"])

        mqtt_client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
