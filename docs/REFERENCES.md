# References and Related Projects

This is a survey of SpotMicro derivatives and similar ESP32 quadrupeds, done
2026-09-26 to check whether a better-maintained base than
SpotMicroESP32-Leika exists. Stars and activity come from the GitHub API on
that date.

## Conclusion

**Keep SpotMicroESP32-Leika as the firmware base.**

- Its parts already printed (the KDY0523 / Kooba / robjk Spot Micro set) lock the mechanical platform to Spot Micro geometry.
- Among firmware that fits that geometry, Leika is the only one still maintained. It had about 100 commits in the last 12 months and 7 in the last 6, a slowing pace worth watching.
- Nobody else runs an ESP32 on the Spot Micro frame and is still active. The other ESP32 Spot Micro firmwares stopped between 2024 and early 2026.
- None of Leika's 26 forks has stars or diverges noticeably.
- The closest active alternative (TNY-360) needs different printed parts and modified servos.

## Spot Micro family (same mechanical platform)

| Project | Stars | Last push | License | Notes |
|---|---|---|---|---|
| [runeharlyk/SpotMicroESP32-Leika](https://github.com/runeharlyk/SpotMicroESP32-Leika) | 85 | 2026-08 | MIT | **Our base.** ESP32/ESP32-S3/P4, ESP-IDF, Svelte web UI, gaits, camera. Has Leika, Leika Mini, and Yertle kinematics. Pinned as `firmware/leika`. |
| [michaelkubina/SpotMicroESP32](https://github.com/michaelkubina/SpotMicroESP32) | 422 | 2024-11 | GPL-3.0 | Source of the "Kooba" support-free printable remix ([Thingiverse 4559827](https://www.thingiverse.com/thing:4559827)) that we printed from. Good assembly guide, BOM, and electronics notes. Its firmware is unfinished and inactive. |
| [maartenweyn/SpotMicro_ESP32](https://github.com/maartenweyn/SpotMicro_ESP32) | 47 | 2026-03 | Apache-2.0 | ESP-IDF firmware for the Kubina frame. No commits in the last 6 months. A community voice-command/gait branch was built on it. |
| Blacksheep909/SpotMicroESP32-Nitro-Fork | — | — | — | Fork linked from Kubina's README. Not checked in detail. |
| [mike4192/spotMicro](https://github.com/mike4192/spotMicro) | 2143 | 2021-03 | — | The best-known Spot Micro software (Raspberry Pi, ROS1). Inactive. A useful reference for gaits and calibration. |
| [FlorianWilk/SpotMicroAI](https://github.com/FlorianWilk/SpotMicroAI) | 453 | 2020-04 | — | Original SpotMicroAI community project and docs ([spotmicroai.readthedocs.io](https://spotmicroai.readthedocs.io)). Inactive. |
| [nicrusso7/rex-gym](https://github.com/nicrusso7/rex-gym) | 1104 | 2023-03 | — | Reinforcement-learning gym environments for Spot Micro. Relevant if we ever train gaits. |
| [chvmp/robots](https://github.com/chvmp/robots) (CHAMP) | 277 | 2024-08 | — | ROS quadruped framework with a Spot Micro config. |
| [KDY0523 original](https://www.thingiverse.com/thing:3445283) / [robjk reinforced shoulder](https://www.thingiverse.com/thing:4937631) | — | — | — | Printed parts we use, together with the Kooba remix. |

## Other ESP32 quadrupeds (different hardware, useful for ideas)

| Project | Stars | Last push | License | Why it's interesting / why not our base |
|---|---|---|---|---|
| [TNY-Robotics/TNY-360](https://github.com/TNY-Robotics/TNY-360) | 304 | 2026-09 (very active) | CC BY-NC-SA 4.0 | 12 servos on an ESP32-S3 with ESP-IDF, PCA9685, OV2640 camera, MPU6050, and a web UI: close to our electronics. Runs closed-loop at 200 Hz using MG996R servos modified for position feedback, on a 3S 18650 pack. **Its own frame and a non-commercial license.** Worth borrowing ideas from: dual-core control split, ESP-IDF drivers, ear servos. |
| [Jerome-Graves/yertle](https://github.com/Jerome-Graves/yertle) | 161 | 2026-09 (active) | MIT | Research quadruped (ESP32 plus an optional Raspberry Pi 4, ROS 2, reinforcement-learned gaits). Leika supports its kinematics. A different frame. |
| [dorianborian/sesame-robot](https://github.com/dorianborian/sesame-robot) | 4506 | 2026-09 (active) | Apache-2.0 | Popular mini quadruped: 8x MG90 servos, about $60. Too small to compare, but good for expressive-behavior and face-display ideas (see REQUIREMENTS X-3). |
| [PetoiCamp/OpenCatEsp32-Quadruped-Robot](https://github.com/PetoiCamp/OpenCatEsp32-Quadruped-Robot) | 431 | 2026-09 (active) | MIT | OpenCat framework on ESP32 (Petoi Bittle class, small). Mature skill/behavior system and voice-command support. Tied to Petoi boards. |
| [Freenove Robot Dog Kit for ESP32](https://github.com/Freenove/Freenove_Robot_Dog_Kit_for_ESP32) | 19 | 2026-09 | — | Commercial kit from the maker of our controller board. Small frame. |
| [waveshare/WAVEGO](https://github.com/waveshare/WAVEGO) | 42 | 2022-05 | — | 12-DOF ESP32 + Raspberry Pi dog. Inactive. |
| [SovGVD/esp32-robot-dog-code](https://github.com/SovGVD/esp32-robot-dog-code) | 153 | 2022-05 | — | ESP32 dog firmware. Inactive. |

## Things to borrow later

- **Ultrasonic in ESP-IDF:** we need an ESP-IDF one-pin driver to enable `USE_USS` (see DESIGN.md Section 6). Check TNY-360's and maartenweyn's ESP-IDF drivers before writing our own.
- **Voice commands (X-2):** the voice-command work on maartenweyn's firmware and OpenCat's voice module are prior art to compare with ESP-SR.
- **Eyes and face (X-3):** Sesame's expressive displays.
- **Assembly:** Kubina's assembly guide matches the printed parts.

Re-check this list before major firmware decisions (for example, if Leika development stalls).
