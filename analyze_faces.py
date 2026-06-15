#!/usr/bin/env python3
"""CLI: analyze a single image and write JSON result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from worker import detect_faces


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = detect_faces(Path(args.image))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
