# path: qi/glyphs/embed.py
"""
LUKHAS AI GLYPH Embedding System

Utilities for embedding cryptographic seals into various file formats.
Supports PNG, JPEG, PDF, text files, and more.
"""
from __future__ import annotations
import os, json, base64
from typing import Optional, Dict, Any, Tuple
from io import BytesIO

# Optional dependencies
try:
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

try:
    import piexif
    _HAS_PIEXIF = True
except ImportError:
    _HAS_PIEXIF = False

GLYPH_METADATA_KEY = "LUKHAS_GLYPH_SEAL"
GLYPH_TEXT_MARKER = "<!-- LUKHAS GLYPH SEAL:"
GLYPH_TEXT_END = "-->"

class EmbeddingError(Exception):
    """Error during seal embedding or extraction"""
    pass

def embed_seal_png(image_path: str, seal_data: Dict[str, Any], output_path: str) -> None:
    """
    Embed GLYPH seal into PNG file using tEXt chunk.
    
    Args:
        image_path: Input PNG file path
        seal_data: Complete seal data (seal + signature)
        output_path: Output PNG file path
    """
    if not _HAS_PIL:
        raise EmbeddingError("PIL (Pillow) required for PNG embedding")
    
    try:
        # Load image
        with Image.open(image_path) as img:
            # Create PNG info for metadata
            pnginfo = PngInfo()
            
            # Preserve existing metadata
            if hasattr(img, 'text'):
                for key, value in img.text.items():
                    if key != GLYPH_METADATA_KEY:  # Don't duplicate our key
                        pnginfo.add_text(key, value)
            
            # Add GLYPH seal
            seal_json = json.dumps(seal_data, separators=(',', ':'))
            pnginfo.add_text(GLYPH_METADATA_KEY, seal_json)
            
            # Save with metadata
            img.save(output_path, "PNG", pnginfo=pnginfo)
            
    except Exception as e:
        raise EmbeddingError(f"PNG embedding failed: {str(e)}")

def extract_seal_png(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract GLYPH seal from PNG file.
    
    Args:
        image_path: PNG file path
        
    Returns:
        Seal data or None if not found
    """
    if not _HAS_PIL:
        raise EmbeddingError("PIL (Pillow) required for PNG extraction")
    
    try:
        with Image.open(image_path) as img:
            if hasattr(img, 'text') and GLYPH_METADATA_KEY in img.text:
                seal_json = img.text[GLYPH_METADATA_KEY]
                return json.loads(seal_json)
        return None
    except Exception as e:
        raise EmbeddingError(f"PNG extraction failed: {str(e)}")

def embed_seal_jpeg(image_path: str, seal_data: Dict[str, Any], output_path: str) -> None:
    """
    Embed GLYPH seal into JPEG file using EXIF UserComment.
    
    Args:
        image_path: Input JPEG file path
        seal_data: Complete seal data
        output_path: Output JPEG file path
    """
    if not _HAS_PIEXIF:
        raise EmbeddingError("piexif required for JPEG embedding")
    
    try:
        # Load existing EXIF data
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        if os.path.exists(image_path):
            try:
                exif_dict = piexif.load(image_path)
            except Exception:
                # Create new EXIF if loading fails
                pass
        
        # Embed seal in UserComment (tag 37510)
        seal_json = json.dumps(seal_data, separators=(',', ':'))
        seal_bytes = seal_json.encode('utf-8')
        
        # EXIF UserComment format: encoding + data
        user_comment = b"UNICODE\x00" + seal_bytes
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = user_comment
        
        # Dump EXIF and save
        exif_bytes = piexif.dump(exif_dict)
        
        with Image.open(image_path) as img:
            img.save(output_path, "JPEG", exif=exif_bytes, quality=95)
            
    except Exception as e:
        raise EmbeddingError(f"JPEG embedding failed: {str(e)}")

def extract_seal_jpeg(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract GLYPH seal from JPEG file.
    
    Args:
        image_path: JPEG file path
        
    Returns:
        Seal data or None if not found
    """
    if not _HAS_PIEXIF:
        raise EmbeddingError("piexif required for JPEG extraction")
    
    try:
        exif_dict = piexif.load(image_path)
        
        if "Exif" in exif_dict and piexif.ExifIFD.UserComment in exif_dict["Exif"]:
            user_comment = exif_dict["Exif"][piexif.ExifIFD.UserComment]
            
            # Skip encoding prefix
            if user_comment.startswith(b"UNICODE\x00"):
                seal_bytes = user_comment[8:]  # Skip "UNICODE\x00"
                seal_json = seal_bytes.decode('utf-8')
                return json.loads(seal_json)
        
        return None
    except Exception as e:
        raise EmbeddingError(f"JPEG extraction failed: {str(e)}")

def embed_seal_text(text_content: str, seal_data: Dict[str, Any]) -> str:
    """
    Embed GLYPH seal into text content using HTML comment.
    
    Args:
        text_content: Original text content
        seal_data: Complete seal data
        
    Returns:
        Text content with embedded seal
    """
    try:
        seal_json = json.dumps(seal_data, separators=(',', ':'))
        seal_b64 = base64.b64encode(seal_json.encode('utf-8')).decode('ascii')
        
        seal_comment = f"{GLYPH_TEXT_MARKER} {seal_b64} {GLYPH_TEXT_END}"
        
        # For markdown/text files, add at the beginning
        return seal_comment + "\n\n" + text_content
        
    except Exception as e:
        raise EmbeddingError(f"Text embedding failed: {str(e)}")

def extract_seal_text(text_content: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Extract GLYPH seal from text content.
    
    Args:
        text_content: Text content potentially containing seal
        
    Returns:
        Tuple of (seal_data, clean_text_content)
    """
    try:
        # Find seal marker
        start_marker = GLYPH_TEXT_MARKER
        end_marker = GLYPH_TEXT_END
        
        start_idx = text_content.find(start_marker)
        if start_idx == -1:
            return None, text_content
        
        end_idx = text_content.find(end_marker, start_idx)
        if end_idx == -1:
            return None, text_content
        
        # Extract seal data
        seal_b64 = text_content[start_idx + len(start_marker):end_idx].strip()
        seal_json = base64.b64decode(seal_b64).decode('utf-8')
        seal_data = json.loads(seal_json)
        
        # Remove seal from content
        clean_content = text_content[:start_idx] + text_content[end_idx + len(end_marker):]
        clean_content = clean_content.strip()
        
        return seal_data, clean_content
        
    except Exception as e:
        raise EmbeddingError(f"Text extraction failed: {str(e)}")

def embed_seal_pdf(pdf_path: str, seal_data: Dict[str, Any], output_path: str) -> None:
    """
    Embed GLYPH seal into PDF metadata.
    
    Args:
        pdf_path: Input PDF file path
        seal_data: Complete seal data
        output_path: Output PDF file path
    """
    try:
        # For now, use simple approach - could integrate with PyPDF2/pypdf
        raise EmbeddingError("PDF embedding requires PyPDF2 integration (TODO)")
    except Exception as e:
        raise EmbeddingError(f"PDF embedding failed: {str(e)}")

def auto_embed_seal(file_path: str, seal_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Automatically embed seal based on file type.
    
    Args:
        file_path: Input file path
        seal_data: Complete seal data
        output_path: Output path (defaults to input_path + .sealed)
        
    Returns:
        Output file path
    """
    if not output_path:
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}.sealed{ext}"
    
    # Detect file type
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in ['.png']:
        embed_seal_png(file_path, seal_data, output_path)
    elif ext in ['.jpg', '.jpeg']:
        embed_seal_jpeg(file_path, seal_data, output_path)
    elif ext in ['.txt', '.md', '.html', '.csv']:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        sealed_content = embed_seal_text(content, seal_data)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sealed_content)
    elif ext in ['.pdf']:
        embed_seal_pdf(file_path, seal_data, output_path)
    else:
        raise EmbeddingError(f"Unsupported file type for embedding: {ext}")
    
    return output_path

def auto_extract_seal(file_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Automatically extract seal based on file type.
    
    Args:
        file_path: File path to extract from
        
    Returns:
        Tuple of (seal_data, clean_content_path_if_applicable)
    """
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in ['.png']:
        seal_data = extract_seal_png(file_path)
        return seal_data, None
    elif ext in ['.jpg', '.jpeg']:
        seal_data = extract_seal_jpeg(file_path)
        return seal_data, None
    elif ext in ['.txt', '.md', '.html', '.csv']:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        seal_data, clean_content = extract_seal_text(content)
        
        # Write clean content if seal was found
        if seal_data:
            base, ext = os.path.splitext(file_path)
            clean_path = f"{base}.clean{ext}"
            with open(clean_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            return seal_data, clean_path
        
        return seal_data, None
    else:
        raise EmbeddingError(f"Unsupported file type for extraction: {ext}")

# CLI Interface
def main():
    """CLI for embedding and extracting GLYPH seals"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LUKHAS AI GLYPH Embedding Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Embed command
    embed_parser = subparsers.add_parser("embed", help="Embed seal into file")
    embed_parser.add_argument("file", help="Input file")
    embed_parser.add_argument("seal", help="Seal JSON file")
    embed_parser.add_argument("--output", help="Output file (default: input.sealed.ext)")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract seal from file")
    extract_parser.add_argument("file", help="Input file")
    extract_parser.add_argument("--output", help="Output JSON file for seal")
    extract_parser.add_argument("--verify", help="Verify extracted seal against content")
    
    args = parser.parse_args()
    
    if args.command == "embed":
        try:
            # Load seal data
            with open(args.seal, 'r') as f:
                seal_data = json.load(f)
            
            # Embed seal
            output_path = auto_embed_seal(args.file, seal_data, args.output)
            print(f"Seal embedded successfully: {output_path}")
            
        except Exception as e:
            print(f"Embedding failed: {e}")
            return 1
    
    elif args.command == "extract":
        try:
            # Extract seal
            seal_data, clean_path = auto_extract_seal(args.file)
            
            if seal_data:
                # Save seal data
                output_file = args.output or f"{args.file}.seal.json"
                with open(output_file, 'w') as f:
                    json.dump(seal_data, f, indent=2)
                
                print(f"Seal extracted: {output_file}")
                if clean_path:
                    print(f"Clean content: {clean_path}")
                
                # Show seal info
                seal = seal_data.get("seal", {})
                print(f"Issuer: {seal.get('issuer')}")
                print(f"Model: {seal.get('model_id')}")
                print(f"Created: {seal.get('created_at')}")
                
            else:
                print("No GLYPH seal found in file")
                return 1
                
        except Exception as e:
            print(f"Extraction failed: {e}")
            return 1
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())