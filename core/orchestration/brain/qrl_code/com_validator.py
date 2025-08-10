"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: com_validator.py
Advanced: com_validator.py
Integration Date: 2025-05-31T07:55:28.201511
"""


def validate_compliance(image_path: str) -> bool:
    with open(image_path, "rb") as f:
        exif_data = ExifImage(f)
    metadata = json.loads(exif_data.user_comment.decode())
    return all(
        [
            metadata.get("compliance", {}).get("GDPR") == "pseudonymized",
            metadata.get("compliance", {}).get("EU_AI_Act", {}).get("article13"),
        ]
    )
