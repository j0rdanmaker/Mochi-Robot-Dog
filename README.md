# RobotDog

A hobby quadruped robot based on
[SpotMicroESP32-Leika](https://github.com/runeharlyk/SpotMicroESP32-Leika)
("Leika" kinematics), running on an ESP32-S3 controller board.

- What it must do and the constraints it's built under: [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)
- How it meets those requirements (parts, wiring, pinout, firmware): [docs/DESIGN.md](docs/DESIGN.md)
- Related projects and why we use Leika: [docs/REFERENCES.md](docs/REFERENCES.md)
- Bill of materials: [hardware/parts/BOM.md](hardware/parts/BOM.md) (generated from [hardware/parts/RobotDog_BOM.csv](hardware/parts/RobotDog_BOM.csv), exported from the [BOM sheet](https://docs.google.com/spreadsheets/d/1W_0snJxdW7laQxYUCTcuxIuaCKTvFyqEI8m0nG-FkIU/edit), view-only link)
- Weight estimate, servo torque check, and run time estimate: [hardware/parts/SERVO_CHECK.md](hardware/parts/SERVO_CHECK.md)
- Wiring diagrams (WireViz source + rendered output): [hardware/wiring/](hardware/wiring/)
- Print checklist: [hardware/PRINT_CHECKLIST.md](hardware/PRINT_CHECKLIST.md) (generated from [hardware/mechanical/print_status.csv](hardware/mechanical/print_status.csv), exported from the print status sheet below)
- 3D print status (Google Sheet, view-only link): [print status](https://docs.google.com/spreadsheets/d/1-Wo08JJC0JB-biMSTE-VE9PVILEnY6z2KyEfmW9u-KA/edit)
- Firmware (upstream submodule + our overlay): [firmware/](firmware/)

## Repo layout

```
docs/                   Requirements and design docs
hardware/
  parts/
    RobotDog_BOM.csv     Bill of materials (Google Sheets export, source of truth)
    BOM.md               Readable bill of materials, generated from RobotDog_BOM.csv
    bom.py               Generates BOM.md from RobotDog_BOM.csv
    servo_check.py       Weight, servo torque, and run time estimates -> SERVO_CHECK.md
  mechanical/            Mechanical drawings (REQUIREMENTS.md X-8)
    print_status.csv     3D print status (Google Sheets export, source of truth)
    print_checklist.py   Generates ../PRINT_CHECKLIST.md from print_status.csv
  PRINT_CHECKLIST.md     Readable print checklist, generated from mechanical/print_status.csv
  wiring/                WireViz diagrams: source/ (YAML) and output/ (rendered)
firmware/
  leika/                 Upstream SpotMicroESP32-Leika firmware (git submodule, never edited)
  overlay/               Our PlatformIO overlay (board env, pins, feature flags)
  build.sh               Builds firmware/leika using the overlay config
```

## Bill of materials

The BOM is maintained in a [Google Sheet](https://docs.google.com/spreadsheets/d/1W_0snJxdW7laQxYUCTcuxIuaCKTvFyqEI8m0nG-FkIU/edit);
`hardware/parts/RobotDog_BOM.csv` is its export. To update it:

1. Edit the sheet.
2. Pull the export and regenerate the readable version:
   `uv run python hardware/parts/bom.py --pull`.
   (Fallback if the sheet isn't link-shared: File -> Download -> Comma-separated
   values, save the download over `hardware/parts/RobotDog_BOM.csv`, then run
   `uv run python hardware/parts/bom.py`.)
3. Commit both `hardware/parts/RobotDog_BOM.csv` and `hardware/parts/BOM.md`.

## Quick start

```sh
git lfs install                            # once per machine; images and 3D models are stored in Git LFS
uv sync                                    # install Python tooling (WireViz, PlatformIO)
make -C hardware/wiring                    # render the wiring diagrams
git submodule update --init --recursive    # fetch the upstream firmware submodule (and its own submodules)
firmware/build.sh                          # build the firmware
```

`firmware/build.sh` passes extra arguments through to PlatformIO, e.g.
`firmware/build.sh -t upload`.

<img width="336" height="272" alt="image" src="https://github.com/user-attachments/assets/1aa0d4c3-1f10-4047-88b7-cb7a0cd4448a" />
