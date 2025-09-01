import json
from pathlib import Path


class DreamSnapshotStore:
    def __init__(self, snapshot_dir="snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(exist_ok=True)

    def save_snapshot(self, user_id: str, snapshot: dict):
        user_dir = self.snapshot_dir / user_id
        user_dir.mkdir(exist_ok=True)
        snapshot_path = user_dir / f"{snapshot['dream_id']}.json"
        with open(snapshot_path, "w") as f:
            json.dump(snapshot, f, indent=4)

    def get_recent_snapshots(self, user_id: str, limit: int = 10) -> list:
        user_dir = self.snapshot_dir / user_id
        if not user_dir.exists():
            return []

        snapshots = []
        # Sort by creation time, newest first
        for snapshot_file in sorted(user_dir.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True):
            if len(snapshots) >= limit:
                break
            with open(snapshot_file) as f:
                snapshots.append(json.load(f))
        return snapshots
