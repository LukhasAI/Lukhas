"""
qr_encoder.py

QR Code encoder for CollapseHash verification data. Generates QR codes containing
hash signatures, verification links, and compact verification metadata for mobile
and offline verification workflows.

Purpose:
- Generate QR codes from CollapseHash data
- Encode verification URLs with embedded hash data
- Support multiple QR formats (URL, JSON, binary)
- Optimize for scanning reliability and data density

Dependencies:
- pip install qrcode[pil] pillow

Author: LUKHAS AGI Core
TODO: Implement QR generation with multiple encoding formats
TODO: Add error correction level optimization
TODO: Support batch QR generation for hash chains
TODO: Add custom QR styling and branding options
"""

# Optional imports for QR code generation
try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    from qrcode.image.pil import PilImage

    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

import base64
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


class CollapseQREncoder:
    """
    QR Code encoder for CollapseHash verification data.

    Supports multiple encoding formats:
    - URL format: Direct verification links
    - JSON format: Structured hash data
    - Binary format: Compact raw data
    """

    def __init__(self, base_url: str = "https://verify.collapsehash.org"):
        """
        Initialize QR encoder.

        Args:
            base_url (str): Base URL for verification links
        """
        self.base_url = base_url
        self.default_error_correction = (
            qrcode.constants.ERROR_CORRECT_M if QR_AVAILABLE else None
        )
        self.qr_config = {
            "box_size": 10,
            "border": 4,
            "fill_color": "black",
            "back_color": "white",
        }

    def encode_hash_to_qr(
        self,
        collapse_hash: str,
        signature: str,
        public_key: str,
        format_type: str = "url",
        error_correction: Optional[str] = None,
        save_path: Optional[str] = None,
        show_inline: bool = False,
        metadata: Optional[dict] = None,
        **kwargs,
    ) -> Optional[Any]:
        """
        Generate QR code from CollapseHash verification data.

        Args:
            collapse_hash (str): The CollapseHash value
            signature (str): Digital signature in hex
            public_key (str): Public key in hex
            format_type (str): Encoding format ("url", "json", "binary")
            error_correction (str): QR error correction level ('L','M','Q','H')
            save_path (str): If set, saves QR image to PNG
            show_inline (bool): If True, displays QR inline (Jupyter/IPython)
            metadata (dict): Optional extra metadata to encode
            **kwargs: Additional QR generation options

        Returns:
            PIL Image or None if QR library unavailable
        """
        if not QR_AVAILABLE:
            print(
                "Warning: QR code libraries not available. Install with: pip install qrcode[pil] pillow"
            )
            return None
        # Choose error correction level
        ec_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }
        ec_level = self.default_error_correction
        if error_correction and error_correction in ec_map:
            ec_level = ec_map[error_correction]
        # Format-specific encoding
        if format_type == "url":
            data = self._encode_url_format(
                collapse_hash, signature, public_key, metadata
            )
        elif format_type == "json":
            data = self._encode_json_format(
                collapse_hash, signature, public_key, metadata
            )
        elif format_type == "binary":
            data = self._encode_binary_format(
                collapse_hash, signature, public_key, metadata
            )
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
        img = self._generate_qr_image(data, error_correction=ec_level, **kwargs)
        if save_path and img:
            img.save(save_path)
        if show_inline and img:
            try:
                from IPython.display import display

                display(img)
            except ImportError:
                pass
        return img

    def _encode_url_format(
        self,
        collapse_hash: str,
        signature: str,
        public_key: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Encode verification data as URL.
        """
        # Minimal URL encoding, can include metadata as base64 if provided
        params = {"h": collapse_hash, "s": signature, "k": public_key}
        if metadata:
            # Encode metadata compactly
            meta_str = base64.urlsafe_b64encode(
                json.dumps(metadata, separators=(",", ":")).encode()
            ).decode()
            params["m"] = meta_str
        param_str = "&".join(
            f"{k}={params[k][:64] if k!='m' else params[k]}" for k in params
        )
        return f"{self.base_url}/verify?{param_str}"

    def _encode_json_format(
        self,
        collapse_hash: str,
        signature: str,
        public_key: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Encode verification data as JSON.
        """
        verification_data = {
            "version": "1.0",
            "hash": collapse_hash,
            "signature": signature,
            "public_key": public_key,
            "timestamp": None,
            "algorithm": "SPHINCS+-SHAKE256-128f-simple",
        }
        if metadata:
            verification_data["metadata"] = metadata
        return json.dumps(verification_data, separators=(",", ":"))

    def _encode_binary_format(
        self,
        collapse_hash: str,
        signature: str,
        public_key: str,
        metadata: Optional[dict] = None,
    ) -> str:
        """
        Encode verification data as base64-encoded binary, with optional metadata.
        """
        fields = [collapse_hash, signature, public_key]
        if metadata:
            fields.append(json.dumps(metadata, separators=(",", ":")))
        binary_data = "|".join(fields).encode("utf-8")
        return base64.b64encode(binary_data).decode("ascii")

    def _generate_qr_image(self, data: str, error_correction=None, **kwargs) -> Any:
        """
        Generate QR code image from encoded data.
        """
        if not QR_AVAILABLE:
            return None
        qr = qrcode.QRCode(
            version=None,
            error_correction=error_correction or self.default_error_correction,
            box_size=kwargs.get("box_size", self.qr_config["box_size"]),
            border=kwargs.get("border", self.qr_config["border"]),
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(
            fill_color=kwargs.get("fill_color", self.qr_config["fill_color"]),
            back_color=kwargs.get("back_color", self.qr_config["back_color"]),
        )
        return img

    def generate_verification_qr_batch(
        self,
        hash_chain: list,
        output_dir: Union[str, Path] = "qr_codes",
        format_type: str = "url",
        **kwargs,
    ) -> list:
        """
        Generate QR codes for a batch of CollapseHash entries.
        Args:
            hash_chain (list): List of dicts with at least hash, signature, public_key
            output_dir (str|Path): Directory to save QR images
        Returns:
            list: Paths to generated QR code files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        generated_files = []
        for i, hash_data in enumerate(hash_chain):
            filename = output_path / f"collapse_hash_{i:04d}.png"
            img = self.encode_hash_to_qr(
                hash_data.get("hash"),
                hash_data.get("signature"),
                hash_data.get("public_key"),
                format_type=format_type,
                save_path=str(filename),
                metadata=hash_data.get("metadata"),
                **kwargs,
            )
            generated_files.append(str(filename))
        return generated_files

    def decode_qr_to_hash(
        self, qr_image_path: Union[str, Path]
    ) -> Optional[Dict[str, Any]]:
        """
        Decode QR code image back to CollapseHash verification data.
        Not implemented; would require pyzbar or similar.
        """
        print(f"TODO: Decode QR code from {qr_image_path}")
        return None


def main():
    """
    Example usage and testing of QR encoder functionality.
    """
    print("CollapseHash QR Encoder")
    print("=======================")
    encoder = CollapseQREncoder()
    sample_hash = "a1b2c3d4e5f6" * 4  # 48 chars
    sample_signature = "0123456789abcdef" * 8  # 128 chars
    sample_pubkey = "fedcba9876543210" * 4  # 64 chars
    metadata = {"experiment_id": "qm_001", "entropy": 7.8}
    print("Generating sample QR codes...")
    for format_type in ["url", "json", "binary"]:
        print(f"- {format_type.upper()} format QR code")
        img = encoder.encode_hash_to_qr(
            sample_hash,
            sample_signature,
            sample_pubkey,
            format_type=format_type,
            error_correction="Q",
            metadata=metadata,
            save_path=f"sample_{format_type}.png",
        )
        if img:
            print(f"  Saved sample_{format_type}.png")
    print("\nQR Encoder ready for implementation!")


if __name__ == "__main__":
    main()
