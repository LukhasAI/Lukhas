"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : symbolic_score.py                              │
│ DESCRIPTION : Calculate symbolic resonance scores            │
│ TYPE        : Resonance Scoring Engine                       │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

symbolic_scores = {}


def update_symbolic_score(user_id: int, category: str, value: float):
    """
    Update symbolic score by category (dreams, ethics, actions, mesh).
    """
    if user_id not in symbolic_scores:
        symbolic_scores[user_id] = {}

    current_score = symbolic_scores[user_id].get(category, 0.0)
    new_score = round(current_score + value, 3)
    symbolic_scores[user_id][category] = new_score

    print(f"🔮 Symbolic Score Updated: {user_id} → {category} = {new_score}")
    return new_score


def get_symbolic_score(user_id: int, category: str = None):
    """
    Retrieve symbolic scores for a user (by category or all).
    """
    if user_id not in symbolic_scores:
        return {} if category is None else 0.0
    if category:
        return symbolic_scores[user_id].get(category, 0.0)
    return symbolic_scores[user_id]


def reset_scores(user_id: int):
    """
    Reset all symbolic scores for a user.
    """
    symbolic_scores[user_id] = {}
    print(f"♻️ Symbolic scores reset for user {user_id}")
