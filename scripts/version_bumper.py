#!/usr/bin/env python3
"""
PASVG Version Bumper

Automatically increments version numbers in pyproject.toml for semantic versioning.
Supports major, minor, and patch version bumps.

Usage:
    python version_bumper.py [major|minor|patch]
    python version_bumper.py --help
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse version string into tuple of integers."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)(?:-.*)?$', version_str.strip())
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    return tuple(map(int, match.groups()))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple into string."""
    return f"{major}.{minor}.{patch}"


def increment_version(current_version: str, bump_type: str) -> str:
    """Increment version based on bump type."""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        return format_version(major + 1, 0, 0)
    elif bump_type == "minor":
        return format_version(major, minor + 1, 0)
    elif bump_type == "patch":
        return format_version(major, minor, patch + 1)
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_pyproject_version(file_path: Path, new_version: str) -> None:
    """Update version in pyproject.toml file."""
    content = file_path.read_text()
    updated_content = re.sub(
        r'^version\s*=\s*["\']([^"\']+)["\']',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )

    if content == updated_content:
        print(f"❌ Could not find version line in {file_path}")
        sys.exit(1)

    file_path.write_text(updated_content)
    print(f"✅ Updated version to {new_version} in {file_path}")


def get_current_version(file_path: Path) -> str:
    """Get current version from pyproject.toml."""
    content = file_path.read_text()
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        print(f"❌ Could not find version in {file_path}")
        sys.exit(1)
    return match.group(1)


def main():
    parser = argparse.ArgumentParser(
        description="Bump version in pyproject.toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s patch    # 1.0.3 → 1.0.4
  %(prog)s minor    # 1.0.3 → 1.1.0
  %(prog)s major    # 1.0.3 → 2.0.0
        """
    )
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--file", "-f",
        default="pyproject.toml",
        help="Path to pyproject.toml file (default: pyproject.toml)"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be changed without making changes"
    )

    args = parser.parse_args()

    # Find pyproject.toml file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # Get current version
    try:
        current_version = get_current_version(file_path)
        print(f"📋 Current version: {current_version}")
    except Exception as e:
        print(f"❌ Error reading current version: {e}")
        sys.exit(1)

    # Calculate new version
    try:
        new_version = increment_version(current_version, args.bump_type)
        print(f"⬆️  New version: {new_version}")
    except Exception as e:
        print(f"❌ Error calculating new version: {e}")
        sys.exit(1)

    # Update file or show dry run
    if args.dry_run:
        print("🔍 Dry run - no changes made")
        print(f"Would update: {current_version} → {new_version}")
    else:
        try:
            update_pyproject_version(file_path, new_version)
            print("🎉 Version bumped successfully!")
            print("💡 Next steps: make publish")
        except Exception as e:
            print(f"❌ Error updating file: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
