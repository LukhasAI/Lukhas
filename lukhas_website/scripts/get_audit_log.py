#!/usr/bin/env python3
import json
import os
import sqlite3


def get_audit_logs():
    """
    Connects to the audit SQLite database, fetches the latest 100 audit entries,
    and returns them as a list of dictionaries.
    This script is self-contained and does not depend on the LUKHAS core modules.
    """
    # The script is in lukhas_website/scripts, the db is in data/
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "audit_trail.db"))

    if not os.path.exists(db_path):
        # If the database doesn't exist, create it and add some mock data
        # so the feature can be demonstrated.
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Create table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_entries (
                audit_id TEXT PRIMARY KEY, timestamp REAL, session_id TEXT,
                interaction_id TEXT, decision_type TEXT, decision TEXT,
                reasoning TEXT, confidence REAL, input_data TEXT,
                output_data TEXT, system_state TEXT, signals TEXT,
                policies TEXT, overrides TEXT, parent_id TEXT,
                child_ids TEXT, related_ids TEXT, model_version TEXT,
                component TEXT, user_id TEXT, tags TEXT,
                checksum TEXT, verified INTEGER
            )
            """
        )
        # Insert mock data
        mock_entries = [
            (
                "audit_1",
                1672531200,
                "session_1",
                "interaction_1",
                "SAFETY",
                "Blocked harmful content",
                "Contained malicious patterns.",
                0.99,
                "{}",
                "{}",
                "{}",
                "{}",
                "[]",
                "[]",
                None,
                "[]",
                "[]",
                "1.0",
                "safety_filter",
                "user_abc",
                "[]",
                "",
                1,
            ),
            (
                "audit_2",
                1672534800,
                "session_1",
                "interaction_2",
                "RESPONSE",
                "Generated helpful response",
                "User asked a clear question.",
                0.95,
                '{"prompt": "Hi"}',
                "{}",
                "{}",
                "{}",
                "[]",
                "[]",
                "audit_1",
                "[]",
                "[]",
                "1.0",
                "response_generator",
                "user_abc",
                "[]",
                "",
                1,
            ),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO audit_entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            mock_entries,
        )
        conn.commit()
    else:
        conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Fetch the latest 100 entries
        cursor.execute("SELECT * FROM audit_entries ORDER BY timestamp DESC LIMIT 100")
        rows = cursor.fetchall()

        # Convert rows to dictionaries
        column_names = [description[0] for description in cursor.description]

        results = []
        for row in rows:
            entry = dict(zip(column_names, row))
            # Parse JSON fields
            for key in [
                "input_data",
                "output_data",
                "system_state",
                "signals",
                "policies",
                "overrides",
                "child_ids",
                "related_ids",
                "tags",
            ]:
                if entry.get(key) and isinstance(entry[key], str):
                    try:
                        entry[key] = json.loads(entry[key])
                    except json.JSONDecodeError:
                        entry[key] = entry[key]  # Keep as string if not valid JSON
            results.append(entry)

        return results

    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}
    finally:
        conn.close()


if __name__ == "__main__":
    logs = get_audit_logs()
    print(json.dumps(logs, indent=2))
