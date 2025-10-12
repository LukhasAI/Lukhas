---
status: wip
type: documentation
---
# LUKHAS Symbolic Glyph Class Dictionary

ΛCLASS_DICT_VERSION: 0.1.0
**Document Version**: 0.1.0 (Draft by Jules-06)
**Date**: $(date +%Y-%m-%d) <!-- Will be replaced by actual date -->
**Status**: DRAFT

## 1. Introduction

This document serves as a centralized dictionary for **Glyph Classes** used within the LUKHAS symbolic system. While individual glyphs are defined in `GLYPH_MAP` (see [`README_glyphs.md`](../README_glyphs.md)), this dictionary organizes those glyphs into broader categories based on their primary semantic function, domain of application, or the type of information they convey.

**Purpose of Glyph Classes:**
-   **Organization**: To logically group related glyphs, making the overall system easier to understand and navigate.
-   **Discoverability**: To help users and agents find relevant glyphs for specific conceptual domains.
-   **Consistent Application**: To guide the assignment of new glyphs to appropriate classes and ensure thematic coherence.
-   **Interpretive Aid**: To provide another layer of context when interpreting glyphs, supplementing the individual meanings and the detailed guidance in [`GLYPH_GUIDANCE.md`](./GLYPH_GUIDANCE.md).

This dictionary is intended to be a living document, evolving alongside the LUKHAS glyph system.

## 2. Glyph Class Table

The following table enumerates the currently defined glyph classes.

| Class ID             | Class Name                      | Glyph Example(s) | Meaning / Function                                                                 | Typically Linked Modules                                  | Notes                                                                                                |
|----------------------|---------------------------------|------------------|------------------------------------------------------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| **G_STATE_VALIDATION** | System State & Validation       | ✅, ☣️             | Representing outcomes of checks, data integrity, or confirmed system states.         | `core/diagnostics/`, `core/ethics/`, Test Suites          | Crucial for system health monitoring and verification processes.                                     |
| **G_PROCESS_FLOW**     | Process & Logical Flow          | 🧭, 🔁           | Indicating movement, direction, recursion, or the progression of processes/logic.  | `core/orchestration/`, `core/reasoning/`, Logging Systems | Helps visualize and trace execution paths and iterative cycles.                                      |
| **G_RISK_INSTABILITY** | Risk, Caution & Instability     | ⚠️, 🌊, 🌪️, 🔱     | Highlighting warnings, potential dangers, drift, collapse risks, or severe divergences. | `core/diagnostic_engine/`, `core/ethics/`, Alert Systems  | Essential for flagging critical conditions that may require attention or intervention.               |
| **G_COGNITIVE_SYMBOL** | Core Symbolic & Cognitive Concepts | 🪞, 🌱, ✨, 💡, 🔗 | Representing abstract Cognitive AI concepts like reflection, emergence, inference, insight, unity. | `core/symbolic/`, `core/advanced/brain/`, `learning/`     | Forms the vocabulary for discussing LUKHAS's internal cognitive and symbolic architecture.           |
| **G_ETHICS_SAFETY**    | Ethical & Safety Constructs     | 🛡️                | Denoting ethical boundaries, safety constraints, or protective mechanisms in action. | `core/ethics/`, `core/governance/`                        | Visual markers for the system's moral compass and safety enforcement. *Proposed glyph: ⚖️ (Justice/Balance)* |
| **G_INFO_NOTE**        | Informational & Annotation      | 📝, ❓, 👁️       | Providing contextual notes, marking ambiguity, or indicating observation/monitoring. | Documentation, Logging, UI/Dashboards                     | Aids human understanding and provides context within complex data streams or code.                   |
| **G_IO_INTERFACE**     | Input/Output & Interfaces       | 👁️ (as #ΛEXPOSE) | Marking points of external interaction, API exposure, or user interface elements.  | `core/interfaces/`, `api/`                                | Distinguishes internal processes from external communication points. `👁️` is overloaded here. |

*(This table will be expanded as more glyphs are added and categorized.)*

## 3. Categorization Guidelines

Glyph classes are primarily defined by their **semantic function** or the **domain of application** of the glyphs they contain. When considering a new glyph or categorizing existing ones:

-   **Primary Meaning**: Focus on the most common and intended meaning/use of the glyph within LUKHAS. A glyph might have secondary applications but should be classed by its primary role.
-   **Distinct Purpose**: A new class should represent a reasonably distinct conceptual domain. Avoid creating too many overly granular classes initially.
-   **Potential Membership**: A class should ideally have the potential for multiple glyph members, even if it starts with one or two. This indicates a valid conceptual grouping.
-   **Emotional Tone (Subtle)**: While not a primary driver, the general "emotional tone" or urgency conveyed by glyphs (e.g., warning vs. informational) can sometimes help in classing.
-   **Alignment with ΛTAG Usage**: Classes may naturally emerge from groups of ΛTAGS that address similar concerns (e.g., tags related to risk might all fall under `G_RISK_INSTABILITY`).

**Proposing a New Glyph Class:**
1.  Identify a set of existing or proposed glyphs that share a strong common theme or function not well-covered by existing classes.
2.  Define a clear, concise name and `Class ID` (e.g., `G_NEW_CLASS`).
3.  Articulate the "Meaning / Function" of the class.
4.  List example glyphs that would belong to it and typical modules where it would apply.
5.  Submit the proposal for review (e.g., to symbolic agents or a governance body).

## 4. Pending or Undefined Classes

The LUKHAS glyph system is evolutionary. Some glyphs in `GLYPH_MAP` may not yet be assigned to a class, or new conceptual domains may emerge requiring new classes.
-   **Unclassed Glyphs**: Individual glyphs might exist in `GLYPH_MAP` before a suitable class is defined for them. These can be noted here or in `README_glyphs.md` as pending categorization.
    -   Example: `⚖️` (Justice/Balance) is proposed for G-ETHICS but could also be a candidate for a future `G_GOVERNANCE` class if more related glyphs emerge.
-   This section encourages future Jules agents and developers to contribute to the classification effort by proposing new classes or assigning unclassed glyphs as the system matures.

## 5. Footer

**Internal System Tags**: `#ΛDICTIONARY`, `#ΛGLYPH_CLASS`, `#ΛTRACE` (for the document's own traceability)

**See Also**:
-   [`README_glyphs.md`](../README_glyphs.md) (for the `GLYPH_MAP` itself)
-   [`GLYPH_GUIDANCE.md`](./GLYPH_GUIDANCE.md) (for interpretive usage and semantics)
-   [`GLYPH_CONFLICT_POLICY.md`](./GLYPH_CONFLICT_POLICY.md) (for glyph governance)
-   `LTAG_USAGE_INDEX.md` (Future link: For cross-referencing ΛTAGS with glyph classes and usage patterns)

---
*This Glyph Class Dictionary was drafted by Jules-06.*
