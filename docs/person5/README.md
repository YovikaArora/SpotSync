# SpotSync Person 5 – Simulator and Integration Kit

The Person 5 helper tools are additive and do not modify backend, database,
Neo4j, or frontend files. The existing sensor simulator has also been updated.
The helper tools and documentation are located under:

- `iot/simulator/person5_tools/`
- `docs/person5/`

## 1. Validate the simulator configuration

From the SpotSync repository root, with the project's Python environment active:

```bash
python3 iot/simulator/person5_tools/validate_config.py
```

Expected mapping:

| Sensor | Slot |
|---|---|
| SENSOR_001 | B1-A1 |
| SENSOR_002 | B1-A2 |
| SENSOR_003 | B1-A3 |
| SENSOR_004 | B2-A1 |
| SENSOR_005 | B2-A2 |
| SENSOR_006 | B2-A3 |
| SENSOR_007 | B2-A4 |
| SENSOR_008 | Entrance/exit only |

## 2. Run offline unit tests

```bash
cd iot/simulator/person5_tools
python3 -m unittest -v
cd ../../..
```

These tests check payload shape and helper behaviour only. They do not connect
to MQTT or the database.

## 3. Preview scenarios without publishing

From the repository root:

```bash
python3 iot/simulator/person5_tools/scenario_runner.py --scenario occupied --sensor-id SENSOR_001 --count 3
python3 iot/simulator/person5_tools/scenario_runner.py --scenario entrance --sensor-id SENSOR_008 --count 1
python3 iot/simulator/person5_tools/scenario_runner.py --scenario flap --sensor-id SENSOR_001 --count 6
```

## 4. Available MQTT scenarios

Only run publish scenarios against a development/test broker after coordinating
with the backend and database owners. Some scenarios deliberately affect
sensor state or create event-history records.

Parking sensors SENSOR_001–SENSOR_007:
- `occupied`
- `available`
- `fault`
- `blocked`
- `offline` (publishes `sensor_offline`)
- `unexpected`
- `flap` (alternates occupied/available)
- `stale` (timestamp is one hour old)
- `invalid` (missing required distance field)
- `missing` (publishes nothing)

SENSOR_008:
- `entrance`
- `entrance-fault`
- `entrance-offline`

The runner defaults to dry-run. Live publishing requires the explicit
`--publish` flag. Do not use that flag until Person 1 confirms the dedicated
test database and Person 2 approves the exact integration procedure.

SENSOR_007 / B2-A4 live publishing is blocked while the space is OUT_OF_SERVICE.

Examples of the publishing syntax (do not execute until approved):

```bash
python3 iot/simulator/person5_tools/scenario_runner.py --scenario occupied --sensor-id SENSOR_001 --count 3 --publish
python3 iot/simulator/person5_tools/scenario_runner.py --scenario entrance --sensor-id SENSOR_008 --count 1 --publish
python3 iot/simulator/person5_tools/scenario_runner.py --scenario stale --sensor-id SENSOR_002 --count 1 --publish
```

The runner reads the existing `iot/simulator/config.json` for sensor mapping,
broker, port, and QoS. `SPOTSYNC_MQTT_BROKER` and `SPOTSYNC_MQTT_PORT`
environment variables override the broker settings.

## Safety notes

- Do not run against production or a shared database without explicit approval.
- `occupied`, `available`, and `sensor_offline` messages can change parking
  status through the backend.
- Entrance and entrance-offline scenarios create sensor event/history activity.
- `stale`, `invalid`, and `missing` are intended for validation/rejection tests.
- The `offline` scenario sends a `sensor_offline` event; it does not physically
  disconnect the MQTT client.
- The Person 5 helper tools do not run migrations or alter databases.
- Do not commit or push without explicit approval.
- The actual backend, database, WebSocket, and dashboard outcomes still require
  live integration testing.

## Known limitations

This is a test publisher, not a full multi-sensor simulator controller. It
publishes a chosen scenario for one sensor per invocation. The main sensor simulator has been updated separately. Do not run it against
MQTT until the backend and database owners approve live integration testing.
