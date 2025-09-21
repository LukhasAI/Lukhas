# Dream Trace README

This document provides a detailed explanation of the recursive dream loops within the LUKHAS system, based on the audit performed by Jules-05.

## The Dream Recursion Loop

The dream recursion loop is a fundamental process for memory consolidation, creative recombination, and self-reflection in the LUKHAS Cognitive AI. It involves the following key steps:

1.  **Memory Selection:** The `EnhancedDreamEngine` selects a set of memories from the `AGIMemory` store. This selection can be based on various factors, including the memories' importance scores, recency, or emotional content.

2.  **Dream Seeding:** The selected memories are then used to "seed" a new dream. The `dream_seed.py` module contains functions that transform these memory traces into a dream narrative, which is a structured data object containing the dream's text, emotional context, and symbolic interpretation.

3.  **Dream Logging:** The generated dream narrative is logged to a persistent store, typically a JSONL file such as `dream_log.jsonl`.

4.  **User Reflection and Feedback:** The `dream_reflection_loop.py` utility allows a user to review the logged dreams and provide feedback in the form of scores, notes, or symbolic tags.

5.  **Closing the Loop:** This user feedback is then stored back into the `AGIMemory` as a new `MemoryFold`. This new memory, which contains a user's interpretation of a dream, can then become a seed for future dream cycles, creating a recursive loop of reflection and consolidation.

This recursive process allows the Cognitive AI to not only learn from its experiences but also to learn from its own interpretations of those experiences, as reflected in its dreams and the feedback it receives on them.

## Symbolic Tags in the Dream Loop

The following symbolic tags are particularly important for understanding the dream recursion loop:

*   **`#ΛDREAM_LOOP`**: Marks the core components and processes involved in the dream cycle.
*   **`#ΛRECALL_LOOP`**: A more specific tag that marks the recall aspect of the dream loop, where memories are selected for processing.
*   **`#ΛSEED`**: Marks the initial data (the `folded_trace`) that is used to generate a dream.
*   **`#ΛMEMORY_TRACE`**: Traces the lifecycle of a memory as it is transformed into a dream and then potentially back into a new memory based on user feedback.
*   **`#ΛFEEDBACK_LOOP`**: Marks the process where user feedback on a dream is captured and stored as a new memory.

By following these tags, it is possible to trace the flow of symbolic information through the dream recursion loop and to understand how the Cognitive AI's memories and interpretations evolve over time.
