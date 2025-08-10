"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : vault_downloads.py                             │
│ DESCRIPTION : Secure download routes for LUKHASID vault files │
│ TYPE        : Vault Data Access                              │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

VAULT_STORAGE_DIR = "vault_storage"


@router.get("/vault/download/{filename}")
def download_vault_file(filename: str):
    """
    Download an encrypted vault file for the user if exists.
    """
    file_path = os.path.join(VAULT_STORAGE_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Vault file not found")

    return FileResponse(
        file_path, media_type="application/octet-stream", filename=filename
    )
