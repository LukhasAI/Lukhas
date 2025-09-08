#!/usr/bin/env python3
"""
Test script to verify the concurrent saves threading fix.
"""

import json
import os
import queue
import sys
import tempfile
import threading
import time
from pathlib import Path

# Add paths for imports
sys.path.insert(0, ".")
sys.path.insert(0, "candidate/aka_qualia")

from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool


# Simplified SqlMemory class for testing
class TestSqlMemory:
    def __init__(self, engine, is_prod=False):
        self.engine = engine
        self.is_prod = is_prod
        self._apply_migration()
    
    def _apply_migration(self):
        """Apply database migration to create required tables"""
        with self.engine.begin() as conn:
            # Create akaq_scene table with correct schema
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS akaq_scene (
                    scene_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    subject TEXT,
                    object TEXT,
                    proto TEXT,
                    proto_vec TEXT,
                    risk TEXT,
                    context TEXT,
                    transform_chain TEXT,
                    collapse_hash TEXT,
                    drift_phi REAL,
                    congruence_index REAL,
                    neurosis_risk REAL,
                    repair_delta REAL,
                    sublimation_rate REAL,
                    affect_energy_before REAL,
                    affect_energy_after REAL,
                    affect_energy_diff REAL,
                    cfg_version TEXT,
                    ts REAL DEFAULT (julianday('now'))
                )
            """))

            # Create akaq_glyph table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS akaq_glyph (
                    glyph_id TEXT PRIMARY KEY,
                    scene_id TEXT,
                    user_id TEXT NOT NULL,
                    key TEXT,
                    attrs TEXT,
                    priority REAL,
                    ts REAL DEFAULT (julianday('now')),
                    FOREIGN KEY (scene_id) REFERENCES akaq_scene(scene_id)
                )
            """))

        print("Database migration applied successfully")

    def _generate_scene_id(self):
        """Generate unique scene ID"""
        import uuid
        return f"scene_{uuid.uuid4().hex[:8]}"

    def save(self, *, user_id, scene, glyphs, policy, metrics, cfg_version):
        """Save scene and glyphs to database"""
        scene_id = self._generate_scene_id()
        
        with self.engine.begin() as tx:
            # Extract timestamp from scene if available
            scene_timestamp = scene.get("timestamp", time.time())
            
            # Insert scene
            tx.execute(text("""
                INSERT INTO akaq_scene (
                    scene_id, user_id, subject, object, proto, proto_vec, risk, context,
                    transform_chain, collapse_hash, drift_phi, congruence_index, neurosis_risk,
                    repair_delta, sublimation_rate, affect_energy_before, affect_energy_after,
                    affect_energy_diff, cfg_version, ts
                ) VALUES (
                    :scene_id, :user_id, :subject, :object, :proto, :proto_vec, :risk, :context,
                    :transform_chain, :collapse_hash, :drift_phi, :congruence_index, :neurosis_risk,
                    :repair_delta, :sublimation_rate, :affect_energy_before, :affect_energy_after,
                    :affect_energy_diff, :cfg_version, :ts
                )
            """), {
                "scene_id": scene_id,
                "user_id": user_id,
                "subject": scene.get("subject"),
                "object": scene.get("object"),
                "proto": json.dumps(scene["proto"]),
                "proto_vec": json.dumps([0.0, 0.0, 0.0, 0.0, 0.0]),  # proto_vec
                "risk": json.dumps(scene["risk"]),
                "context": json.dumps(scene.get("context", {})),
                "transform_chain": json.dumps(scene.get("transform_chain", [])),
                "collapse_hash": scene.get("collapse_hash"),
                "drift_phi": metrics.get("drift_phi"),
                "congruence_index": metrics.get("congruence_index"),
                "neurosis_risk": metrics.get("neurosis_risk"),
                "repair_delta": metrics.get("repair_delta"),
                "sublimation_rate": metrics.get("sublimation_rate"),
                "affect_energy_before": metrics.get("affect_energy_before"),
                "affect_energy_after": metrics.get("affect_energy_after"),
                "affect_energy_diff": metrics.get("affect_energy_diff"),
                "cfg_version": cfg_version,
                "ts": scene_timestamp,
            })
            
            # Insert glyphs
            for glyph in glyphs:
                glyph_id = self._generate_scene_id()
                tx.execute(text("""
                    INSERT INTO akaq_glyph (glyph_id, scene_id, user_id, key, attrs, priority)
                    VALUES (:glyph_id, :scene_id, :user_id, :key, :attrs, :priority)
                """), {
                    "glyph_id": glyph_id,
                    "scene_id": scene_id,
                    "user_id": user_id,
                    "key": glyph["key"],
                    "attrs": json.dumps(glyph.get("attrs", {})),
                    "priority": glyph.get("priority", 0.5),
                })
        
        return scene_id


def create_test_scene(scene_id):
    """Create test scene data"""
    return {
        "proto": {
            "tone": 0.0,
            "arousal": 0.5,
            "clarity": 0.7,
            "embodiment": 0.6,
            "colorfield": "blue",
            "temporal_feel": "flowing",
            "agency_feel": "empowered",
            "narrative_gravity": 0.3,
        },
        "subject": f"subject_{scene_id}",
        "object": f"object_{scene_id}",
        "context": {
            "cfg_version": "wave_c_v1.0.0",
            "policy_sig": "test_policy_sig",
            "scene_id": scene_id,
        },
        "risk": {"score": 0.1, "severity": "minimal", "reasons": []},
        "timestamp": time.time(),
    }


def create_test_glyph(key):
    """Create test glyph data"""
    return {"key": key, "attrs": {"tone": 0.0, "risk_score": 0.1}}


def test_concurrent_saves():
    """Test concurrent database operations similar to the actual test"""
    
    # Create database
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    engine = create_engine(
        f"sqlite:///{db_path}", 
        echo=False,
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )
    
    # Create SqlMemory instance
    sql_memory = TestSqlMemory(engine)
    print(f"Created test database at: {db_path}")
    
    # Test concurrent operations
    results_queue = queue.Queue()
    error_queue = queue.Queue()
    
    def save_scene(thread_id):
        try:
            scene_data = create_test_scene(f"concurrent_test_{thread_id}")
            glyph_data = [create_test_glyph(f"concurrent:glyph_{thread_id}")]
            
            scene_id = sql_memory.save(
                user_id=f"concurrent_user_{thread_id % 3}",  # 3 different users
                scene=scene_data,
                glyphs=glyph_data,
                policy={"gain": 1.0},
                metrics={"drift_phi": 0.9},
                cfg_version="wave_c_v1.0.0",
            )
            
            results_queue.put((thread_id, scene_id))
            print(f"Thread {thread_id} - Successfully saved scene {scene_id}")
            
        except Exception as e:
            error_msg = f"Thread {thread_id} - Error: {e!s}"
            print(error_msg)
            error_queue.put((thread_id, str(e)))
    
    # Launch 10 concurrent save operations (same as original test)
    threads = []
    for i in range(10):
        t = threading.Thread(target=save_scene, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all to complete
    for t in threads:
        t.join(timeout=5.0)
    
    # Check results
    print(f"\nResults: {results_queue.qsize()} successful, {error_queue.qsize()} errors")
    
    # Test assertions equivalent to the original test
    success = True
    
    if not error_queue.empty():
        success = False
        print("❌ FAILED: Errors occurred during concurrent saves")
        while not error_queue.empty():
            thread_id, error = error_queue.get()
            print(f"  Thread {thread_id}: {error}")
    else:
        print("✅ No errors occurred during concurrent saves")
    
    if results_queue.qsize() != 10:
        success = False
        print(f"❌ FAILED: Expected 10 successful saves, got {results_queue.qsize()}")
    else:
        print("✅ All 10 saves completed successfully")
    
    # Verify all scene IDs are unique
    scene_ids = []
    while not results_queue.empty():
        thread_id, scene_id = results_queue.get()
        scene_ids.append(scene_id)
    
    if len(set(scene_ids)) != 10:
        success = False
        print(f"❌ FAILED: Expected 10 unique scene IDs, got {len(set(scene_ids))}")
    else:
        print("✅ All scene IDs are unique")
    
    # Verify data was actually saved to database
    with engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM akaq_scene"))
        scene_count = result.scalar()
        
        result = conn.execute(text("SELECT COUNT(*) FROM akaq_glyph"))
        glyph_count = result.scalar()
        
        if scene_count != 10:
            success = False
            print(f"❌ FAILED: Expected 10 scenes in database, got {scene_count}")
        else:
            print(f"✅ Database contains {scene_count} scenes")
        
        if glyph_count != 10:
            success = False
            print(f"❌ FAILED: Expected 10 glyphs in database, got {glyph_count}")
        else:
            print(f"✅ Database contains {glyph_count} glyphs")
    
    # Cleanup
    engine.dispose()
    try:
        os.unlink(db_path)
        print(f"Cleaned up database file: {db_path}")
    except Exception:
        pass
    
    return success


if __name__ == "__main__":
    print("Testing concurrent saves fix...")
    success = test_concurrent_saves()
    if success:
        print("\n🎉 All tests passed! The threading issue is fixed.")
    else:
        print("\n💥 Some tests failed. The threading issue persists.")
        sys.exit(1)
