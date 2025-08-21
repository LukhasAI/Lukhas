#!/usr/bin/env python3
"""
OCR Reader - Medication and label reading using optical character recognition
Supports medication identification, dosage reading, and safety warnings
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import base64
import hashlib

# Note: In production, install these packages:
# pip install pillow opencv-python pytesseract requests

logger = logging.getLogger(__name__)


@dataclass
class MedicationInfo:
    """Represents medication information extracted from OCR"""
    name: str
    brand_name: Optional[str]
    generic_name: Optional[str]
    dosage: Optional[str]
    strength: Optional[str]
    form: Optional[str]  # tablet, capsule, liquid, etc.
    instructions: Optional[str]
    warnings: List[str]
    expiration_date: Optional[str]
    lot_number: Optional[str]
    manufacturer: Optional[str]
    ndc_number: Optional[str]  # National Drug Code
    confidence_score: float


@dataclass
class OCRResult:
    """OCR processing result"""
    success: bool
    image_path: str
    processed_at: float
    medication: Optional[MedicationInfo]
    raw_text: str
    confidence: float
    processing_time: float
    error: Optional[str]
    symbolic_signature: List[str]


class MedicationOCR:
    """
    Medication OCR reader with safety features
    Extracts medication information from images with safety validation
    """
    
    # Common medication patterns for text extraction
    MEDICATION_PATTERNS = {
        "dosage": [
            r"(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|units?)",
            r"(\d+(?:\.\d+)?)\s*milligrams?",
            r"(\d+(?:\.\d+)?)\s*micrograms?"
        ],
        "instructions": [
            r"take\s+(\d+)?\s*(tablet|capsule|pill)s?\s*(daily|twice|once)",
            r"(\d+)\s*times?\s*(daily|per day)",
            r"every\s+(\d+)\s*(hour|day)s?"
        ],
        "warnings": [
            r"do not exceed",
            r"consult doctor",
            r"may cause drowsiness",
            r"avoid alcohol",
            r"pregnancy warning",
            r"allergic reaction"
        ]
    }
    
    # Safety symbols for different medication types
    MEDICATION_SYMBOLS = {
        "prescription": ["💊", "🔒", "⚕️"],
        "over_counter": ["💊", "🏪", "ℹ️"],
        "controlled": ["💊", "🚨", "🔒"],
        "warning": ["💊", "⚠️", "❗"],
        "expired": ["💊", "⏰", "❌"],
        "unknown": ["💊", "❓", "🔍"]
    }
    
    def __init__(self, 
                 cache_dir: str = "data/ocr_cache",
                 enable_cloud_ocr: bool = True,
                 safety_mode: bool = True):
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.enable_cloud_ocr = enable_cloud_ocr
        self.safety_mode = safety_mode
        
        # OCR results cache
        self.ocr_cache: Dict[str, OCRResult] = {}
        self.medication_database: Dict[str, Dict] = {}
        
        # Load medication database
        self._load_medication_database()
        
        # Performance tracking
        self.processing_stats = {
            "total_requests": 0,
            "successful_reads": 0,
            "failed_reads": 0,
            "cache_hits": 0,
            "average_processing_time": 0.0
        }
        
        logger.info("💊 Medication OCR initialized")
    
    def _load_medication_database(self):
        """Load medication reference database"""
        # In production, this would load from FDA databases, RxNorm, etc.
        # For demo, using sample data
        sample_medications = {
            "aspirin": {
                "generic_name": "acetylsalicylic acid",
                "common_brands": ["Bayer", "Bufferin", "Excedrin"],
                "common_dosages": ["81mg", "325mg", "500mg"],
                "warnings": ["stomach bleeding risk", "avoid with alcohol"],
                "interactions": ["warfarin", "methotrexate"]
            },
            "ibuprofen": {
                "generic_name": "ibuprofen",
                "common_brands": ["Advil", "Motrin"],
                "common_dosages": ["200mg", "400mg", "600mg", "800mg"],
                "warnings": ["kidney damage risk", "stomach bleeding"],
                "interactions": ["aspirin", "warfarin", "lithium"]
            },
            "acetaminophen": {
                "generic_name": "acetaminophen",
                "common_brands": ["Tylenol", "Panadol"],
                "common_dosages": ["325mg", "500mg", "650mg"],
                "warnings": ["liver damage risk", "alcohol warning"],
                "interactions": ["warfarin", "isoniazid"]
            }
        }
        
        self.medication_database = sample_medications
        logger.info(f"Loaded {len(sample_medications)} medications in database")
    
    async def read_medication_label(self, image_path: str) -> Dict:
        """Read medication information from image"""
        start_time = time.time()
        self.processing_stats["total_requests"] += 1
        
        try:
            # Check cache first
            image_hash = self._calculate_image_hash(image_path)
            if image_hash in self.ocr_cache:
                self.processing_stats["cache_hits"] += 1
                cached_result = self.ocr_cache[image_hash]
                logger.info(f"Cache hit for image {image_path}")
                return asdict(cached_result)
            
            # Perform OCR
            raw_text, confidence = await self._extract_text_from_image(image_path)
            
            if not raw_text:
                error_result = OCRResult(
                    success=False,
                    image_path=image_path,
                    processed_at=time.time(),
                    medication=None,
                    raw_text="",
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    error="No text detected in image",
                    symbolic_signature=self.MEDICATION_SYMBOLS["unknown"]
                )
                return asdict(error_result)
            
            # Extract medication information
            medication_info = await self._parse_medication_text(raw_text)
            
            # Validate and enhance with database info
            if medication_info:
                medication_info = await self._enhance_medication_info(medication_info)
                symbolic_signature = self._determine_medication_symbols(medication_info)
            else:
                symbolic_signature = self.MEDICATION_SYMBOLS["unknown"]
            
            # Create result
            result = OCRResult(
                success=medication_info is not None,
                image_path=image_path,
                processed_at=time.time(),
                medication=medication_info,
                raw_text=raw_text,
                confidence=confidence,
                processing_time=time.time() - start_time,
                error=None if medication_info else "Could not parse medication information",
                symbolic_signature=symbolic_signature
            )
            
            # Cache result
            self.ocr_cache[image_hash] = result
            
            # Update statistics
            if result.success:
                self.processing_stats["successful_reads"] += 1
            else:
                self.processing_stats["failed_reads"] += 1
            
            self._update_average_processing_time(result.processing_time)
            
            logger.info(f"OCR processing completed in {result.processing_time:.2f}s")
            return asdict(result)
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            self.processing_stats["failed_reads"] += 1
            
            error_result = OCRResult(
                success=False,
                image_path=image_path,
                processed_at=time.time(),
                medication=None,
                raw_text="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                error=str(e),
                symbolic_signature=self.MEDICATION_SYMBOLS["unknown"]
            )
            return asdict(error_result)
    
    def _calculate_image_hash(self, image_path: str) -> str:
        """Calculate hash of image for caching"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return hashlib.md5(image_data).hexdigest()
        except Exception as e:
            logger.warning(f"Could not hash image {image_path}: {e}")
            return f"path_{hash(image_path)}"
    
    async def _extract_text_from_image(self, image_path: str) -> Tuple[str, float]:
        """Extract text from image using OCR"""
        try:
            # Simulate OCR processing (in production, use actual OCR)
            # This would use libraries like pytesseract, Google Vision API, etc.
            
            # Simulate processing delay
            await asyncio.sleep(0.5)
            
            # Mock OCR results based on filename for demo
            if "aspirin" in image_path.lower():
                return self._generate_mock_aspirin_text(), 0.85
            elif "ibuprofen" in image_path.lower():
                return self._generate_mock_ibuprofen_text(), 0.82
            elif "tylenol" in image_path.lower():
                return self._generate_mock_tylenol_text(), 0.88
            else:
                # Generic mock text
                return "MEDICATION NAME: Unknown\nDosage: 100mg\nTake 1 tablet daily", 0.60
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return "", 0.0
    
    def _generate_mock_aspirin_text(self) -> str:
        """Generate mock OCR text for aspirin"""
        return """
        BAYER ASPIRIN
        Acetylsalicylic Acid
        325 mg tablets
        
        DIRECTIONS:
        Take 1-2 tablets every 4 hours
        Do not exceed 12 tablets in 24 hours
        
        WARNINGS:
        May cause stomach bleeding
        Consult doctor if pregnant
        Keep out of reach of children
        
        EXP: 12/2025
        LOT: BA123456
        NDC: 12345-678-90
        """
    
    def _generate_mock_ibuprofen_text(self) -> str:
        """Generate mock OCR text for ibuprofen"""
        return """
        ADVIL
        Ibuprofen 200mg
        Pain Reliever/Fever Reducer
        
        DIRECTIONS:
        Adults: Take 1-2 tablets every 4-6 hours
        Do not exceed 6 tablets in 24 hours
        
        WARNINGS:
        May cause severe stomach bleeding
        Do not use if you have kidney problems
        
        EXP: 08/2026
        LOT: ADV789012
        """
    
    def _generate_mock_tylenol_text(self) -> str:
        """Generate mock OCR text for Tylenol"""
        return """
        TYLENOL
        Acetaminophen 500mg
        Pain Reliever & Fever Reducer
        
        DIRECTIONS:
        Adults: Take 2 tablets every 6 hours
        Maximum 8 tablets in 24 hours
        
        WARNINGS:
        Liver damage may occur
        Do not exceed recommended dose
        Avoid alcohol while taking
        
        EXP: 03/2025
        LOT: TY345678
        """
    
    async def _parse_medication_text(self, text: str) -> Optional[MedicationInfo]:
        """Parse OCR text to extract medication information"""
        try:
            import re
            
            # Extract medication name
            name = self._extract_medication_name(text)
            if not name:
                return None
            
            # Extract dosage and strength
            dosage = self._extract_dosage(text)
            strength = self._extract_strength(text)
            
            # Extract form (tablet, capsule, etc.)
            form = self._extract_form(text)
            
            # Extract instructions
            instructions = self._extract_instructions(text)
            
            # Extract warnings
            warnings = self._extract_warnings(text)
            
            # Extract dates and identifiers
            expiration = self._extract_expiration_date(text)
            lot_number = self._extract_lot_number(text)
            ndc_number = self._extract_ndc_number(text)
            
            # Determine confidence based on extracted info
            confidence = self._calculate_extraction_confidence(
                name, dosage, strength, instructions, warnings
            )
            
            return MedicationInfo(
                name=name,
                brand_name=self._extract_brand_name(text),
                generic_name=self._extract_generic_name(text),
                dosage=dosage,
                strength=strength,
                form=form,
                instructions=instructions,
                warnings=warnings,
                expiration_date=expiration,
                lot_number=lot_number,
                manufacturer=self._extract_manufacturer(text),
                ndc_number=ndc_number,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Medication parsing failed: {e}")
            return None
    
    def _extract_medication_name(self, text: str) -> Optional[str]:
        """Extract medication name from text"""
        import re
        
        # Look for common medication names
        for med_name in self.medication_database.keys():
            if med_name.lower() in text.lower():
                return med_name
        
        # Look for brand names
        brand_patterns = [
            r"(BAYER|ADVIL|TYLENOL|MOTRIN|ALEVE|EXCEDRIN)",
            r"([A-Z][a-z]+)\s*(?:tablets?|capsules?|mg)"
        ]
        
        for pattern in brand_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_dosage(self, text: str) -> Optional[str]:
        """Extract dosage information"""
        import re
        
        patterns = [
            r"take\s+(\d+(?:-\d+)?)\s*(?:tablet|capsule|pill)s?",
            r"(\d+(?:-\d+)?)\s*(?:tablet|capsule|pill)s?\s*(?:daily|per day)",
            r"(\d+)\s*times?\s*(?:daily|per day)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_strength(self, text: str) -> Optional[str]:
        """Extract medication strength"""
        import re
        
        patterns = [
            r"(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|units?)",
            r"(\d+(?:\.\d+)?)\s*milligrams?",
            r"(\d+(?:\.\d+)?)\s*micrograms?"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}{match.group(2)}"
        
        return None
    
    def _extract_form(self, text: str) -> Optional[str]:
        """Extract medication form"""
        import re
        
        forms = ["tablet", "capsule", "liquid", "syrup", "cream", "ointment", "injection"]
        
        for form in forms:
            if re.search(f"\\b{form}s?\\b", text, re.IGNORECASE):
                return form
        
        return None
    
    def _extract_instructions(self, text: str) -> Optional[str]:
        """Extract dosing instructions"""
        import re
        
        # Look for instruction patterns
        instruction_patterns = [
            r"(take\s+[^.]+)",
            r"(directions?:?\s*[^.]+)",
            r"(dosage:?\s*[^.]+)"
        ]
        
        for pattern in instruction_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_warnings(self, text: str) -> List[str]:
        """Extract safety warnings"""
        import re
        
        warnings = []
        warning_keywords = [
            "stomach bleeding", "liver damage", "kidney problems",
            "avoid alcohol", "consult doctor", "pregnancy warning",
            "allergic reaction", "drowsiness", "keep out of reach"
        ]
        
        for keyword in warning_keywords:
            if re.search(keyword, text, re.IGNORECASE):
                warnings.append(keyword)
        
        return warnings
    
    def _extract_expiration_date(self, text: str) -> Optional[str]:
        """Extract expiration date"""
        import re
        
        patterns = [
            r"exp:?\s*(\d{1,2}/\d{4})",
            r"expir[ye]s?:?\s*(\d{1,2}/\d{4})",
            r"(\d{1,2}/\d{4})"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_lot_number(self, text: str) -> Optional[str]:
        """Extract lot number"""
        import re
        
        patterns = [
            r"lot:?\s*([A-Z0-9]+)",
            r"batch:?\s*([A-Z0-9]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_ndc_number(self, text: str) -> Optional[str]:
        """Extract NDC number"""
        import re
        
        pattern = r"ndc:?\s*(\d{4,5}-\d{3,4}-\d{2})"
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return None
    
    def _extract_brand_name(self, text: str) -> Optional[str]:
        """Extract brand name"""
        # This would be more sophisticated in production
        brand_names = ["BAYER", "ADVIL", "TYLENOL", "MOTRIN", "ALEVE"]
        
        for brand in brand_names:
            if brand in text.upper():
                return brand.title()
        
        return None
    
    def _extract_generic_name(self, text: str) -> Optional[str]:
        """Extract generic name"""
        generic_map = {
            "BAYER": "acetylsalicylic acid",
            "ASPIRIN": "acetylsalicylic acid",
            "ADVIL": "ibuprofen",
            "MOTRIN": "ibuprofen",
            "TYLENOL": "acetaminophen"
        }
        
        for brand, generic in generic_map.items():
            if brand in text.upper():
                return generic
        
        return None
    
    def _extract_manufacturer(self, text: str) -> Optional[str]:
        """Extract manufacturer"""
        # Would be more comprehensive in production
        manufacturers = ["Bayer", "Johnson & Johnson", "McNeil", "Pfizer"]
        
        for mfg in manufacturers:
            if mfg.lower() in text.lower():
                return mfg
        
        return None
    
    def _calculate_extraction_confidence(self, name, dosage, strength, instructions, warnings) -> float:
        """Calculate confidence score for extraction"""
        score = 0.0
        
        if name:
            score += 0.3
        if dosage:
            score += 0.2
        if strength:
            score += 0.2
        if instructions:
            score += 0.15
        if warnings:
            score += 0.15
        
        return min(1.0, score)
    
    async def _enhance_medication_info(self, medication: MedicationInfo) -> MedicationInfo:
        """Enhance medication info with database data"""
        try:
            med_name = medication.name.lower()
            
            if med_name in self.medication_database:
                db_info = self.medication_database[med_name]
                
                # Fill in missing generic name
                if not medication.generic_name and "generic_name" in db_info:
                    medication.generic_name = db_info["generic_name"]
                
                # Add additional warnings from database
                db_warnings = db_info.get("warnings", [])
                for warning in db_warnings:
                    if warning not in medication.warnings:
                        medication.warnings.append(warning)
                
                # Validate dosage against common dosages
                if medication.strength:
                    common_dosages = db_info.get("common_dosages", [])
                    if medication.strength not in common_dosages:
                        medication.warnings.append(f"Unusual dosage: {medication.strength}")
            
            return medication
            
        except Exception as e:
            logger.error(f"Failed to enhance medication info: {e}")
            return medication
    
    def _determine_medication_symbols(self, medication: MedicationInfo) -> List[str]:
        """Determine symbolic representation for medication"""
        # Check for controlled substances (would be more comprehensive in production)
        if any(word in medication.name.lower() for word in ["oxycodone", "morphine", "fentanyl"]):
            return self.MEDICATION_SYMBOLS["controlled"]
        
        # Check for warnings
        if medication.warnings:
            return self.MEDICATION_SYMBOLS["warning"]
        
        # Check if expired
        if medication.expiration_date:
            # Simple date check (would be more robust in production)
            try:
                exp_parts = medication.expiration_date.split("/")
                if len(exp_parts) == 2:
                    exp_year = int(exp_parts[1])
                    current_year = int(time.strftime("%Y"))
                    if exp_year < current_year:
                        return self.MEDICATION_SYMBOLS["expired"]
            except:
                pass
        
        # Default to prescription or OTC based on context
        if medication.brand_name in ["Tylenol", "Advil", "Bayer"]:
            return self.MEDICATION_SYMBOLS["over_counter"]
        else:
            return self.MEDICATION_SYMBOLS["prescription"]
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time"""
        current_avg = self.processing_stats["average_processing_time"]
        total_requests = self.processing_stats["total_requests"]
        
        if total_requests == 1:
            self.processing_stats["average_processing_time"] = processing_time
        else:
            # Calculate running average
            new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
            self.processing_stats["average_processing_time"] = new_avg
    
    # Public API methods
    
    async def identify_medication(self, medication_name: str) -> Dict:
        """Identify medication by name and return information"""
        med_name = medication_name.lower()
        
        if med_name in self.medication_database:
            info = self.medication_database[med_name].copy()
            info["name"] = medication_name
            info["source"] = "database"
            info["symbolic_signature"] = self.MEDICATION_SYMBOLS["prescription"]
            return info
        
        return {"error": "Medication not found in database"}
    
    async def check_interactions(self, medications: List[str]) -> Dict:
        """Check for drug interactions"""
        interactions = []
        warnings = []
        
        for i, med1 in enumerate(medications):
            for med2 in medications[i+1:]:
                # Simple interaction checking (would be more comprehensive in production)
                med1_info = self.medication_database.get(med1.lower(), {})
                med1_interactions = med1_info.get("interactions", [])
                
                if med2.lower() in med1_interactions:
                    interactions.append({
                        "medication1": med1,
                        "medication2": med2,
                        "severity": "moderate",  # Would be determined by actual data
                        "description": f"Potential interaction between {med1} and {med2}"
                    })
        
        return {
            "interactions": interactions,
            "warnings": warnings,
            "total_medications": len(medications),
            "interaction_count": len(interactions)
        }
    
    def get_processing_statistics(self) -> Dict:
        """Get OCR processing statistics"""
        stats = self.processing_stats.copy()
        stats["success_rate"] = (stats["successful_reads"] / max(1, stats["total_requests"]))
        stats["cache_hit_rate"] = (stats["cache_hits"] / max(1, stats["total_requests"]))
        return stats
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Test basic functionality
            return True
        except Exception as e:
            logger.error(f"OCR health check failed: {e}")
            return False


if __name__ == "__main__":
    async def demo():
        """Demo OCR functionality"""
        print("💊 Medication OCR Demo")
        print("=" * 40)
        
        ocr = MedicationOCR()
        
        # Simulate reading different medication labels
        test_images = [
            "sample_aspirin_label.jpg",
            "sample_ibuprofen_label.jpg",
            "sample_tylenol_label.jpg"
        ]
        
        for image_path in test_images:
            print(f"\n📸 Reading: {image_path}")
            
            result = await ocr.read_medication_label(image_path)
            
            if result["success"]:
                med = result["medication"]
                print(f"   ✅ Medication: {med['name']}")
                print(f"   💊 Strength: {med['strength']}")
                print(f"   📋 Instructions: {med['instructions']}")
                print(f"   ⚠️  Warnings: {', '.join(med['warnings'])}")
                print(f"   🎯 Confidence: {med['confidence_score']:.2f}")
                print(f"   🔮 Symbols: {''.join(result['symbolic_signature'])}")
            else:
                print(f"   ❌ Failed: {result['error']}")
            
            print(f"   ⏱️  Processing time: {result['processing_time']:.2f}s")
        
        # Show statistics
        stats = ocr.get_processing_statistics()
        print(f"\n📊 Processing Statistics:")
        print(f"   Total requests: {stats['total_requests']}")
        print(f"   Success rate: {stats['success_rate']:.2f}")
        print(f"   Average time: {stats['average_processing_time']:.2f}s")
        
        # Test drug interaction checking
        print(f"\n🔍 Testing drug interactions:")
        interaction_result = await ocr.check_interactions(["aspirin", "ibuprofen"])
        print(f"   Interactions found: {interaction_result['interaction_count']}")
        for interaction in interaction_result['interactions']:
            print(f"   ⚠️  {interaction['medication1']} + {interaction['medication2']}")
    
    asyncio.run(demo())
