#!/usr/bin/env python3
"""Add a non-intrusive ownership footer to generated Allure HTML pages."""

from __future__ import annotations

import sys
from pathlib import Path

OWNER_TEXT = "Prepared by Muhamad Suryana | Public portfolio / educational reference"
MARKER = "owner-footer-marker"


def add_footer_to_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False

    footer = f"""
    <div id="{MARKER}" style="position:fixed;left:0;right:0;bottom:0;z-index:9999;padding:8px 14px;font-size:12px;line-height:1.4;text-align:center;color:#e5e7eb;background:rgba(15,23,42,0.88);border-top:1px solid rgba(148,163,184,0.45);font-family:Arial,Helvetica,sans-serif;letter-spacing:0.02em;">
      {OWNER_TEXT}
    </div>
    """

    if "</body>" in text:
        updated = text.replace("</body>", f"{footer}\n</body>", 1)
    else:
        updated = text + footer

    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: add_owner_footer.py <report_dir>", file=sys.stderr)
        return 1

    report_dir = Path(sys.argv[1]).resolve()
    if not report_dir.exists():
        print(f"Report directory not found: {report_dir}", file=sys.stderr)
        return 1

    changed = 0
    for html_file in sorted(report_dir.rglob("*.html")):
        if add_footer_to_html(html_file):
            changed += 1

    print(f"Updated {changed} HTML files with owner footer in {report_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
