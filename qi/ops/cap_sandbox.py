# path: qi/ops/cap_sandbox.py
from __future__ import annotations
import os, time, json, fnmatch, hashlib, contextlib, builtins, io, subprocess, shlex
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional, Tuple, Iterable, Callable

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
AUDIT_DIR = os.path.join(STATE, "audit"); os.makedirs(AUDIT_DIR, exist_ok=True)
LEASES_PATH = os.path.join(STATE, "leases.json")  # persistent leases (ephemeral by default)

# --- capture originals before any monkey-patching happens ---
_ORIG_OPEN = builtins.open
_ORIG_REMOVE = os.remove
_ORIG_RENAME = os.rename
_ORIG_MKDIR = os.mkdir
_ORIG_MAKEDIRS = os.makedirs
_ORIG_RMDIR = os.rmdir

# ----------------- utilities -----------------
def _now() -> float: return time.time()
def _sha(s: str) -> str: return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _audit_write(kind: str, rec: Dict[str, Any]):
    """Write audit JSONL using original OS functions to avoid FileGuard recursion."""
    try:
        payload = {"ts": _now(), "kind": kind, **rec}
        _ORIG_MAKEDIRS(AUDIT_DIR, exist_ok=True)  # bypass patched makedirs
        path = os.path.join(AUDIT_DIR, "caps.jsonl")
        with _ORIG_OPEN(path, "a", encoding="utf-8") as f:  # bypass patched open
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # never explode the caller due to auditing problems
        pass

# ----------------- leases -----------------
@dataclass
class Lease:
    subject: str                 # e.g., "user:gonzalo" or "service:api"
    caps: List[str]              # e.g., ["net", "fs:read:/data/*.json", "api:google", "fs:write:/tmp/**"]
    ttl_sec: int                 # seconds from issued_at
    issued_at: float
    meta: Dict[str, Any]

    @property
    def expires_at(self) -> float:
        return self.issued_at + self.ttl_sec

    def alive(self, now: Optional[float] = None) -> bool:
        return (now or _now()) < self.expires_at

class CapError(Exception): pass
class FsDenied(CapError): pass

class CapManager:
    """
    Deny-by-default capability registry with TTL leases.

    Capability kinds (strings):
      - "net"                          -> network allowed
      - "api:<name>"                   -> named API allowed
      - "fs:read:<glob_or_path>"       -> allow read for path/glob
      - "fs:write:<glob_or_path>"      -> allow write for path/glob
    """
    def __init__(self, persist_path: str = LEASES_PATH):
        self.persist_path = persist_path
        self._leases: Dict[str, List[Lease]] = self._load()

    def _load(self) -> Dict[str, List[Lease]]:
        try:
            with _ORIG_OPEN(self.persist_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            out: Dict[str, List[Lease]] = {}
            for subj, arr in raw.items():
                out[subj] = [Lease(**x) for x in arr]
            return out
        except Exception:
            return {}

    def _save(self):
        tmp = self.persist_path + ".tmp"
        payload = {k: [asdict(lease) for lease in v] for k, v in self._leases.items()}
        _ORIG_MAKEDIRS(os.path.dirname(self.persist_path), exist_ok=True)
        with _ORIG_OPEN(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        os.replace(tmp, self.persist_path)

    def grant(self, subject: str, caps: List[str], ttl_sec: int, meta: Optional[Dict[str,Any]] = None, persist: bool = False) -> Lease:
        lease = Lease(subject=subject, caps=list(dict.fromkeys(caps)), ttl_sec=int(ttl_sec), issued_at=_now(), meta=meta or {})
        self._leases.setdefault(subject, []).append(lease)
        if persist: self._save()
        _audit_write("lease_grant", {"subject": subject, "caps": lease.caps, "ttl_sec": ttl_sec, "persist": persist})
        return lease

    def revoke(self, subject: str, cap_prefix: Optional[str] = None, persist: bool = False) -> int:
        arr = self._leases.get(subject, [])
        before = len(arr)
        if cap_prefix is None:
            arr = []
        else:
            arr = [l for l in arr if not any(c.startswith(cap_prefix) for c in l.caps)]
        self._leases[subject] = arr
        if persist: self._save()
        removed = before - len(arr)
        _audit_write("lease_revoke", {"subject": subject, "cap_prefix": cap_prefix, "removed": removed})
        return removed

    def list(self, subject: str, now: Optional[float] = None) -> List[Lease]:
        now = now or _now()
        return [l for l in self._leases.get(subject, []) if l.alive(now)]

    def require(self, subject: str, cap: str):
        if not self.has(subject, cap):
            raise CapError(f"Capability '{cap}' not granted for {subject}")

    def has(self, subject: str, cap: str) -> bool:
        """
        Supports:
          exact match (net, api:foo)
          fs:read:<path> / fs:write:<path> matches any lease with same prefix and glob pattern
        """
        now = _now()
        leases = self._leases.get(subject, [])
        cap_kind = cap.split(":", 1)[0]
        for l in leases:
            if not l.alive(now): 
                continue
            for c in l.caps:
                if c == cap:
                    return True
                if cap_kind in ("fs",) and c.startswith(cap_kind + ":"):
                    # c example: fs:read:/tmp/** ; fs:write:/var/log/*.log
                    try:
                        _, mode, patt = c.split(":", 2)
                    except ValueError:
                        continue
                    try:
                        _, need_mode, need_path = cap.split(":", 2)
                    except ValueError:
                        continue
                    if mode != need_mode:
                        continue
                    if fnmatch.fnmatch(os.path.abspath(need_path), os.path.abspath(patt)):
                        return True
        return False

# ----------------- ENV & FS sandbox -----------------
@dataclass
class EnvSpec:
    allow: List[str] = None        # prefixes allowed
    inject: Dict[str, str] = None  # explicit env vars

@dataclass
class FsSpec:
    read: List[str] = None   # glob patterns
    write: List[str] = None  # glob patterns
    cwd: Optional[str] = None

def _env_build(spec: Optional[EnvSpec]) -> Dict[str, str]:
    base = {}
    if spec and spec.inject:
        base.update(spec.inject)
    if spec and spec.allow:
        for k, v in os.environ.items():
            if any(k.startswith(p) for p in spec.allow):
                base[k] = v
    return base

def _check_path_allowed(path: str, allowed_globs: Iterable[str]) -> bool:
    ap = os.path.abspath(path)
    for patt in allowed_globs:
        if fnmatch.fnmatch(ap, os.path.abspath(patt)):
            return True
    return False

class FileGuard:
    """
    Python in-process guard that intercepts open/remove/rename *for this process*.
    It is NOT a kernel sandbox; it prevents accidental leaks in Python plugins.
    """
    def __init__(self, fs: FsSpec):
        self.fs = fs
        self._orig_open = builtins.open
        self._orig_remove = os.remove
        self._orig_rename = os.rename
        self._orig_mkdir = os.mkdir
        self._orig_makedirs = os.makedirs
        self._orig_rmdir = os.rmdir

    def _deny(self, path: str, op: str):
        _audit_write("fs_denied", {"op": op, "path": path})
        raise FsDenied(f"FS {op} not permitted for {path}")

    def _open(self, file, mode="r", *args, **kwargs):
        path = str(file)
        writing = any(m in mode for m in ("w", "a", "+", "x"))
        if writing:
            if not _check_path_allowed(path, self.fs.write or []):
                return self._deny(path, f"open({mode})")
        else:
            if not _check_path_allowed(path, self.fs.read or []):
                return self._deny(path, f"open({mode})")
        return self._orig_open(file, mode, *args, **kwargs)

    def _rm(self, path, *a, **k):
        if not _check_path_allowed(path, self.fs.write or []):
            return self._deny(path, "remove")
        return self._orig_remove(path, *a, **k)

    def _rn(self, src, dst, *a, **k):
        if not _check_path_allowed(src, self.fs.write or []) or not _check_path_allowed(dst, self.fs.write or []):
            return self._deny(f"{src} -> {dst}", "rename")
        return self._orig_rename(src, dst, *a, **k)

    def _mk(self, path, *a, **k):
        if not _check_path_allowed(path, self.fs.write or []):
            return self._deny(path, "mkdir")
        return self._orig_mkdir(path, *a, **k)

    def _mks(self, path, *a, **k):
        if not _check_path_allowed(path, self.fs.write or []):
            return self._deny(path, "makedirs")
        return self._orig_makedirs(path, *a, **k)

    def _rd(self, path, *a, **k):
        if not _check_path_allowed(path, self.fs.write or []):
            return self._deny(path, "rmdir")
        return self._orig_rmdir(path, *a, **k)

    @contextlib.contextmanager
    def activate(self):
        builtins.open = self._open  # type: ignore
        os.remove = self._rm        # type: ignore
        os.rename = self._rn        # type: ignore
        os.mkdir = self._mk         # type: ignore
        os.makedirs = self._mks     # type: ignore
        os.rmdir = self._rd         # type: ignore
        cwd_prev = None
        try:
            if self.fs.cwd:
                cwd_prev = os.getcwd()
                os.chdir(self.fs.cwd)
            yield
        finally:
            builtins.open = self._orig_open
            os.remove = self._orig_remove
            os.rename = self._orig_rename
            os.mkdir = self._orig_mkdir
            os.makedirs = self._orig_makedirs
            os.rmdir = self._orig_rmdir
            if cwd_prev: os.chdir(cwd_prev)

# ----------------- sandbox runner -----------------
@dataclass
class SandboxPlan:
    subject: str
    env: EnvSpec
    fs: FsSpec
    require: List[str]  # caps to check before run
    meta: Dict[str, Any]

class Sandbox:
    def __init__(self, manager: CapManager):
        self.mgr = manager

    def check_requirements(self, plan: SandboxPlan):
        for cap in plan.require:
            # FS requirements are expressed as concrete paths to be used
            if cap.startswith("fs:"):
                self.mgr.require(plan.subject, cap)
            else:
                self.mgr.require(plan.subject, cap)

    @contextlib.contextmanager
    def activate(self, plan: SandboxPlan):
        # Check caps
        self.check_requirements(plan)
        # Build env
        env = _env_build(plan.env) if plan.env else {}
        # Install FileGuard
        fg = FileGuard(plan.fs or FsSpec())
        with fg.activate():
            # apply env for child procs; in-proc env reads should use os.getenv (we left base empty by default)
            _audit_write("sandbox_enter", {"subject": plan.subject, "require": plan.require, "env_keys": list(env.keys()), "fs": asdict(plan.fs) if plan.fs else {}})
            try:
                yield env
            finally:
                _audit_write("sandbox_exit", {"subject": plan.subject})

    def run_cmd(self, plan: SandboxPlan, cmd: List[str], timeout: Optional[int] = None) -> Tuple[int, str]:
        with self.activate(plan) as env:
            # merge env with minimal PATH (unless provided)
            if "PATH" not in env:
                env["PATH"] = "/usr/bin:/bin:/usr/local/bin"
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
            try:
                out = proc.communicate(timeout=timeout)[0]
            except subprocess.TimeoutExpired:
                proc.kill()
                out = proc.communicate()[0]
            _audit_write("sandbox_run", {"cmd": cmd, "rc": proc.returncode})
            return proc.returncode, out

# ----------------- CLI -----------------
def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Lukhas Capability Sandbox (leases, FS/ENV isolation, audit)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g1 = sub.add_parser("grant")
    g1.add_argument("--subject", required=True)
    g1.add_argument("--cap", action="append", required=True, help="Capability (repeatable). Examples: net, api:google, fs:read:/tmp/**, fs:write:/tmp/**")
    g1.add_argument("--ttl", type=int, default=600)
    g1.add_argument("--persist", action="store_true")

    g2 = sub.add_parser("revoke")
    g2.add_argument("--subject", required=True)
    g2.add_argument("--prefix", help="cap prefix to revoke e.g. fs:write:", default=None)
    g2.add_argument("--persist", action="store_true")

    g3 = sub.add_parser("list")
    g3.add_argument("--subject", required=True)

    g4 = sub.add_parser("check")
    g4.add_argument("--subject", required=True)
    g4.add_argument("--cap", required=True)

    g5 = sub.add_parser("run")
    g5.add_argument("--subject", required=True)
    g5.add_argument("--require", action="append", default=[])
    g5.add_argument("--cwd")
    g5.add_argument("--fs-read", action="append", default=[])
    g5.add_argument("--fs-write", action="append", default=[])
    g5.add_argument("--env-allow", action="append", default=["PATH","HOME"])  # env prefixes to leak in
    g5.add_argument("--env", action="append", default=[], help="KEY=VALUE injections")
    g5.add_argument("--timeout", type=int)
    g5.add_argument("cmd", nargs=argparse.REMAINDER)

    args = ap.parse_args()
    mgr = CapManager()
    if args.cmd == "grant":
        lease = mgr.grant(args.subject, args.cap, args.ttl, persist=args.persist)
        print(json.dumps(asdict(lease), indent=2)); return
    if args.cmd == "revoke":
        n = mgr.revoke(args.subject, args.prefix, persist=args.persist)
        print(json.dumps({"removed": n}, indent=2)); return
    if args.cmd == "list":
        print(json.dumps([asdict(x) for x in mgr.list(args.subject)], indent=2)); return
    if args.cmd == "check":
        ok = mgr.has(args.subject, args.cap)
        print(json.dumps({"ok": ok}, indent=2)); raise SystemExit(0 if ok else 2)
    if args.cmd == "run":
        if not args.cmd:
            raise SystemExit("Provide command after --")
        env_inject = {}
        for kv in args.env:
            if "=" not in kv: continue
            k, v = kv.split("=", 1); env_inject[k] = v
        plan = SandboxPlan(
            subject=args.subject,
            env=EnvSpec(allow=args.env_allow, inject=env_inject),
            fs=FsSpec(read=args.fs_read, write=args.fs_write, cwd=args.cwd),
            require=list(args.require),
            meta={}
        )
        sb = Sandbox(mgr)
        rc, out = sb.run_cmd(plan, [c for c in args.cmd if c], timeout=args.timeout)
        print(out, end=""); raise SystemExit(rc)

if __name__ == "__main__":
    _cli()