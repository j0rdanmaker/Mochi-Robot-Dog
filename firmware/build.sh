#!/usr/bin/env bash
# Builds the RobotDog firmware: upstream SpotMicroESP32-Leika (firmware/leika,
# a pinned git submodule, never edited in place) plus our overlay
# (firmware/overlay/platformio.ini), which defines the `robotdog` PlatformIO
# env. See docs/DESIGN.md Section 6 and REQUIREMENTS.md F-1/F-2.
#
# Usage: firmware/build.sh [extra pio args...]
#   firmware/build.sh              # build
#   firmware/build.sh -t upload    # build and upload
#   firmware/build.sh -t clean     # clean

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

submodule_dir="${repo_root}/firmware/leika"
overlay_conf="${repo_root}/firmware/overlay/platformio.ini"

if [ ! -f "${submodule_dir}/platformio.ini" ]; then
	echo "error: ${submodule_dir} is empty or missing." >&2
	echo "The firmware/leika submodule isn't checked out. Run:" >&2
	echo "  git submodule update --init --recursive" >&2
	exit 1
fi

exec uv run --project "${repo_root}" pio run -d "${submodule_dir}" -c "${overlay_conf}" -e robotdog "$@"
