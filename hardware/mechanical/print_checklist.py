#!/usr/bin/env python3
"""Generate hardware/PRINT_CHECKLIST.md from hardware/mechanical/print_status.csv.

print_status.csv is a Google Sheets export (File -> Download -> Comma-separated
values) of the print status sheet's first tab, saved verbatim over this file.

Usage (from the repo root):
    uv run python hardware/mechanical/print_checklist.py            # write hardware/PRINT_CHECKLIST.md
    uv run python hardware/mechanical/print_checklist.py --check    # verify it is up to date (exit 1 if not)
    uv run python hardware/mechanical/print_checklist.py --pull     # download print_status.csv from the
                                                                     # print status sheet, then write the MD
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "print_status.csv"
MD_PATH = SCRIPT_DIR.parent / "PRINT_CHECKLIST.md"

# The print status sheet, link-shared read-only. First tab, exported as CSV.
PRINT_SHEET_ID = "1-Wo08JJC0JB-biMSTE-VE9PVILEnY6z2KyEfmW9u-KA"
SHEET_EDIT_URL = f"https://docs.google.com/spreadsheets/d/{PRINT_SHEET_ID}/edit"

STL_EXTENSIONS = (".stl", ".3mf")

REQUIRED_COLUMNS = [
    "Name",
    "normal copies",
    "mirrored copies",
    "total amount",
    "infill",
    "total weight",
    "Printed",
    "Done",
]


@dataclass
class Part:
    name: str
    total_amount: str
    weight_g: int | None  # None = template ("-" in the sheet)
    printed: str
    done: bool

    @property
    def in_build(self) -> bool:
        return self.weight_g is not None and self.printed != "x"


def load_parts(csv_path: Path) -> list[Part]:
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            print(
                f"error: {csv_path} is missing required column(s): {', '.join(missing)}",
                file=sys.stderr,
            )
            raise SystemExit(1)

        parts = []
        for row in reader:
            name = (row.get("Name") or "").strip()
            if not name:
                continue
            if not any((v or "").strip() for v in row.values()):
                continue

            weight_raw = (row.get("total weight") or "").strip()
            if weight_raw == "-":
                weight_g = None
            else:
                try:
                    weight_g = int(weight_raw.rstrip("g").strip())
                except ValueError:
                    print(
                        f"error: {csv_path}: bad 'total weight' in row "
                        f"{reader.line_num} ({name!r}): {weight_raw!r}",
                        file=sys.stderr,
                    )
                    raise SystemExit(1)

            parts.append(
                Part(
                    name=name,
                    total_amount=(row.get("total amount") or "").strip(),
                    weight_g=weight_g,
                    printed=(row.get("Printed") or "").strip(),
                    done=(row.get("Done") or "").strip().upper() == "TRUE",
                )
            )
    return parts


def escape_cell(text: str) -> str:
    # Names contain quotes and parentheses, which are safe in plain markdown text
    # and inside [brackets]; only "|" (table cell separator) needs escaping, and
    # this file has no tables, but keep this for consistency with bom.py/notes.
    return text.replace("|", "\\|")


def normalize(name: str) -> str:
    return name.lower().replace(" ", "_")


def find_model_file(name: str, mech_dir: Path) -> str | None:
    """Return the STL/3MF file name in mech_dir matching name, or None."""
    normalized = normalize(name)
    candidates = [
        p
        for p in mech_dir.iterdir()
        if p.suffix.lower() in STL_EXTENSIONS and p.stem.lower().startswith(normalized)
    ]
    if not candidates:
        return None
    # Prefer .stl over .3mf when a part matches more than one file.
    candidates.sort(key=lambda p: (p.suffix.lower() != ".stl", p.name))
    return candidates[0].name


def part_label(part: Part, mech_dir: Path) -> str:
    model_file = find_model_file(part.name, mech_dir)
    name = escape_cell(part.name)
    if model_file:
        return f"[{name}](mechanical/{model_file})"
    return name


def printed_text(part: Part) -> str:
    if part.printed == "?":
        return "printed: unknown"
    if "/" in part.printed:
        return f"{part.printed} printed"
    return f"{part.printed}/{part.total_amount} printed"


def render(parts: list[Part], mech_dir: Path) -> str:
    build = [p for p in parts if p.in_build]
    not_needed = [p for p in parts if not p.in_build]
    to_print = [p for p in build if not p.done]
    done = [p for p in build if p.done]

    total_g = sum(p.weight_g for p in build)
    done_g = sum(p.weight_g for p in done)

    lines: list[str] = []
    lines.append("# Print checklist")
    lines.append("")
    lines.append(
        "<!-- Generated from print_status.csv (a Google Sheets export) by "
        "print_checklist.py; do not edit by hand. Regenerate with: "
        "uv run python hardware/mechanical/print_checklist.py. "
        f"Sheet: {SHEET_EDIT_URL} -->"
    )
    lines.append("")
    lines.append(
        f"**{len(done)} / {len(build)} parts done** &mdash; "
        f"**{done_g} g / {total_g} g** printed."
    )
    lines.append("")

    lines.append("## To print")
    lines.append("")
    if to_print:
        for p in to_print:
            lines.append(
                f"- [ ] {part_label(p, mech_dir)}: {printed_text(p)}, {p.weight_g} g"
            )
    else:
        lines.append("Nothing left to print.")
    lines.append("")

    lines.append("## Done")
    lines.append("")
    if done:
        for p in done:
            lines.append(
                f"- [x] {part_label(p, mech_dir)}: {printed_text(p)}, {p.weight_g} g"
            )
    else:
        lines.append("Nothing done yet.")
    lines.append("")

    lines.append("## Not needed")
    lines.append("")
    if not_needed:
        for p in not_needed:
            lines.append(f"- {escape_cell(p.name)}")
    else:
        lines.append("None.")
    lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


def pull_csv(sheet_id: str, dest: Path, *, timeout: float = 30.0) -> int:
    """Download sheet_id's first tab as CSV to dest, verbatim, and return the row count.

    Writes to a temp file in dest's directory and os.replace()s it over dest, so a
    failed download never touches the existing file. Raises RuntimeError with a
    human-readable message on any failure (bad status, wrong content type, or a
    network error).
    """
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            status = resp.status
            content_type = resp.headers.get_content_type()
            data = resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"download failed: HTTP {e.code} (is the sheet link-shared?)") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"download failed: {e.reason}") from e

    if status != 200:
        raise RuntimeError(f"download failed: HTTP {status} (is the sheet link-shared?)")
    if content_type != "text/csv":
        raise RuntimeError(
            f"download failed: got content type {content_type!r} instead of text/csv "
            "(sheet not link-shared, or Google returned a sign-in page)"
        )

    row_count = max(0, sum(1 for _ in csv.reader(data.decode("utf-8-sig").splitlines())) - 1)

    fd, tmp_name = tempfile.mkstemp(dir=dest.parent, prefix=dest.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp_name, dest)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise

    return row_count


def main(argv: list[str]) -> int:
    check = "--check" in argv
    pull = "--pull" in argv

    if pull and check:
        print("error: --pull and --check cannot be used together", file=sys.stderr)
        return 1

    if pull:
        try:
            row_count = pull_csv(PRINT_SHEET_ID, CSV_PATH)
        except RuntimeError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(f"pulled {CSV_PATH} ({row_count} rows)", file=sys.stderr)

    parts = load_parts(CSV_PATH)
    generated = render(parts, SCRIPT_DIR)

    if check:
        if not MD_PATH.exists():
            print(f"error: {MD_PATH} does not exist; run without --check to generate it", file=sys.stderr)
            return 1
        current = MD_PATH.read_text(encoding="utf-8")
        if current != generated:
            print(
                f"error: {MD_PATH} is out of date; run: "
                "uv run python hardware/mechanical/print_checklist.py",
                file=sys.stderr,
            )
            return 1
        return 0

    MD_PATH.write_text(generated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
