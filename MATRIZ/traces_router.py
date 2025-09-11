from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/traces", tags=["MATRIZ Traces"])

# Precedence: env override -> LIVE -> GOLD
_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def _roots() -> list[Path]:
    env = os.getenv("MATRIZ_TRACES_DIR")
    roots: list[Path] = []
    if env:
        p = Path(env).resolve()
        if p.exists() and p.is_dir():
            roots.append(p)
    live = Path("reports/matriz/traces").resolve()
    gold = Path("tests/golden/tier1").resolve()
    if live.exists() and live.is_dir():
        roots.append(live)
    if gold.exists() and gold.is_dir():
        roots.append(gold)
    return roots


def _iter_traces_dirs() -> list[Path]:
    # Deterministic, capped
    roots = _roots()
    # ensure uniqueness while preserving order
    seen = set()
    uniq: list[Path] = []
    for r in roots:
        if r not in seen:
            uniq.append(r)
            seen.add(r)
    return uniq


def _is_within(child: Path, root: Path) -> bool:
    try:
        child.relative_to(root)
        return True
    except Exception:
        return False


def _list_json_traces(root: Path, cap: int = 2000) -> list[Path]:
    out: list[Path] = []
    if not root.exists():
        return out
    for p in sorted(root.glob("*.json")):
        if len(out) >= cap:
            break
        if _is_within(p.resolve(), root.resolve()):
            out.append(p)
    return out


def _mtime_key(p: Path) -> tuple[float, str]:
    try:
        return (-p.stat().st_mtime, p.name)
    except Exception:
        return (0.0, p.name)


def _load_json(path: Path) -> dict:
    # Size guard: 5 MiB
    if path.stat().st_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Trace too large")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as err:
        raise HTTPException(status_code=422, detail="Malformed JSON") from err
    # Minimal schema: trace_id and timestamp
    if not isinstance(data, dict) or "trace_id" not in data or "timestamp" not in data:
        raise HTTPException(status_code=422, detail="Invalid trace schema")
    return data


def _classify(path: Path) -> str:
    roots = _iter_traces_dirs()
    labels = []
    env = os.getenv("MATRIZ_TRACES_DIR")
    for r in roots:
        if env and r == Path(env).resolve() and _is_within(path, r):
            labels.append("env")
        elif str(r).endswith("reports/matriz/traces") and _is_within(path, r):
            labels.append("live")
        elif str(r).endswith("tests/golden/tier1") and _is_within(path, r):
            labels.append("golden")
    return labels[0] if labels else "unknown"


@router.get("/", summary="List traces with paging and filters")
def list_traces(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    source: str | None = Query(None, pattern="^(env|live|golden)$"),
    q: str | None = Query(None, min_length=1, max_length=128),
):
    roots = _iter_traces_dirs()
    candidates: list[Path] = []
    for r in roots:
        candidates.extend(_list_json_traces(r))
    # sort before filtering/paging to get deterministic windows
    candidates.sort(key=_mtime_key)

    items = []
    for p in candidates:
        try:
            data = _load_json(p)
        except HTTPException:
            # Skip malformed in list; individual GET will surface 422
            continue
        tid = str(data.get("trace_id"))
        src = _classify(p.resolve())
        if source and src != source:
            continue
        if q and (q not in tid and q not in p.stem):
            continue
        items.append(
            {
                "id": tid,
                "source": src,
                "size_bytes": p.stat().st_size,
                "mtime": p.stat().st_mtime,
                "path": str(p),
            }
        )

    total = len(items)
    window = items[offset : offset + limit]
    next_offset = offset + limit if (offset + limit) < total else None
    resp = {"total": total, "offset": offset, "limit": limit, "next_offset": next_offset, "traces": window}
    return JSONResponse(content=resp, headers={"Cache-Control": "no-store"})


@router.get("/latest", summary="Return the latest trace")
def latest_trace():
    roots = _iter_traces_dirs()
    ranked: list[tuple[Path, float, str]] = [
        (p, p.stat().st_mtime, p.name) for r in roots for p in _list_json_traces(r)
    ]
    ranked.sort(key=lambda t: (-t[1], t[2]))
    if not ranked:
        raise HTTPException(status_code=404, detail="No traces available")

    path = ranked[0][0].resolve()
    data = _load_json(path)
    # hint if golden
    if _classify(path) == "golden":
        data.setdefault("source", "golden_fallback")
    return JSONResponse(content=data, headers={"Cache-Control": "no-store"})


@router.get("/{trace_id}", summary="Fetch a trace by id (trace_id field or filename stem)")
def by_id(trace_id: str):
    if not _ID_RE.match(trace_id):
        raise HTTPException(status_code=400, detail="Invalid trace_id")
    roots = _iter_traces_dirs()
    # Prefer matching JSON field trace_id; fallback to file stem
    # First pass: by JSON field
    for r in roots:
        for p in _list_json_traces(r):
            try:
                data = _load_json(p)
            except HTTPException:
                continue
            if str(data.get("trace_id")) == trace_id:
                return JSONResponse(content=data, headers={"Cache-Control": "no-store"})
    # Second pass: by filename stem
    for r in roots:
        cand = r / f"{trace_id}.json"
        if cand.exists():
            data = _load_json(cand.resolve())
            return JSONResponse(content=data, headers={"Cache-Control": "no-store"})
    raise HTTPException(status_code=404, detail="Trace not found")
