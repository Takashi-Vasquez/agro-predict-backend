#!/usr/bin/env python3
"""
Version bump utility for model versioning.
Supports semantic versioning: MAJOR.MINOR.PATCH
Usage: python bump_version.py [patch|minor|major]
"""

import sys
import os
import re
from pathlib import Path
from typing import Optional


VERSION_FILE = Path(__file__).parent / "model_version.txt"
VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def read_version() -> str:
    """Read current version from file."""
    if not VERSION_FILE.exists():
        return "1.0.0"
    content = VERSION_FILE.read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.match(content):
        raise ValueError(f"Invalid version format in {VERSION_FILE}: {content}")
    return content


def write_version(version: str) -> None:
    """Write version to file atomically."""
    if not VERSION_PATTERN.match(version):
        raise ValueError(f"Invalid version format: {version}")
    tmp_file = VERSION_FILE.with_suffix(".tmp")
    tmp_file.write_text(version + "\n", encoding="utf-8")
    tmp_file.replace(VERSION_FILE)


def bump_version(level: str) -> str:
    """
    Bump version according to semantic versioning rules.
    
    Args:
        level: "patch", "minor", or "major"
        
    Returns:
        New version string
        
    Raises:
        ValueError: If level is invalid
    """
    level = level.lower()
    if level not in ("patch", "minor", "major"):
        raise ValueError(f"Invalid bump level: {level}. Use 'patch', 'minor', or 'major'")
    
    current = read_version()
    major, minor, patch = map(int, current.split("."))
    
    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    write_version(new_version)
    return new_version


class VersionBumpContext:
    """
    Context manager for atomic version bump with automatic rollback on failure.
    
    Usage:
        with VersionBumpContext("minor") as new_version:
            # Do DB operations
            db.commit()
        # If exception raised, version file is rolled back automatically
    """
    
    def __init__(self, level: str):
        self.level = level
        self.previous_version: Optional[str] = None
        self.new_version: Optional[str] = None
    
    def __enter__(self) -> str:
        self.previous_version = read_version()
        self.new_version = bump_version(self.level)
        return self.new_version
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback on exception
            write_version(self.previous_version)
            return False  # Re-raise exception
        return True


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python bump_version.py [patch|minor|major]")
        print(f"Current version: {read_version()}")
        sys.exit(1)
    
    level = sys.argv[1].lower()
    
    try:
        new_version = bump_version(level)
        print(f"Version bumped: {new_version}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()