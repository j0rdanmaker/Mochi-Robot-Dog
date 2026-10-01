# RobotDog Design

This is how RobotDog meets [REQUIREMENTS.md](REQUIREMENTS.md). The BOM
(`hardware/parts/RobotDog_BOM.csv`) and the wiring diagrams (`hardware/wiring/`) must
agree with this file. If they differ, update this file first.

## 1. Electronics

| Ref | Part | Role | Notes |
|-----|------|------|-------|
| U1 | Freenove ESP32-S3-WROOM CAM (N8R8, USB-C) | Main controller | Comes with an OV2640 camera on its FPC connector. Matches upstream's `esp32-wroom-camera` env. |
| U2 | OV2640 camera (bundled with U1) | Camera | An OV5640 or 120-160° wide-angle module with the same 24-pin FPC can replace it later. |
| U3 | PCA9685 16-ch PWM board | Servo driver | I2C 0x40. Reinforce the V+ and GND rails by soldering 16 AWG wire along the through-hole pads, as upstream recommends. |
| U4 | GY-87 (MPU6050 + HMC5883L + BMP180) | IMU, compass, barometer | Buy one listed as **HMC5883L**. The QMC5883L clone (0x0D) does not work with the upstream driver. |
| U5 | SSD1306 0.96" 128x64 I2C OLED | Display | I2C 0x3C. 4-pin (VCC/GND/SCL/SDA). |
| U6 | PAJ7620U2 module | Gesture sensor | I2C 0x73. |
| U7, U8 | HC-SR04P (or RCWL-1601), 3.3 V-capable | Ultrasonic left/right | Powered at 3.3 V so the echo is 3.3 V. TRIG and ECHO tied together for NewPing one-pin mode. |
| U9 | MAX98357A I2S amp breakout | Audio out | 5 V supply. Headers soldered by hand. |
| LS1 | 3 W 4 Ω speaker | Speaker | On the amp's screw terminal. |
| U10 | INMP441 I2S mic | Voice input | **Future**: pins reserved, not in the BOM yet. |
| M1, M4, M7, M10 | DS3225MG-class 25 kg-cm servo, 180° | Shoulders | Rated 4.8-6.8 V. Metal gear. |
| M2, M3, M5, M6, M8, M9, M11, M12 | DSServo DS3235 35 kg-cm coreless servo, 180° | Upper and lower limbs (hips, knees) | Rated 5-7.4 V; 32 kg-cm / 2.1 A stall at 6 V. Not the DS3235SG (HV, 35 kg-cm only at 8.4 V) and not the 270° version. Upgraded from DS3225MG because a full-stride trot would load the knees to ~61% and hips to ~48% of DS3225MG stall (`hardware/parts/SERVO_CHECK.md`). Same 40x20 mm footprint and 60 g. |
| PS1 | SZBK07 20 A buck | Servo rail | Set to **6.3 V**. Screw terminals. |
| PS2 | XL4015 5 A buck (with voltmeter) | Logic rail | Set to **5.0 V**. Screw terminals. |
| BT1 | 2S LiPo hard case, 5200-6200 mAh, XT60 | Battery | Check that it fits the printed body before buying. |
| F1 | Inline ATC blade fuse holder, 12-14 AWG, 20 A fuse | Main fuse | Next to the battery connector. |
| SW1 | Main power switch, ≥30 A DC (XT60 anti-spark switch or high-current rocker) | Main power | |
| SW2 | 16/19 mm momentary metal push button with **5 V** LED ring | Mode button + power-on light | The LED runs off the 5 V rail, so it lights whenever logic power is on. The 12 V LED version will not light at 5 V. |
| R1, R2 | 100 kΩ + 47 kΩ through-hole resistors | Battery sense divider | 8.4 V → 2.69 V at GPIO3. **Future** in firmware. |
| — | 4x servo extension cables, silicone wire (14 AWG and 22 AWG), XT60 pairs, Dupont jumpers, heat shrink | Harness | Power/ground distribution points are soldered splices covered with heat shrink (no lever connectors). |
| — | 2S balance charger, plug-in LiPo voltage alarm, LiPo charging bag | Support | Not mounted on the robot. |

## 2. Power

```
BT1 (2S, 7.4-8.4 V) ──XT60── F1 (20 A) ── SW1 ──┬── PS1 SZBK07 → 6.3 V ── PCA9685 V+ ── servos M1-M12
                                                 ├── PS2 XL4015 → 5.0 V ──┬── U1 5V pin
                                                 │                        ├── U9 MAX98357A VIN
                                                 │                        └── SW2 LED (+)
                                                 └── R1/R2 divider ── U1 GPIO3 (battery sense)
U1 3V3 pin ── PCA9685 VCC, GY-87, OLED, PAJ7620, HC-SR04P x2, (future INMP441)
All grounds common. Star point: the SW1 output side / buck input negatives.
```

- **Wire gauge:** 14 AWG from the battery through the fuse, switch, and SZBK07 to the PCA9685 V+. 22 AWG for logic power and signals.
- **3.3 V load:** the ESP32 board's 3.3 V regulator supplies the sensors. The total is well under 200 mA.
- **5 V load:** ESP32 plus camera about 0.5 A, amp peaks about 0.8 A. The XL4015 has plenty of headroom.
- **Do not** power the ESP32 from USB and the 5 V rail at the same time unless the board isolates the two (check before connecting both).

## 3. ESP32-S3 pin map (Freenove ESP32-S3-WROOM CAM)

The upstream `esp32-wroom-camera` pins are kept unchanged.

| GPIO | Function | Connected to | Status |
|------|----------|--------------|--------|
| 47 | I2C SDA | PCA9685, GY-87, OLED, PAJ7620 | upstream |
| 21 | I2C SCL | same | upstream |
| 1 | Ultrasonic left (TRIG+ECHO) | U7 | upstream `USS_LEFT_PIN` |
| 14 | Ultrasonic right (TRIG+ECHO) | U8 | upstream `USS_RIGHT_PIN` |
| 48 | WS2812 RGB LED | onboard | upstream |
| 4-13, 15-18 | Camera | onboard FPC | upstream (ESP32S3_EYE mapping) |
| 3 | Battery sense (ADC1_CH2) | R1/R2 divider | future firmware |
| 41 | I2S BCLK | MAX98357A BCLK, (INMP441 SCK) | future firmware |
| 42 | I2S LRCLK/WS | MAX98357A LRC, (INMP441 WS) | future firmware |
| 2 | I2S DOUT | MAX98357A DIN | future firmware; the onboard LED on GPIO2 flickers during audio (harmless) |
| 40 | I2S DIN | INMP441 SD | **reserved**; the microSD slot is not used |
| 38 | Mode button (to GND, internal pull-up) | SW2 | future firmware |
| 39, 46 | spare | — | GPIO46 is a strapping pin. These are the only pins left after all Section 7 provisions. |
| 0 | BOOT button | onboard | do not use |
| 19, 20 | USB | onboard | do not use |
| 35-37 | Octal PSRAM | internal | not available |
| 43, 44 | UART0 (serial console) | onboard | do not use |

## 4. I2C bus (GPIO47/21, 3.3 V)

| Device | Address |
|--------|---------|
| PCA9685 | 0x40 (0x70 all-call) |
| MPU6050 (GY-87) | 0x68 |
| HMC5883L (GY-87, via MPU6050 bypass) | 0x1E |
| BMP180 (GY-87) | 0x77 |
| SSD1306 | 0x3C |
| PAJ7620U2 | 0x73 |
| *Future:* TCA9548A mux for the eye OLEDs (X-3) | 0x71 (A0 tied high on its header) |
| *Future:* 2x eye OLEDs, behind the mux | 0x3C each, on mux channels 0/1 |

There are no address conflicts. Most breakouts already have pull-ups on board. If
the bus has too many in parallel, remove or ignore extras only by cutting a jumper
(no SMD rework).

## 5. Servo channels (PCA9685, upstream order)

| PWM | Servo | Joint |
|-----|-------|-------|
| 0 | M1 | Front left shoulder |
| 1 | M2 | Front left upper limb |
| 2 | M3 | Front left lower limb |
| 3 | M4 | Front right shoulder |
| 4 | M5 | Front right upper limb |
| 5 | M6 | Front right lower limb |
| 6 | M7 | Rear left shoulder |
| 7 | M8 | Rear left upper limb |
| 8 | M9 | Rear left lower limb |
| 9 | M10 | Rear right shoulder |
| 10 | M11 | Rear right upper limb |
| 11 | M12 | Rear right lower limb |

Channels 12-15 are unused.

## 6. Firmware

- `firmware/leika` is upstream SpotMicroESP32-Leika as a git submodule, pinned. Never edit it in place.
- `firmware/overlay/` holds our PlatformIO config: a `robotdog` env based on `esp32-wroom-camera`, with our feature flags (`USE_MPU6050`, `USE_HMC5883`, `USE_BMP180`, `USE_PAJ7620U2`, `USE_PCA9685`, `USE_WS2812`) and the pins above.
- `USE_USS` is **off** for now. The ultrasonic sensors are wired, but upstream's USS code uses NewPing, an Arduino-only library, and upstream builds with ESP-IDF, so enabling it fails to compile. To turn it on, the overlay needs an ESP-IDF one-pin ultrasonic driver that provides NewPing's constructor and `ping_cm()`.
- `firmware/build.sh` builds by pointing PlatformIO at the overlay config, so the submodule stays clean.

## 7. Future provisions

These correspond to REQUIREMENTS.md Section 7. None of the parts below are in the BOM
yet (except the X-1 speaker and amp, which are installed now). The wiring diagrams show
reserved connections as dashed or labeled "future".

| ID | Feature | Part (module, no SMD) | Connection | Power | Notes |
|----|---------|------------------------|------------|-------|-------|
| X-1 | Sounds/speech | MAX98357A + 3 W 4 Ω speaker (installed now) | I2S BCLK 41, LRC 42, DIN 2 | 5 V, ~0.8 A peak | Firmware only. |
| X-2 | Voice commands | INMP441 I2S MEMS mic module | SCK 41 and WS 42 (shared with the amp, one full-duplex I2S port), SD → GPIO40, L/R → GND | 3.3 V, <2 mA | ESP-SR needs PSRAM (N8R8 has 8 MB). Don't use the microSD slot: GPIO40 is its data line. |
| X-3 | OLED eyes/face | 2x 0.96" or 1.3" I2C OLED (SSD1306 or SH1106) + TCA9548A mux breakout | Mux on the main I2C bus at 0x71; eyes on mux channels 0 and 1 | 3.3 V, ~20-30 mA per OLED | Set the address with the mux's A0 header pin, no SMD jumpers. 0x70 is avoided because the PCA9685 answers its all-call address there. Round SPI TFT eyes (GC9A01) would need ~6 GPIOs we don't have. |
| X-4 | Battery monitoring | R1/R2 divider (installed now) | GPIO3 (ADC1_CH2), 8.4 V → 2.69 V | — | Calibrate against a multimeter in firmware. |
| X-5 | Mode button actions | SW2 (installed now) | GPIO38 to GND, internal pull-up | — | |
| X-6 | Better camera | OV5640 or wide-angle OV2640, 24-pin FPC | Onboard FPC | 5 V/3.3 V from board | OV5640 runs warmer; leave airflow. |
| X-7 | Custom firmware | — | — | — | Keep using the overlay approach until firmware forks for real. |
| X-8 | Mechanical drawing | — | — | — | Goes in `hardware/mechanical/`. |

**Power headroom:** with all provisions fitted, 3.3 V stays under about 250 mA and 5 V
under about 1.5 A peak. Both are within the ESP32 board's regulator and the XL4015.
