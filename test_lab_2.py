#!/usr/bin/env python3
"""
Autograding validation for Lab 2: Introduction to ROS 2.
Run with: pytest test_lab_2.py -v
"""

import os
import warnings

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
README_STARTER_FINGERPRINT = "Update this README"
EXPECTED_SCREENSHOTS = {
    "turtlesim_remap",
    "nodes_info",
    "topics_graph",
    "services_spawn",
    "params_background",
}


def _get_images(docs_dir="docs"):
    if not os.path.isdir(docs_dir):
        return []
    return [
        f for f in os.listdir(docs_dir)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ]


# ── Required files (hard fail) ──────────────────────────────


def test_readme_exists():
    assert os.path.isfile("README.md"), "README.md not found"


def test_readme_not_empty():
    assert os.path.getsize("README.md") > 0, "README.md is empty"


def test_readme_updated():
    with open("README.md", "r", errors="replace") as f:
        content = f.read()
    assert README_STARTER_FINGERPRINT not in content, (
        "README.md still contains the starter template text. "
        "Please update it with your name, NetID, and completion notes."
    )


def test_docs_directory_exists():
    assert os.path.isdir("docs"), "docs/ directory not found"


# ── Screenshots (warnings) ──────────────────────────────────


def test_screenshot_count():
    images = _get_images()
    print(f"\nFound {len(images)} image(s) in docs/:")
    for img in sorted(images):
        print(f"  - {img}")
    if len(images) < 5:
        warnings.warn(f"Expected 5 screenshots, found {len(images)}")


def test_screenshot_names():
    images = _get_images()
    stems = {os.path.splitext(f)[0].lower() for f in images}
    missing = EXPECTED_SCREENSHOTS - stems
    if missing:
        warnings.warn(
            f"Screenshots with non-standard names. "
            f"Expected names not found: {', '.join(sorted(missing))}"
        )


# ── Optional ─────────────────────────────────────────────────


def test_optional_move_turtle():
    if not os.path.isfile("move_turtle.sh"):
        print("move_turtle.sh not found (optional stretch goal)")
