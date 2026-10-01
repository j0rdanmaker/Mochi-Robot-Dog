#!/usr/bin/env python3
"""Estimate RobotDog's weight, check the leg servos can carry it, and estimate run time.

Writes SERVO_CHECK.md next to this script. Edit the MASSES table below when
real weights are known (weigh the printed parts and battery on a kitchen
scale) and re-run.

Usage (from the repo root):
    uv run python hardware/parts/servo_check.py            # write SERVO_CHECK.md
    uv run python hardware/parts/servo_check.py --check    # verify it is up to date

Model: static load only. Each stance foot takes an equal share of the weight
as a vertical force; joint torque = force x horizontal lever arm from the
joint to the foot. Leg masses, friction, and acceleration are ignored, so
real peak torques are higher - hence the margin thresholds below.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MD_PATH = SCRIPT_DIR / "SERVO_CHECK.md"

G = 9.81

# (item, grams, source). "est." = typical listing weight, not measured.
MASSES = [
    ("Servos DS3225MG x4 (shoulders)", 4 * 60, "60 g each, DS3225MG spec"),
    ("Servos DS3235 x8 (hips, knees)", 8 * 60, "60 g each, DS3235 datasheet"),
    ("Servo horns (metal, 25T) x12", 12 * 6, "est. 6 g each"),
    ("Printed parts (Spot Micro set)", 1089, "slicer weights from the print-status sheet (35 parts in the build)"),
    ("Battery 2S 5200 mAh hard case", 270, "est. 250-300 g"),
    ("Bearings 625ZZ x12", 12 * 4.8, "4.8 g each"),
    ("Screws M2x8 x84", 84 * 0.3, "est. 0.3 g each"),
    ("Screws M3x8 x92", 92 * 0.7, "est. 0.7 g each"),
    ("Screws M3x20 x64", 64 * 1.3, "est. 1.3 g each"),
    ("Nuts M2 x84", 84 * 0.1, "est. 0.1 g each"),
    ("Lock nuts M3 x156", 156 * 0.55, "est. 0.55 g each"),
    ("Buck converter SZBK07 (servo rail)", 65, "est., with heatsinks"),
    ("Buck converter XL4015 (logic rail)", 25, "est."),
    ("ESP32-S3 CAM + camera", 15, "est."),
    ("PCA9685, GY-87, PAJ7620, OLED, amp", 26, "est."),
    ("HC-SR04P x2", 18, "est. 9 g each"),
    ("Speaker 40 mm", 15, "est."),
    ("Fuse holder, XT60 switch, mode button", 47, "est."),
    ("Wiring, connectors, lever nuts, heat shrink", 120, "est."),
]

# Leg geometry, from firmware/leika/esp32/include/kinematics.h (SPOTMICRO_ESP32).
COXA = 0.0605  # m, lateral offset from the shoulder roll axis to the leg plane
FEMUR = 0.1112  # m
TIBIA = 0.1185  # m
REACH = FEMUR + TIBIA - 0.010  # max_leg_reach (coxa_offset = 10 mm)
H_MIN = REACH * 0.45
H_MAX = REACH * 0.9
H_DEFAULT = H_MIN + (H_MAX - H_MIN) / 2
MAX_STEP = REACH * 0.8  # full stride at full stick; the foot moves +-MAX_STEP/2

RAIL_V = 6.3  # servo rail (PS1)


def interp(v: float, v0: float, t0: float, v1: float, t1: float) -> float:
    return t0 + (v - v0) / (v1 - v0) * (t1 - t0)


# Stall torque at the rail voltage, kg-cm.
# DS3225MG: 21 kg-cm @ 5 V, 25 kg-cm @ 6.8 V.
# DS3235 (5-7.4 V coreless, not the SG/HV version): 32 kg-cm @ 6 V, 35 kg-cm @ 7.4 V.
SERVOS = {
    "DS3225MG": interp(RAIL_V, 5.0, 21, 6.8, 25),
    "DS3235": interp(RAIL_V, 6.0, 32, 7.4, 35),
}
JOINT_SERVO = {"Shoulder": "DS3225MG", "Hip": "DS3235", "Knee": "DS3235"}

# Stall and idle current at the rail voltage, A.
# DS3225MG: stall 1.9 A @ 5 V, 2.3 A @ 6.8 V; idle 5 mA.
# DS3235: stall 2.1 A @ 6 V, 2.3 A @ 7.4 V; idle 5 mA.
STALL_A = {
    "DS3225MG": interp(RAIL_V, 5.0, 1.9, 6.8, 2.3),
    "DS3235": interp(RAIL_V, 6.0, 2.1, 7.4, 2.3),
}
IDLE_A = 0.005

# Power budget. Battery: 2S LiPo 5200 mAh (BT1), 80% usable to protect the pack.
BATTERY_WH = 2 * 3.7 * 5.2
USABLE = 0.8
SERVO_BUCK_EFF = 0.90  # SZBK07 at a few amps (est.)
LOGIC_BUCK_EFF = 0.85  # XL4015 at light load (est.)
# 5 V logic rail, W (est.): ESP32-S3 with Wi-Fi + camera streaming ~1.5 W,
# PCA9685/IMU/gesture/OLED/ultrasonics ~0.3 W, amp idle + button LED ~0.2 W.
LOGIC_W = 2.0
# Walking: accelerating the legs and dynamic foot loads on top of the static
# weight. Swing legs carry only their own weight; assume 10% of stall for moving.
WALK_DYNAMIC = 1.5
SWING_SHARE = 0.10

# Share of stall torque used under static load: hobby servos run cool and last
# at <= 1/3; up to 1/2 works but runs hot; above that expect stalls and
# brownouts once walking dynamics (about 1.5-2x static) are added.
OK_SHARE = 1 / 3
MARGINAL_SHARE = 1 / 2

# (name, stance feet, body height, foot fore/aft offset from the hip)
CASES = [
    ("Standing, 4 feet, default height", 4, H_DEFAULT, 0.0),
    ("Standing, 4 feet, lowest crouch", 4, H_MIN, 0.0),
    ("Crawl gait, 3 feet, default height", 3, H_DEFAULT, 0.0),
    ("Trot, 2 feet, default height, foot under hip", 2, H_DEFAULT, 0.0),
    ("Trot, 2 feet, default height, half stride", 2, H_DEFAULT, MAX_STEP / 4),
    ("Trot, 2 feet, default height, full stride", 2, H_DEFAULT, MAX_STEP / 2),
    ("Trot, 2 feet, low height, half stride", 2, H_MIN + 0.02, MAX_STEP / 4),
]


def nm_to_kgcm(nm: float) -> float:
    return nm / G * 100


def leg_levers(h: float, x: float) -> tuple[float, float]:
    """Horizontal lever arms (m) at the hip-pitch and knee joints.

    Hip at the origin, foot at (x, -h). Both knee solutions are tried and the
    worse one kept, since the knee direction depends on the leg build.
    """
    d = math.hypot(x, h)
    if d > FEMUR + TIBIA or d < abs(FEMUR - TIBIA):
        raise ValueError(f"foot out of reach: h={h:.3f} x={x:.3f}")
    foot_angle = math.atan2(-h, x)
    alpha = math.acos((FEMUR**2 + d**2 - TIBIA**2) / (2 * FEMUR * d))
    knee = max(
        abs(x - FEMUR * math.cos(foot_angle + s * alpha)) for s in (1, -1)
    )
    return abs(x), knee


def verdict(share: float) -> str:
    if share <= OK_SHARE:
        return "OK"
    if share <= MARGINAL_SHARE:
        return "marginal"
    return "**too high**"


def render() -> str:
    total_g = sum(g for _, g, _ in MASSES)
    weight_n = total_g / 1000 * G
    out = [
        "# Weight estimate and servo check",
        "",
        "<!-- Generated by servo_check.py; do not edit by hand. "
        "Regenerate with: uv run python hardware/parts/servo_check.py -->",
        "",
        "## Weight estimate",
        "",
        "| Item | Mass | Source |",
        "| --- | --- | --- |",
    ]
    for name, g, src in MASSES:
        out.append(f"| {name} | {g:.0f} g | {src} |")
    out += [
        f"| **Total** | **{total_g:.0f} g** | |",
        "",
        "## Load model",
        "",
        f"- Geometry (Leika `SPOTMICRO_ESP32`): coxa {COXA * 1000:.1f} mm, femur "
        f"{FEMUR * 1000:.1f} mm, tibia {TIBIA * 1000:.1f} mm. Body height "
        f"{H_MIN * 1000:.0f}-{H_MAX * 1000:.0f} mm, default {H_DEFAULT * 1000:.0f} mm. "
        f"Full stride {MAX_STEP * 1000:.0f} mm.",
        "- Servos (stall torque interpolated to the "
        f"{RAIL_V} V servo rail): "
        + "; ".join(
            f"{joint.lower()} {name} {SERVOS[name]:.1f} kg-cm"
            for joint, name in JOINT_SERVO.items()
        )
        + ".",
        "- Static load only: weight split evenly over the stance feet, torque = "
        "force x horizontal lever arm. Walking adds roughly 1.5-2x on top.",
        f"- Verdict per joint as a share of stall: OK <= {OK_SHARE:.0%}, marginal "
        f"<= {MARGINAL_SHARE:.0%}, above that too high.",
        "",
        "## Joint torques",
        "",
        "| Case | Foot force | "
        + " | ".join(f"{j} ({n})" for j, n in JOINT_SERVO.items())
        + " |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, feet, h, x in CASES:
        f = weight_n / feet
        hip_lever, knee_lever = leg_levers(h, x)
        cells = []
        for joint, lever in zip(JOINT_SERVO, (COXA, hip_lever, knee_lever)):
            kgcm = nm_to_kgcm(f * lever)
            share = kgcm / SERVOS[JOINT_SERVO[joint]]
            cells.append(f"{kgcm:.1f} kg-cm ({share:.0%}) {verdict(share)}")
        out.append(f"| {name} | {f:.1f} N | " + " | ".join(cells) + " |")

    # Weight at which the trot, default height, half stride knee hits each threshold.
    f_per_kg = G / 2
    _, knee_lever = leg_levers(H_DEFAULT, MAX_STEP / 4)
    knee_per_kg = nm_to_kgcm(f_per_kg * knee_lever)
    knee_stall = SERVOS[JOINT_SERVO["Knee"]]
    ok_kg = OK_SHARE * knee_stall / knee_per_kg
    marginal_kg = MARGINAL_SHARE * knee_stall / knee_per_kg
    out += [
        "",
        "## Weight budget",
        "",
        "For the typical walking case (trot, default height, half stride), the knee "
        f"stays OK up to **{ok_kg:.2f} kg** and marginal up to **{marginal_kg:.2f} kg** "
        f"total robot weight. Current estimate: **{total_g / 1000:.2f} kg**.",
        "",
    ]
    out += runtime_section(weight_n)
    return "\n".join(out)


def leg_current(foot_force: float, h: float, x: float, factor: float = 1.0) -> float:
    """Current (A) drawn by one leg's three servos holding a vertical foot force."""
    hip_lever, knee_lever = leg_levers(h, x)
    amps = 0.0
    for joint, lever in zip(JOINT_SERVO, (COXA, hip_lever, knee_lever)):
        servo = JOINT_SERVO[joint]
        share = min(1.0, factor * nm_to_kgcm(foot_force * lever) / SERVOS[servo])
        amps += IDLE_A + share * STALL_A[servo]
    return amps


def runtime_section(weight_n: float) -> list[str]:
    usable_wh = BATTERY_WH * USABLE
    swing_a = sum(IDLE_A + SWING_SHARE * STALL_A[s] for s in JOINT_SERVO.values())
    # Trot (duty 0.75, diagonal pairs half a cycle apart): all 4 feet down for
    # half the cycle, 2 feet down (other 2 swinging) for the other half.
    half = MAX_STEP / 4
    trot_a = 0.5 * 4 * leg_current(weight_n / 4, H_DEFAULT, half, WALK_DYNAMIC) + 0.5 * (
        2 * leg_current(weight_n / 2, H_DEFAULT, half, WALK_DYNAMIC) + 2 * swing_a
    )
    modes = [
        ("Resting (lying down, servos powered, no load)", 12 * IDLE_A),
        ("Standing still, default height", 4 * leg_current(weight_n / 4, H_DEFAULT, 0.0)),
        ("Trot, default height, half stride (x1.5 dynamics)", trot_a),
    ]
    out = [
        "## Run time estimate",
        "",
        f"- Battery: 2S 5200 mAh = {BATTERY_WH:.1f} Wh, {USABLE:.0%} usable = "
        f"{usable_wh:.1f} Wh.",
        f"- Servo current: idle {IDLE_A * 1000:.0f} mA + (share of stall torque) x stall "
        "current; stall at the rail: "
        + ", ".join(f"{n} {a:.2f} A" for n, a in STALL_A.items())
        + ".",
        f"- Logic rail: {LOGIC_W:.1f} W (est.) through the XL4015 at "
        f"{LOGIC_BUCK_EFF:.0%}; servo rail through the SZBK07 at {SERVO_BUCK_EFF:.0%}.",
        f"- Walking: static load x{WALK_DYNAMIC} for dynamics; swinging legs at "
        f"{SWING_SHARE:.0%} of stall.",
        "",
        "| Mode | Servo rail | Battery draw | Run time |",
        "| --- | --- | --- | --- |",
    ]
    for name, amps in modes:
        servo_w = amps * RAIL_V
        battery_w = servo_w / SERVO_BUCK_EFF + LOGIC_W / LOGIC_BUCK_EFF
        minutes = usable_wh / battery_w * 60
        runtime = f"{minutes / 60:.1f} h" if minutes >= 120 else f"{minutes:.0f} min"
        out.append(
            f"| {name} | {amps:.2f} A ({servo_w:.1f} W) | {battery_w:.1f} W | {runtime} |"
        )
    out += [
        "",
        "Treat these as rough: real servo draw depends on gait speed, terrain, and "
        "how hard the servos fight each other. Measure with a USB/XT60 power meter "
        "once built.",
        "",
    ]
    return out


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        if not MD_PATH.exists() or MD_PATH.read_text(encoding="utf-8") != text:
            print(f"error: {MD_PATH} is out of date; run: uv run python hardware/parts/servo_check.py", file=sys.stderr)
            return 1
        return 0
    MD_PATH.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
