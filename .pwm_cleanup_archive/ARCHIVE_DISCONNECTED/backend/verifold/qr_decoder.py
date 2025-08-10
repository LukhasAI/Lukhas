"""
qr_decoder.py

QR-G Decoder for GLYMPH symbolic memory capsules.

Purpose:
- Decode QR code from uploaded image
- Extract CollapseHash payload and Lukhas_ID
- Return decoded data as a dictionary

Dependencies:
- pip install pyzbar pillow

Author: LUKHAS AGI Core
"""

from io import BytesIO
from typing import Any, Dict

try:
    from PIL import Image
    from pyzbar.pyzbar import decode
except ImportError:
    raise ImportError(
        "Required packages not found. Please install with: pip install pyzbar pillow"
    )


def decode_from_image(image_bytes: BytesIO) -> Dict[str, Any]:
    """
    Decode symbolic memory QR-G from uploaded image.

    Args:
        image_bytes (BytesIO): The uploaded image in memory.

    Returns:
        dict: Decoded QR data, assumed to be JSON or URL-encoded.
    """
    image = Image.open(image_bytes)
    decoded_objects = decode(image)

    if not decoded_objects:
        raise ValueError("No QR code detected in image.")

    raw_data = decoded_objects[0].data.decode("utf-8")

    # Try JSON parse first, else fallback to URL parsing
    import json
    import urllib.parse

    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        # Try parsing URL query string format
        parsed = urllib.parse.urlparse(raw_data)
        query_params = urllib.parse.parse_qs(parsed.query)
        flattened = {k: v[0] for k, v in query_params.items()}
        return flattened
