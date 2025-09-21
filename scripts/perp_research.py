#!/usr/bin/env python3
"""
Perplexity Research Runner: scout → sift → synthesize → stress-test → score
T4/0.01% Enhancement of LUKHAS 3-Layer Tone System

Pipeline stages:
- Scout: Evidence-first literature scan with citations
- Sift: Anti-repetition engine with rotation matrices
- Synthesize: MATRIZ + 3-layer generation with constraints
- Stress-test: Adversarial validation with multiple personas
- Score: Measurable quality metrics

Usage:
    python scripts/perp_research.py

Output: Versioned JSON files in ./perp_runs/ with full audit trail
"""

import os
import json
import time
import pathlib
import uuid
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar"  # Use basic sonar model

OUTDIR = pathlib.Path(os.getenv("LUKHAS_PERP_OUT", "./perp_runs")).resolve()
OUTDIR.mkdir(parents=True, exist_ok=True)

def _post(payload, stream=False, max_retries=5):
    """Make API request with exponential backoff."""
    assert API_KEY, "PERPLEXITY_API_KEY missing from .env file"

    for attempt in range(max_retries):
        try:
            r = requests.post(
                BASE_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload,
                stream=stream,
                timeout=120
            )

            if r.status_code == 429 or r.status_code >= 500:
                # Backoff on rate limit / transient errors
                wait = 2 ** attempt
                print(f"Rate limited or server error. Waiting {wait}s...")
                time.sleep(wait)
                continue

            r.raise_for_status()
            return r

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"Request failed, retry {attempt + 1}/{max_retries} in {wait}s: {e}")
            time.sleep(wait)

    raise RuntimeError("Exhausted retries")

def chat(messages, temperature=0.7, top_p=0.9, max_tokens=4000, expect_json=False, stream=False):
    """Send chat request to Perplexity API."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": stream
    }

    # Perplexity doesn't support response_format, remove this section
    # We'll handle JSON parsing manually

    # Clean payload (remove None values)
    payload = {k: v for k, v in payload.items() if v is not None}

    if stream:
        resp = _post(payload, stream=True)
        chunks = []
        print("Streaming response: ", end="", flush=True)

        for line in resp.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                delta = json.loads(data)
                chunk = delta["choices"][0]["delta"].get("content", "")
                if chunk:
                    chunks.append(chunk)
                    print(chunk, end="", flush=True)
            except Exception:
                continue
        print()  # New line after streaming
        content = "".join(chunks)
    else:
        resp = _post(payload)
        content = resp.json()["choices"][0]["message"]["content"]

    if expect_json:
        # Best-effort JSON extraction and validation
        first_brace = content.find("{")
        last_brace = content.rfind("}")

        if first_brace != -1 and last_brace != -1:
            content = content[first_brace:last_brace + 1]

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Content: {content[:500]}...")

            # Try repair pass
            print("Attempting JSON repair...")
            repair_messages = [
                {"role": "system", "content": "You fix malformed JSON. Return valid JSON only."},
                {"role": "user", "content": f"Repair this into valid JSON:\n\n{content}"}
            ]
            return chat(repair_messages, expect_json=False, stream=False)

    return content

def save(run_id, stage, obj):
    """Save stage output to versioned file."""
    path = OUTDIR / f"{run_id}__{stage}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    print(f"Saved {stage} → {path}")
    return str(path)

def run_scout(run_id, meta):
    """
    Stage A: Scout - Evidence-first literature scan

    Returns citations, metaphor families, and taboo list of clichés to avoid.
    """
    print("\n🔍 STAGE A: SCOUT - Literature Scan")
    print("=" * 50)

    scout_messages = [
        {
            "role": "system",
            "content": "You are a research scout. Return JSON only. Search recent sources."
        },
        {
            "role": "user",
            "content": """Task: Survey contemporary poetry & premium-brand copy to find metaphor/device trends that AVOID celestial imagery.

Requirements:
- Search the open web for 2020-2025 sources
- Include 6-10 citations (title, url, year, author)
- Extract metaphor_families with concrete examples
- Produce taboo_list of overused clichés (ranked by prevalence)
- Focus on: organic/biological, architectural, musical, textile, geological, liquid, light, quantum patterns

Output schema:
{
  "citations": [
    {"title": "...", "url": "...", "year": 2024, "author": "...", "key_insight": "..."}
  ],
  "metaphor_families": [
    {
      "name": "Neural Gardens",
      "description": "...",
      "exemplar_quotes": ["phrase ≤12 words", "..."],
      "devices": ["metaphor", "synecdoche", "..."],
      "domains": ["biology", "technology", "..."]
    }
  ],
  "taboo_list": [
    {"phrase": "stars align", "why": "overused celestial", "prevalence": "high"},
    {"phrase": "quantum dance", "why": "vague science", "prevalence": "medium"}
  ]
}

Return valid JSON, no prose."""
        }
    ]

    scout_data = chat(scout_messages, expect_json=True, temperature=0.3)

    result = {
        "meta": meta,
        "stage": "scout",
        "data": scout_data,
        "timestamp": time.time()
    }

    save(run_id, "scout", result)
    print(f"Found {len(scout_data.get('citations', []))} citations")
    print(f"Found {len(scout_data.get('metaphor_families', []))} metaphor families")
    print(f"Found {len(scout_data.get('taboo_list', []))} taboo phrases")

    return scout_data

def run_sift(run_id, meta, scout_data):
    """
    Stage B: Sift - Anti-repetition engine

    Builds rotation matrices and constraint systems.
    """
    print("\n🔧 STAGE B: SIFT - Anti-Repetition Engine")
    print("=" * 50)

    sift_messages = [
        {
            "role": "system",
            "content": "You design anti-repetition constraints. Return JSON only."
        },
        {
            "role": "user",
            "content": f"""Using this SCOUT data, design a rotation system to prevent repetition in the LUKHAS 3-layer tone system (Poetic → Academic → User-Friendly).

SCOUT_DATA:
{json.dumps(scout_data, indent=2)}

Build a system that ensures:
1. No metaphor family dominates (max 30% usage)
2. Minimum semantic distance between selections (≥0.6)
3. Tone-appropriate vocabulary for each layer
4. Required sophistication patterns for consciousness technology

Output schema:
{{
  "rotation_matrix": {{
    "Neural_Gardens": {{
      "poetic": {{"allowed_devices": [], "banned_tokens": [], "min_distance": 0.6}},
      "academic": {{"allowed_devices": [], "banned_tokens": [], "min_distance": 0.6}},
      "user": {{"allowed_devices": [], "banned_tokens": [], "min_distance": 0.6}}
    }}
  }},
  "required_list": [
    {{"pattern": "consciousness technology", "why": "brand core"}},
    {{"pattern": "dynamic systems", "why": "sophistication"}}
  ],
  "banned_list": [
    {{"pattern": "quantum dance", "severity": "high"}},
    {{"pattern": "stars align", "severity": "high"}}
  ],
  "diversity_budget": {{
    "max_family_usage_percent": 30,
    "min_distance": 0.6,
    "required_rotation_cycles": 8
  }}
}}

Return valid JSON only."""
        }
    ]

    sift_data = chat(sift_messages, expect_json=True, temperature=0.4)

    result = {
        "meta": meta,
        "stage": "sift",
        "data": sift_data,
        "timestamp": time.time()
    }

    save(run_id, "sift", result)
    print("Built rotation matrix and constraint system")

    return sift_data

def run_synthesize(run_id, meta, scout_data, sift_data):
    """
    Stage C: Synthesize - Generate MATRIZ + 3-layer content

    Creates 8 metaphor families with full layered expressions.
    """
    print("\n🎨 STAGE C: SYNTHESIZE - Content Generation")
    print("=" * 50)

    synthesize_messages = [
        {
            "role": "system",
            "content": "You produce stylistically diverse content under strict constraints. Return JSON only."
        },
        {
            "role": "user",
            "content": f"""Generate 8 metaphor families for LUKHAS consciousness technology, following these constraints:

SCOUT_DATA: {json.dumps(scout_data, indent=2)}
SIFT_DATA: {json.dumps(sift_data, indent=2)}

Requirements:
1. 8 distinct families: Neural Gardens, Architectural Bridges, Harmonic Resonance, Woven Patterns, Geological Strata, Fluid Dynamics, Prismatic Light, Circuit Patterns
2. Each family has 3 layers: Poetic (sophisticated, rebellious) → Academic (technical precision) → User-Friendly (grandma-accessible)
3. MATRIZ mapping: Memory, Attention, Thought, Risk, Intent, Action stages
4. Zero violations of banned_list
5. Axes scoring for measurable quality

Output schema:
{{
  "families": [
    {{
      "family": "Neural Gardens",
      "poetic": "Where synaptic blooms unfold consciousness through organic wisdom...",
      "academic": "Implementing hierarchical neural architectures with bio-inspired learning algorithms...",
      "user": "Think of it like a garden where your thoughts grow and connect naturally...",
      "MATRIZ": {{
        "Memory": ["rooted experiences", "neural soil"],
        "Attention": ["selective pruning", "focused cultivation"],
        "Thought": ["branching insights", "cognitive blossoming"],
        "Risk": ["toxic detection", "growth boundaries"],
        "Intent": ["directional growth", "purposeful flowering"],
        "Action": ["fruit bearing", "seed dispersal"]
      }},
      "axes": {{
        "concreteness": 0.8,
        "technicality": 0.6,
        "novelty": 0.9,
        "sensory": ["tactile", "visual", "olfactory"]
      }},
      "violations": [],
      "repaired": false
    }}
  ]
}}

Ensure 0 violations; auto-repair if needed. Return valid JSON only."""
        }
    ]

    synthesize_data = chat(synthesize_messages, expect_json=True, temperature=0.6, max_tokens=6000)

    result = {
        "meta": meta,
        "stage": "synthesize",
        "data": synthesize_data,
        "timestamp": time.time()
    }

    save(run_id, "synthesize", result)
    print(f"Generated {len(synthesize_data.get('families', []))} metaphor families")

    return synthesize_data

def run_stress_test(run_id, meta, synthesize_data):
    """
    Stage D: Stress-test - Adversarial validation

    Multiple personas check quality and force repairs.
    """
    print("\n🛡️ STAGE D: STRESS-TEST - Adversarial Validation")
    print("=" * 50)

    stress_messages = [
        {
            "role": "system",
            "content": "You are a panel of editors: CMO (brand), Referee #2 (academic), Grandma (accessibility). Return JSON only."
        },
        {
            "role": "user",
            "content": f"""Review this SYNTHESIZE output against T4/0.01% standards:

SYNTH_DATA: {json.dumps(synthesize_data, indent=2)}

Check for:
- CMO: Brand vagueness, cliché usage, sophistication lapses
- Referee #2: Jargon bloat, academic precision, citation needs
- Grandma: Comprehension failures, complexity overload, accessibility

Requirements:
- grandma_check.pass_rate must be ≥0.999
- If pass_rate < 0.999, rewrite ONLY the user-layer lines
- Score each family on novelty, clarity, duplication_distance

Output schema:
{{
  "issues": [
    {{"family": "Neural Gardens", "layer": "academic", "problem": "...", "fix": "..."}}
  ],
  "grandma_check": {{
    "pass_rate": 0.995,
    "notes": ["family X user layer too complex", "..."],
    "repairs": ["original → fixed"]
  }},
  "scores": {{
    "avg_novelty": 0.87,
    "avg_clarity": 0.92,
    "avg_duplication_distance": 0.78,
    "families": [
      {{"name": "Neural Gardens", "novelty": 0.9, "clarity": 0.95, "duplication": 0.8}}
    ]
  }}
}}

Return valid JSON only."""
        }
    ]

    stress_data = chat(stress_messages, expect_json=True, temperature=0.3)

    result = {
        "meta": meta,
        "stage": "stress_test",
        "data": stress_data,
        "timestamp": time.time()
    }

    save(run_id, "stress_test", result)

    grandma_pass = stress_data.get("grandma_check", {}).get("pass_rate", 0)
    print(f"Grandma validation pass rate: {grandma_pass:.3f}")
    print(f"Found {len(stress_data.get('issues', []))} issues")

    return stress_data

def run_pipeline(theme_statement: str):
    """
    Execute complete research pipeline.

    Args:
        theme_statement: Research premise and constraints

    Returns:
        dict with run_id and summary metrics
    """
    print("🚀 LUKHAS T4 RESEARCH PIPELINE")
    print("=" * 60)

    # Generate run metadata
    run_id = time.strftime("%Y%m%d-%H%M%S") + "_" + uuid.uuid4().hex[:8]
    meta = {
        "run_id": run_id,
        "model": MODEL,
        "premise": theme_statement,
        "pipeline_version": "1.0.0",
        "lukhas_version": "Constellation Framework",
        "timestamp": time.time()
    }

    print(f"Run ID: {run_id}")
    print(f"Theme: {theme_statement}")
    print(f"Output: {OUTDIR}")

    try:
        # Execute pipeline stages
        scout_data = run_scout(run_id, meta)
        sift_data = run_sift(run_id, meta, scout_data)
        synthesize_data = run_synthesize(run_id, meta, scout_data, sift_data)
        stress_data = run_stress_test(run_id, meta, synthesize_data)

        # Generate summary
        summary = {
            "run_id": run_id,
            "success": True,
            "families_generated": len(synthesize_data.get("families", [])),
            "citations_found": len(scout_data.get("citations", [])),
            "taboo_phrases": len(scout_data.get("taboo_list", [])),
            "grandma_pass_rate": stress_data.get("grandma_check", {}).get("pass_rate", 0),
            "avg_novelty": stress_data.get("scores", {}).get("avg_novelty", 0),
            "issues_found": len(stress_data.get("issues", [])),
            "output_dir": str(OUTDIR)
        }

        # Save final summary
        save(run_id, "summary", {"meta": meta, "summary": summary})

        print("\n✅ PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Families: {summary['families_generated']}")
        print(f"Citations: {summary['citations_found']}")
        print(f"Grandma Pass: {summary['grandma_pass_rate']:.3f}")
        print(f"Avg Novelty: {summary['avg_novelty']:.3f}")
        print(f"Issues: {summary['issues_found']}")

        return summary

    except Exception as e:
        error_summary = {
            "run_id": run_id,
            "success": False,
            "error": str(e),
            "output_dir": str(OUTDIR)
        }
        save(run_id, "error", {"meta": meta, "error": error_summary})
        print(f"\n❌ PIPELINE FAILED: {e}")
        raise

if __name__ == "__main__":
    # Execute with consciousness technology focus
    premise = (
        "Replace celestial metaphors with 8 diverse families: "
        "Neural Gardens (organic), Architectural Bridges (structural), "
        "Harmonic Resonance (musical), Woven Patterns (textile), "
        "Geological Strata (earth), Fluid Dynamics (liquid), "
        "Prismatic Light (optical), Circuit Patterns (electronic). "
        "Enforce novelty ≥0.8, clarity ≥0.95, zero repetition. "
        "Target: consciousness technology with 3-layer flow "
        "(Poetic → Academic → User-Friendly) and MATRIZ integration."
    )

    try:
        result = run_pipeline(premise)
        print(f"\n📁 All outputs saved to: {result['output_dir']}")
        print(f"🆔 Run ID: {result['run_id']}")

    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        exit(1)