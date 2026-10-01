# RobotDog Requirements

RobotDog is a hobby quadruped based on
[SpotMicroESP32-Leika](https://github.com/runeharlyk/SpotMicroESP32-Leika)
(standard "Leika" kinematics). This document states what the robot must do and
the constraints on how it is built. The design that meets these requirements is
in [DESIGN.md](DESIGN.md).

Requirement levels: **must** = required for the first build, **should** =
wanted but can slip. Features we don't want now but must not rule out are in
[Section 7, Future provisions](#7-future-provisions): the first build reserves
pins, bus addresses, power, and space for them.

## 1. Build and assembly

| ID | Level | Requirement |
|----|-------|-------------|
| B-1 | must | All electronics are off-the-shelf modules/breakout boards. **No SMD soldering.** |
| B-2 | must | Allowed soldering: pin headers, wires, through-hole resistors, and wire reinforcement on through-hole pads. |
| B-3 | must | Modules connect with Dupont/servo-style headers, screw terminals, or XT60 connectors wherever the module offers them, so parts can be swapped without desoldering. |
| B-4 | must | Structural parts are 3D-printed from the Leika part set (KDY0523 original, Kooba SpotMicroESP32 remix, robjk reinforced shoulder remix). |
| B-5 | must | Fasteners and bearings match the Leika part list: 84x M2x8 + M2 nuts, 92x M3x8 + M3 nuts, 64x M3x20 + M3 nuts, 12x 625ZZ bearings. |
| B-6 | must | Print progress is tracked in `hardware/PRINT_CHECKLIST.md`. |
| B-7 | should | Total parts cost stays hobby-level: mid-range components, no premium/HV servos. |

## 2. Motion

| ID | Level | Requirement |
|----|-------|-------------|
| M-1 | must | 12 servos (3 per leg: shoulder, upper limb, lower limb), 20-35 kg-cm class. |
| M-2 | must | Servos are driven by a PCA9685 over I2C, in the upstream channel order (PWM 0-11, see DESIGN.md). |
| M-3 | must | Servo supply voltage stays within the servo's rating (regulated rail, not raw battery, unless the servos are rated for 2S). |
| M-4 | must | Runs upstream Leika firmware with its gaits and web UI. |

## 3. Sensing

| ID | Level | Requirement |
|----|-------|-------------|
| S-1 | must | IMU with accelerometer, gyro, and **compass**, supported by upstream drivers. |
| S-2 | must | Camera streaming to the web UI. |
| S-3 | must | Two front ultrasonic distance sensors (left, right), 3.3 V logic-safe. |
| S-4 | must | Hand-gesture sensor. |
| S-5 | should | Barometer (comes with the chosen IMU module). |

## 4. User interface

| ID | Level | Requirement |
|----|-------|-------------|
| U-1 | must | 0.96" OLED status display. |
| U-2 | must | Main power switch and a lit mode button. |
| U-3 | must | Onboard RGB status LED. |
| U-4 | must | Speaker and I2S amplifier installed and wired (sound firmware is future, see X-1). |

## 5. Power and safety

| ID | Level | Requirement |
|----|-------|-------------|
| P-1 | must | Rechargeable 2S battery with enough current for 12 servos at peak (20 A+). |
| P-2 | must | Main fuse as close to the battery as practical. |
| P-3 | must | Main switch rated for the full servo current (30 A DC or better). |
| P-4 | must | Separate regulated rails for servos and for logic (5 V), with a common ground. |
| P-5 | must | Battery is removable for charging with a standard balance charger. |
| P-6 | should | Low-voltage warning (plug-in LiPo alarm). |
| P-7 | must | Battery-sense voltage divider wired to an ADC pin (firmware reading is future, see X-4). |

## 6. Firmware and repository

| ID | Level | Requirement |
|----|-------|-------------|
| F-1 | must | Upstream firmware is a git submodule pinned to a known commit and is never edited in place. |
| F-2 | must | Our changes (board env, pins, feature flags) live in overlay files under `firmware/overlay/`. |
| R-1 | must | Wiring is documented as WireViz diagrams (YAML source + rendered output) in `hardware/wiring/`. |
| R-2 | must | The BOM (`hardware/parts/RobotDog_BOM.csv`) matches the wiring diagrams and this document. |

## 7. Future provisions

These are features we don't want now. The first build must not rule them
out, so each row records what is reserved for it. Every future part must still
meet B-1/B-2 (modules only, no SMD soldering). Details are in
[DESIGN.md Section 7](DESIGN.md#7-future-provisions).

| ID | Feature | Reserved now |
|----|---------|--------------|
| X-1 | Dog sounds and speech (barks, whines, text-to-speech) | Speaker and MAX98357A amp installed; I2S pins GPIO41/42/2; 5 V rail headroom. |
| X-2 | Microphone and offline voice commands (ESP-SR wake word and commands) | INMP441 I2S mic: shares BCLK/WS (GPIO41/42), data on GPIO40; microSD slot left unused; 8 MB PSRAM board chosen for ESP-SR. |
| X-3 | OLED "eyes"/face display (two eyes, animated) | I2C bus GPIO47/21; TCA9548A mux module at address 0x71 (0x70 collides with the PCA9685 all-call), so two identical 0x3C OLEDs can share the bus; 3.3 V budget; mounting space in the head. |
| X-4 | Battery voltage monitoring and low-battery behavior | 100k/47k divider already wired to GPIO3 (ADC1). |
| X-5 | Mode/menu button actions | Button wired to GPIO38. |
| X-6 | Wider-angle or higher-resolution camera (OV5640, 120-160°) | Same 24-pin FPC connector; no wiring change. |
| X-7 | Custom firmware extending or replacing upstream | Overlay structure (F-2) keeps our config separate from upstream. |
| X-8 | Mechanical drawing of the assembled robot | Space in `hardware/mechanical/` and `docs/`. |

Pins left after all provisions: GPIO39 and GPIO46 (strapping pin, output use
only after boot). A future feature that needs more GPIOs must drop or share
something above; record that as a decision.

## 8. Out of scope (for now)

- Custom PCBs.
- Autonomous navigation and SLAM.
- Tethered or remote power.
