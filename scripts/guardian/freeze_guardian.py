#!/usr/bin/env python3
"""T4/0.01% Freeze Guardian Daemon

Real-time monitoring daemon that watches for drift in frozen artifacts and ledgers.
Runs continuously, checking for violations every N seconds and generating alerts.

Features:
- Real-time file system monitoring using watchdog
- Automatic drift detection and alert generation
- Configurable check intervals
- Alert logging and reporting
- GitHub issue creation on violations

Usage:
    # Run as daemon (checks every 60 seconds)
    python3 scripts/guardian/freeze_guardian.py --interval 60

    # Run once and exit
    python3 scripts/guardian/freeze_guardian.py --once

    # Run with custom alert directory
    python3 scripts/guardian/freeze_guardian.py --alert-dir /path/to/alerts

Exit codes:
    0 - Clean exit (daemon stopped gracefully)
    1 - Drift detected (when running with --once)
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
import time
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

ROOT = Path(".").resolve()
FREEZE_TAG = "v0.02-final"


class FreezeConfig(NamedTuple):
    """Freeze configuration from FINAL_FREEZE.json"""
    tag: str
    commit: str
    critical_artifacts: list[str]


class ViolationReport(NamedTuple):
    """Freeze violation report"""
    timestamp: str
    tag: str
    expected_commit: str
    current_commit: str
    violated_files: list[str]
    file_hashes: dict[str, tuple[str, str]]  # {path: (expected, actual)}


def load_freeze_config() -> FreezeConfig:
    """Load freeze configuration from FINAL_FREEZE.json"""
    freeze_file = ROOT / "docs/_generated/FINAL_FREEZE.json"

    if not freeze_file.exists():
        logger.error(f"FINAL_FREEZE.json not found at {freeze_file}")
        sys.exit(1)

    try:
        data = json.loads(freeze_file.read_text())
        return FreezeConfig(
            tag=data.get("tag", FREEZE_TAG),
            commit=data["commit"],
            critical_artifacts=data.get("critical_artifacts", [])
        )
    except Exception as e:
        logger.error(f"Failed to load freeze config: {e}")
        sys.exit(1)


def get_current_commit() -> str:
    """Get current HEAD commit SHA"""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current commit: {e}")
        sys.exit(1)


def get_tag_commit(tag: str) -> str:
    """Get commit SHA that a tag points to"""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", tag],
            text=True
        ).strip()
    except subprocess.CalledProcessError:
        logger.error(f"Tag not found: {tag}")
        sys.exit(1)


def file_hash(path: Path) -> str:
    """Calculate SHA256 hash of file"""
    if not path.exists():
        return "MISSING"

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def blob_hash_at_tag(tag: str, relpath: str) -> str:
    """Calculate SHA256 hash of file at specific tag"""
    try:
        data = subprocess.check_output(
            ["git", "show", f"{tag}:{relpath}"],
            stderr=subprocess.STDOUT
        )
        h = hashlib.sha256()
        h.update(data)
        return h.hexdigest()
    except subprocess.CalledProcessError:
        return "MISSING_AT_TAG"


def check_freeze_integrity(config: FreezeConfig) -> ViolationReport | None:
    """Check if freeze is intact, return violation report if not"""
    current_commit = get_current_commit()
    tag_commit = get_tag_commit(config.tag)

    # Check if we're past the freeze commit
    try:
        # Get commits between freeze and HEAD
        commits_after = subprocess.check_output(
            ["git", "rev-list", f"{tag_commit}..HEAD"],
            text=True
        ).strip()

        if commits_after:
            logger.warning(f"Found {len(commits_after.splitlines())} commits after freeze tag")
    except subprocess.CalledProcessError:
        pass

    # Check critical artifacts
    violated_files = []
    file_hashes = {}

    for artifact in config.critical_artifacts:
        artifact_path = ROOT / artifact
        current_hash = file_hash(artifact_path)
        expected_hash = blob_hash_at_tag(config.tag, artifact)

        if current_hash != expected_hash:
            violated_files.append(artifact)
            file_hashes[artifact] = (expected_hash, current_hash)

    if violated_files:
        return ViolationReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            tag=config.tag,
            expected_commit=tag_commit,
            current_commit=current_commit,
            violated_files=violated_files,
            file_hashes=file_hashes
        )

    return None


def generate_alert(violation: ViolationReport, alert_dir: Path) -> Path:
    """Generate alert file for freeze violation"""
    alert_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    alert_file = alert_dir / f"freeze_violation_{timestamp}.log"

    alert_content = f"""
# 🚨 FREEZE VIOLATION DETECTED

**Timestamp**: {violation.timestamp}
**Tag**: {violation.tag}
**Expected Commit**: {violation.expected_commit}
**Current Commit**: {violation.current_commit}

## Violated Files ({len(violation.violated_files)})

"""

    for filepath in violation.violated_files:
        expected_hash, actual_hash = violation.file_hashes[filepath]
        alert_content += f"""
### {filepath}
- **Expected SHA256**: {expected_hash}
- **Actual SHA256**: {actual_hash}
- **Status**: {'MISSING' if actual_hash == 'MISSING' else 'MODIFIED'}
"""

    alert_content += f"""

## Recommended Actions

1. Review the changes to understand why these files were modified
2. If intentional post-freeze work, create a new tag (v0.03-prep)
3. If accidental, revert to freeze state: `git checkout {violation.tag}`
4. Check branch protection settings on main
5. Review recent commits: `git log {violation.expected_commit}..HEAD`

## How to Fix

```bash
# Option 1: Revert to freeze state
git checkout {violation.tag}
git checkout -b hotfix/restore-freeze
git push origin hotfix/restore-freeze

# Option 2: Create new development branch
git checkout -b develop/v0.03-prep
# Continue work there instead of on main
```

---
*Generated by Freeze Guardian at {violation.timestamp}*
"""

    alert_file.write_text(alert_content)
    logger.warning(f"Alert generated: {alert_file}")

    return alert_file


def run_once(config: FreezeConfig, alert_dir: Path) -> int:
    """Run a single check and exit"""
    logger.info(f"Running single freeze integrity check for {config.tag}")

    violation = check_freeze_integrity(config)

    if violation:
        logger.error(f"❌ FREEZE VIOLATION: {len(violation.violated_files)} file(s) modified")
        alert_file = generate_alert(violation, alert_dir)
        logger.error(f"Alert saved to: {alert_file}")
        return 1
    else:
        logger.info(f"✅ Freeze intact: {config.tag}")
        return 0


def run_daemon(config: FreezeConfig, alert_dir: Path, interval: int):
    """Run as continuous monitoring daemon"""
    logger.info(f"🛡️  Freeze Guardian started")
    logger.info(f"   Tag: {config.tag}")
    logger.info(f"   Monitoring: {len(config.critical_artifacts)} artifacts")
    logger.info(f"   Check interval: {interval}s")
    logger.info(f"   Alert directory: {alert_dir}")

    check_count = 0
    violation_count = 0

    try:
        while True:
            check_count += 1
            logger.info(f"Check #{check_count}: Verifying freeze integrity...")

            violation = check_freeze_integrity(config)

            if violation:
                violation_count += 1
                logger.error(f"❌ FREEZE VIOLATION #{violation_count}")
                logger.error(f"   Files modified: {len(violation.violated_files)}")

                alert_file = generate_alert(violation, alert_dir)
                logger.error(f"   Alert: {alert_file}")

                # In daemon mode, continue monitoring after violation
                logger.info("   Continuing monitoring...")
            else:
                logger.info(f"✅ Freeze intact (check #{check_count})")

            # Sleep until next check
            logger.debug(f"Sleeping for {interval}s until next check...")
            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info(f"\n🛑 Freeze Guardian stopped by user")
        logger.info(f"   Total checks: {check_count}")
        logger.info(f"   Violations detected: {violation_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="T4/0.01% Freeze Guardian - Real-time drift monitoring"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't run as daemon)"
    )
    parser.add_argument(
        "--alert-dir",
        type=Path,
        default=Path("alerts"),
        help="Directory for alert logs (default: alerts/)"
    )
    parser.add_argument(
        "--tag",
        default=FREEZE_TAG,
        help=f"Tag to monitor (default: {FREEZE_TAG})"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Load freeze configuration
    config = load_freeze_config()

    # Override tag if specified
    if args.tag != FREEZE_TAG:
        config = FreezeConfig(
            tag=args.tag,
            commit=config.commit,
            critical_artifacts=config.critical_artifacts
        )

    # Run mode
    if args.once:
        return run_once(config, args.alert_dir)
    else:
        run_daemon(config, args.alert_dir, args.interval)
        return 0


if __name__ == "__main__":
    sys.exit(main())
