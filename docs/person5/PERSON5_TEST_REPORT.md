# Person 5 – Integration and Offline Test Report

**Date:** 20 November 2026  
**Role:** Person 5 – Sensor Simulator, Integration, Testing and Documentation

## 1. Summary

Offline simulator preparation and validation have been completed.

- The simulator uses the official sensor IDs and parking-slot mapping.
- SENSOR_007 → B2-A4 is excluded from active simulation and publishing.
- SENSOR_008 is reserved for entrance and exit events.
- The simulator defaults to offline dry-run mode.
- Automated Person 5 offline tests: 16 passed.
- No live MQTT messages were published.
- No database changes were performed during offline testing.

Live integration testing remains pending until isolated PostgreSQL, Neo4j and MQTT test environments are provisioned and approved by the responsible team members.

## 2. Official sensor mapping

| Sensor ID | Assigned location | Purpose |
|---|---|---|
| SENSOR_001 | B1-A1 | Parking occupancy |
| SENSOR_002 | B1-A2 | Parking occupancy |
| SENSOR_003 | B1-A3 | Parking occupancy |
| SENSOR_004 | B2-A1 | Parking occupancy |
| SENSOR_005 | B2-A2 | Parking occupancy |
| SENSOR_006 | B2-A3 | Parking occupancy |
| SENSOR_007 | B2-A4 | Excluded; slot remains OUT_OF_SERVICE |
| SENSOR_008 | No parking slot | Entrance and exit events |

B2-A4 must remain OUT_OF_SERVICE and unavailable until physical installation and controlled integration are verified. SENSOR_008 must not generate parking occupancy updates.

## 3. Simulator implementation

The main simulator (`iot/simulator/sensor_simulator.py`) was updated to:

- Load parking sensor assignments from `iot/simulator/config.json`.
- Support offline dry-run execution by default.
- Require an explicit `--publish` flag before attempting MQTT publishing.
- Require `--publish` when using `--continuous`.
- Exclude SENSOR_007 / B2-A4 from active simulation and publishing.
- Generate readings for the six active parking sensors.
- Support entrance events through SENSOR_008.

The offline simulator run displayed six active parking sensor readings and skipped B2-A4. No MQTT connection or message publishing was performed during this verification.

## 4. Scenario toolkit

The Person 5 scenario runner (`iot/simulator/person5_tools/scenario_runner.py`) supports these offline test scenarios:

- `occupied` – occupied parking reading
- `available` – available parking reading
- `fault` – sensor fault
- `blocked` – blocked sensor reading
- `offline` – sensor offline
- `unexpected` – unexpected occupancy
- `flap` – alternating occupied and available readings
- `stale` – stale timestamp
- `invalid` – malformed or incomplete payload
- `missing` – no message generated
- `entrance` – entrance or exit event
- `entrance-fault` – entrance sensor fault
- `entrance-offline` – entrance sensor offline

The scenario runner defaults to dry-run mode. Its publishing safeguards prevent live publishing for SENSOR_007 / B2-A4.

## 5. Automated offline test results

**Test command:**

```bash
python3 -m unittest discover -s iot/simulator/person5_tools -p 'test_*.py' -v
```

**Verified result:** 16 tests passed.

Coverage includes payload validation, entrance events, fault and offline scenarios, stale and invalid readings, dry-run safety, continuous-mode safety and B2-A4 protection.

## 6. Backend integration contract

The backend team confirmed:

- Parking topic: `spotsync/parking/+/occupancy`
- Entrance topic: `spotsync/sensors/+/events`
- Payload includes sensor ID, status, distance and timezone-aware timestamp.
- Normal occupied/available transitions require three consecutive stable readings.
- Fault, blocked and unexpected readings must not trigger normal occupancy transitions.
- WebSocket endpoint: `ws://localhost:8000/ws/parking`
- WebSocket event: `parking_update`

## 7. Pending integration work

The following work remains pending approval and provisioning of isolated test environments:

- Verify MQTT delivery to the backend.
- Verify database occupancy updates.
- Verify WebSocket delivery to connected frontend clients.
- Verify stable-reading behaviour.
- Test booking, allocation, ticket, navigation and vehicle entry/exit workflows.
- Complete physical Arduino integration.

The first controlled sensor test is planned for SENSOR_001 → B1-A1.

## 8. Safety and coordination

No live MQTT publishing or database modifications were performed as part of this offline validation. The simulator must not connect to shared or primary environments without explicit approval.

