# RobotDog Bill of Materials

<!-- Generated from RobotDog_BOM.csv (a Google Sheets export) by bom.py; do not edit by hand. Regenerate with: uv run python hardware/parts/bom.py -->

| Category | Items | Subtotal |
| --- | --- | --- |
| Controller | 1 | $19.95 |
| Sensors | 3 | $30.46 |
| Actuators | 3 | $191.73 |
| Power | 6 | $64.85 |
| Audio | 2 | $15.87 |
| UI | 2 | $17.48 |
| Harness | 7 | $52.80 |
| Mechanical | 6 | $49.10 |
| Support | 3 | $38.36 |
| **Total** | | **$480.60** |

Future items are excluded from the total above.

**Short** (Extras below 0 and not marked Already Have): 1/4 W through-hole resistor kit incl. 100k and 47k (battery-sense divider); Dupont jumper wire kit, 120 pcs (M-F, M-M, F-F); WAGO 221 lever connector assortment (221-412/413/415), for power/ground distribution.

## Controller

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | [Freenove ESP32-S3-WROOM CAM (N8R8, USB-C) main controller with bundled OV2640 camera (DESIGN.md U2)](https://a.co/d/05nr03tF) | 1 | 1 | 1 | 0 | $19.95 | $19.95 | — | Get the 8 MB flash (N8R8) kit. |
| | **Subtotal** | | | | | | **$19.95** | | |

## Sensors

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U4 | [GY-87 10-DOF IMU module (MPU6050 + HMC5883L + BMP180)](https://a.co/d/0evNC5np) | 1 | 5 | 1 | 4 | $13.98 | $13.98 | — | Must be HMC5883L; QMC5883L (0x0D) clones are not supported by the upstream driver. Check the chip after it arrives. |
| U6 | [PAJ7620U2 gesture recognition sensor module, 9 hand gestures](https://a.co/d/0guiQUuV) | 1 | 1 | 1 | 0 | $10.49 (est.) | $10.49 | — |  |
| U7,U8 | [HC-SR04P (3.3 V-capable) ultrasonic distance sensor, 5-pack](https://a.co/d/06Udz26W) | 2 | 2 | 1 | 0 | $5.99 | $5.99 | — | Front left/right (need 2 of 5). The old 5 V HC-SR04 is not 3.3 V-safe in one-pin mode; do not substitute. |
| | **Subtotal** | | | | | | **$30.46** | | |

## Actuators

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U3 | [HiLetgo PCA9685 16-channel 12-bit PWM/Servo driver board](https://a.co/d/0iVQweyX) | 1 | 2 | 1 | 1 | $13.99 | $13.99 | — |  |
| M1,M4,M7,M10 | [DSSERVO DS3225MG 25 kg-cm 180-degree metal-gear digital servo, 4-pack (shoulders)](https://a.co/d/0hHIrBWt) | 4 | 4 | 1 | 0 | $54.98 | $54.98 | — | 180-degree version. |
| M2,M3,M5,M6,M8,M9,M11,M12 | [DS3235 35 kg-cm coreless 180-degree digital servo, 2-pack (hips, knees)](https://a.co/d/027v6bOo) | 8 | 2 | 4 | 0 | $30.69 | $122.76 | — | Check the listing's torque table: want ~32 kg-cm at 6 V (35 kg-cm @ 7.4 V). Avoid DS3235SG / 8.4 V versions (only ~27 kg-cm at our 6.3 V rail) and 270-degree versions. |
| | **Subtotal** | | | | | | **$191.73** | | |

## Power

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PS1 | [300 W 20 A adjustable buck converter module with heatsinks (SZBK07 type)](https://a.co/d/0bQUYJnL) | 1 | 1 | 1 | 0 | $9.90 | $9.90 | — | Set to 6.3 V for the servo rail. |
| PS2 | [XL4015 5 A buck converter module with LED voltmeter](https://a.co/d/0e8PGeMC) | 1 | 6 | 1 | 5 | $12.99 | $12.99 | — | Set to 5.0 V for the logic rail. |
| BT1 | [2S 7.4 V 5200 mAh hard-case LiPo, XT60, 2-pack](https://a.co/d/0igi7Jwp) | 1 | 1 | 1 | 0 | $16.99 | $16.99 | — | ~138x47x25 mm, ~250 g each; check it fits the printed body. 2-pack gives a spare for swaps. |
| F1 | [Inline ATC blade fuse holder, 12 AWG, with 20/30/40 A fuses](https://a.co/d/01nNmfXO) | 1 | 4 | 1 | 3 | $6.98 | $6.98 | — | Use the 20 A fuse. |
| SW1 | [XT60 inline rocker main power switch, 30 A, with XT60 leads](https://a.co/d/0cqr6yiG) | 1 | 1 | 1 | 0 | $17.99 | $17.99 | — | Not anti-spark: the XT60 anti-spark modules found are for 3S-8S packs, not 2S. At 2S the connect spark is small. |
| R1,R2 | [1/4 W through-hole resistor kit incl. 100k and 47k (battery-sense divider)](https://www.amazon.com/dp/B008MH97I4) | 1 |  | 0 | **-1** | $9.95 | $0.00 | — | Skip if you already have 100k and 47k resistors. |
| | **Subtotal** | | | | | | **$64.85** | | |

## Audio

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U9 | [MAX98357A I2S class-D amplifier breakout](https://a.co/d/0bTKkGus) | 1 | 2 | 1 | 1 | $6.88 | $6.88 | — |  |
| LS1 | [3 W 4-ohm 40 mm speaker, 2-pack](https://a.co/d/0e7x7qMr) | 1 | 2 | 1 | 1 | $8.99 | $8.99 | — | Adafruit 3968 ($4.95) is out of stock. |
| | **Subtotal** | | | | | | **$15.87** | | |

## UI

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U5 | [SSD1306 0.96" 128x64 I2C OLED display module](https://a.co/d/0edxMXPg) | 1 | 3 | 1 | 2 | $9.99 | $9.99 | — |  |
| SW2 | [16 mm momentary metal push button with 5 V LED ring (mode button + power-on light)](https://a.co/d/0ga2wm9x) | 1 | 1 | 1 | 0 | $7.49 | $7.49 | — | Must be the 5 V LED version. Adafruit 481 ($4.95, 6 V LED) is out of stock. |
| | **Subtotal** | | | | | | **$17.48** | | |

## Harness

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | [Servo extension cable, 300 mm](https://a.co/d/07IDUnZi) | 4 | 15 | 1 | 11 | $7.99 | $7.99 | — | Amazon link is a 10-pack. |
| — | [14 AWG silicone wire, 20 ft red + 20 ft black](https://a.co/d/0hDzrqEY) | 10 | 20 | 1 | 10 | $9.88 | $9.88 | — | ~10ft needed |
| — | [22 AWG silicone wire kit, 6 colors](https://a.co/d/0he00ZIX) | 30 | 150 | 1 | 120 | $16.95 | $16.95 | — | ~20ft needed |
| — | [Amass XT60H connector pairs (male/female), 10 pairs](https://a.co/d/00SHROxq) | 1 | 10 | 1 | 9 | $9.99 | $9.99 | — |  |
| — | [Dupont jumper wire kit, 120 pcs (M-F, M-M, F-F)](https://www.amazon.com/dp/B01EV70C78) | 1 |  | 0 | **-1** | — | $0.00 | — |  |
| — | [WAGO 221 lever connector assortment (221-412/413/415), for power/ground distribution](https://a.co/d/06cyWtGx) | 4 | 8 | 0 | **-4** | $25.95 | $0.00 | — | Solder instead |
| — | [Heat shrink tubing assortment](https://a.co/d/0dZggJAK) | 1 | 1 | 1 | 0 | $7.99 | $7.99 | — |  |
| | **Subtotal** | | | | | | **$52.80** | | |

## Mechanical

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | [625ZZ deep groove ball bearings 5x16x5 mm, double shielded, 10-pack](https://a.co/d/0dtdLn0u) | 12 | 25 | 1 | 13 | $7.89 | $7.89 | — | Need 12 (REQUIREMENTS B-5). |
| — | [M2 x 8 mm socket head cap screws, stainless, 100-pack](https://a.co/d/00GUEqO6) | 84 | 100 | 1 | 16 | $7.99 | $7.99 | — | Need 84 (REQUIREMENTS B-5). |
| — | [M3 x 8 mm socket head cap screws, stainless, 100-pack](https://a.co/d/08k9iUNP) | 92 | 100 | 1 | 8 | $6.86 | $6.86 | — | Need 92 (REQUIREMENTS B-5). |
| — | [M3 x 20 mm socket head cap screws, stainless, 100-pack](https://a.co/d/05J76axt) | 64 | 100 | 1 | 36 | $6.99 | $6.99 | — | Need 64 (REQUIREMENTS B-5). |
| — | [M2 x 0.4 mm hex nuts, stainless, 100-pack](https://a.co/d/09dHX57F) | 84 | 100 | 1 | 16 | $7.99 | $7.99 | — | Need 84 (REQUIREMENTS B-5). |
| — | [M3 x 0.5 mm nylon insert lock nuts, 120-pack](https://a.co/d/06KlZL9m) | 156 | 100 | 2 | 44 | $5.69 | $11.38 | — | Need 156 (REQUIREMENTS B-5). |
| | **Subtotal** | | | | | | **$49.10** | | |

## Support

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | [ISDT PD60S 60 W balance charger, XT60, USB-C input](https://a.co/d/0cJyZKtr) | 1 | 1 | 1 | 0 | $17.98 | $17.98 | — | Needs a USB-C PD power supply (60 W for full rate). |
| — | [LiPo low-voltage checker/alarm, 1S-8S](https://a.co/d/0ifVDRqW) | 1 | 1 | 1 | 0 | $5.99 | $5.99 | — |  |
| — | [LiPo fireproof charging/storage bag, 2-pack](https://a.co/d/03SlpZyW) | 1 | 1 | 1 | 0 | $14.39 | $14.39 | — |  |
| | **Subtotal** | | | | | | **$38.36** | | |

## Future (not included in total)

| Ref | Item | Need | Per item | Order | Extras | Price | Line total | Have / Ordered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| — | [INMP441 I2S MEMS microphone module, 3-pack](https://a.co/d/0iWwmaVm) | 1 | 3 | 0 | -1 | $9.99 | $0.00 | — | X-2: offline voice commands (future); shares I2S BCLK/WS with the amp, data on GPIO40. |
| — | [TCA9548A I2C multiplexer breakout](https://a.co/d/06iKkjDw) | 1 | 10 | 0 | -1 | $9.99 | $0.00 | — | X-3: OLED eyes mux, address 0x71 via A0 (0x70 collides with the PCA9685 all-call). |
| — | [0.96" SSD1306 I2C OLED display, 2-pack (eyes)](https://www.amazon.com/dp/B0D5MB9VHK) | 1 |  | 0 | -1 | — | $0.00 | — | X-3: two eyes, both 0x3C, behind the TCA9548A mux. |
| — | [OV5640 5 MP camera module, 24-pin FPC, 160-degree](https://www.amazon.com/dp/B0BVHTFKQG) | 1 |  | 0 | -1 | — | $0.00 | — | X-6: camera upgrade; same 24-pin FPC as the bundled OV2640. |
