import sqlite3

from dream.dashboard import DreamMetricsDB


def test_add_dream_metrics(tmp_path):
    db_path = tmp_path / "dream_metrics.db"
    db = DreamMetricsDB(db_path=str(db_path))
    db.add_dream_metrics("dream_1", 0.4, 0.1, 0.9)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "SELECT dream_id, drift_score, entropy_delta, alignment_score FROM dream_metrics"
        )
        row = cursor.fetchone()

    assert row == ("dream_1", 0.4, 0.1, 0.9)
