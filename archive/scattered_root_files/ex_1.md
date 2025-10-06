---
status: wip
type: documentation
---
⚠️  Ruff issues found (non-blocking)
[pre-commit] 🤖 AI-powered analysis...
[LUKHAS-LLM] ✅ Ollama and deepseek-coder model are available
[LUKHAS-LLM] Running comprehensive analysis on changed Python files...
[LUKHAS-LLM] Analyzing MATRIZ/__init__.py for security issues...
[LUKHAS-LLM] ⚠️  MATRIZ/__init__.py - security issues detected:
ISSUES FOUND: 1
28 SECURITY: Unsafe import from .core. It can lead to unauthorized access and potential security vulnerabilities if not properly controlled.
FIX: Implement proper control over the imported modules or packages, especially '.core'. Ensure it is being imported correctly with appropriate permissions and use a secure method of handling any potential security issues that may arise from improperly controlled imports.
[LUKHAS-LLM] Analyzing MATRIZ/__init__.py for lint issues...
[LUKHAS-LLM] ✅ MATRIZ/__init__.py - No lint issues found
[LUKHAS-LLM] Analyzing MATRIZ/__init__.py for bugs issues...
[LUKHAS-LLM] ⚠️  MATRIZ/__init__.py - bugs issues detected:
There doesn't seem to be any obvious issues in this Python script. However, it does contain some potential problems that might not cause a runtime error or buggy behavior. Here are the things I would look for:

1. `__author__` and `__version__` attributes should have meaningful values but it seems you've provided generic ones. You may want to update these in your actual script.
2. The Python imports at the start of the file could be wrong. It's not clear from this code snippet what modules are being imported, so double-check against the rest of your project for consistency and errors. In general, it is considered good practice to use absolute paths in Python imports unless you have a specific reason to do otherwise.
3. There doesn't seem to be any executable logic in this script. It seems more like a blueprint or module initialization file that might need further development before being used. If not using as intended, it will likely result in runtime errors.
4. The `__all__` variable should list the names of all public objects defined in this module for Python's built-in `dir()` function and similar tools to work correctly. Make sure these are indeed exported by your modules.
5. There is also a potential security risk here if there are any hardcoded credentials or sensitive data that should not be shared with others (not shown in the snippet).
6. Lastly, it's worth considering readability and formatting of this script as well to make sure it follows Python's best practices such as PEP8 style guide.

Note: No runtime problems or bugs found based on a static analysis of your code sample. The provided code doesn't seem executable due to lack of actual logic, import errors etc.

If these are not issues and there is no clear logical error or edge case identified then I would recommend running the program to see if it runs without any syntax or runtime issues.
[LUKHAS-LLM] ⚠️  Found issues in 2 analysis(es)
[pre-commit] ⚠️  AI analysis found issues (non-blocking - see output above)
[pre-commit] 🧪 Quick smoke tests...
 LUKHAS AI Governance Module loaded: Phase 7 - Registry Updates and Policy Integration
< Constellation Framework: Identity-Consciousness-Guardian
 Phase 7 ID Integration: Available
{"$kind": "MATRIZ_NODE", "version": 1, "schema_ref": "lukhas://schemas/matriz_node_v1.json", "id": "LT-66a6f7f2-92e4-4b24-911c-621976c925af", "type": "CONSENT", "state": {"confidence": 0.8, "salience": 0.6, "urgency": 0.2}, "timestamps": {"created_ts": 1756216532011}, "provenance": {"producer": "lukhas.governance.consent_ledger.api.record_consent", "capabilities": ["core:op"], "tenant": "default", "trace_id": "LT-local", "consent_scopes": ["system:internal"]}, "labels": ["governance:record"]}
✅ Core modules import and basic functionality works
[pre-commit] ✅ Core modules functional
[pre-commit] ✅ All validation checks completed successfully!
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
detect private key.......................................................Failed
- hook id: detect-private-key
- exit code: 1

Private key found: packages/auth/src/jwt.ts

Block trivial tests......................................................Passed
Block wildcard/sneaky mocks..............................................Passed
Block suspicious skip/xfail..............................................Passed
(.venv) agi_dev@g Lukhas %


..... then it goes:

help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:174:29
    |
172 |     def __init__(self):
173 |         self.anonymization_cache: Dict[str, str] = {}
174 |         self.reverse_cache: Dict[str, str] = {}
    |                             ^^^^
175 |         self.noise_epsilon = 1.0  # Differential privacy parameter
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:204:43
    |
202 |         return value + noise
203 |
204 |     def anonymize_statistics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
    |                                           ^^^^
205 |         """Anonymize statistics with differential privacy"""
206 |         anonymous_stats = {}
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:204:62
    |
202 |         return value + noise
203 |
204 |     def anonymize_statistics(self, stats: Dict[str, Any]) -> Dict[str, Any]:
    |                                                              ^^^^
205 |         """Anonymize statistics with differential privacy"""
206 |         anonymous_stats = {}
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:232:23
    |
230 |     def __init__(self, user_id: str):
231 |         self.user_id = user_id
232 |         self.symbols: Dict[str, PrivateSymbol] = {}
    |                       ^^^^
233 |         self.bindings: Dict[str, PrivateBinding] = {}
234 |         self.render_preferences: Dict[str, str] = {}  # concept_id -> preferred_symbol_id
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:233:24
    |
231 |         self.user_id = user_id
232 |         self.symbols: Dict[str, PrivateSymbol] = {}
233 |         self.bindings: Dict[str, PrivateBinding] = {}
    |                        ^^^^
234 |         self.render_preferences: Dict[str, str] = {}  # concept_id -> preferred_symbol_id
235 |         self.encryption = SymbolEncryption()
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:234:34
    |
232 |         self.symbols: Dict[str, PrivateSymbol] = {}
233 |         self.bindings: Dict[str, PrivateBinding] = {}
234 |         self.render_preferences: Dict[str, str] = {}  # concept_id -> preferred_symbol_id
    |                                  ^^^^
235 |         self.encryption = SymbolEncryption()
236 |         self.anonymizer = ConceptAnonymizer()
    |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/privacy.py:238:25
    |
236 |         self.anonymizer = ConceptAnonymizer()
237 |         self.privacy_mode = PrivacyLevel.LOCAL_ONLY
238 |         self.audit_log: List[Dict[str, Any]] = []
    |                         ^^^^
239 |
240 |         # Generate user-specific salt
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:238:30
    |
236 |         self.anonymizer = ConceptAnonymizer()
237 |         self.privacy_mode = PrivacyLevel.LOCAL_ONLY
238 |         self.audit_log: List[Dict[str, Any]] = []
    |                              ^^^^
239 |
240 |         # Generate user-specific salt
    |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/privacy.py:247:60
    |
246 |     def bind_symbol(self, token: Any, token_type: str, meaning_id: str,
247 |                    confidence: float = 1.0, tags: Optional[List[str]] = None) -> PrivateSymbol:
    |                                                            ^^^^
248 |         """Bind a private token to a universal meaning"""
249 |         # Create private symbol
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/privacy.py:291:54
    |
289 |         self._log_event("unbind", {"symbol_id": symbol_id})
290 |
291 |     def translate_private_to_universal(self, tokens: List[Any]) -> List[str]:
    |                                                      ^^^^
292 |         """
293 |         Translate private tokens to universal concept IDs.
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/privacy.py:291:68
    |
289 |         self._log_event("unbind", {"symbol_id": symbol_id})
290 |
291 |     def translate_private_to_universal(self, tokens: List[Any]) -> List[str]:
    |                                                                    ^^^^
292 |         """
293 |         Translate private tokens to universal concept IDs.
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/privacy.py:328:59
    |
326 |         return concept_ids
327 |
328 |     def translate_universal_to_private(self, concept_ids: List[str],
    |                                                           ^^^^
329 |                                       mode: str = "preferred") -> List[Any]:
330 |         """
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/privacy.py:329:67
    |
328 |     def translate_universal_to_private(self, concept_ids: List[str],
329 |                                       mode: str = "preferred") -> List[Any]:
    |                                                                   ^^^^
330 |         """
331 |         Translate universal concept IDs to private tokens.
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:495:36
    |
493 |             return False
494 |
495 |     def get_privacy_stats(self) -> Dict[str, Any]:
    |                                    ^^^^
496 |         """Get privacy-preserving statistics"""
497 |         raw_stats = {
    |
help: Replace with `dict`

C401 Unnecessary generator (rewrite as a set comprehension)
   --> universal_language/privacy.py:502:36
    |
500 |             "active_bindings": sum(1 for b in self.bindings.values() if b.active),
501 |             "total_usage": sum(s.usage_count for s in self.symbols.values()),
502 |             "unique_concepts": len(set(b.meaning_id for b in self.bindings.values()))
    |                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
503 |         }
    |
help: Rewrite as a set comprehension

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/privacy.py:527:60
    |
525 |         return None
526 |
527 |     def _find_symbols_by_meaning(self, meaning_id: str) -> List[PrivateSymbol]:
    |                                                            ^^^^
528 |         """Find all symbols bound to a meaning"""
529 |         matching_symbols = []
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:546:53
    |
544 |         return None
545 |
546 |     def _log_event(self, event_type: str, metadata: Dict[str, Any]):
    |                                                     ^^^^
547 |         """Log vault event for audit"""
548 |         self.audit_log.append({
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/privacy.py:560:19
    |
559 | # Singleton instances per user
560 | _vault_instances: Dict[str, PrivateSymbolVault] = {}
    |                   ^^^^
    |
help: Replace with `dict`

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> universal_language/service.py:23:1
   |
21 | from datetime import datetime, timedelta, timezone
22 | from pathlib import Path
23 | from typing import Any, Dict, List, Optional, Tuple
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
24 |
25 | from cryptography.fernet import Fernet
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> universal_language/service.py:23:1
   |
21 | from datetime import datetime, timedelta, timezone
22 | from pathlib import Path
23 | from typing import Any, Dict, List, Optional, Tuple
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
24 |
25 | from cryptography.fernet import Fernet
   |

UP035 `typing.Tuple` is deprecated, use `tuple` instead
  --> universal_language/service.py:23:1
   |
21 | from datetime import datetime, timedelta, timezone
22 | from pathlib import Path
23 | from typing import Any, Dict, List, Optional, Tuple
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
24 |
25 | from cryptography.fernet import Fernet
   |

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/service.py:57:23
   |
55 |         self.storage_path = Path(storage_path)
56 |         self.encryption_key = None
57 |         self.symbols: Dict[str, PersonalSymbol] = {}
   |                       ^^^^
58 |         self.compositions: Dict[str, Dict[str, Any]] = {}
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/service.py:58:28
   |
56 |         self.encryption_key = None
57 |         self.symbols: Dict[str, PersonalSymbol] = {}
58 |         self.compositions: Dict[str, Dict[str, Any]] = {}
   |                            ^^^^
59 |
60 |     def initialize(self, device_key: str):
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/service.py:58:38
   |
56 |         self.encryption_key = None
57 |         self.symbols: Dict[str, PersonalSymbol] = {}
58 |         self.compositions: Dict[str, Dict[str, Any]] = {}
   |                                      ^^^^
59 |
60 |     def initialize(self, device_key: str):
   |
help: Replace with `dict`

F841 Local variable `key` is assigned to but never used
  --> universal_language/service.py:73:9
   |
71 |             iterations=100000,
72 |         )
73 |         key = kdf.derive(device_key.encode())
   |         ^^^
74 |         self.encryption_key = Fernet(Fernet.generate_key())  # Mock for now
   |
help: Remove assignment to unused variable `key`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/service.py:121:56
    |
119 |         return symbol
120 |
121 |     def find_symbols_by_meaning(self, meaning: str) -> List[PersonalSymbol]:
    |                                                        ^^^^
122 |         """Find all symbols bound to a specific meaning"""
123 |         return [
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/service.py:152:57
    |
150 |         return False
151 |
152 |     def create_composition(self, name: str, symbol_ids: List[str], operators: List[str], meaning: str) -> str:
    |                                                         ^^^^
153 |         """
154 |         Create a symbol composition.
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/service.py:152:79
    |
150 |         return False
151 |
152 |     def create_composition(self, name: str, symbol_ids: List[str], operators: List[str], meaning: str) -> str:
    |                                                                               ^^^^
153 |         """
154 |         Create a symbol composition.
    |
help: Replace with `list`

F841 Local variable `decrypted_data` is assigned to but never used
   --> universal_language/service.py:183:13
    |
181 |             # Decrypt (mock for development)
182 |             # In production: use Fernet or similar
183 |             decrypted_data = encrypted_data  # Mock: pretend it's decrypted
    |             ^^^^^^^^^^^^^^
184 |
185 |             # Parse JSON (if it were real encrypted data)
    |
help: Remove assignment to unused variable `decrypted_data`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/service.py:211:37
    |
209 |         self.storage_path.write_bytes(encrypted_data)
210 |
211 |     def _serialize_symbols(self) -> Dict[str, Any]:
    |                                     ^^^^
212 |         """Serialize symbols for storage"""
213 |         return {
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/service.py:243:33
    |
242 |     def __init__(self):
243 |         self.active_challenges: Dict[str, CompositionChallenge] = {}
    |                                 ^^^^
244 |         self.verified_signatures: Dict[str, ULSignature] = {}
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/service.py:244:35
    |
242 |     def __init__(self):
243 |         self.active_challenges: Dict[str, CompositionChallenge] = {}
244 |         self.verified_signatures: Dict[str, ULSignature] = {}
    |                                   ^^^^
245 |
246 |     async def generate_challenge(
    |
help: Replace with `dict`

ARG002 Unused method argument: `lid`
   --> universal_language/service.py:248:9
    |
246 |     async def generate_challenge(
247 |         self,
248 |         lid: str,
    |         ^^^
249 |         action: str,
250 |         required_meanings: List[str]
    |

ARG002 Unused method argument: `action`
   --> universal_language/service.py:249:9
    |
247 |         self,
248 |         lid: str,
249 |         action: str,
    |         ^^^^^^
250 |         required_meanings: List[str]
251 |     ) -> CompositionChallenge:
    |

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/service.py:250:28
    |
248 |         lid: str,
249 |         action: str,
250 |         required_meanings: List[str]
    |                            ^^^^
251 |     ) -> CompositionChallenge:
252 |         """
    |
help: Replace with `list`

ARG002 Unused method argument: `lid`
   --> universal_language/service.py:291:9
    |
289 |     async def verify_composition_proof(
290 |         self,
291 |         lid: str,
    |         ^^^
292 |         proof: CompositionProof
293 |     ) -> bool:
    |

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/service.py:334:24
    |
332 |         lid: str,
333 |         action: str,
334 |         symbol_proofs: List[str],
    |                        ^^^^
335 |         composition_proof: Optional[CompositionProof] = None
336 |     ) -> ULSignature:
    |
help: Replace with `list`

SIM103 Return the negated condition directly
   --> universal_language/service.py:395:9
    |
394 |           # Check composition if required
395 | /         if requires_composition(action) and not signature.composition_proof:
396 | |             return False
397 | |
398 | |         return True
    | |___________________^
    |
help: Inline condition

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/service.py:484:27
    |
482 |         self,
483 |         challenge: CompositionChallenge,
484 |         symbol_data_list: List[Tuple[Any, SymbolType]]
    |                           ^^^^
485 |     ) -> CompositionProof:
486 |         """
    |
help: Replace with `list`

UP006 Use `tuple` instead of `Tuple` for type annotation
   --> universal_language/service.py:484:32
    |
482 |         self,
483 |         challenge: CompositionChallenge,
484 |         symbol_data_list: List[Tuple[Any, SymbolType]]
    |                                ^^^^^
485 |     ) -> CompositionProof:
486 |         """
    |
help: Replace with `tuple`

F841 Local variable `power_symbol_id` is assigned to but never used
   --> universal_language/service.py:579:5
    |
577 |     print("📝 Binding personal symbols...")
578 |
579 |     power_symbol_id = await service.bind_symbol(
    |     ^^^^^^^^^^^^^^^
580 |         SymbolType.EMOJI,
581 |         "⚡️💪",  # Lightning + muscle = power
    |
help: Remove assignment to unused variable `power_symbol_id`

F841 Local variable `responsibility_symbol_id` is assigned to but never used
   --> universal_language/service.py:586:5
    |
584 |     )
585 |
586 |     responsibility_symbol_id = await service.bind_symbol(
    |     ^^^^^^^^^^^^^^^^^^^^^^^^
587 |         SymbolType.WORD,
588 |         "with great power",
    |
help: Remove assignment to unused variable `responsibility_symbol_id`

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> universal_language/translator.py:13:1
   |
11 | from dataclasses import dataclass, field
12 | from enum import Enum
13 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
14 |
15 | from universal_language.core import Concept, ConceptType, Symbol, SymbolicDomain
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> universal_language/translator.py:13:1
   |
11 | from dataclasses import dataclass, field
12 | from enum import Enum
13 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
14 |
15 | from universal_language.core import Concept, ConceptType, Symbol, SymbolicDomain
   |

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/translator.py:41:15
   |
39 |     translation_type: TranslationType
40 |     confidence: float = 1.0
41 |     metadata: Dict[str, Any] = field(default_factory=dict)
   |               ^^^^
42 |     trace: List[str] = field(default_factory=list)
   |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
  --> universal_language/translator.py:42:12
   |
40 |     confidence: float = 1.0
41 |     metadata: Dict[str, Any] = field(default_factory=dict)
42 |     trace: List[str] = field(default_factory=list)
   |            ^^^^
43 |
44 |     def is_successful(self) -> bool:
   |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/translator.py:48:26
   |
46 |         return self.target is not None and self.confidence > 0.5
47 |
48 |     def to_dict(self) -> Dict[str, Any]:
   |                          ^^^^
49 |         """Convert to dictionary representation"""
50 |         return {
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/translator.py:68:29
   |
66 |     def __init__(self):
67 |         self.vocabulary = get_unified_vocabulary()
68 |         self.concept_cache: Dict[str, Concept] = {}
   |                             ^^^^
69 |         self.symbol_cache: Dict[str, Symbol] = {}
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/translator.py:69:28
   |
67 |         self.vocabulary = get_unified_vocabulary()
68 |         self.concept_cache: Dict[str, Concept] = {}
69 |         self.symbol_cache: Dict[str, Symbol] = {}
   |                            ^^^^
70 |
71 |     def symbol_to_concept(self, symbol: Symbol) -> Optional[Concept]:
   |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
  --> universal_language/translator.py:90:53
   |
88 |         return concept
89 |
90 |     def symbols_to_composite_concept(self, symbols: List[Symbol]) -> Concept:
   |                                                     ^^^^
91 |         """Combine multiple symbols into a composite concept"""
92 |         # Determine primary domain
   |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/translator.py:111:55
    |
109 |         return concept
110 |
111 |     def concept_to_symbols(self, concept: Concept) -> List[Symbol]:
    |                                                       ^^^^
112 |         """Extract symbols from a concept"""
113 |         if concept.symbols:
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/translator.py:141:78
    |
139 |         return symbols
140 |
141 |     def find_related_concepts(self, concept: Concept, max_depth: int = 2) -> List[Concept]:
    |                                                                              ^^^^
142 |         """Find concepts related to a given concept"""
143 |         related = []
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/translator.py:215:39
    |
213 |         self.modality_mappings = self._initialize_mappings()
214 |
215 |     def _initialize_mappings(self) -> Dict[str, Dict[str, Any]]:
    |                                       ^^^^
216 |         """Initialize modality mappings"""
217 |         return {
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/translator.py:215:49
    |
213 |         self.modality_mappings = self._initialize_mappings()
214 |
215 |     def _initialize_mappings(self) -> Dict[str, Dict[str, Any]]:
    |                                                 ^^^^
216 |         """Initialize modality mappings"""
217 |         return {
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/translator.py:301:33
    |
299 |         self.vocabulary = get_unified_vocabulary()
300 |         self.glyph_engine = get_glyph_engine()
301 |         self.translation_cache: Dict[str, TranslationResult] = {}
    |                                 ^^^^
302 |         logger.info("Universal Translator initialized")
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/translator.py:305:36
    |
304 |     def translate(self, source: Any, target_type: str,
305 |                  context: Optional[Dict[str, Any]] = None) -> TranslationResult:
    |                                    ^^^^
306 |         """
307 |         Translate from any source to target type.
    |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/translator.py:354:35
    |
353 |     def _perform_translation(self, source: Any, source_type: str, target_type: str,
354 |                            trace: List[str], context: Optional[Dict[str, Any]]) -> TranslationResult:
    |                                   ^^^^
355 |         """Perform the actual translation"""
356 |         target = None
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/translator.py:354:64
    |
353 |     def _perform_translation(self, source: Any, source_type: str, target_type: str,
354 |                            trace: List[str], context: Optional[Dict[str, Any]]) -> TranslationResult:
    |                                                                ^^^^
355 |         """Perform the actual translation"""
356 |         target = None
    |
help: Replace with `dict`

SIM102 Use a single `if` statement instead of nested `if` statements
   --> universal_language/translator.py:397:13
    |
395 |           # List translations
396 |           elif source_type == "list":
397 | /             if all(isinstance(item, Symbol) for item in source):
398 | |                 if target_type == "concept":
    | |____________________________________________^
399 |                       target = self.concept_mapper.symbols_to_composite_concept(source)
400 |                       translation_type = TranslationType.SYMBOL_TO_CONCEPT
    |
help: Combine `if` statements using `and`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/translator.py:445:52
    |
443 |         return new_symbol
444 |
445 |     def private_to_universal(self, private_tokens: List[Any]) -> List[str]:
    |                                                    ^^^^
446 |         """
447 |         Translate private tokens to universal concept IDs.
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/translator.py:445:66
    |
443 |         return new_symbol
444 |
445 |     def private_to_universal(self, private_tokens: List[Any]) -> List[str]:
    |                                                                  ^^^^
446 |         """
447 |         Translate private tokens to universal concept IDs.
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/translator.py:474:49
    |
472 |         return concept_ids
473 |
474 |     def universal_to_private(self, concept_ids: List[str],
    |                                                 ^^^^
475 |                            user_preferences: Optional[Dict[str, Any]] = None) -> List[Any]:
476 |         """
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/translator.py:475:55
    |
474 |     def universal_to_private(self, concept_ids: List[str],
475 |                            user_preferences: Optional[Dict[str, Any]] = None) -> List[Any]:
    |                                                       ^^^^
476 |         """
477 |         Translate universal concept IDs to user's private representation.
    |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/translator.py:475:82
    |
474 |     def universal_to_private(self, concept_ids: List[str],
475 |                            user_preferences: Optional[Dict[str, Any]] = None) -> List[Any]:
    |                                                                                  ^^^^
476 |         """
477 |         Translate universal concept IDs to user's private representation.
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/translator.py:524:40
    |
522 |         return private_tokens
523 |
524 |     def get_translation_stats(self) -> Dict[str, Any]:
    |                                        ^^^^
525 |         """Get translation statistics"""
526 |         successful = sum(1 for r in self.translation_cache.values() if r.is_successful())
    |
help: Replace with `dict`

UP035 `typing.Dict` is deprecated, use `dict` instead
  --> universal_language/vocabulary.py:12:1
   |
10 | from dataclasses import dataclass, field
11 | from pathlib import Path
12 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 |
14 | from universal_language.core import Concept, Symbol, SymbolicDomain
   |

UP035 `typing.List` is deprecated, use `list` instead
  --> universal_language/vocabulary.py:12:1
   |
10 | from dataclasses import dataclass, field
11 | from pathlib import Path
12 | from typing import Any, Dict, List, Optional
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
13 |
14 | from universal_language.core import Concept, Symbol, SymbolicDomain
   |

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/vocabulary.py:28:14
   |
26 |     """
27 |     domain: SymbolicDomain
28 |     symbols: Dict[str, Symbol] = field(default_factory=dict)
   |              ^^^^
29 |     concepts: Dict[str, Concept] = field(default_factory=dict)
30 |     aliases: Dict[str, str] = field(default_factory=dict)  # alias -> symbol_id
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/vocabulary.py:29:15
   |
27 |     domain: SymbolicDomain
28 |     symbols: Dict[str, Symbol] = field(default_factory=dict)
29 |     concepts: Dict[str, Concept] = field(default_factory=dict)
   |               ^^^^
30 |     aliases: Dict[str, str] = field(default_factory=dict)  # alias -> symbol_id
31 |     relationships: Dict[str, List[str]] = field(default_factory=dict)  # symbol_id -> related_ids
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/vocabulary.py:30:14
   |
28 |     symbols: Dict[str, Symbol] = field(default_factory=dict)
29 |     concepts: Dict[str, Concept] = field(default_factory=dict)
30 |     aliases: Dict[str, str] = field(default_factory=dict)  # alias -> symbol_id
   |              ^^^^
31 |     relationships: Dict[str, List[str]] = field(default_factory=dict)  # symbol_id -> related_ids
32 |     metadata: Dict[str, Any] = field(default_factory=dict)
   |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/vocabulary.py:31:20
   |
29 |     concepts: Dict[str, Concept] = field(default_factory=dict)
30 |     aliases: Dict[str, str] = field(default_factory=dict)  # alias -> symbol_id
31 |     relationships: Dict[str, List[str]] = field(default_factory=dict)  # symbol_id -> related_ids
   |                    ^^^^
32 |     metadata: Dict[str, Any] = field(default_factory=dict)
   |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
  --> universal_language/vocabulary.py:31:30
   |
29 |     concepts: Dict[str, Concept] = field(default_factory=dict)
30 |     aliases: Dict[str, str] = field(default_factory=dict)  # alias -> symbol_id
31 |     relationships: Dict[str, List[str]] = field(default_factory=dict)  # symbol_id -> related_ids
   |                              ^^^^
32 |     metadata: Dict[str, Any] = field(default_factory=dict)
   |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
  --> universal_language/vocabulary.py:32:15
   |
30 |     aliases: Dict[str, str] = field(default_factory=dict)  # alias -> symbol_id
31 |     relationships: Dict[str, List[str]] = field(default_factory=dict)  # symbol_id -> related_ids
32 |     metadata: Dict[str, Any] = field(default_factory=dict)
   |               ^^^^
33 |
34 |     def add_symbol(self, symbol: Symbol) -> bool:
   |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
  --> universal_language/vocabulary.py:94:54
   |
92 |         return None
93 |
94 |     def get_related_symbols(self, symbol_id: str) -> List[Symbol]:
   |                                                      ^^^^
95 |         """Get symbols related to a given symbol"""
96 |         related_ids = self.relationships.get(symbol_id, [])
   |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/vocabulary.py:106:28
    |
105 |     def __init__(self):
106 |         self.vocabularies: Dict[SymbolicDomain, DomainVocabulary] = {}
    |                            ^^^^
107 |         self.global_index: Dict[str, SymbolicDomain] = {}  # symbol_id -> domain
108 |         self._initialize_vocabularies()
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/vocabulary.py:107:28
    |
105 |     def __init__(self):
106 |         self.vocabularies: Dict[SymbolicDomain, DomainVocabulary] = {}
107 |         self.global_index: Dict[str, SymbolicDomain] = {}  # symbol_id -> domain
    |                            ^^^^
108 |         self._initialize_vocabularies()
109 |         self._load_core_vocabularies()
    |
help: Replace with `dict`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/vocabulary.py:410:34
    |
408 |         return None
409 |
410 |     def get_all_symbols(self) -> List[Symbol]:
    |                                  ^^^^
411 |         """Get all symbols across all domains"""
412 |         all_symbols = []
    |
help: Replace with `list`

UP006 Use `list` instead of `List` for type annotation
   --> universal_language/vocabulary.py:417:35
    |
415 |         return all_symbols
416 |
417 |     def get_all_concepts(self) -> List[Concept]:
    |                                   ^^^^
418 |         """Get all concepts across all domains"""
419 |         all_concepts = []
    |
help: Replace with `list`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/vocabulary.py:424:33
    |
422 |         return all_concepts
423 |
424 |     def get_statistics(self) -> Dict[str, Any]:
    |                                 ^^^^
425 |         """Get vocabulary statistics"""
426 |         stats = {
    |
help: Replace with `dict`

SIM102 Use a single `if` statement instead of nested `if` statements
   --> universal_language/vocabulary.py:460:13
    |
458 |           if vocab:
459 |               success = vocab.add_symbol(symbol)
460 | /             if success:
461 | |                 # Also register GLYPH if present
462 | |                 if symbol.glyph:
    | |________________________________^
463 |                       self.glyph_engine.register_custom_glyph(symbol.glyph, symbol.name)
464 |               return success
    |
help: Combine `if` statements using `and`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/vocabulary.py:475:36
    |
473 |         return False
474 |
475 |     def lookup(self, term: str) -> Dict[str, Any]:
    |                                    ^^^^
476 |         """Look up a term in the vocabulary"""
477 |         results = {
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/vocabulary.py:503:64
    |
501 |         return results
502 |
503 |     def get_domain_vocabulary(self, domain: SymbolicDomain) -> Dict[str, Any]:
    |                                                                ^^^^
504 |         """Get all vocabulary for a domain"""
505 |         vocab = self.manager.get_vocabulary(domain)
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/vocabulary.py:516:65
    |
514 |         return {}
515 |
516 |     def export_vocabulary(self, path: Optional[Path] = None) -> Dict[str, Any]:
    |                                                                 ^^^^
517 |         """Export the entire vocabulary"""
518 |         export_data = {
    |
help: Replace with `dict`

UP006 Use `dict` instead of `Dict` for type annotation
   --> universal_language/vocabulary.py:533:39
    |
531 |         return export_data
532 |
533 |     def import_vocabulary(self, data: Dict[str, Any]) -> bool:
    |                                       ^^^^
534 |         """Import vocabulary data"""
535 |         try:
    |
help: Replace with `dict`

B007 Loop control variable `domain_name` not used within loop body
   --> universal_language/vocabulary.py:538:21
    |
536 |             # Import domain vocabularies
537 |             if "domains" in data:
538 |                 for domain_name, domain_data in data["domains"].items():
    |                     ^^^^^^^^^^^
539 |                     # TODO: Implement import logic
540 |                     pass
    |
help: Rename unused `domain_name` to `_domain_name`

B007 Loop control variable `domain_data` not used within loop body
   --> universal_language/vocabulary.py:538:34
    |
536 |             # Import domain vocabularies
537 |             if "domains" in data:
538 |                 for domain_name, domain_data in data["domains"].items():
    |                                  ^^^^^^^^^^^
539 |                     # TODO: Implement import logic
540 |                     pass
    |
help: Rename unused `domain_data` to `_domain_data`

⚠️  Ruff issues found (non-blocking)
[pre-commit] 🤖 AI-powered analysis...
[LUKHAS-LLM] ✅ Ollama and deepseek-coder model are available
[LUKHAS-LLM] Running comprehensive analysis on changed Python files...
[LUKHAS-LLM] Analyzing MATRIZ/__init__.py for security issues...
[LUKHAS-LLM] ✅ MATRIZ/__init__.py - No security issues found
[LUKHAS-LLM] Analyzing MATRIZ/__init__.py for lint issues...
