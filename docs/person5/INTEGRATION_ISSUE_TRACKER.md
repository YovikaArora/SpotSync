# SpotSync – Person 5 Integration Issue Tracker

Last updated: 20 November 2026

## Status definitions
- DONE: Completed and verified offline or through code inspection.
- BLOCKED: Waiting for environment provisioning or owner approval.
- PENDING: Person 5 work remains.
- DEFERRED: Requires physical hardware integration.

## 1. Simulator and MQTT preparation

| ID | Task | Status | Notes |
|---|---|---|---|
| P5-001 | Inspect MQTT infrastructure | DONE | Local Mosquitto inspected; no live publishing |
| P5-002 | Standardize sensor IDs | DONE | SENSOR_001 to SENSOR_008 |
| P5-003 | Align seven parking mappings | DONE | Confirmed by Person 1 |
| P5-004 | Configure entrance sensor | DONE | SENSOR_008, no parking slot ID |
| P5-005 | Make simulator offline by default | DONE | Explicit --publish required |
| P5-006 | Exclude B2-A4 from publishing | DONE | SENSOR_007 excluded |
| P5-007 | Validate payload formats | DONE | Offline tests passing |
| P5-008 | Test occupied/available scenarios | DONE | Offline |
| P5-009 | Test fluctuating occupancy | DONE | Flap scenario |
| P5-010 | Test fault/offline/stale/invalid scenarios | DONE | Offline |
| P5-011 | Test entrance fault/offline scenarios | DONE | Offline |
| P5-012 | Verify actual MQTT delivery | BLOCKED | Await isolated broker and owner approval |

## 2. Backend and database integration

| ID | Task | Status | Notes |
|---|---|---|---|
| P5-013 | Provision isolated PostgreSQL test database | BLOCKED | Person 1 coordinating |
| P5-014 | Provision isolated Neo4j environment | BLOCKED | Person 1 coordinating |
| P5-015 | Provision isolated MQTT test broker | BLOCKED | Person 2 coordinating |
| P5-016 | Verify backend subscriber connectivity | BLOCKED | Actual broker test pending |
| P5-017 | Verify SENSOR_001 occupancy processing | BLOCKED | First controlled test |
| P5-018 | Verify three-reading stability rule | DONE | Mocked tests cover three consecutive occupied and available readings |
| P5-019 | Verify abnormal sensor handling | DONE | Mocked tests cover fault, blocked, unexpected, stale and offline handling |
| P5-020 | Verify database occupancy updates | BLOCKED | Requires isolated environment |
| P5-021 | Verify MQTT-to-WebSocket delivery | BLOCKED | Connected-client test pending |
| P5-022 | Verify frontend live updates | BLOCKED | Depends on WebSocket delivery |

## 3. Application workflow testing

| ID | Task | Status | Notes |
|---|---|---|---|
| P5-023 | Review booking/allocation tests | DONE | Existing backend tests inspected |
| P5-024 | Test automatic allocation integration | BLOCKED | Isolated environment required |
| P5-025 | Test reservation conflicts | BLOCKED | Isolated environment required |
| P5-026 | Test session entry/exit integration | BLOCKED | Isolated environment required |
| P5-027 | Test ticket creation/validation integration | BLOCKED | Isolated environment required |
| P5-028 | Review navigation implementation | DONE | Code inspected |
| P5-029 | Add dedicated navigation tests | DONE | Four mocked tests pass: shortest route, directed paths, invalid weights and incomplete metadata |
| P5-030 | Verify actual navigation metrics | BLOCKED | Neo4j path values unverified |

## 4. Documentation and hardware

| ID | Task | Status | Notes |
|---|---|---|---|
| P5-031 | Prepare test-case template | DONE | Person 5 documentation |
| P5-032 | Prepare Arduino handoff checklist | DONE | UNO R3 |
| P5-033 | Create integration issue tracker | DONE | This document |
| P5-034 | Prepare consolidated test report | DONE | Updated with backend offline test results and environment limitation |
| P5-035 | Confirm exact sensor modules and wiring | DEFERRED | Await hardware details |
| P5-036 | Implement UNO R3 serial-to-MQTT bridge | DEFERRED | Requires confirmed sensor protocol |
| P5-037 | Verify physical sensor readings | DEFERRED | Hardware integration pending |

## 5. Confirmed backend contract

### MQTT subscriptions
- spotsync/parking/+/occupancy
- spotsync/sensors/+/events

### Parking payload
- sensor_id
- status
- distance_cm
- timestamp
- slot_id (optional according to backend contract)

### First controlled test
- SENSOR_001 -> B1-A1
- Three consecutive stable readings are required before a normal occupancy transition.
- Exact distance calibration thresholds still need confirmation.

### Abnormal readings
- Malformed/incomplete messages: rejected.
- Unknown sensors or mismatched mappings: rejected.
- Stale/future-skewed timestamps: rejected.
- Fault, blocked and unexpected readings: recorded without normal occupancy transition.
- Offline/stale sensors: can cause UNKNOWN and unavailable state.

### Entrance events
- SENSOR_008 is entrance/exit only.
- Entrance events do not change parking occupancy.

### WebSocket
- Endpoint: ws://localhost:8000/ws/parking
- Event type: parking_update
- Backend commits database changes before broadcasting.

Actual broker connectivity and connected-client WebSocket delivery remain unverified.

## 6. Owner dependencies

### Person 1
- Provision and confirm isolated PostgreSQL and Neo4j test environments.
- Confirm test access and approved procedure.
- Retain ownership of database mappings and B2-A4 status.

### Person 2
- Provision and confirm isolated MQTT test broker.
- Share final backend testing procedure and calibration thresholds.
- Coordinate controlled MQTT and WebSocket verification.

### Person 5
- Continue offline testing and documentation.
- Prepare mocked tests for navigation and backend contracts.
- Coordinate controlled testing after environment confirmation.

## 7. Safety restrictions

- Do not use Render primary or shared databases for integration testing.
- Do not publish to an unverified MQTT broker.
- Do not terminate or restart the existing Mosquitto service.
- Do not reset or modify shared database records.
- Keep SENSOR_007 / B2-A4 OUT_OF_SERVICE and unavailable.
- SENSOR_008 must remain exclusively for entrance/exit events.
- Do not report actual MQTT, database, WebSocket or frontend delivery as verified until tested.
- Do not treat Neo4j placeholder route distances or times as verified.
- Use the confirmed Arduino UNO R3; verify sensor modules and wiring before hardware integration.

## 8. Completion criteria

Person 5 integration work is not complete until:
1. Isolated test environments are confirmed by the owners.
2. Controlled SENSOR_001 MQTT processing is verified.
3. Database occupancy updates are verified.
4. WebSocket delivery to a connected client is verified.
5. Required booking, session, ticket and navigation tests are completed or formally assigned.
6. UNO R3 hardware integration is tested, or explicitly recorded as deferred by the team.
7. Test results and unresolved issues are documented.
