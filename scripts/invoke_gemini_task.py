#!/usr/bin/env python3
"""
Invoke Gemini API to execute a task from a brief file.

Usage:
    python scripts/invoke_gemini_task.py docs/agents/GEMINI_TASK_BLACK_FORMATTER.md
"""

import os
import sys
from pathlib import Path

def invoke_gemini_with_task(task_brief_path: str):
    """Invoke Gemini 2.0 Flash with code execution to handle a task."""

    # Read the task brief
    brief_path = Path(task_brief_path)
    if not brief_path.exists():
        print(f"❌ Task brief not found: {task_brief_path}")
        return 1

    task_brief = brief_path.read_text()

    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("💡 Set it in .env or export GOOGLE_API_KEY=your_key")
        return 1

    print(f"📋 Loading task brief from: {task_brief_path}")
    print(f"📏 Brief length: {len(task_brief)} characters\n")

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("❌ google-genai package not installed")
        print("💡 Install with: pip install google-genai")
        return 1

    # Create client
    client = genai.Client(api_key=api_key)

    # Construct prompt
    prompt = f"""You are Gemini Code Assist, a specialized AI agent for code refactoring and quality improvements.

I'm assigning you a task to work on the LUKHAS AI codebase. Please read the task brief below and execute it autonomously.

**IMPORTANT INSTRUCTIONS:**
1. Read the entire task brief carefully
2. Follow the 4-phase plan exactly as described
3. Use code execution to run commands when needed
4. Report progress after each phase
5. If you encounter blockers, explain them clearly
6. Create the PR as described in Phase 4

**YOUR TASK BRIEF:**

{task_brief}

---

**BEGIN EXECUTION:**

Please start by confirming you understand the task, then proceed with Phase 1 (Setup and Validation).
"""

    print("🚀 Invoking Gemini 2.0 Flash with code execution...")
    print("⏳ This may take several minutes...\n")

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(code_execution=types.ToolCodeExecution())],
                temperature=0.1,  # Low temperature for deterministic code execution
            )
        )

        print("📊 Gemini Response:")
        print("=" * 80)
        print(response.text)
        print("=" * 80)

        # Check if code was executed
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'executable_code'):
                            print("\n🔧 Code executed by Gemini:")
                            print(part.executable_code.code)
                        if hasattr(part, 'code_execution_result'):
                            print("\n📤 Execution result:")
                            print(part.code_execution_result.output)

        print("\n✅ Gemini invocation complete!")
        return 0

    except Exception as e:
        print(f"\n❌ Error invoking Gemini: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/invoke_gemini_task.py <task_brief_path>")
        print("Example: python scripts/invoke_gemini_task.py docs/agents/GEMINI_TASK_BLACK_FORMATTER.md")
        sys.exit(1)

    task_brief_path = sys.argv[1]
    sys.exit(invoke_gemini_with_task(task_brief_path))
