# Arduino UNO R3 – Person 5 Hardware Handoff Checklist

This is a planning and verification checklist, not a wiring diagram. Confirm the
actual sensor modules, voltage requirements, pinout, power budget, and motor
driver with the hardware owner before connecting components.

## Hardware readiness
- [ ] Confirm exact ultrasonic sensor model and operating voltage.
- [ ] Confirm Arduino UNO R3 power source and common ground requirements.
- [ ] Confirm motor model and motor-driver board; do not drive a DC motor directly from an Arduino I/O pin.
- [ ] Confirm wiring and pin assignments with the team.
- [ ] Check for loose wires and short circuits before power-up.

## Firmware and data contract
- [ ] Read distance measurements reliably.
- [ ] Define and document calibrated occupied/available distance thresholds.
- [ ] Add a measurement timeout/error state.
- [ ] Include sensor ID, slot ID (parking sensors only), status, distance_cm, and timezone-aware timestamp.
- [ ] Keep SENSOR_008 entrance/exit payload free of slot_id.
- [ ] Ensure hardware-generated statuses match the backend contract.
- [ ] Avoid sending unstable readings as confirmed occupancy without applying the agreed stability rule.

## MQTT bridge
- [ ] Decide whether the Arduino sends MQTT directly or sends serial data to a gateway.
- [ ] Document gateway/broker address and credentials securely.
- [ ] Verify reconnect behaviour.
- [ ] Verify message timestamps and payload encoding.
- [ ] Test one sensor before enabling multiple sensors.

## Acceptance
- [ ] Keep B2-A4 OUT_OF_SERVICE and unavailable until Person 1 approves its
      operational status after physical installation and complete integration verification.
- [ ] Compare physical readings with simulator readings.
- [ ] Verify backend receipt and event history.
- [ ] Verify parking status changes only after the agreed stable readings.
- [ ] Verify SENSOR_008 never changes slot occupancy.
- [ ] Record wiring, firmware version, test evidence, and known limitations.
