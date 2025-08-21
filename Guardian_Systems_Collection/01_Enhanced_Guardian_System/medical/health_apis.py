#!/usr/bin/env python3
"""
Health APIs - Integration with healthcare systems and medical databases
Provides access to medication information, healthcare services, and medical data
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import hashlib
import uuid

logger = logging.getLogger(__name__)


@dataclass
class HealthAPICredentials:
    """API credentials for healthcare services"""
    service_name: str
    api_key: str
    base_url: str
    rate_limit: int
    enabled: bool
    region: Optional[str]
    version: Optional[str]


@dataclass
class MedicationQuery:
    """Medication information query"""
    query_id: str
    medication_name: str
    query_type: str  # info, interactions, dosage, warnings
    timestamp: float
    results: Optional[Dict]
    source_api: Optional[str]
    confidence: float
    cached: bool


class HealthAPIManager:
    """
    Healthcare API integration manager
    Provides unified access to multiple healthcare APIs and databases
    """
    
    # Supported healthcare APIs
    SUPPORTED_APIS = {
        "clicsalud": {
            "name": "ClicSalud API",
            "description": "Spanish healthcare information system",
            "base_url": "https://api.clicsalud.com/v1",
            "features": ["medication_info", "drug_interactions", "healthcare_providers"],
            "regions": ["ES", "MX", "AR", "CO"],
            "rate_limit": 1000  # requests per hour
        },
        "fda_orange_book": {
            "name": "FDA Orange Book API",
            "description": "FDA approved drug products database",
            "base_url": "https://api.fda.gov/drug",
            "features": ["drug_approval", "generic_equivalents", "labeling"],
            "regions": ["US"],
            "rate_limit": 240  # requests per hour
        },
        "rxnorm": {
            "name": "RxNorm API",
            "description": "Normalized drug names and codes",
            "base_url": "https://rxnav.nlm.nih.gov/REST",
            "features": ["drug_names", "codes", "relationships"],
            "regions": ["US"],
            "rate_limit": 1000
        },
        "drugbank": {
            "name": "DrugBank API",
            "description": "Comprehensive drug information database",
            "base_url": "https://api.drugbank.com/v1",
            "features": ["drug_info", "interactions", "targets", "pathways"],
            "regions": ["GLOBAL"],
            "rate_limit": 500
        },
        "local_pharmacy": {
            "name": "Local Pharmacy API",
            "description": "Local pharmacy inventory and services",
            "base_url": "https://api.localpharmacy.com/v2",
            "features": ["inventory", "prescriptions", "refills"],
            "regions": ["LOCAL"],
            "rate_limit": 100
        }
    }
    
    # API response symbols
    API_SYMBOLS = {
        "success": ["✅", "💊", "📋"],
        "error": ["❌", "⚠️", "💊"],
        "cached": ["💾", "⚡", "💊"],
        "rate_limited": ["⏰", "🚫", "💊"],
        "no_data": ["❓", "🔍", "💊"]
    }
    
    def __init__(self, 
                 credentials_path: str = "config/api_credentials.yaml",
                 enabled_apis: List[str] = None,
                 cache_dir: str = "data/api_cache"):
        
        self.credentials_path = Path(credentials_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # API management
        self.credentials: Dict[str, HealthAPICredentials] = {}
        self.enabled_apis = enabled_apis or ["clicsalud", "fda_orange_book", "local_pharmacy"]
        
        # Response caching
        self.response_cache: Dict[str, Dict] = {}
        self.query_history: List[MedicationQuery] = []
        
        # Rate limiting
        self.api_usage: Dict[str, List[float]] = {}
        
        # Performance tracking
        self.api_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "cache_hits": 0,
            "rate_limited": 0,
            "average_response_time": 0.0
        }
        
        # Load credentials
        self._load_api_credentials()
        
        logger.info("🏥 Health API Manager initialized")
    
    def _load_api_credentials(self):
        """Load API credentials from configuration"""
        try:
            if self.credentials_path.exists():
                with open(self.credentials_path, 'r') as f:
                    import json
                    config = json.load(f)
                
                for api_name, creds in config.get("health_apis", {}).items():
                    if api_name in self.SUPPORTED_APIS:
                        credential = HealthAPICredentials(
                            service_name=api_name,
                            api_key=creds.get("api_key", ""),
                            base_url=creds.get("base_url", self.SUPPORTED_APIS[api_name]["base_url"]),
                            rate_limit=creds.get("rate_limit", self.SUPPORTED_APIS[api_name]["rate_limit"]),
                            enabled=creds.get("enabled", True),
                            region=creds.get("region"),
                            version=creds.get("version")
                        )
                        self.credentials[api_name] = credential
                
                logger.info(f"Loaded credentials for {len(self.credentials)} health APIs")
            else:
                # Create sample credentials file
                self._create_sample_credentials()
                
        except Exception as e:
            logger.warning(f"Failed to load API credentials: {e}")
            self._create_sample_credentials()
    
    def _create_sample_credentials(self):
        """Create sample credentials configuration"""
        sample_config = {
            "health_apis": {
                "clicsalud": {
                    "api_key": "your_clicsalud_api_key_here",
                    "enabled": True,
                    "region": "ES"
                },
                "fda_orange_book": {
                    "api_key": "your_fda_api_key_here",
                    "enabled": True,
                    "region": "US"
                },
                "local_pharmacy": {
                    "api_key": "your_pharmacy_api_key_here",
                    "base_url": "https://your-pharmacy-api.com/v1",
                    "enabled": False
                }
            }
        }
        
        try:
            self.credentials_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.credentials_path, 'w') as f:
                json.dump(sample_config, f, indent=2)
            
            logger.info(f"Created sample credentials file: {self.credentials_path}")
        except Exception as e:
            logger.error(f"Failed to create sample credentials: {e}")
    
    async def initialize_connections(self):
        """Initialize connections to health APIs"""
        logger.info("🏥 Initializing health API connections")
        
        # Test connectivity to each enabled API
        for api_name in self.enabled_apis:
            if api_name in self.credentials:
                try:
                    await self._test_api_connection(api_name)
                except Exception as e:
                    logger.warning(f"Failed to connect to {api_name}: {e}")
    
    async def _test_api_connection(self, api_name: str) -> bool:
        """Test connection to a health API"""
        try:
            # Simulate API connection test
            await asyncio.sleep(0.1)
            
            if api_name in self.credentials and self.credentials[api_name].enabled:
                logger.info(f"✅ Connected to {api_name}")
                return True
            else:
                logger.warning(f"❌ {api_name} not configured or disabled")
                return False
                
        except Exception as e:
            logger.error(f"Connection test failed for {api_name}: {e}")
            return False
    
    async def get_medication_info(self, medication_name: str, preferred_apis: List[str] = None) -> Dict:
        """Get comprehensive medication information"""
        start_time = time.time()
        query_id = str(uuid.uuid4())
        
        self.api_stats["total_queries"] += 1
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key("medication_info", medication_name)
            if cache_key in self.response_cache:
                self.api_stats["cache_hits"] += 1
                cached_result = self.response_cache[cache_key]
                cached_result["cached"] = True
                cached_result["response_time"] = time.time() - start_time
                
                logger.info(f"Cache hit for medication: {medication_name}")
                return cached_result
            
            # Query APIs
            apis_to_query = preferred_apis or self.enabled_apis
            results = {}
            
            for api_name in apis_to_query:
                if api_name in self.credentials and self.credentials[api_name].enabled:
                    try:
                        # Check rate limits
                        if not self._check_rate_limit(api_name):
                            self.api_stats["rate_limited"] += 1
                            continue
                        
                        # Query the API
                        api_result = await self._query_medication_api(api_name, medication_name)
                        if api_result:
                            results[api_name] = api_result
                            
                    except Exception as e:
                        logger.error(f"Error querying {api_name}: {e}")
                        continue
            
            # Combine results
            combined_result = self._combine_medication_results(medication_name, results)
            combined_result["response_time"] = time.time() - start_time
            combined_result["cached"] = False
            
            # Cache the result
            self.response_cache[cache_key] = combined_result
            
            # Log query
            query = MedicationQuery(
                query_id=query_id,
                medication_name=medication_name,
                query_type="info",
                timestamp=start_time,
                results=combined_result,
                source_api=list(results.keys())[0] if results else None,
                confidence=combined_result.get("confidence", 0.0),
                cached=False
            )
            self.query_history.append(query)
            
            if combined_result.get("success", False):
                self.api_stats["successful_queries"] += 1
            else:
                self.api_stats["failed_queries"] += 1
            
            self._update_average_response_time(combined_result["response_time"])
            
            logger.info(f"Medication info retrieved for {medication_name} in {combined_result['response_time']:.2f}s")
            return combined_result
            
        except Exception as e:
            logger.error(f"Medication info query failed: {e}")
            self.api_stats["failed_queries"] += 1
            
            return {
                "success": False,
                "error": str(e),
                "medication_name": medication_name,
                "response_time": time.time() - start_time,
                "symbolic_signature": self.API_SYMBOLS["error"]
            }
    
    async def _query_medication_api(self, api_name: str, medication_name: str) -> Optional[Dict]:
        """Query a specific medication API"""
        try:
            # Record API usage
            self._record_api_usage(api_name)
            
            # Simulate API call delay
            await asyncio.sleep(0.2)
            
            # Mock API responses based on medication name and API
            if api_name == "clicsalud":
                return self._mock_clicsalud_response(medication_name)
            elif api_name == "fda_orange_book":
                return self._mock_fda_response(medication_name)
            elif api_name == "local_pharmacy":
                return self._mock_pharmacy_response(medication_name)
            elif api_name == "drugbank":
                return self._mock_drugbank_response(medication_name)
            else:
                return None
                
        except Exception as e:
            logger.error(f"API query failed for {api_name}: {e}")
            return None
    
    def _mock_clicsalud_response(self, medication_name: str) -> Dict:
        """Mock ClicSalud API response"""
        return {
            "api": "clicsalud",
            "medication": medication_name,
            "generic_name": f"generic_{medication_name.lower()}",
            "therapeutic_class": "analgesic" if "aspirin" in medication_name.lower() else "unknown",
            "dosage_forms": ["tablet", "capsule"],
            "common_doses": ["100mg", "200mg", "500mg"],
            "contraindications": ["pregnancy", "kidney disease"],
            "side_effects": ["nausea", "dizziness"],
            "manufacturer": "Various",
            "availability": "prescription_required",
            "price_range": "€5-15",
            "language": "es",
            "confidence": 0.85
        }
    
    def _mock_fda_response(self, medication_name: str) -> Dict:
        """Mock FDA Orange Book API response"""
        return {
            "api": "fda_orange_book",
            "medication": medication_name,
            "approval_status": "approved",
            "approval_date": "2020-01-15",
            "ndc_numbers": ["12345-678-90", "98765-432-10"],
            "generic_available": True,
            "therapeutic_equivalents": ["AB", "AN"],
            "labeling_info": {
                "indication": f"Treatment with {medication_name}",
                "dosage": "As directed by physician",
                "warnings": ["Keep out of reach of children"]
            },
            "manufacturer_info": [
                {"name": "Pharmaceutical Co.", "status": "active"}
            ],
            "confidence": 0.9
        }
    
    def _mock_pharmacy_response(self, medication_name: str) -> Dict:
        """Mock local pharmacy API response"""
        return {
            "api": "local_pharmacy",
            "medication": medication_name,
            "in_stock": True,
            "quantity_available": 50,
            "price": "$12.99",
            "insurance_covered": True,
            "refills_remaining": 2,
            "last_filled": "2024-11-15",
            "pharmacy_info": {
                "name": "Local Pharmacy",
                "address": "123 Main St",
                "phone": "+1-555-PHARMACY"
            },
            "pickup_ready": False,
            "estimated_ready_time": "30 minutes",
            "confidence": 0.8
        }
    
    def _mock_drugbank_response(self, medication_name: str) -> Dict:
        """Mock DrugBank API response"""
        return {
            "api": "drugbank",
            "medication": medication_name,
            "drugbank_id": f"DB{hash(medication_name) % 10000:05d}",
            "chemical_formula": "C9H8O4",
            "molecular_weight": 180.16,
            "mechanism_of_action": "Inhibits cyclooxygenase enzymes",
            "pharmacokinetics": {
                "absorption": "Well absorbed orally",
                "metabolism": "Hepatic",
                "half_life": "2-3 hours",
                "excretion": "Renal"
            },
            "drug_interactions": [
                {
                    "drug": "warfarin",
                    "severity": "major",
                    "description": "Increased bleeding risk"
                }
            ],
            "targets": ["COX-1", "COX-2"],
            "pathways": ["Arachidonic acid metabolism"],
            "confidence": 0.92
        }
    
    def _combine_medication_results(self, medication_name: str, results: Dict[str, Dict]) -> Dict:
        """Combine results from multiple APIs"""
        if not results:
            return {
                "success": False,
                "medication_name": medication_name,
                "error": "No API responses received",
                "symbolic_signature": self.API_SYMBOLS["no_data"]
            }
        
        combined = {
            "success": True,
            "medication_name": medication_name,
            "api_sources": list(results.keys()),
            "source_count": len(results),
            "symbolic_signature": self.API_SYMBOLS["success"]
        }
        
        # Merge information from all sources
        all_info = {}
        confidence_scores = []
        
        for api_name, api_result in results.items():
            all_info[api_name] = api_result
            if "confidence" in api_result:
                confidence_scores.append(api_result["confidence"])
        
        # Calculate overall confidence
        if confidence_scores:
            combined["confidence"] = sum(confidence_scores) / len(confidence_scores)
        else:
            combined["confidence"] = 0.5
        
        # Extract key information
        combined["detailed_results"] = all_info
        
        # Merge common fields
        combined["generic_names"] = []
        combined["therapeutic_classes"] = []
        combined["warnings"] = []
        combined["side_effects"] = []
        
        for api_result in results.values():
            if "generic_name" in api_result:
                combined["generic_names"].append(api_result["generic_name"])
            if "therapeutic_class" in api_result:
                combined["therapeutic_classes"].append(api_result["therapeutic_class"])
            if "warnings" in api_result:
                combined["warnings"].extend(api_result["warnings"])
            if "side_effects" in api_result:
                combined["side_effects"].extend(api_result["side_effects"])
        
        # Remove duplicates
        combined["generic_names"] = list(set(combined["generic_names"]))
        combined["therapeutic_classes"] = list(set(combined["therapeutic_classes"]))
        combined["warnings"] = list(set(combined["warnings"]))
        combined["side_effects"] = list(set(combined["side_effects"]))
        
        return combined
    
    def _generate_cache_key(self, query_type: str, medication_name: str) -> str:
        """Generate cache key for API responses"""
        key_string = f"{query_type}_{medication_name.lower()}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """Check if API rate limit allows a request"""
        if api_name not in self.credentials:
            return False
        
        rate_limit = self.credentials[api_name].rate_limit
        current_time = time.time()
        
        # Initialize usage tracking
        if api_name not in self.api_usage:
            self.api_usage[api_name] = []
        
        # Remove old requests (older than 1 hour)
        hour_ago = current_time - 3600
        self.api_usage[api_name] = [
            timestamp for timestamp in self.api_usage[api_name]
            if timestamp > hour_ago
        ]
        
        # Check if under rate limit
        return len(self.api_usage[api_name]) < rate_limit
    
    def _record_api_usage(self, api_name: str):
        """Record API usage for rate limiting"""
        if api_name not in self.api_usage:
            self.api_usage[api_name] = []
        
        self.api_usage[api_name].append(time.time())
    
    def _update_average_response_time(self, response_time: float):
        """Update average response time"""
        current_avg = self.api_stats["average_response_time"]
        total_queries = self.api_stats["total_queries"]
        
        if total_queries == 1:
            self.api_stats["average_response_time"] = response_time
        else:
            new_avg = ((current_avg * (total_queries - 1)) + response_time) / total_queries
            self.api_stats["average_response_time"] = new_avg
    
    # Public API methods
    
    async def check_drug_interactions(self, medications: List[str]) -> Dict:
        """Check for drug interactions between medications"""
        start_time = time.time()
        
        try:
            interactions = []
            
            # Query each medication for interaction data
            medication_data = {}
            for med in medications:
                med_info = await self.get_medication_info(med)
                if med_info.get("success"):
                    medication_data[med] = med_info
            
            # Check for interactions
            for i, med1 in enumerate(medications):
                for med2 in medications[i+1:]:
                    interaction = await self._check_pair_interaction(med1, med2, medication_data)
                    if interaction:
                        interactions.append(interaction)
            
            return {
                "success": True,
                "medications": medications,
                "interactions": interactions,
                "interaction_count": len(interactions),
                "response_time": time.time() - start_time,
                "symbolic_signature": self.API_SYMBOLS["success"] if not interactions else ["⚠️", "💊", "🚨"]
            }
            
        except Exception as e:
            logger.error(f"Drug interaction check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "medications": medications,
                "response_time": time.time() - start_time,
                "symbolic_signature": self.API_SYMBOLS["error"]
            }
    
    async def _check_pair_interaction(self, med1: str, med2: str, medication_data: Dict) -> Optional[Dict]:
        """Check interaction between two specific medications"""
        # Simple interaction checking (would be more sophisticated in production)
        known_interactions = {
            ("aspirin", "warfarin"): {
                "severity": "major",
                "description": "Increased bleeding risk",
                "recommendation": "Monitor closely, consider alternative"
            },
            ("ibuprofen", "aspirin"): {
                "severity": "moderate",
                "description": "Reduced cardioprotective effect",
                "recommendation": "Space doses apart"
            }
        }
        
        # Check both directions
        for (drug1, drug2), interaction in known_interactions.items():
            if ((med1.lower() == drug1 and med2.lower() == drug2) or
                (med1.lower() == drug2 and med2.lower() == drug1)):
                
                return {
                    "medication1": med1,
                    "medication2": med2,
                    "severity": interaction["severity"],
                    "description": interaction["description"],
                    "recommendation": interaction["recommendation"],
                    "source": "internal_database"
                }
        
        return None
    
    async def find_local_pharmacies(self, location: str, medication: str = None) -> Dict:
        """Find local pharmacies with optional medication availability"""
        start_time = time.time()
        
        try:
            # Mock pharmacy search
            pharmacies = [
                {
                    "name": "Main Street Pharmacy",
                    "address": "123 Main St, Anytown",
                    "phone": "+1-555-PHARMACY",
                    "distance": "0.5 miles",
                    "hours": "Mon-Fri 9AM-9PM, Sat-Sun 9AM-6PM",
                    "services": ["prescription", "vaccinations", "consultation"],
                    "medication_available": True if medication else None,
                    "estimated_wait": "15 minutes"
                },
                {
                    "name": "Corner Drugstore",
                    "address": "456 Oak Ave, Anytown",
                    "phone": "+1-555-DRUGSTORE",
                    "distance": "1.2 miles",
                    "hours": "Mon-Sat 8AM-10PM, Sun 10AM-8PM",
                    "services": ["prescription", "delivery"],
                    "medication_available": False if medication else None,
                    "estimated_wait": "30 minutes"
                }
            ]
            
            return {
                "success": True,
                "location": location,
                "medication": medication,
                "pharmacies": pharmacies,
                "count": len(pharmacies),
                "response_time": time.time() - start_time,
                "symbolic_signature": ["🏪", "💊", "📍"]
            }
            
        except Exception as e:
            logger.error(f"Pharmacy search failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "location": location,
                "response_time": time.time() - start_time,
                "symbolic_signature": self.API_SYMBOLS["error"]
            }
    
    def get_api_statistics(self) -> Dict:
        """Get API usage statistics"""
        stats = self.api_stats.copy()
        
        # Add rate limit status
        stats["rate_limit_status"] = {}
        for api_name, usage_times in self.api_usage.items():
            current_usage = len(usage_times)
            rate_limit = self.credentials[api_name].rate_limit if api_name in self.credentials else 0
            stats["rate_limit_status"][api_name] = {
                "current_usage": current_usage,
                "rate_limit": rate_limit,
                "remaining": max(0, rate_limit - current_usage)
            }
        
        # Calculate success rate
        total_queries = stats["total_queries"]
        if total_queries > 0:
            stats["success_rate"] = stats["successful_queries"] / total_queries
            stats["cache_hit_rate"] = stats["cache_hits"] / total_queries
        else:
            stats["success_rate"] = 0.0
            stats["cache_hit_rate"] = 0.0
        
        return stats
    
    def get_available_apis(self) -> List[Dict]:
        """Get list of available APIs and their status"""
        apis = []
        
        for api_name, api_info in self.SUPPORTED_APIS.items():
            status = {
                "name": api_name,
                "description": api_info["description"],
                "features": api_info["features"],
                "regions": api_info["regions"],
                "configured": api_name in self.credentials,
                "enabled": api_name in self.credentials and self.credentials[api_name].enabled,
                "rate_limit": api_info["rate_limit"]
            }
            
            if api_name in self.api_usage:
                status["current_usage"] = len(self.api_usage[api_name])
            else:
                status["current_usage"] = 0
            
            apis.append(status)
        
        return apis
    
    async def health_check(self) -> bool:
        """Perform health check"""
        try:
            # Check if at least one API is configured and enabled
            enabled_apis = [
                api_name for api_name, creds in self.credentials.items()
                if creds.enabled
            ]
            
            if not enabled_apis:
                logger.warning("No health APIs are enabled")
                return False
            
            # Test connectivity to enabled APIs
            connectivity_tests = []
            for api_name in enabled_apis[:2]:  # Test first 2 APIs
                connectivity_tests.append(self._test_api_connection(api_name))
            
            results = await asyncio.gather(*connectivity_tests, return_exceptions=True)
            
            # Consider healthy if at least one API is reachable
            return any(result is True for result in results)
            
        except Exception as e:
            logger.error(f"Health API health check failed: {e}")
            return False


if __name__ == "__main__":
    async def demo():
        """Demo health API functionality"""
        print("🏥 Health API Manager Demo")
        print("=" * 40)
        
        api_manager = HealthAPIManager()
        await api_manager.initialize_connections()
        
        # Test medication information
        medications = ["aspirin", "ibuprofen", "unknown_medication"]
        
        for medication in medications:
            print(f"\n💊 Getting info for: {medication}")
            
            result = await api_manager.get_medication_info(medication)
            
            if result["success"]:
                print(f"   ✅ Found information")
                print(f"   📊 Confidence: {result['confidence']:.2f}")
                print(f"   🏥 Sources: {', '.join(result['api_sources'])}")
                print(f"   ⏱️  Response time: {result['response_time']:.2f}s")
                print(f"   🔮 Symbols: {''.join(result['symbolic_signature'])}")
                
                if result.get("warnings"):
                    print(f"   ⚠️  Warnings: {', '.join(result['warnings'][:2])}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Test drug interactions
        print(f"\n🔍 Checking interactions: aspirin + warfarin")
        interaction_result = await api_manager.check_drug_interactions(["aspirin", "warfarin"])
        
        if interaction_result["success"]:
            interactions = interaction_result["interactions"]
            print(f"   🚨 Found {len(interactions)} interactions")
            
            for interaction in interactions:
                print(f"   ⚠️  {interaction['medication1']} + {interaction['medication2']}")
                print(f"      Severity: {interaction['severity']}")
                print(f"      Description: {interaction['description']}")
        
        # Show API statistics
        stats = api_manager.get_api_statistics()
        print(f"\n📊 API Statistics:")
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Success rate: {stats['success_rate']:.2f}")
        print(f"   Cache hit rate: {stats['cache_hit_rate']:.2f}")
        print(f"   Average response time: {stats['average_response_time']:.2f}s")
        
        # Show available APIs
        available_apis = api_manager.get_available_apis()
        print(f"\n🌐 Available APIs:")
        for api in available_apis:
            status = "✅" if api["enabled"] else "❌"
            print(f"   {status} {api['name']}: {api['description'][:50]}...")
    
    asyncio.run(demo())
