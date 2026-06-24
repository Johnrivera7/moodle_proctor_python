#!/usr/bin/env python3
"""
Moodle Proctor — face detection worker.

Processes JSON job files from analysis_queue/ on shared storage.
Writes result JSON to analysis_results/ for Moodle scheduled task to import.

Usage:
  python worker.py --storage /mnt/proctor
  python analyze_faces.py --image /path/snap.jpg --output /path/result.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("moodle_proctor")


def detect_faces(image_path: Path) -> dict:
    """Detect faces using OpenCV Haar cascade (no extra ML deps required)."""
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Install opencv-python: pip install opencv-python-headless") from exc

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    img = cv2.imread(str(image_path))
    if img is None:
        return {"face_count": -1, "alert": False, "error": "cannot_read_image"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    count = len(faces) if faces is not None else 0
    return {
        "face_count": int(count),
        "alert": count > 1 or count == 0,
        "alert_reason": "multiple_faces" if count > 1 else ("no_face" if count == 0 else "ok"),
    }


def process_job(job_path: Path) -> bool:
    data = json.loads(job_path.read_text(encoding="utf-8"))
    image = Path(data["image"])
    result_path = Path(data["result"])
    if not image.is_file():
        logger.warning("Missing image for job %s", job_path)
        job_path.unlink(missing_ok=True)
        return False

    result = detect_faces(image)
    result["snapshotid"] = data.get("snapshotid")
    result["processed"] = int(time.time())
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    job_path.unlink(missing_ok=True)
    logger.info("Processed snapshot %s: %s faces", data.get("snapshotid"), result["face_count"])
    return True


def run_worker(storage: Path, interval: float = 5.0) -> None:
    queue = storage / "analysis_queue"
    queue.mkdir(parents=True, exist_ok=True)
    logger.info("Watching %s", queue)
    while True:
        jobs = sorted(queue.glob("job_*.json"))
        for job in jobs:
            try:
                process_job(job)
            except Exception as exc:
                logger.exception("Job failed %s: %s", job, exc)
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Moodle Proctor Python worker")
    parser.add_argument("--storage", required=True, help="Shared storage root (same as Moodle setting)")
    parser.add_argument("--once", action="store_true", help="Process queue once and exit")
    parser.add_argument("--interval", type=float, default=5.0, help="Poll interval seconds")
    args = parser.parse_args()
    storage = Path(args.storage)

    if args.once:
        queue = storage / "analysis_queue"
        for job in sorted(queue.glob("job_*.json")):
            process_job(job)
        return

    run_worker(storage, args.interval)


if __name__ == "__main__":
    main()
