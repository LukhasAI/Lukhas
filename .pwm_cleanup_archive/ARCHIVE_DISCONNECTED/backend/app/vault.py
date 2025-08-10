"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : vault.py                                       │
│ DESCRIPTION : Upload + retrieve symbolic LUKHASID vault data  │
│ TYPE        : Encrypted Vault API                            │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import os
from datetime import datetime

from backend.app.audit_logger import log_action
from backend.app.cloud_storage import save_file_to_storage
from backend.app.crypto import (
    encrypt_data,
    generate_collapse_hash,
    generate_key_from_seed,
)
from backend.app.kyi_check import record_interaction
from backend.app.mesh_registry import register_mesh_event
from backend.app.symbolic_score import update_symbolic_score
from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter()

VAULT_STORAGE_DIR = "vault_storage"


@router.post("/vault/upload")
async def upload_vault_entry(
    user_id: int = Form(...),
    vault_type: str = Form(...),
    seed_phrase: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload a vault file encrypted using AES-256 based on user's seed phrase.
    """
    if not os.path.exists(VAULT_STORAGE_DIR):
        os.makedirs(VAULT_STORAGE_DIR)

    raw_data = await file.read()
    aes_key = generate_key_from_seed(seed_phrase)
    encrypted_data = encrypt_data(raw_data, aes_key)

    filename = f"{user_id}_{vault_type}_{datetime.utcnow().timestamp()}.enc"
    file_path = os.path.join(VAULT_STORAGE_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(encrypted_data)

    cloud_path = save_file_to_storage(file_path, filename)
    collapse_hash = generate_collapse_hash(user_id, vault_type, str(datetime.utcnow()))

    log_action(user_id, "VAULT_UPLOAD", f"type: {vault_type}, path: {cloud_path}")
    record_interaction(user_id, "vault_upload")
    update_symbolic_score(user_id, category="vault", value=1.0)
    register_mesh_event(
        user_id, event_type="vault", description=f"Uploaded {vault_type}"
    )

    print(
        f"✅ Encrypted vault uploaded for user {user_id}: {cloud_path} (collapse hash: {collapse_hash})"
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Encrypted vault uploaded successfully",
            "cloud_path": cloud_path,
            "collapse_hash": collapse_hash,
        },
    )


@router.get("/vault/test")
def test_vault_route():
    return {"message": "Vault endpoint online"}
