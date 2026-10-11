#!/usr/bin/env python3
"""Convert BBotF's six core research templates to native WodTeX LaTeX.

This is an optional *example pipeline*; it does not modify the manuscript and
is not the general Markdown ingestion interface for WodTeX.
Requires the separately installed `pandoc` command.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
CORE = (
    "rote", "wonder", "practice", "node", "grimoire-or-black-book", "labyrinth-chantry"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("templates", type=Path, help="Path to BBotF's top-level templates/ directory")
    parser.add_argument("--out", type=Path, default=HERE / "generated", help="Destination for generated .tex fragments")
    parser.add_argument("--all", action="store_true", help="Also convert all 15 supporting templates")
    args = parser.parse_args()
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        parser.error("pandoc is required; WodTeX itself does not parse Markdown")
    templates = args.templates.expanduser().resolve()
    source = templates / "01-core"
    out = args.out.expanduser().resolve()
    if not source.is_dir():
        parser.error(f"Expected BBotF templates/01-core directory: {source}")
    out.mkdir(parents=True, exist_ok=True)

    input_files = [source / (name + ".md") for name in CORE]
    if args.all:
        supporting = templates / "02-supporting"
        if not supporting.is_dir():
            parser.error(f"Expected supporting templates directory: {supporting}")
        input_files += sorted(supporting.glob("*.md"))

    fragments = []
    for src in input_files:
        name = src.stem
        if not src.is_file():
            parser.error(f"Template missing: {src}")
        dst = out / (name + ".tex")
        subprocess.run(
            [pandoc, str(src), "--from=markdown+pipe_tables+fenced_divs+yaml_metadata_block",
             "--to=latex", "--wrap=none", "--top-level-division=section", "--no-highlight",
             "--lua-filter=" + str(HERE / "pandoc-wodtex.lua"), "--output=" + str(dst)],
            check=True,
        )
        print(f"{src.name} -> {dst}")
        fragments.append(f"\\input{{generated/{name}.tex}}")

    (out / "contents.tex").write_text(
        "% Generated from BBotF research templates; do not edit by hand.\n"
        + "\n".join(fragments) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()