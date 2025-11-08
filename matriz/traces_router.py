from __future__ import annotations

import json
import logging
import os
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, TypedDict, Union

from fastapi import APIRouter, HTTPException, Query, Response, status

"""
MATRIZ Traces Router
Provides API endpoints for retrieving golden traces and execution artifacts.
Part of Stream B implementation for issue #185.

Environment:
- `MATRIZ_TRACES_DIR` (optional): If set, use this directory as the sole
  source for traces. When unset, the router checks live traces under
  `reports/matriz/traces` first, then falls back to goldens under
  `tests/golden/tier1`.
"""

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/traces", tags=["traces"])

# Base paths for trace data
TRACES_BASE_PATH = Path("reports/matriz/traces")
GOLDEN_TRACES_PATH = Path("tests/golden/tier1")

# Limits and guards
MAX_SCAN = 2000
MAX_SIZE = 5 * 1024 * 1024  # 5 MiB


class TraceMeta(TypedDict, total=False):
    trace_id: str
    timestamp: object
    source: str


def _iter_trace_dirs() -> list[Path]:
    """Return prioritized directories to search for traces.

    Priority:
    1) Env override `MATRIZ_TRACES_DIR` if set (single directory)
    2) Live traces `reports/matriz/traces`
    3) Golden traces `tests/golden/tier1`
    """
    env_dir = os.getenv("MATRIZ_TRACES_DIR", "").strip()
    roots: list[Path] = []
    if env_dir:
        env_path = Path(env_dir)
        if not env_path.exists() or not env_path.is_dir():
            raise HTTPException(status_code=400, detail={"error": "invalid_dir"})
        roots.append(env_path)
    roots.extend([TRACES_BASE_PATH, GOLDEN_TRACES_PATH])
    return [p for p in roots if p.exists() and p.is_dir()]


def _is_within(root: Path, candidate: Path) -> bool:
    """Return True if candidate resolves under root (no traversal/symlink escape)."""
    try:
        root_r = root.resolve()
        cand_r = candidate.resolve()
    except Exception:
        return False
    root_s = str(root_r)
    cand_s = str(cand_r)
    return cand_s == root_s or cand_s.startswith(root_s + os.sep)


def _iter_json_files(root: Path) -> Iterable[Path]:
    """Yield up to MAX_SCAN json files under root, path-safe only."""
    count = 0
    for p in root.glob("*.json"):
        # Skip entries that are not files or escape root via symlink
        try:
            if not p.is_file() or not _is_within(root, p):
                continue
        except Exception:
            continue
        yield p
        count += 1
        if count >= MAX_SCAN:
            break


def _sorted_files_in(root: Path) -> list[Path]:
    files = [(p, p.stat().st_mtime) for p in _iter_json_files(root)]
    # Latest first by mtime desc, tiebreak by filename asc
    files.sort(key=lambda t: (-t[1], t[0].name))
    return [p for p, _ in files]


def _sorted_all_files() -> list[Path]:
    files: list[Path] = []
    for root in _iter_trace_dirs():
        files.extend(_iter_json_files(root))
    # Sort across all for list endpoint; not used for latest selection
    items = [(p, p.stat().st_mtime) for p in files]
    items.sort(key=lambda t: (-t[1], t[0].name))
    return [p for p, _ in items]


def _classify_root(p: Path) -> str:
    """Classify a path as env/live/golden/unknown based on root containment."""
    env_dir = os.getenv("MATRIZ_TRACES_DIR", "").strip()
    try:
        if env_dir:
            ed = Path(env_dir)
            if ed.exists() and ed.is_dir() and _is_within(ed, p):
                return "env"
        if _is_within(TRACES_BASE_PATH, p):
            return "live"
        if _is_within(GOLDEN_TRACES_PATH, p):
            return "golden"
    except Exception:
        return "unknown"
    return "unknown"


def load_trace_file(file_path: Path) -> dict[str, Any] | None:
    """Load and validate a trace JSON file."""
    try:
        if not file_path.exists():
            return None

        # Size guard
        size = file_path.stat().st_size
        if size > MAX_SIZE:
            raise HTTPException(status_code=413, detail={"error": "too_large"})

        with open(file_path, encoding="utf-8") as f:
            try:
                data: dict[str, Any] = json.load(f)
            except json.JSONDecodeError as e:  # precise 422
                logger.warning(f"Invalid JSON in {file_path}: {e}")
                raise HTTPException(status_code=422, detail={"error": "invalid_json"}) from e

        # Minimal schema sanity: trace_id and timestamp must exist
        trace_id = data.get("trace_id")
        ts = data.get("timestamp")
        if not isinstance(trace_id, str) or ts is None or not isinstance(ts, (str, int, float)):
            raise HTTPException(status_code=422, detail={"error": "invalid_trace"})

        return data
    except OSError as e:
        logger.error(f"Failed to load trace file {file_path}: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found"}) from e


@router.get("/latest", response_model=dict, summary="Get latest MATRIZ trace")
async def get_latest_trace() -> Response:
    """
    Retrieve the most recent trace from the MATRIZ traces directory.

    Returns:
        JSON trace data with trace_id, or 404 if no traces available
    """
    try:
        # Determine prioritized search directories (ENV → LIVE → GOLD)
        for root in _iter_trace_dirs():
            files = _sorted_files_in(root)
            if not files:
                continue
            latest_file = files[0]
            trace_data = load_trace_file(latest_file)
            # Source hint when using goldens
            if root == GOLDEN_TRACES_PATH:
                trace_data["source"] = "golden_fallback"
            return Response(
                content=json.dumps(trace_data),
                status_code=status.HTTP_200_OK,
                media_type="application/json; charset=utf-8",
                headers={"Cache-Control": "no-store"},
            )

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found"})

    except HTTPException:
        # propagate precise errors (400/413/422/404)
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest trace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving trace",
        ) from e


SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]{1,256}$")


@router.get("/{trace_id}", response_model=dict, summary="Get trace by ID")
async def get_trace_by_id(trace_id: str) -> Response:
    """
    Retrieve a specific trace by its ID.

    Args:
        trace_id: The trace identifier

    Returns:
        JSON trace data, or 404 if trace not found
    """
    try:
        # quick guard against traversal attempts
        if not SAFE_ID_RE.match(trace_id):
            raise HTTPException(status_code=400, detail={"error": "bad_id"})

        # Build prioritized search set (ENV → LIVE → GOLD)
        dirs = _iter_trace_dirs()

        # Pass 1: match by trace_id in JSON
        for base in dirs:
            for trace_file in _iter_json_files(base):
                try:
                    trace_data = load_trace_file(trace_file)
                except HTTPException:
                    continue
                if str(trace_data.get("trace_id")) == str(trace_id):
                    if base == GOLDEN_TRACES_PATH:
                        trace_data["source"] = trace_data.get("source", "golden")
                    return Response(
                        content=json.dumps(trace_data),
                        media_type="application/json; charset=utf-8",
                        headers={"Cache-Control": "no-store"},
                    )

        # Pass 2: match by filename stem
        for base in dirs:
            candidate = (base / f"{trace_id}.json").resolve()
            if not _is_within(base, candidate) or not candidate.exists():
                continue
            trace_data = load_trace_file(candidate)
            if base == GOLDEN_TRACES_PATH:
                trace_data["source"] = trace_data.get("source", "golden")
            else:
                trace_data.setdefault("source", "direct_lookup")
            return Response(
                content=json.dumps(trace_data),
                media_type="application/json; charset=utf-8",
                headers={"Cache-Control": "no-store"},
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Trace '{trace_id}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trace {trace_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving trace",
        ) from e


@router.get(
    "/",
    response_model=dict,
    summary="List available traces with metadata",
    description=(
        "List traces across sources with paging and filters. Ordering: mtime desc, name asc. "
        "Query params: offset>=0, 1<=limit<=200, optional source filter (env|live|golden), "
        "q substring matches id or filename."
    ),
)
async def list_traces(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    source: Union[Literal["env", "live", "golden"], None] = None,
    q: Union[str, None] = None,
) -> Response:
    """
    Return a paged, filtered list of traces with metadata.
    """
    try:
        files = _sorted_all_files()
        items: list[dict[str, Any]] = []

        for p in files:
            try:
                size = p.stat().st_size
                mtime = int(p.stat().st_mtime)
            except OSError:
                continue

            src = _classify_root(p)
            if source and src != source:
                continue

            # Best-effort id from JSON, fallback to filename stem if invalid JSON/too-large
            try:
                data = load_trace_file(p)
                ident = str(data["trace_id"]) if data and "trace_id" in data else p.stem
            except HTTPException:
                ident = p.stem

            if q:
                ql = q.lower()
                if ql not in (ident.lower() + " " + p.name.lower()):
                    continue

            items.append(
                {
                    "id": ident,
                    "source": src,
                    "size_bytes": size,
                    "mtime": mtime,
                    "path": str(p),
                }
            )

        total = len(items)
        slice_items = items[offset : offset + limit]
        next_offset = offset + limit if (offset + limit) < total else None

        payload = {
            "total": total,
            "offset": offset,
            "limit": limit,
            "next_offset": next_offset,
            "traces": slice_items,
        }

        return Response(
            content=json.dumps(payload),
            status_code=status.HTTP_200_OK,
            media_type="application/json; charset=utf-8",
            headers={"Cache-Control": "no-store"},
        )
    except Exception as e:
        logger.error(f"Error listing traces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error listing traces",
        ) from e
