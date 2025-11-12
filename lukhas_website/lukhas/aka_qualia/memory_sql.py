#!/usr/bin/env python3
"""
Aka Qualia SQL Memory Implementation (C4.2)
============================================

SQL-based memory client for PostgreSQL and SQLite with GDPR compliance,
privacy hashing, and vector similarity support.

Follows Freud-2025 C4 specifications for memory persistence.
"""

import datetime as dt
import hashlib
import json
import logging
from datetime import timezone
from typing import Any, Optional
from urllib.parse import urlparse

try:
    import sqlalchemy as sa
    from sqlalchemy import (
        create_engine,
        Column,
        String,
        Float,
        Text,
        ForeignKey,
        DateTime,
        desc,
        func,
    )
    from sqlalchemy.orm import sessionmaker, relationship, declarative_base
    from sqlalchemy.engine import Engine
except ImportError:
    raise ImportError("SQLAlchemy required. Install with: pip install sqlalchemy")

try:
    import ulid
except ImportError:
    import uuid
    ulid = None

from .memory import AkaqMemory
from .observability import get_observability, measure_memory_operation

logger = logging.getLogger(__name__)

Base = declarative_base()


class AkaqScene(Base):
    __tablename__ = "akaq_scene"
    scene_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    subject = Column(String)
    object = Column(String)
    proto = Column(Text)
    proto_vec = Column(Text)
    risk = Column(Text)
    context = Column(Text)
    transform_chain = Column(Text)
    collapse_hash = Column(String)
    drift_phi = Column(Float)
    congruence_index = Column(Float)
    neurosis_risk = Column(Float)
    repair_delta = Column(Float)
    sublimation_rate = Column(Float)
    affect_energy_before = Column(Float)
    affect_energy_after = Column(Float)
    affect_energy_diff = Column(Float)
    cfg_version = Column(String)
    ts = Column(Float, default=lambda: dt.datetime.now(timezone.utc).timestamp(), index=True)
    glyphs = relationship("AkaqGlyph", back_populates="scene", cascade="all, delete-orphan")


class AkaqGlyph(Base):
    __tablename__ = "akaq_glyph"
    glyph_id = Column(String, primary_key=True)
    scene_id = Column(String, ForeignKey("akaq_scene.scene_id"), index=True)
    user_id = Column(String, nullable=False, index=True)
    key = Column(String)
    attrs = Column(Text)
    priority = Column(Float)
    ts = Column(Float, default=lambda: dt.datetime.now(timezone.utc).timestamp())
    scene = relationship("AkaqScene", back_populates="glyphs")


class AkaqMemoryOps(Base):
    __tablename__ = "akaq_memory_ops"
    operation_id = Column(String, primary_key=True)
    operation = Column(String, nullable=False)
    user_id = Column(String)
    op_metadata = Column(Text)
    timestamp = Column(DateTime, default=dt.datetime.now(timezone.utc))


class SqlMemory(AkaqMemory):
    def __init__(
        self,
        engine: Optional[Engine] = None,
        dsn: Optional[str] = None,
        rotate_salt: str = "default_salt_change_in_prod",
        is_prod: bool = False,
        config: Optional[dict[str, Any]] = None,
    ):
        if engine is None:
            if dsn is None:
                raise ValueError("Either engine or dsn must be provided")
            engine = self._create_engine(dsn)

        self.engine = engine
        self.rotate_salt = rotate_salt
        self.is_prod = is_prod
        self.config = config or {}
        self.driver = self._detect_driver()
        self._apply_migration()

        self.Session = sessionmaker(bind=self.engine)
        self.scenes_saved = 0
        self.save_failures = 0
        logger.info(f"SqlMemory initialized with {self.driver} driver (prod={is_prod})")

    def _create_engine(self, dsn: str) -> Engine:
        parsed = urlparse(dsn)
        if parsed.scheme == "postgresql":
            return create_engine(dsn, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=3600)
        elif parsed.scheme == "sqlite":
            engine = create_engine(dsn, connect_args={"check_same_thread": False})
            with engine.begin() as conn:
                conn.execute(sa.text("PRAGMA journal_mode=WAL"))
                conn.execute(sa.text("PRAGMA foreign_keys=ON"))
            return engine
        else:
            return create_engine(dsn)

    def _detect_driver(self) -> str:
        return self.engine.name

    def _apply_migration(self) -> None:
        Base.metadata.create_all(self.engine)
        logger.info("Database migration applied successfully")

    def _hash_safe(self, s: Optional[str]) -> Optional[str]:
        if not s or not self.is_prod:
            return s
        h = hashlib.sha3_256()
        h.update((self.rotate_salt + s).encode("utf-8"))
        return h.hexdigest()

    def _sanitize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        safe_fields = {
            "safe_palette", "approach_avoid_score", "colorfield", "temporal_feel",
            "agency_feel", "scenario", "test_context", "cfg_version", "policy_sig",
            "session_id",
        }
        return {k: v for k, v in context.items() if k in safe_fields}

    def _generate_scene_id(self) -> str:
        if ulid:
            return ulid.new().str
        else:
            return f"uuid_{uuid.uuid4().hex}"

    def save(
        self,
        *,
        user_id: str,
        scene: dict[str, Any],
        glyphs: list[dict[str, Any]],
        policy: dict[str, Any],
        metrics: dict[str, Any],
        cfg_version: str,
    ) -> str:
        obs = get_observability()
        with measure_memory_operation("save", "sql"):
            scene_id = self._generate_scene_id()
            session = self.Session()
            try:
                user_id_hash = self._hash_safe(user_id)
                subject = self._hash_safe(scene.get("subject"))
                object_field = self._hash_safe(scene.get("object"))
                proto = scene["proto"]
                proto_vec = self._proto_to_vector(proto)
                sanitized_context = self._sanitize_context(scene.get("context", {}))
                proto_vec_param = json.dumps(proto_vec) if self.driver != "postgresql" else proto_vec

                new_scene = AkaqScene(
                    scene_id=scene_id,
                    user_id=user_id_hash,
                    subject=subject,
                    object=object_field,
                    proto=json.dumps(proto),
                    proto_vec=proto_vec_param,
                    risk=json.dumps(scene["risk"]),
                    context=json.dumps(sanitized_context),
                    transform_chain=json.dumps(scene.get("transform_chain", [])),
                    collapse_hash=scene.get("collapse_hash"),
                    drift_phi=metrics.get("drift_phi"),
                    congruence_index=metrics.get("congruence_index"),
                    neurosis_risk=metrics.get("neurosis_risk"),
                    repair_delta=metrics.get("repair_delta"),
                    sublimation_rate=metrics.get("sublimation_rate"),
                    affect_energy_before=metrics.get("affect_energy_before"),
                    affect_energy_after=metrics.get("affect_energy_after"),
                    affect_energy_diff=metrics.get("affect_energy_diff"),
                    cfg_version=cfg_version,
                    ts=scene.get("timestamp", dt.datetime.now(timezone.utc).timestamp()),
                )
                session.add(new_scene)

                for glyph in glyphs:
                    new_glyph = AkaqGlyph(
                        glyph_id=self._generate_scene_id(),
                        scene_id=scene_id,
                        user_id=user_id,
                        key=glyph["key"],
                        attrs=json.dumps(glyph.get("attrs", {})),
                        priority=glyph.get("priority", 0.5),
                    )
                    session.add(new_glyph)

                session.commit()
                self.scenes_saved += 1
                logger.debug(f"Saved scene {scene_id} with {len(glyphs)} glyphs")
                obs.update_memory_storage("sql", "scenes", self.scenes_saved * 1024)
                obs.record_scene_processed(status="success")
                return scene_id
            except Exception as e:
                session.rollback()
                self.save_failures += 1
                logger.error(f"Failed to save scene: {e!s}")
                raise
            finally:
                session.close()

    def _proto_to_vector(self, proto: dict[str, Any]) -> list[float]:
        return [
            float(proto.get("tone", 0.0)), float(proto.get("arousal", 0.0)),
            float(proto.get("clarity", 0.0)), float(proto.get("embodiment", 0.0)),
            float(proto.get("narrative_gravity", 0.0)),
        ]

    def fetch_prev_scene(self, *, user_id: str, before_ts: Optional[dt.datetime] = None) -> Optional[dict[str, Any]]:
        session = self.Session()
        try:
            if before_ts is None:
                before_ts = dt.datetime.now(timezone.utc)

            ts_timestamp = before_ts.timestamp()

            scene = (
                session.query(AkaqScene)
                .filter(AkaqScene.user_id == user_id, AkaqScene.ts < ts_timestamp)
                .order_by(desc(AkaqScene.ts))
                .first()
            )

            if not scene:
                return None

            return {
                "scene_id": scene.scene_id, "proto": json.loads(scene.proto),
                "risk": json.loads(scene.risk), "drift_phi": scene.drift_phi,
                "congruence_index": scene.congruence_index, "neurosis_risk": scene.neurosis_risk,
                "repair_delta": scene.repair_delta, "timestamp": scene.ts,
            }
        except Exception as e:
            logger.error(f"Failed to fetch previous scene: {e!s}")
            return None
        finally:
            session.close()

    def history(self, *, user_id: str, limit: int = 50, since: Optional[dt.datetime] = None) -> list[dict[str, Any]]:
        with measure_memory_operation("sql_history"):
            session = self.Session()
            try:
                user_id_hash = self._hash_safe(user_id)
                query = session.query(AkaqScene).filter(AkaqScene.user_id == user_id_hash)
                if since:
                    query = query.filter(AkaqScene.ts > since.timestamp())

                scenes_data = query.order_by(desc(AkaqScene.ts)).limit(limit).all()

                scenes = [
                    {
                        "scene_id": s.scene_id, "timestamp": s.ts,
                        "proto": json.loads(s.proto or "{}"), "risk": json.loads(s.risk or "{}"),
                        "context": json.loads(s.context or "{}"), "drift_phi": s.drift_phi,
                        "congruence_index": s.congruence_index, "neurosis_risk": s.neurosis_risk,
                        "subject": s.subject, "object": s.object,
                    }
                    for s in scenes_data
                ]
                logger.debug(f"Retrieved {len(scenes)} scenes for user {user_id}")
                return scenes
            finally:
                session.close()

    def get_scene_history(self, *, user_id: str, limit: int = 50, since: Optional[dt.datetime] = None) -> list[dict[str, Any]]:
        return self.history(user_id=user_id, limit=limit, since=since)

    def search_by_glyph(self, *, user_id: str, key: Optional[str] = None, glyph_key: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
        search_key = key or glyph_key
        if not search_key:
            raise ValueError("Either 'key' or 'glyph_key' must be provided")

        session = self.Session()
        try:
            user_id_hash = self._hash_safe(user_id)
            results = (
                session.query(AkaqScene, AkaqGlyph)
                .join(AkaqGlyph, AkaqScene.scene_id == AkaqGlyph.scene_id)
                .filter(AkaqScene.user_id == user_id_hash, AkaqGlyph.key == search_key)
                .order_by(desc(AkaqScene.ts))
                .limit(limit)
                .all()
            )
            scenes = [
                {
                    "scene_id": s.scene_id, "timestamp": s.ts,
                    "proto": json.loads(s.proto), "risk": json.loads(s.risk),
                    "subject": s.subject, "object": s.object,
                    "glyph_attrs": json.loads(g.attrs), "glyph_key": search_key,
                }
                for s, g in results
            ]
            return scenes
        except Exception as e:
            logger.error(f"Failed to search by glyph: {e!s}")
            return []
        finally:
            session.close()

    def top_drift(self, *, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        session = self.Session()
        try:
            scenes_data = (
                session.query(AkaqScene)
                .filter(AkaqScene.user_id == user_id, AkaqScene.drift_phi.isnot(None))
                .order_by(desc(AkaqScene.drift_phi))
                .limit(limit)
                .all()
            )
            return [
                {
                    "scene_id": s.scene_id, "timestamp": s.ts,
                    "proto": json.loads(s.proto), "drift_phi": s.drift_phi,
                    "congruence_index": s.congruence_index,
                }
                for s in scenes_data
            ]
        except Exception as e:
            logger.error(f"Failed to fetch top drift scenes: {e!s}")
            return []
        finally:
            session.close()

    def delete_user(self, *, user_id: str) -> int:
        session = self.Session()
        try:
            count = session.query(AkaqScene).filter(AkaqScene.user_id == user_id).count()

            if count > 0:
                session.query(AkaqScene).filter(AkaqScene.user_id == user_id).delete()
                session.commit()

            logger.info(f"Deleted {count} scenes for user {user_id}")
            return count
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete user data: {e!s}")
            raise
        finally:
            session.close()

    def get_stats(self) -> dict[str, Any]:
        return {
            "driver": self.driver, "is_prod": self.is_prod,
            "scenes_saved": self.scenes_saved, "save_failures": self.save_failures,
            "success_rate": (
                self.scenes_saved / (self.scenes_saved + self.save_failures)
                if (self.scenes_saved + self.save_failures) > 0 else 0
            ),
        }
