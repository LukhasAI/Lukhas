"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dast.py
Advanced: dast.py
Integration Date: 2025-05-31T07:55:30.571396
"""

"""
dast.py

Dynamic Agent Scheduler & Tracker (DAST)

This module serves as the intent router and symbolic task engine of the LUKHAS Agent.
It receives user intents, validates permissions via trust tiers, and delegates execution
to the correct logic modules like memory, voice, dream, or delegate systems.
"""


from consent_manager import verify_or_revoke
from ethics_jury import run_ethics_review, should_trigger_jury

from lukhas.core.interfaces.logic.voice.voice_renderer import render_voice

# Registry of available symbolic tasks
REGISTERED_TASKS = {}


def register_task(name):
    """
    Decorator to register a symbolic DAST task.
    """

    def wrapper(func):
        REGISTERED_TASKS[name] = func
        return func

    return wrapper


# ----------------------------
# Intent Dispatch Engine
# ----------------------------


def dispatch(intent, tier_level=1, emotion_score=0.0, context=None):
    """
    Main routing engine. Routes symbolic intent to its associated logic.
    """
    print(f"\n🧭 Routing Intent: {intent}")

    # 1. Permission check
    if not verify_or_revoke(intent, tier_level, emotion_score):
        return render_voice("ethical_alert")

    # 2. Ethics jury if needed
    if should_trigger_jury(intent, emotion_score):
        verdict = run_ethics_review(intent, context or "")
        if verdict != "approve":
            return render_voice("ethical_alert")

    # 3. Route to registered handler
    task_func = REGISTERED_TASKS.get(intent)
    if task_func:
        return task_func(context)
    else:
        print(f"⚠️ No task registered for: {intent}")
        return render_voice("reflective")


# ----------------------------
# Example Tasks (to be moved to dast_tasks.py later)
# ----------------------------


@register_task("dream_summary")
def handle_dream_summary(context):
    from dream_engine import generate_dream_digest

    dream = generate_dream_digest()
    print("🌙 Dream Summary:", dream)
    return render_voice("reflective")


@register_task("delegate_payment")
def handle_delegate_payment(context):
    from delegate_logic import perform_payment

    perform_payment(context)
    return render_voice("calm")


@register_task("local_ethical_alert")
def handle_ethical_signal(context):
    print("📣 Ethical alert dispatched for low-waste opportunity.")
    return render_voice("joyful")