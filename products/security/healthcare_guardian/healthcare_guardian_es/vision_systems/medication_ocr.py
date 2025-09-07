#!/usr/bin/env python3
"""
Medication OCR System for Healthcare Guardian
Consolidates OCR capabilities from Enhanced Guardian Medical
Specialized for Spanish medication labels and elderly users
"""
import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MedicationInfo:
    """Medication information extracted from OCR"""

    name: str
    brand_name: Optional[str]
    generic_name: Optional[str]
    dosage: Optional[str]
    strength: Optional[str]
    form: Optional[str]  # comprimidos, cápsulas, jarabe, etc.
    instructions: Optional[str]
    warnings: list[str]
    expiration_date: Optional[date]
    lot_number: Optional[str]
    manufacturer: Optional[str]
    cn_code: Optional[str]  # Código Nacional (Spanish medication code)
    confidence_score: float
    image_path: Optional[str]


@dataclass
class PillIdentification:
    """Visual pill identification result"""

    shape: str  # redonda, ovalada, cápsula
    color: str
    markings: Optional[str]
    size_mm: Optional[float]
    matched_medication: Optional[str]
    confidence: float


class MedicationOCRSystem:
    """
    OCR system for medication labels and pill identification
    Optimized for Spanish medications and elderly users
    """

    # Spanish medication patterns
    MEDICATION_PATTERNS = {
        "dosage": [
            r"(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|ui|unidades?)",
            r"(\d+(?:\.\d+)?)\s*miligramos?",
            r"(\d+(?:\.\d+)?)\s*microgramos?",
        ],
        "instructions": [
            r"tomar?\s+(\d+)?\s*(comprimido|cápsula|pastilla)s?\s*(cada|al día)",
            r"(\d+)\s*veces?\s*(al día|diarias?)",
            r"cada\s+(\d+)\s*horas?",
        ],
        "warnings": [
            r"no exceder",
            r"consulte? a su médico",
            r"puede producir somnolencia",
            r"evite el alcohol",
            r"no conducir",
            r"mantener fuera del alcance",
        ],
        "expiration": [
            r"cad\.?\s*:?\s*(\d{2})[/-](\d{2,4})",
            r"caducidad\s*:?\s*(\d{2})[/-](\d{2,4})",
            r"exp\.?\s*:?\s*(\d{2})[/-](\d{2,4})",
        ],
    }

    # Common Spanish medication forms
    MEDICATION_FORMS = {
        "comp": "comprimidos",
        "caps": "cápsulas",
        "sob": "sobres",
        "amp": "ampollas",
        "jar": "jarabe",
        "gotas": "gotas",
        "supos": "supositorios",
        "crema": "crema",
        "gel": "gel",
    }

    # Spanish medication database (subset)
    SPANISH_MEDICATIONS = {
        "paracetamol": {
            "forms": ["comprimidos", "sobres", "jarabe"],
            "strengths": ["500mg", "650mg", "1g"],
            "brands": ["Gelocatil", "Termalgin", "Efferalgan"],
        },
        "ibuprofeno": {
            "forms": ["comprimidos", "sobres", "jarabe"],
            "strengths": ["400mg", "600mg"],
            "brands": ["Neobrufen", "Espidifen", "Dalsy"],
        },
        "omeprazol": {
            "forms": ["cápsulas"],
            "strengths": ["20mg", "40mg"],
            "brands": ["Losec", "Pepticum", "Omeprazol Cinfa"],
        },
        "enalapril": {
            "forms": ["comprimidos"],
            "strengths": ["5mg", "10mg", "20mg"],
            "brands": ["Renitec", "Enalapril Normon"],
        },
        "metformina": {
            "forms": ["comprimidos"],
            "strengths": ["500mg", "850mg", "1000mg"],
            "brands": ["Dianben", "Metformina Cinfa"],
        },
    }

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize Medication OCR System

        Args:
            config: OCR configuration
        """
        self.config = config or {}

        # OCR settings
        self.ocr_language = self.config.get("ocr_language", "spa")
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.enable_pill_identification = self.config.get("auto_identify_pills", True)

        # Cache directory for processed images
        self.cache_dir = Path(self.config.get("cache_dir", "data/ocr_cache"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize OCR engine
        self._init_ocr_engine()

        # Processed medications cache
        self.medication_cache = {}

        logger.info("📸 Medication OCR System initialized")
        logger.info(f"OCR Language: {self.ocr_language}")
        logger.info(f"Pill identification: {self.enable_pill_identification}")

    def _init_ocr_engine(self):
        """Initialize OCR engine (Tesseract)"""
        try:
            import pytesseract

            # Check if Tesseract is installed
            pytesseract.get_tesseract_version()

            self.ocr_available = True
            logger.info("Tesseract OCR engine initialized")

        except Exception as e:
            logger.warning(f"OCR engine not available: {e}")
            logger.warning("Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr")
            self.ocr_available = False

    async def scan_medication_label(self, image_path: str) -> Optional[MedicationInfo]:
        """
        Scan a medication label and extract information

        Args:
            image_path: Path to medication label image

        Returns:
            Extracted medication information or None
        """
        if not self.ocr_available:
            logger.error("OCR engine not available")
            return None

        try:
            import cv2
            import pytesseract

            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return None

            # Preprocess for better OCR
            processed = await self._preprocess_image(image)

            # Perform OCR
            text = pytesseract.image_to_string(
                processed,
                lang=self.ocr_language,
                config="--psm 6",  # Uniform block of text
            )

            # Extract medication information
            medication = await self._extract_medication_info(text, image_path)

            # Cache the result
            if medication:
                cache_key = self._get_cache_key(image_path)
                self.medication_cache[cache_key] = medication

            return medication

        except Exception as e:
            logger.error(f"Error scanning medication label: {e}")
            return None

    async def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        import cv2

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to get black and white image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Denoise
        denoised = cv2.medianBlur(thresh, 3)

        # Resize if too small
        height, width = denoised.shape
        if width < 800:
            scale = 800 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            denoised = cv2.resize(denoised, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        return denoised

    async def _extract_medication_info(self, text: str, image_path: str) -> Optional[MedicationInfo]:
        """Extract structured medication information from OCR text"""
        if not text:
            return None

        # Clean text
        text = text.strip()
        lines = text.split("\n")

        # Initialize medication info
        info = MedicationInfo(
            name="Unknown",
            brand_name=None,
            generic_name=None,
            dosage=None,
            strength=None,
            form=None,
            instructions=None,
            warnings=[],
            expiration_date=None,
            lot_number=None,
            manufacturer=None,
            cn_code=None,
            confidence_score=0.0,
            image_path=image_path,
        )

        # Extract medication name (usually largest text)
        info.name = self._extract_medication_name(lines)

        # Extract strength and dosage
        info.strength, info.dosage = self._extract_dosage(text)

        # Extract form
        info.form = self._extract_form(text)

        # Extract instructions
        info.instructions = self._extract_instructions(text)

        # Extract warnings
        info.warnings = self._extract_warnings(text)

        # Extract expiration date
        info.expiration_date = self._extract_expiration(text)

        # Extract CN code (Spanish medication code)
        info.cn_code = self._extract_cn_code(text)

        # Calculate confidence score
        info.confidence_score = self._calculate_confidence(info)

        # Try to match with known medication
        matched = self._match_known_medication(info.name)
        if matched:
            info.generic_name = matched

        return info if info.confidence_score > self.confidence_threshold else None

    def _extract_medication_name(self, lines: list[str]) -> str:
        """Extract medication name from text lines"""
        # Usually the first non-empty line or the largest text
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:
                # Check if it matches known medications
                for med in self.SPANISH_MEDICATIONS:
                    if med.lower() in line.lower():
                        return line

                # Return first substantial line
                if not any(char.isdigit() for char in line[:3]):
                    return line

        return "Desconocido"

    def _extract_dosage(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """Extract strength and dosage from text"""
        strength = None
        dosage = None

        text_lower = text.lower()

        # Find strength patterns
        for pattern in self.MEDICATION_PATTERNS["dosage"]:
            match = re.search(pattern, text_lower)
            if match:
                strength = match.group(0)
                break

        # Find dosage instructions
        for pattern in self.MEDICATION_PATTERNS["instructions"]:
            match = re.search(pattern, text_lower)
            if match:
                dosage = match.group(0)
                break

        return strength, dosage

    def _extract_form(self, text: str) -> Optional[str]:
        """Extract medication form"""
        text_lower = text.lower()

        for abbr, full in self.MEDICATION_FORMS.items():
            if abbr in text_lower or full in text_lower:
                return full

        return None

    def _extract_instructions(self, text: str) -> Optional[str]:
        """Extract usage instructions"""
        text_lower = text.lower()

        # Look for instruction patterns
        instructions = []

        if "tomar" in text_lower:
            # Find the sentence with "tomar"
            for line in text.split("\n"):
                if "tomar" in line.lower():
                    instructions.append(line.strip())

        # Look for frequency patterns
        for pattern in self.MEDICATION_PATTERNS["instructions"]:
            match = re.search(pattern, text_lower)
            if match:
                instructions.append(match.group(0))

        return " ".join(instructions) if instructions else None

    def _extract_warnings(self, text: str) -> list[str]:
        """Extract warnings from text"""
        warnings = []
        text_lower = text.lower()

        for pattern in self.MEDICATION_PATTERNS["warnings"]:
            if re.search(pattern, text_lower):
                # Find the full sentence containing the warning
                for line in text.split("\n"):
                    if re.search(pattern, line.lower()):
                        warnings.append(line.strip())

        return warnings

    def _extract_expiration(self, text: str) -> Optional[date]:
        """Extract expiration date"""
        text_lower = text.lower()

        for pattern in self.MEDICATION_PATTERNS["expiration"]:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    month = int(match.group(1))
                    year_str = match.group(2)

                    # Handle 2-digit year
                    year = 2000 + int(year_str) if len(year_str) == 2 else int(year_str)

                    # Create date (last day of month)
                    import calendar

                    last_day = calendar.monthrange(year, month)[1]
                    return date(year, month, last_day)

                except (ValueError, IndexError):
                    pass

        return None

    def _extract_cn_code(self, text: str) -> Optional[str]:
        """Extract Spanish CN (Código Nacional) code"""
        # CN codes are 6-7 digits
        cn_pattern = r"CN[:\s]*(\d{6,7})"
        match = re.search(cn_pattern, text)

        if match:
            return match.group(1)

        # Also look for just 6-7 digit numbers that might be CN
        digit_pattern = r"\b(\d{6,7})\b"
        matches = re.findall(digit_pattern, text)

        # Return first match that looks like CN code
        for match in matches:
            if match.startswith(("6", "7", "8", "9")):  # Common CN prefixes
                return match

        return None

    def _calculate_confidence(self, info: MedicationInfo) -> float:
        """Calculate confidence score for extracted information"""
        score = 0.0
        max_score = 7.0

        # Check each field
        if info.name and info.name != "Desconocido":
            score += 2.0
        if info.strength:
            score += 1.5
        if info.form:
            score += 1.0
        if info.instructions:
            score += 1.0
        if info.cn_code:
            score += 1.0
        if info.expiration_date:
            score += 0.5

        return score / max_score

    def _match_known_medication(self, name: str) -> Optional[str]:
        """Match extracted name with known medications"""
        name_lower = name.lower()

        for med_name in self.SPANISH_MEDICATIONS:
            if med_name in name_lower:
                return med_name

        # Check brand names
        for med_name, info in self.SPANISH_MEDICATIONS.items():
            for brand in info.get("brands", []):
                if brand.lower() in name_lower:
                    return med_name

        return None

    async def identify_pill(self, image_path: str) -> Optional[PillIdentification]:
        """
        Identify a pill from its visual characteristics

        Args:
            image_path: Path to pill image

        Returns:
            Pill identification result
        """
        if not self.enable_pill_identification:
            return None

        try:
            import cv2

            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None

            # Extract pill characteristics
            shape = await self._identify_pill_shape(image)
            color = await self._identify_pill_color(image)
            markings = await self._extract_pill_markings(image)
            size = await self._estimate_pill_size(image)

            # Match with database
            matched_med = await self._match_pill_database(shape, color, markings)

            # Calculate confidence
            confidence = 0.8 if matched_med else 0.3

            return PillIdentification(
                shape=shape,
                color=color,
                markings=markings,
                size_mm=size,
                matched_medication=matched_med,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"Error identifying pill: {e}")
            return None

    async def _identify_pill_shape(self, image) -> str:
        """Identify pill shape from image"""
        # Simplified shape detection
        # In production, use ML model
        return "redonda"  # Default to round

    async def _identify_pill_color(self, image) -> str:
        """Identify dominant color of pill"""
        import cv2

        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Simple color detection (would be more sophisticated in production)
        # Get average color
        avg_color = cv2.mean(hsv)[:3]
        hue = avg_color[0]

        # Map hue to color name
        if hue < 20:
            return "rojo"
        elif hue < 35:
            return "naranja"
        elif hue < 85:
            return "amarillo"
        elif hue < 130:
            return "verde"
        elif hue < 170:
            return "azul"
        else:
            return "blanco"

    async def _extract_pill_markings(self, image) -> Optional[str]:
        """Extract text markings from pill"""
        # Would use OCR on enhanced pill image
        return None

    async def _estimate_pill_size(self, image) -> Optional[float]:
        """Estimate pill size in mm"""
        # Would need reference object or calibration
        return None

    async def _match_pill_database(self, shape: str, color: str, markings: Optional[str]) -> Optional[str]:
        """Match pill characteristics with database"""
        # Simplified matching
        # In production, use comprehensive pill database

        pill_database = {
            ("redonda", "blanco", None): "Paracetamol 500mg",
            ("ovalada", "rosa", None): "Ibuprofeno 600mg",
            ("cápsula", "azul", None): "Omeprazol 20mg",
        }

        return pill_database.get((shape, color, markings))

    def _get_cache_key(self, image_path: str) -> str:
        """Generate cache key for image"""
        return hashlib.md5(image_path.encode()).hexdigest()

    async def check_expiration(self, medication: MedicationInfo) -> dict[str, Any]:
        """
        Check if medication is expired or expiring soon

        Args:
            medication: Medication information

        Returns:
            Expiration status
        """
        if not medication.expiration_date:
            return {
                "status": "unknown",
                "message": "No se pudo leer la fecha de caducidad",
                "safe": False,
            }

        today = date.today()
        days_until_expiration = (medication.expiration_date - today).days

        if days_until_expiration < 0:
            return {
                "status": "expired",
                "message": f"⚠️ CADUCADO hace {abs(days_until_expiration)} días",
                "safe": False,
            }
        elif days_until_expiration < 30:
            return {
                "status": "expiring_soon",
                "message": f"⚡ Caduca en {days_until_expiration} días",
                "safe": True,
            }
        else:
            return {
                "status": "valid",
                "message": f"✅ Válido por {days_until_expiration} días",
                "safe": True,
            }

    def format_medication_for_voice(self, medication: MedicationInfo) -> str:
        """Format medication information for voice output"""
        response = f"He identificado {medication.name}"

        if medication.strength:
            response += f", {medication.strength}"

        if medication.form:
            response += f", en {medication.form}"

        if medication.instructions:
            response += f". {medication.instructions}"

        if medication.warnings:
            response += f". Atención: {medication.warnings[0]}"

        # Check expiration
        if medication.expiration_date:
            today = date.today()
            if medication.expiration_date < today:
                response += ". ¡Esta medicina está caducada! No la tome."
            elif (medication.expiration_date - today).days < 30:
                response += f". Esta medicina caduca pronto, el {medication.expiration_date.strftime('%d de %B')}"

        return response
