---
status: wip
type: documentation
---
# LUKHAS Symbolic Glyph Visual Debug Legend

ΛVISUAL_LEGEND_VERSION: 0.1.0
**Document Version**: 0.1.0 (Draft by Jules-06)
**Date**: $(date +%Y-%m-%d) <!-- Will be replaced by actual date -->
**Status**: DRAFT

## 1. Purpose & Developer Utility

This document provides a developer-facing guide and legend for the visual representation of LUKHAS symbolic glyphs and their classes, particularly within debugging tools, logs, IDE overlays, and potential future graphical user interfaces (GUIs) for system monitoring.

**Why a Visual Debug Legend?**
-   **Enhanced Interpretability**: Standardized visual cues (icons, colors, shapes) associated with glyph classes can significantly speed up human comprehension of complex symbolic states or log traces.
-   **Debugging Efficiency**: Allows developers and symbolic agents to quickly identify patterns, anomalies, or critical states in debug outputs.
-   **Consistent Developer Experience**: Ensures that different debugging tools or visualizations across the LUKHAS ecosystem represent symbolic information in a harmonized way.
-   **Accessibility**: Provides a framework for considering visual accessibility (e.g., color choices, alternative representations).
-   **Foundation for Tooling**: Serves as a reference for building glyph-aware developer tools, symbolic state debuggers, drift map visualizers, etc.

This legend builds upon the classifications in [`GLYPH_CLASS_DICTIONARY.md`](./GLYPH_CLASS_DICTIONARY.md) and the glyph definitions in [`README_glyphs.md`](../README_glyphs.md).

## 2. Legend Format Proposal

The following table proposes visual and textual attributes for representing glyph classes in debug UIs, tooltips, or enhanced log viewers.

| Class ID             | Symbolic Class Name          | Suggested Visual Icon(s) (from GLYPH_MAP) | Tooltip Text (Summary of Class Function)                                  | Suggested Color Tone / Outline | Potential Debug Shape/Cue (for GUI) |
|----------------------|------------------------------|-------------------------------------------|---------------------------------------------------------------------------|--------------------------------|-------------------------------------|
| **G_STATE_VALIDATION** | System State & Validation    | ✅, ☣️                                     | Status of checks, data integrity, system state validity.                  | Green (Pass: ✅), Red (Fail/Corrupt: ☣️) | Circle (✅), Diamond (☣️)            |
| **G_PROCESS_FLOW**     | Process & Logical Flow       | 🧭, 🔁                                     | Movement, direction, recursion, or progression of processes/logic.        | Blue (Neutral Flow)            | Arrow / Directed Line               |
| **G_RISK_INSTABILITY** | Risk, Caution & Instability  | ⚠️, 🌊, 🌪️, 🔱                             | Warnings, potential dangers, drift, collapse risks, severe divergences.   | Orange (Caution: ⚠️, 🌊), Red (Critical: 🌪️, 🔱) | Triangle (⚠️), Jagged Shape (🌪️) |
| **G_COGNITIVE_SYMBOL** | Core Symbolic & Cognitive Concepts | 🪞, 🌱, ✨, 💡, 🔗                         | Abstract Cognitive AI concepts: reflection, emergence, inference, insight, unity.    | Purple (Abstract/Cognitive)    | Star / Hexagon                      |
| **G_ETHICS_SAFETY**    | Ethical & Safety Constructs  | 🛡️                                        | Ethical boundaries, safety constraints, protective mechanisms.              | Dark Blue / Teal (Protective)  | Shield Shape / Octagon              |
| **G_INFO_NOTE**        | Informational & Annotation   | 📝, ❓, 👁️ (as observation)              | Contextual notes, ambiguity markers, observation/monitoring states.         | Grey / Light Blue (Informational) | Square / Speech Bubble              |
| **G_IO_INTERFACE**     | Input/Output & Interfaces    | 👁️ (as #ΛEXPOSE)                           | External interaction points, API exposure, UI elements.                   | Cyan (Interface/Connectivity)  | Rectangle with Arrow (In/Out)     |

**Notes on Visuals:**
-   **Icons**: Primarily uses the glyphs themselves. If a class has multiple representative glyphs, a primary one might be chosen for a class-level icon, or the specific glyph instance used.
-   **Color Tones**: Suggestions are based on common semantic color associations (e.g., green for success, red for danger). Accessibility (color blindness) should be considered; relying on color alone is not advised. Outlines or fill patterns can supplement color.
-   **Debug Shapes/Cues**: These are abstract suggestions for GUIs where glyphs might be nodes in a graph or markers on a timeline, providing additional visual differentiation beyond the Unicode character itself.

## 3. Visual Overlay Use Case Concepts

Here are some conceptual examples of how this visual legend could be applied:

### A. Enriched Log Traces (Text-Based or IDE Tooltip)

Imagine a log viewer or IDE tooltip that enhances raw logs:

**Raw Log:**
`[2023-10-27T10:00:05Z CRITICAL] #ΛCOLLAPSE_POINT Reactor core overheating! Temp: 1500C. Immediate shutdown initiated. #ΛACTION_TRIGGERED`

**Enhanced Representation (Conceptual Tooltip/Display):**
`[CRITICAL] 🌪️ Reactor core overheating! Temp: 1500C. 🛡️ Immediate shutdown initiated.`
-   `🌪️` (G_RISK_INSTABILITY) might be colored **Red**.
-   `🛡️` (G_ETHICS_SAFETY, if shutdown is a safety protocol) might be colored **Dark Blue**.
-   Tooltip for `🌪️`: "Collapse Risk / High Instability: Indicates potential for system instability or chaotic state."
-   Tooltip for `🛡️`: "Safety Constraint / Ethical Boundary: Represents an active safety measure or ethical rule."

### B. Symbolic Debug Map (Graphical UI Concept)

A graph visualization where nodes are system components or symbolic states:
-   Nodes could be colored based on their dominant glyph class (e.g., `core/ethics/` nodes might have a Dark Blue outline from `G_ETHICS_SAFETY`).
-   Connections (edges) might display `🧭` (G_PROCESS_FLOW) glyphs.
-   A node representing a recently corrupted data store would display `☣️` (G_STATE_VALIDATION) and be colored Red.
-   Hovering over a node or glyph shows the detailed tooltip text from the legend.

### C. Alert Overlays (Based on GLYPH_AUDIT_MACROS.md)

If an audit macro from `GLYPH_AUDIT_MACROS.md` flags an issue:
-   **Example Flag**: `FLAG_MISMATCH(context, 🌊, "Risk glyph 🌊 used with INFO log level.")`
-   **Visual Overlay**: In an IDE or log viewer, the log line containing `🌊` could have a small `⚠️` (from `G_RISK_INSTABILITY` class, as a general warning) icon displayed next to it, or its background subtly highlighted in Orange.
    -   Tooltip on the `⚠️` overlay: "Audit Flag: Risk glyph 🌊 may be miscontextualized (see GLYPH_AUDIT_MACROS.md for CHECK_DRIFT_CONTEXT)."

## 4. Semantic Color Palette (Proposed Basic Palette)

This provides a starting point for associating colors with semantic meaning, primarily driven by glyph class or inherent severity. Accessibility must be a key concern in final implementation (e.g., ensuring sufficient contrast, not relying on color alone).

-   **Critical / High Risk / Failure**: **Red** (e.g., `🌪️`, `🔱`, `☣️`)
    -   *Class Examples*: G_RISK_INSTABILITY (severe), G_STATE_VALIDATION (corrupt/fail)
-   **Caution / Warning / Moderate Risk**: **Orange / Yellow** (e.g., `⚠️`, `🌊`)
    -   *Class Examples*: G_RISK_INSTABILITY (moderate)
-   **Positive Confirmation / Success / Valid**: **Green** (e.g., `✅`)
    -   *Class Examples*: G_STATE_VALIDATION (pass)
-   **Process / Flow / Neutral Operation**: **Blue** (e.g., `🧭`, `🔁`)
    -   *Class Examples*: G_PROCESS_FLOW
-   **Informational / Annotation / Observation**: **Grey / Light Blue** (e.g., `📝`, `❓`, `👁️` as observation)
    -   *Class Examples*: G_INFO_NOTE
-   **Symbolic / Cognitive / Abstract**: **Purple / Magenta** (e.g., `🪞`, `🌱`, `✨`, `💡`, `🔗`)
    -   *Class Examples*: G_COGNITIVE_SYMBOLIC
-   **Ethical / Safety / Protective**: **Dark Blue / Teal** (e.g., `🛡️`)
    -   *Class Examples*: G_ETHICS_SAFETY
-   **Interface / Connectivity**: **Cyan** (e.g., `👁️` as #ΛEXPOSE)
    *   *Class Examples*: G_IO_INTERFACE

## 5. Footer & Internal Tags

**Internal System Tags**: `#ΛVISUAL_GLYPH`, `#ΛDEBUG_GUIDE`, `#ΛTOOLTIP`, `#ΛTRACE` (for document evolution), `#ΛAUDIT_NOTE` (as it supports auditability)

**See Also**:
-   [`README_glyphs.md`](../README_glyphs.md) (for the `GLYPH_MAP` itself)
-   [`GLYPH_CLASS_DICTIONARY.md`](./GLYPH_CLASS_DICTIONARY.md) (for definitions of glyph classes)
-   [`GLYPH_AUDIT_MACROS.md`](./GLYPH_AUDIT_MACROS.md) (for logic that might trigger visual alerts)
-   [`GLYPH_CONFLICT_POLICY.md`](./GLYPH_CONFLICT_POLICY.md) (for glyph governance)

---
*This Visual Debug Legend was drafted by Jules-06.*
