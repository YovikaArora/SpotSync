import contextlib
import io
import sys
import unittest
from unittest.mock import MagicMock, patch

import scenario_runner


class ScenarioRunnerSafetyTests(unittest.TestCase):

    def test_default_run_does_not_connect_to_mqtt(self):
        output = io.StringIO()
        mqtt_mock = MagicMock()

        with patch.object(sys, "argv", [
            "scenario_runner.py",
            "--scenario", "occupied",
            "--sensor-id", "SENSOR_001",
            "--count", "1",
        ]):
            with patch.object(scenario_runner, "mqtt", mqtt_mock):
                with contextlib.redirect_stdout(output):
                    result = scenario_runner.main()

        self.assertEqual(result, 0)
        self.assertIn("DRY RUN", output.getvalue())
        mqtt_mock.Client.assert_not_called()

    def test_live_publish_to_b2_a4_is_blocked(self):
        mqtt_mock = MagicMock()
        errors = io.StringIO()

        with patch.object(sys, "argv", [
            "scenario_runner.py",
            "--scenario", "occupied",
            "--sensor-id", "SENSOR_007",
            "--publish",
        ]):
            with patch.object(scenario_runner, "mqtt", mqtt_mock):
                with contextlib.redirect_stderr(errors):
                    with self.assertRaises(SystemExit) as raised:
                        scenario_runner.main()

        self.assertEqual(raised.exception.code, 2)
        self.assertIn("B2-A4 is blocked", errors.getvalue())
        mqtt_mock.Client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
