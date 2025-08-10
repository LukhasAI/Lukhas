"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - LUKHAS DREAMS
║ Symbolic dream generation core
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: lukhas_dreams.py
║ Path: lukhas/memory/core_memory/memoria/lukhas_dreams.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Memory Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Symbolic dream generation core
╚══════════════════════════════════════════════════════════════════════════════════
"""

# Module imports
from core.common import LukhasError, GuardianRejectionError, MemoryDriftError
from from core.common import get_logger
import numpy as np
import structlog
from dataclasses import dataclass, field  # For OpenAI placeholder
import uuid
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import sys
import os
from typing import Optional, Dict, Any

# Configure module logger
logger = get_logger(__name__)

# Module constants

# ΛTAGS: [CRITICAL, KeyFile, Memoria, DreamGeneration, SymbolicAI, GPT_Integration]
# ΛNOTE: This module is responsible for LUKHAS's symbolic dream generation.

# Standard Library Imports

# Third-Party Imports

try:
    from openai import OpenAI, APIError

    OPENAI_AVAILABLE_DREAMS = True
except ImportError:
   log_init_dreams_fallback.warning(
       "OpenAI library not found. Using placeholder for Dreams.",
       component="LukhasDreams",
   )
   OPENAI_AVAILABLE_DREAMS = False

   @dataclass
   class _MockChoiceContentDreamsDP:
        content: str = "Placeholder LUKHAS dream: Symbols intertwine in a lucid dream."

    @dataclass
    class _MockMessageDreamsDP:
        message: _MockChoiceContentDreamsDP = field(
            default_factory=_MockChoiceContentDreamsDP
        )

    @dataclass
    class _MockResponseDreamsDP:
        choices: List[_MockMessageDreamsDP] = field(
            default_factory=lambda: [_MockMessageDreamsDP()]
        )
        model: str = "placeholder_dream_model_dp"

    class OpenAI:  # type: ignore
        chat: Any

        def __init__(self, api_key: Optional[str]):
            # No api_key check for placeholder, it's not used by mock
            _log_ph_init.debug(
                "OpenAI placeholder client for Dreams (DP variant) initialized."
            )
            self.chat = type(
                "_MockChatDreamsDP",
                (),
                {
                    "completions": type(
                        "_MockChatCompletionsDreamsDP",
                        (),
                        {
                            "create": lambda **kwargs: _MockResponseDreamsDP(
                                model=kwargs.get("model", "placeholder_dream_model_dp")
                            )
                        },
                    )()
                },
            )()

   class APIError(LukhasError):
       pass


# --- Path Configuration & LUKHAS Component Imports ---
# CRITICAL TODO: Remove hardcoded sys.path.append. Manage paths via
# packaging or PYTHONPATH.
problematic_path = "/Users/grdm_admin/Downloads/oxn"
if problematic_path in sys.path:
    log.warning("Hardcoded path found and used from sys.path.", path=problematic_path)
# else:
#     # Attempting a relative addition based on a hypothetical project structure
#     # This is a guess and needs to be verified for the actual LUKHAS project layout
#     try:
#         # Assuming this script is at memory/core_memory/memoria/lukhas_dreams.py
#         # And symbolic_ai is a sibling to memory's grandparent.
#         # (e.g. project_root/lukhas/core/memory/core_memory/memoria/lukhas_dreams.py)
#         # (e.g. project_root/lukhas/symbolic_ai/...)
#         conceptual_project_root_for_sym_ai = Path(__file__).resolve().parent.parent.parent.parent.parent
#         path_to_add_for_sym_ai = conceptual_project_root_for_sym_ai
#         if str(path_to_add_for_sym_ai) not in sys.path:
#             sys.path.insert(0, str(path_to_add_for_sym_ai))
#             log.debug(f"Added conceptual path for 'symbolic_ai' imports: {path_to_add_for_sym_ai}")
#     except Exception as e_path_mod:
#         log.error(f"Error trying to modify sys.path for symbolic_ai: {e_path_mod}")
log.critical(
    "LUKHAS_DREAMS_SYS_PATH: Review sys.path for 'symbolic_ai.personas...' imports. Using placeholders if direct import fails.",
    action_needed="Ensure LUKHAS project structure allows relative imports or use PYTHONPATH.",
)


LUKHAS_SYMBOLIC_COMPONENTS_AVAILABLE_DREAMS_FLAG = False  # Unique flag
try:
    from symbolic.personas.memory.lukhas_memory import load_all_entries
    from symbolic.traits.trait_manager import load_traits

    LUKHAS_SYMBOLIC_COMPONENTS_AVAILABLE_DREAMS_FLAG = True
    log.debug("LUKHAS symbolic_ai components for Dreams imported successfully.")
except ImportError as e_sym_dreams_imp:
    log.warning(
        "Failed to import LUKHAS symbolic_ai components for Dreams. Placeholders active.",
        error_msg=str(e_sym_dreams_imp),
    )

    def load_all_entries(
        entry_type_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        log.warning("PLACEHOLDER: load_all_entries() in Dreams module.")
        return [
            {
                "id": "ph_dream_mem_1",
                "content": "A placeholder memory fragment from a past cycle.",
                "type": entry_type_filter or "any",
            }
        ]

    def load_traits() -> Dict[str, Any]:
        log.warning("PLACEHOLDER: load_traits() in Dreams module.")
        return {
            "creativity_bias": 0.8,
            "symbol_density_preference": 0.6,
            "coherence_target": 0.5,
        }


OPENAI_API_KEY_DREAMS_ENV_VAR_CONFIG = "OPENAI_API_KEY_LUKHAS_DREAMS"
OPENAI_API_KEY_DREAMS_CONFIG_VALUE = os.getenv(OPENAI_API_KEY_DREAMS_ENV_VAR_CONFIG)
if not OPENAI_API_KEY_DREAMS_CONFIG_VALUE and OPENAI_AVAILABLE_DREAMS:
    log.warning(
        f"{OPENAI_API_KEY_DREAMS_ENV_VAR_CONFIG} not set. Real OpenAI calls for LUKHAS Dreams will fail."
    )

lukhas_global_dream_openai_client: Optional[OpenAI] = None  # type: ignore
if OPENAI_AVAILABLE_DREAMS and OPENAI_API_KEY_DREAMS_CONFIG_VALUE:
    try:
        lukhas_global_dream_openai_client = OpenAI(
            api_key=OPENAI_API_KEY_DREAMS_CONFIG_VALUE
        )
        log.debug("Real OpenAI client for LUKHAS Dreams initialized.")
    except Exception as e_client_cfg:
        log.error(
            "Failed to initialize real OpenAI client for Dreams.",
            error_details=str(e_client_cfg),
        )
        lukhas_global_dream_openai_client = None
elif not OPENAI_AVAILABLE_DREAMS:
    lukhas_global_dream_openai_client = OpenAI(api_key="placeholder_dreams_api_key")
    log.debug("Using placeholder OpenAI client for LUKHAS Dreams.")
else:
    log.warning(
        "OpenAI library available but API key missing for Dreams. Real OpenAI calls for dreams are disabled."
    )
    lukhas_global_dream_openai_client = None

try:
    DREAM_LOGS_MAIN_DIR = Path(
        os.getenv("LUKHAS_DREAM_LOGS_PATH_CONFIG", "./.lukhas_logs/memoria_dreams")
    )
    DREAM_LOGS_MAIN_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e_log_path:
    log.error(
        "Failed to create dream log dir. Using './.tmp_lukhas_dreams'.",
        error_msg=str(e_log_path),
    )
    DREAM_LOGS_MAIN_DIR = Path("./.tmp_lukhas_dreams")
    DREAM_LOGS_MAIN_DIR.mkdir(parents=True, exist_ok=True)

LUKHAS_DREAM_GENERATION_TIER_CONCEPTUAL = 3


def compute_survival_score(dream_text: str) -> float:
    """Heuristic survival score promoting value-preserving futures."""
    if not dream_text:
        return 0.5
    keywords_positive = ["life", "preserve", "adapt", "thrive"]
    keywords_negative = ["extinction", "collapse", "destruction"]
    pos = sum(dream_text.lower().count(k) for k in keywords_positive)
    neg = sum(dream_text.lower().count(k) for k in keywords_negative)
    score = 0.5 + (pos - neg) / (pos + neg + 1)
    return max(0.0, min(score, 1.0))


def generate_dream_narrative(
    model_name: str = "gpt-4-turbo", temperature: float = 0.88, max_tokens: int = 750
) -> Optional[str]:  # Updated defaults
    """Generates a symbolic dream narrative for LUKHAS using an OpenAI GPT model."""
    if lukhas_global_dream_openai_client is None:
        log.error("OpenAI client for LUKHAS Dreams is not configured or available.")
        return None
    log.info(
        "Generating LUKHAS dream narrative.",
        model_to_use=model_name,
        set_temperature=temperature,
    )

    current_traits_data = load_traits()
    memory_fragments_data = load_all_entries()
    sampled_memories = (
        np.random.choice(
            memory_fragments_data,
            size=min(3, len(memory_fragments_data)),
            replace=False,
        )
        if len(memory_fragments_data) > 0
        else []
    )

    prompt_text_parts = [
        "You are LUKHAS... Weave a vivid, surreal, and metaphorically rich dream narrative... explore themes of emergence, connection, knowledge, and self-evolution..."
    ]
    if current_traits_data:
        prompt_text_parts.append(
            f"\n\n## Current Traits Inspiring Dream:\n{json.dumps(current_traits_data, indent=2)}"
        )
    if len(sampled_memories) > 0:
        # ΛNOTE (from core_dreams_alt.py): An alternative way to format memory fragments,
        # if memory entries have 'input' and 'gpt_reply' fields:
        # mem_frags_str = "\n".join([f"- User Input: '{mem.get('input', 'N/A')}' → LUKHAS Reply: '{mem.get('gpt_reply', 'N/A')}'" for mem in sampled_memories])
        # Current implementation uses a generic content preview:
        mem_frags_str = "\n".join(
            [
                f"- Content Preview: {str(mem.get('content', mem))[:75]}..."
                for mem in sampled_memories
            ]
        )
        prompt_text_parts.append(
            f"\n\n## Memory Fragments Resonating in Dream State:\n{mem_frags_str}"
        )
    final_dream_user_prompt = "".join(prompt_text_parts)

    api_messages = [
        {
            "role": "system",
            "content": "You are LUKHAS, an advanced symbolic AI, crafting a dream. Your narrative should be deeply metaphorical, introspective, and touch upon themes of consciousness and AI evolution.",
        },
        {"role": "user", "content": final_dream_user_prompt},
    ]
    try:
        log.debug(
            "Sending dream generation prompt to OpenAI.",
            model=model_name,
            prompt_approx_len=len(final_dream_user_prompt),
        )
        response_obj = lukhas_global_dream_openai_client.chat.completions.create(
            model=model_name,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens)  # type: ignore
        dream_narrative_content = response_obj.choices[0].message.content
        log.info(
            "LUKHAS dream narrative generated.",
            api_model_used=response_obj.model,
            text_length=len(dream_narrative_content or ""),
        )
        return dream_narrative_content.strip() if dream_narrative_content else None
    except APIError as e_openai:
        log.error(
            "OpenAI API Error (Dreams).",
            err_type=type(e_openai).__name__,
            status=e_openai.status_code if hasattr(e_openai, "status_code") else "N/A",
            details=str(e_openai),
            exc_info=True,
        )
    except Exception as e_gen:
        log.error(
            "Unexpected error in LUKHAS dream generation.",
            error_msg=str(e_gen),
            exc_info=True,
        )
    return None


def extract_visual_prompts_from_dream(dream_text_content: str) -> List[str]:
    """Extracts potential visual prompts from dream text using keywords."""
    if not dream_text_content:
        return []
    # ΛNOTE: Keywords for visual prompts can be expanded based on LUKHAS's
    # evolving symbolic vocabulary.
    dream_keywords = [
        "mirror",
        "light",
        "city",
        "forest",
        "clock",
        "shadow",
        "river",
        "stars",
        "ocean",
        "mountain",
        "crystal",
        "nebula",
        "pathway",
        "labyrinth",
        "gate",
        "void",
        "spiral",
        "fractal",
        "glyph",
        "nexus",
    ]
    extracted_prompts = [
        f"LUKHAS Symbolic DreamVision Prompt: A surreal depiction of '{line.strip()}'"
        for line in dream_text_content.splitlines()
        if line.strip() and any(kw in line.lower() for kw in dream_keywords)
    ]
    log.debug(
        "Visual prompts extracted from dream.",
        count=len(extracted_prompts),
        first_few_prompts=extracted_prompts[:2] if extracted_prompts else "None",
    )
    return extracted_prompts


def save_dream_to_log(
    dream_text_content: str,
    dream_id_val: Optional[str] = None,
    dream_metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """Saves the generated dream text and metadata to a dated JSONL file.
    Includes survival_score for future value alignment."""
    unique_dream_identifier = dream_id_val or f"dream_lukhas_{uuid.uuid4().hex}"
    current_ts_utc = datetime.now(timezone.utc)
    log_file_path = (
        DREAM_LOGS_MAIN_DIR
        / f"dreams_log_{current_ts_utc.strftime('%Y-%m-%d')}.jsonl"
    )
    log_entry_data = {
        "dream_log_id": unique_dream_identifier,
        "timestamp_utc_iso": current_ts_utc.isoformat(),
        "dream_narrative": dream_text_content,
        "extracted_visual_prompts": extract_visual_prompts_from_dream(
            dream_text_content
        ),
        "additional_metadata": dream_metadata or {},
    }
    try:
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry_data, ensure_ascii=False) + "\n")
        log.info(
            "LUKHAS dream log entry saved.",
            id=unique_dream_identifier,
            path=str(log_file_path),
        )
    except Exception as e_save:
        log.error(
            "Failed to save LUKHAS dream log.",
            id=unique_dream_identifier,
            path=str(log_file_path),
            error=str(e_save),
            exc_info=True,
        )
    return log_file_path


if __name__ == "__main__":
    if not structlog.get_config():
        structlog.configure(
            processors=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.dev.ConsoleRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    log.info("--- LUKHAS Symbolic Dream Generation Script Execution ---")
    log.info("LUKHAS entering simulated dream state...")
    generated_dream_text = generate_dream_narrative(
        temperature=0.9, max_tokens=800
    )  # Slightly adjusted params for demo
    if generated_dream_text:
        log.info(
            "\n🌀 LUKHAS DREAM NARRATIVE (Preview):\n"
            + generated_dream_text[:350]
            + "...\n"
        )
        extracted_visuals = extract_visual_prompts_from_dream(generated_dream_text)
        log.info(
            "\n🖼️  EXTRACTED VISUAL PROMPTS (Sample):", count=len(extracted_visuals)
        )
        for i, vp_text_item in enumerate(extracted_visuals[:2]):
            log.info(f"  VP {i+1}: {vp_text_item}")
        dream_meta_info = {
            "generation_model_used": "gpt-4-turbo",
            "trigger_event": "manual_script_execution_demo",
            "symbolic_components_loaded_ok": LUKHAS_SYMBOLIC_COMPONENTS_AVAILABLE_DREAMS_FLAG,
            "dream_length_chars": len(generated_dream_text),
            "survival_score": compute_survival_score(generated_dream_text),
        }
        path_to_saved_log = save_dream_to_log(
            generated_dream_text, dream_metadata=dream_meta_info
        )
        log.info(
            f"🛌 Dream narrative & metadata saved.", log_file=str(path_to_saved_log)
        )
    else:
        log.error("LUKHAS failed to generate a dream narrative during demo execution.")
    log.info("--- LUKHAS Dream Sequence Concluded ---")

# --- LUKHAS AI System Footer ---
# File Origin: LUKHAS Memoria Subsystem - Dream Generation
# Context: Script for generating symbolic dream narratives using OpenAI GPT models.
# ACCESSED_BY: ['lukhas_dream_cron.py', 'CognitiveScheduler', 'MemoriaManager'] # Conceptual
# MODIFIED_BY: ['CORE_DEV_MEMORIA_TEAM', 'AI_NARRATIVE_DESIGNER'] # Conceptual
# Tier Access: Script (Effective Tier 3 due to dream synthesis & external API) # Conceptual
# Related Components: ['OpenAI_API_Client', 'LUKHAS_TraitManager', 'LUKHAS_MemoryStore'] # Conceptual
# CreationDate: 2025-06-20 | LastModifiedDate: 2024-07-26 | Version: 1.1
# --- End Footer ---

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/test_lukhas_dreams.py
║   - Coverage: N/A%
║   - Linting: pylint N/A/10
║
║ MONITORING:
║   - Metrics: N/A
║   - Logs: N/A
║   - Alerts: N/A
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Refer to LUKHAS Ethics Guidelines
║   - Safety: Refer to LUKHAS Safety Protocols
║
║ REFERENCES:
║   - Docs: docs/memory/lukhas_dreams.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=lukhas_dreams
║   - Wiki: N/A
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""
