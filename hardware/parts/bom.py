#!/usr/bin/env python3
"""Generate hardware/parts/BOM.md from hardware/parts/RobotDog_BOM.csv.

RobotDog_BOM.csv is a Google Sheets export (File -> Download -> Comma-separated
values), saved verbatim over this file. Sheets exports can vary a little in
header names, CRLF line endings, and a leading UTF-8 BOM, so this script reads
columns by name and tolerates both the legacy and current header layouts.

Usage (from the repo root):
    uv run python hardware/parts/bom.py            # write hardware/parts/BOM.md
    uv run python hardware/parts/bom.py --check    # verify BOM.md is up to date (exit 1 if not)
    uv run python hardware/parts/bom.py --pull     # download RobotDog_BOM.csv from the
                                                    # BOM sheet, then write BOM.md
"""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote_plus

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "RobotDog_BOM.csv"
MD_PATH = SCRIPT_DIR / "BOM.md"

# The BOM sheet, link-shared read-only. First tab, exported as CSV.
BOM_SHEET_ID = "1W_0snJxdW7laQxYUCTcuxIuaCKTvFyqEI8m0nG-FkIU"

FUTURE_CATEGORY = "Future"
ESTIMATED_MARKER = "(est.)"

# Column names that have changed between the legacy hand-edited CSV and the
# current Google Sheets export. Each entry lists acceptable header names in
# preference order.
LINK_COLUMNS = ["Link", "Link to Item", "Amazon Link"]
PRICE_COLUMNS = ["Unit Price (USD)", "$/Item"]
# "Qty To Order" is the number of listings (packs) to buy; "$/Item" is the
# price per listing. "Qty Needed" (units the robot uses) and "Qty In Item"
# (units per listing) are shown when present, and so is "Extras" (units left
# over after the order; negative = short). The sheet's "Total Price" column is
# ignored and recomputed.
QTY_COLUMNS = ["Qty To Order", "Qty"]
REQUIRED_SIMPLE_COLUMNS = ["Category", "Description"]


@dataclass
class Item:
    ref: str
    category: str
    description: str
    part_number: str
    link: str
    amazon_link: str
    already_have: str
    ordered: str
    unit_price: Decimal | None  # None = no price in the sheet yet
    qty: int  # listings to order
    qty_needed: str
    qty_per_item: str
    extras: str
    estimated: bool
    notes: str

    @property
    def line_total(self) -> Decimal:
        return (self.unit_price or Decimal("0")) * self.qty

    @property
    def short(self) -> bool:
        """Ordering leaves fewer units than needed, and none are on hand."""
        try:
            extras = int(self.extras)
        except ValueError:
            return False
        return extras < 0 and self.already_have.lower() != "yes"

    @property
    def unpriced(self) -> bool:
        return self.unit_price is None and self.qty > 0


def _find_column(fieldnames: list[str], candidates: list[str]) -> str | None:
    for name in candidates:
        if name in fieldnames:
            return name
    return None


def _parse_money(raw: str) -> Decimal | None:
    text = (raw or "").strip().replace("$", "").replace(",", "").strip()
    if not text:
        return None
    return Decimal(text)


def load_items(csv_path: Path) -> list[Item]:
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        link_col = _find_column(fieldnames, LINK_COLUMNS)
        price_col = _find_column(fieldnames, PRICE_COLUMNS)
        qty_col = _find_column(fieldnames, QTY_COLUMNS)
        has_estimated_col = "Estimated" in fieldnames

        missing = [c for c in REQUIRED_SIMPLE_COLUMNS if c not in fieldnames]
        if link_col is None:
            missing.append("/".join(LINK_COLUMNS))
        if price_col is None:
            missing.append("/".join(PRICE_COLUMNS))
        if qty_col is None:
            missing.append("/".join(QTY_COLUMNS))
        if missing:
            print(
                f"error: {csv_path} is missing required column(s): {', '.join(missing)}",
                file=sys.stderr,
            )
            raise SystemExit(1)

        items = []
        for row in reader:
            category = (row.get("Category") or "").strip()
            description = (row.get("Description") or "").strip()
            # Skip the old TOTAL row and any fully blank rows.
            if not category:
                continue
            if not any((v or "").strip() for v in row.values()):
                continue

            notes = (row.get("Notes") or "").strip()
            if has_estimated_col:
                estimated = (row.get("Estimated") or "").strip().lower() == "yes"
            else:
                estimated = ESTIMATED_MARKER in notes
                if estimated:
                    notes = notes.replace(ESTIMATED_MARKER, "").strip()
                    notes = " ".join(notes.split()) if notes else ""

            try:
                qty = int((row.get(qty_col) or "0").strip())
                unit_price = _parse_money(row.get(price_col, ""))
            except (ValueError, InvalidOperation):
                print(
                    f"error: {csv_path}: bad Qty or price in row "
                    f"{reader.line_num} ({description!r})",
                    file=sys.stderr,
                )
                raise SystemExit(1)

            items.append(
                Item(
                    ref=(row.get("Ref") or "").strip(),
                    category=category,
                    description=description,
                    part_number=(row.get("Part Number") or "").strip(),
                    link=(row.get(link_col) or "").strip(),
                    amazon_link=(row.get("Amazon Link") or "").strip(),
                    already_have=(row.get("Already Have") or "").strip(),
                    ordered=(row.get("Ordered") or "").strip(),
                    unit_price=unit_price,
                    qty=qty,
                    qty_needed=(row.get("Qty Needed") or "").strip(),
                    qty_per_item=(row.get("Qty In Item") or "").strip(),
                    extras=(row.get("Extras") or "").strip(),
                    estimated=estimated,
                    notes=notes,
                )
            )
    return items


def escape_cell(text: str) -> str:
    return text.replace("|", "\\|")


def format_money(amount: Decimal) -> str:
    return f"${amount:.2f}"


def part_cell(item: Item) -> str:
    """The item name (part number, or the description if the sheet has none), linked."""
    part = escape_cell(item.part_number or item.description)
    link = item.link
    if link.startswith("http"):
        cell = f"[{part}]({link})"
        if item.amazon_link and item.amazon_link != link:
            cell += f" ([Amazon]({item.amazon_link}))"
        return cell
    if link.startswith("Search: "):
        query = link[len("Search: ") :]
        url = f"https://www.amazon.com/s?k={quote_plus(query)}"
        return f"[{part}]({url})"
    if item.amazon_link and item.amazon_link != link:
        part += f" ([Amazon]({item.amazon_link}))"
    return part


def unit_cell(item: Item) -> str:
    if item.unit_price is None:
        return "—"
    text = format_money(item.unit_price)
    if item.estimated:
        text += " (est.)"
    return text


def have_ordered_cell(item: Item) -> str:
    if item.already_have.lower() == "yes":
        return "Have"
    if item.ordered.lower() == "yes":
        return "Ordered"
    return "—"


def first_appearance_categories(items: list[Item]) -> list[str]:
    seen: list[str] = []
    for item in items:
        if item.category not in seen:
            seen.append(item.category)
    return seen


def render(items: list[Item]) -> str:
    categories = first_appearance_categories(items)
    non_future_categories = [c for c in categories if c != FUTURE_CATEGORY]

    by_category: dict[str, list[Item]] = {c: [] for c in categories}
    for item in items:
        by_category[item.category].append(item)

    subtotals = {
        c: sum((i.line_total for i in by_category[c]), Decimal("0"))
        for c in categories
    }
    grand_total = sum(
        (subtotals[c] for c in non_future_categories), Decimal("0")
    )

    lines: list[str] = []
    lines.append("# RobotDog Bill of Materials")
    lines.append("")
    lines.append(
        "<!-- Generated from RobotDog_BOM.csv (a Google Sheets export) by bom.py; "
        "do not edit by hand. Regenerate with: uv run python hardware/parts/bom.py -->"
    )
    lines.append("")
    lines.append("| Category | Items | Subtotal |")
    lines.append("| --- | --- | --- |")
    for c in non_future_categories:
        lines.append(
            f"| {escape_cell(c)} | {len(by_category[c])} | {format_money(subtotals[c])} |"
        )
    lines.append(f"| **Total** | | **{format_money(grand_total)}** |")
    lines.append("")
    lines.append("Future items are excluded from the total above.")
    unpriced = [i for c in non_future_categories for i in by_category[c] if i.unpriced]
    if unpriced:
        lines.append("")
        lines.append(
            f"**{len(unpriced)} items have no price yet** (shown as —) and are not "
            "in the totals; fill in `$/Item` in the sheet."
        )
    short = [i for c in non_future_categories for i in by_category[c] if i.short]
    if short:
        lines.append("")
        lines.append(
            "**Short** (Extras below 0 and not marked Already Have): "
            + "; ".join(escape_cell(i.description) for i in short)
            + "."
        )
    lines.append("")

    for c in categories:
        if c == FUTURE_CATEGORY:
            lines.append(f"## {FUTURE_CATEGORY} (not included in total)")
        else:
            lines.append(f"## {c}")
        lines.append("")
        lines.append(
            "| Ref | Item | Need | Per item | Order | Extras | Price | Line total "
            "| Have / Ordered | Notes |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for item in by_category[c]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        escape_cell(item.ref),
                        part_cell(item),
                        escape_cell(item.qty_needed),
                        escape_cell(item.qty_per_item),
                        str(item.qty),
                        ("**" + item.extras + "**") if item.short and c != FUTURE_CATEGORY else escape_cell(item.extras),
                        unit_cell(item),
                        "—" if item.unpriced else format_money(item.line_total),
                        have_ordered_cell(item),
                        escape_cell(item.notes),
                    ]
                )
                + " |"
            )
        if c != FUTURE_CATEGORY:
            lines.append(
                "| | **Subtotal** | | | | | | **"
                + format_money(subtotals[c])
                + "** | | |"
            )
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
            row_count = pull_csv(BOM_SHEET_ID, CSV_PATH)
        except RuntimeError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(f"pulled {CSV_PATH} ({row_count} rows)", file=sys.stderr)

    items = load_items(CSV_PATH)
    generated = render(items)

    if check:
        if not MD_PATH.exists():
            print(f"error: {MD_PATH} does not exist; run without --check to generate it", file=sys.stderr)
            return 1
        current = MD_PATH.read_text(encoding="utf-8")
        if current != generated:
            print(f"error: {MD_PATH} is out of date; run: uv run python hardware/parts/bom.py", file=sys.stderr)
            return 1
        return 0

    MD_PATH.write_text(generated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
