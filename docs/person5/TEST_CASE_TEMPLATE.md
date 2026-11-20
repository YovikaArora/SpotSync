# SpotSync Person 5 – Test Case Record

Copy this template for each test. Record actual results only after running it.

| Field | Value |
|---|---|
| Test ID | |
| Date/time | |
| Tester | |
| Environment | Local / Development |
| Sensor ID | |
| Scenario | |
| MQTT topic | |
| Expected result | |
| Actual result | |
| Backend log evidence | |
| Database evidence | |
| WebSocket/dashboard evidence | |
| Status | Not run / Pass / Fail / Blocked |
| Bug/reference | |

## Suggested test cases

| ID | Scenario | Expected result |
|---|---|---|
| P5-001 | SENSOR_001 occupied, three consecutive readings | Slot becomes OCCUPIED after stability rule |
| P5-002 | SENSOR_001 available, three consecutive readings | Slot becomes AVAILABLE subject to reservation/out-of-service rules |
| P5-003 | Alternating occupied/available | No false stable transition |
| P5-004 | Parking sensor fault | Event recorded; fault does not count as occupancy reading |
| P5-005 | Parking sensor blocked | Event handled according to backend rules |
| P5-006 | Parking sensor_offline | Assigned slot becomes UNKNOWN, subject to backend rules |
| P5-007 | Stale timestamp | Message rejected; no occupancy update |
| P5-008 | Invalid payload | Message rejected |
| P5-009 | Missing message | No new event; stale-sensor monitor behaviour checked separately |
| P5-010 | SENSOR_008 entry_detected | Entrance event recorded; health updated; no slot update/broadcast |
| P5-011 | SENSOR_008 exit_detected | Entrance event recorded; health updated; no slot update/broadcast |
| P5-012 | SENSOR_008 sensor_offline | Entrance health updated; no parking slot becomes UNKNOWN |
| P5-013 | B2-A4 / SENSOR_007 status check | Slot remains OUT_OF_SERVICE and unavailable until formally approved by Person 1 |

Do not mark a test Pass based only on a publisher saying it sent a message. Confirm backend receipt and the expected persisted/application result.
