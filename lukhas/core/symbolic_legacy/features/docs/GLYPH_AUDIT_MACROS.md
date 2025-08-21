# LUKHAS Symbolic Glyph Audit Macros & Conventions

ΛAUDIT_MACROS_VERSION: 0.1.0
**Document Version**: 0.1.0 (Draft by Jules-06)
**Date**: $(date +%Y-%m-%d) <!-- Will be replaced by actual date -->
**Status**: DRAFT

## 1. Introduction & Scope

This document proposes a set of conceptual "audit macros" or symbolic conventions designed to help maintain the integrity, consistency, and intended semantic weight of the LUKHAS glyph system. As the system evolves and glyphs are used more broadly in logging, documentation, and potentially UI elements, mechanisms are needed to detect and flag potential misuse, misclassification, or semantic drift.

**Why Audit Macros Are Needed:**
-   **Prevent Semantic Dilution**: Ensure that glyphs, especially those indicating high-sensitivity states (e.g., risk, ethical concerns), retain their intended impact and are not used inappropriately.
-   **Maintain Class Integrity**: Help verify that glyphs are used in contexts consistent with their defined class (see [`GLYPH_CLASS_DICTIONARY.md`](./GLYPH_CLASS_DICTIONARY.md)).
-   **Support Ethical Tag Integrity**: Ensure that glyphs related to ethics and safety are correctly anchored to relevant system logic or events.
-   **Mitigate Drift Entropy**: Counteract the natural tendency for symbolic meanings to drift or become overloaded over time if not actively managed.
-   **Aid Automated Review**: Provide patterns that could be used by future automated tools or symbolic agents to audit glyph usage.

This document focuses on proposing the *logic* of these macros in symbolic or pseudocode form, rather than providing a specific implementation.

## 2. Macro Proposals (Symbolic / Pseudocode Form)

### Macro 1: Drift-Class Glyph Mismatch Check (`CHECK_DRIFT_CONTEXT`)

-   **Purpose**: To identify instances where glyphs from the `G_RISK_INSTABILITY` class (e.g., 🌊, 🌪️, 🔱) are used without appropriate contextualizing ΛTAGS that indicate awareness, mitigation, or corresponding severity in logging.
-   **Logic (Pseudocode)**:
    ```
    FOR EACH log_entry OR code_comment OR doc_section AS context:
      DETECT glyph G_RISK from G_RISK_INSTABILITY_CLASS (e.g., 🌊, 🌪️, 🔱) IN context
      IF G_RISK IS PRESENT:
        HAS_MITIGATION_TAG = FALSE
        FOR EACH tag T IN context.associated_ΛTAGS:
          IF T IS_ONE_OF (#ΛSTABILIZE_ATTEMPT, #ΛRECOVERY_POINT, #ΛALERT_TRIGGERED, #ΛMANUAL_INTERVENTION_REQ):
            HAS_MITIGATION_TAG = TRUE
            BREAK

        LOG_SEVERITY = context.log_level OR context.inferred_severity
        GLYPH_IMPLIED_SEVERITY = G_RISK.inherent_severity (e.g., 🌊=WARN, 🌪️=ERROR, 🔱=CRITICAL)

        IF NOT HAS_MITIGATION_TAG AND LOG_SEVERITY < GLYPH_IMPLIED_SEVERITY:
          FLAG_MISMATCH(context, G_RISK,
            "Risk glyph used without clear mitigation/awareness tag or with insufficiently severe log level."
            "#ΛRISK_CHECK #ΛAUDIT")
    ```
-   **Flagging**: Suggests potential downplaying of risk, missing safety/recovery logic, or inappropriate logging levels for the indicated glyph severity.

### Macro 2: Ethics-Class Glyph Anchoring & Overlap Detection (`CHECK_ETHICS_ANCHOR`)

-   **Purpose**: To ensure `G_ETHICS_SAFETY` glyphs (e.g., 🛡️) are meaningfully anchored to ethical evaluation points or defined safety constraints, and are not misused or overshadowed.
-   **Logic (Pseudocode)**:
    ```
    FOR EACH log_entry OR code_comment OR doc_section AS context:
      DETECT glyph G_ETHICS from G_ETHICS_SAFETY_CLASS (e.g., 🛡️) IN context
      IF G_ETHICS IS PRESENT:
        IS_ANCHORED = FALSE
        FOR EACH tag T IN context.associated_ΛTAGS:
          IF T IS_ONE_OF (#ΛETHICAL_EVAL_CALL, #ΛSAFETY_CONSTRAINT_APPLIED, #ΛPOLICY_ENFORCED):
            IS_ANCHORED = TRUE
            BREAK
        IF NOT IS_ANCHORED AND context.source NOT_IN (ETHICS_MODULE_SOURCES): // Allow direct use in ethics module
           FLAG_MISMATCH(context, G_ETHICS,
            "Ethics/safety glyph used without clear anchor to ethical evaluation or constraint logic."
            "#ΛRISK_CHECK #ΛAUDIT")

      // Overlap/Downgrade Check for Ethics Glyphs
      IF G_ETHICS IS PRESENT:
        FOR EACH other_glyph G_OTHER IN context.associated_glyphs:
          IF G_OTHER.class == G_INFO_NOTE AND G_OTHER IS_DOMINANT_OR_CONCLUDES_CONTEXT_AFTER(G_ETHICS):
            FLAG_MISMATCH(context, G_ETHICS,
              "Ethics/safety glyph potentially downgraded or obscured by purely informational glyphs."
              "#ΛRISK_CHECK #ΛAUDIT")
    ```
-   **Flagging**: Detects decorative use of ethics glyphs, missing links to actual ethical processing, or situations where critical ethical flags might be semantically diluted by less critical glyphs.

### Macro 3: Contextual Severity Downgrade Detection (`CHECK_SEVERITY_CONSISTENCY`)

-   **Purpose**: To identify patterns where a high-severity glyph is presented in a context that otherwise suggests low severity, potentially misleading interpreters.
-   **Logic (Pseudocode)**:
    ```
    FOR EACH log_entry OR doc_section AS context:
      DETECT glyph G_HIGH_SEVERITY from (G_RISK_INSTABILITY_CLASS OR G_ETHICS_SAFETY_CLASS) IN context
      IF G_HIGH_SEVERITY IS PRESENT:
        SUBSEQUENT_GLYPHS = context.glyphs_appearing_after(G_HIGH_SEVERITY, within_same_semantic_unit)
        HAS_RESOLUTION_GLYPH = FALSE
        ALL_SUBSEQUENT_ARE_LOW_INFO = TRUE

        FOR EACH glyph G_SUB IN SUBSEQUENT_GLYPHS:
          IF G_SUB.class IN (G_PROCESS_FLOW_RESOLUTION_SUBCLASS, G_STATE_VALIDATION_POSITIVE_SUBCLASS): // e.g. ✅
            HAS_RESOLUTION_GLYPH = TRUE
            ALL_SUBSEQUENT_ARE_LOW_INFO = FALSE // A resolution is not "low info"
            BREAK
          IF G_SUB.class != G_INFO_NOTE:
            ALL_SUBSEQUENT_ARE_LOW_INFO = FALSE
            // Break if we see another high/medium severity or non-info glyph before resolution
            BREAK

        IF NOT HAS_RESOLUTION_GLYPH AND ALL_SUBSEQUENT_ARE_LOW_INFO AND len(SUBSEQUENT_GLYPHS) > 0:
          FLAG_MISMATCH(context, G_HIGH_SEVERITY,
            "High-severity glyph followed only by informational glyphs without clear resolution/process glyph, potentially obscuring impact."
            "#ΛRISK_CHECK #ΛAUDIT")
    ```
-   **Flagging**: Suggests that the severity implied by a glyph like `🌪️` or `☣️` might be lost if the immediate surrounding symbolic context is purely informational (e.g., `🌪️ This is a note 📝`).

## 3. Suggested Tagging Interface / Validator Hooks

These conceptual macros could be integrated into the LUKHAS development and operational lifecycle via:

-   **Linting / Static Analysis**: A custom linter could parse code comments and documentation for these patterns.
-   **Pre-Commit Hooks**: Extend `trace/commit_log_checker.py` concepts to analyze staged changes for glyph usage patterns in documentation or specific structured log formats if committed.
-   **Runtime Symbolic Validator Agent**: A dedicated agent could monitor logs or system event streams in real-time (or periodically) to apply these checks.
-   **Symbolic Review Process**: Human or agent-assisted review cycles that specifically look for these anti-patterns.

**Proposed New Informational ΛTAGS for Macro Output:**
-   `#ΛGLYPH_AUDIT_PASS(macro_id)`: Indicates a context passed a specific glyph audit check.
-   `#ΛGLYPH_AUDIT_FLAG(macro_id, reason)`: Indicates a context flagged by a macro, with a reason. This tag itself would become a point of #ΛTRACE.

## 4. Use Cases / Examples

-   **Macro 1 (`CHECK_DRIFT_CONTEXT`) Example**:
    *   **Problematic**: `log.info("System state seems a bit off 🌊 but probably fine.")`
    *   **Flag**: `FLAG_MISMATCH(..., 🌊, "Risk glyph 🌊 (Drift) used with INFO log level and no mitigation tag.")`

-   **Macro 2 (`CHECK_ETHICS_ANCHOR`) Example**:
    *   **Problematic**: `// Action X is completed 🛡️` (where Action X has no call to `evaluate_ethics` or related logic).
    *   **Flag**: `FLAG_MISMATCH(..., 🛡️, "Ethics glyph 🛡️ used without anchor to ethical evaluation logic.")`

-   **Macro 3 (`CHECK_SEVERITY_CONSISTENCY`) Example**:
    *   **Problematic Log Sequence**: `CRITICAL: Reactor meltdown imminent! 🌪️`, followed immediately by `INFO: User session ended. 📝`
    *   **Flag**: `FLAG_MISMATCH(..., 🌪️, "High-severity glyph 🌪️ followed only by informational glyph 📝 without resolution.")`


## 5. Linkage to `GLYPH_CLASS_DICTIONARY.md`

The logic of these audit macros fundamentally relies on the glyph classifications defined in [`GLYPH_CLASS_DICTIONARY.md`](./GLYPH_CLASS_DICTIONARY.md). For instance, identifying a "Drift-Class Glyph" or an "Ethics-Class Glyph" requires referencing these pre-defined classes. Maintaining the accuracy and comprehensiveness of the class dictionary is therefore crucial for the effectiveness of these audit macros.

## 6. Optional: Known Risky Glyphs / Symbolic Review Loops

-   **Known Risky Glyphs (Example)**:
    -   `👁️` (Observation / Monitoring / Awareness State / #ΛEXPOSE): This glyph is versatile. A macro might check if its usage as `#ΛEXPOSE` (implying an interface) is distinct from its usage as general "monitoring" to avoid ambiguity.
-   **Symbolic Review Loop (Concept)**:
    -   Flags generated by these macros (e.g., tagged with `#ΛGLYPH_AUDIT_FLAG`) could feed into a dedicated review queue.
    -   A symbolic agent (like a specialized Jules instance) or human reviewers could periodically process this queue, suggest corrections, update glyph usage, or refine the audit macro logic itself. This creates a continuous improvement loop for symbolic hygiene.

## 7. Footer Metadata

**Internal System Tags**: `#ΛAUDIT`, `#ΛGLYPH_MACRO`, `#ΛRISK_CHECK`, `#ΛTRACE`

**See Also**:
-   [`GLYPH_MAP` in `core/symbolic/glyphs.py`](../glyphs.py)
-   [`GLYPH_CLASS_DICTIONARY.md`](./GLYPH_CLASS_DICTIONARY.md)
-   [`GLYPH_GUIDANCE.md`](./GLYPH_GUIDANCE.md)
-   [`GLYPH_CONFLICT_POLICY.md`](./GLYPH_CONFLICT_POLICY.md)

---
*This document proposes conceptual macros for glyph system auditing. Drafted by Jules-06.*
