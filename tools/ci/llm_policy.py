# tools/ci/llm_policy.py
from __future__ import annotations

import os
import sqlite3
from datetime import datetime

import requests

DB = "reports/todos/intent_registry.db"

PRICING = {
    "gpt-4o": {"prompt": 0.03, "completion": 0.06},
    "gpt-4o-mini": {"prompt": 0.005, "completion": 0.01},
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
}


def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def create_llm_tables():
    c = conn()
    c.execute("""
    CREATE TABLE IF NOT EXISTS llm_usage (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      timestamp TEXT,
      api_key TEXT,
      agent_id TEXT,
      model TEXT,
      prompt_tokens INTEGER,
      completion_tokens INTEGER,
      est_cost REAL
    )""")
    c.commit()
    c.close()


create_llm_tables()


def estimate_cost(model, prompt_tokens, completion_tokens):
    pr = PRICING.get(model, PRICING["gpt-4o-mini"])
    return (prompt_tokens / 1000.0) * pr["prompt"] + (completion_tokens / 1000.0) * pr["completion"]


def count_tokens_approx(text: str) -> int:
    return max(1, int(len(text) / 4))


def record_usage(api_key, agent_id, model, prompt_tokens, completion_tokens, est_cost):
    c = conn()
    c.execute(
        "INSERT INTO llm_usage (timestamp,api_key,agent_id,model,prompt_tokens,completion_tokens,est_cost) VALUES (?,?,?,?,?,?,?)",
        (
            datetime.utcnow().isoformat(),
            api_key,
            agent_id,
            model,
            prompt_tokens,
            completion_tokens,
            est_cost,
        ),
    )
    c.execute(
        "UPDATE api_keys SET daily_used = COALESCE(daily_used,0) + ? WHERE key=?",
        (est_cost, api_key),
    )
    c.commit()
    c.close()


def call_openai_chat(
    prompt: str,
    model: str,
    api_key_env: str = "OPENAI_API_KEY",
    max_completion_tokens: int = 1024,
    agent_api_key=None,
    agent_id=None,
):
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    p_tokens = count_tokens_approx(prompt)
    c_tokens = max_completion_tokens
    est = estimate_cost(model, p_tokens, c_tokens)
    if agent_api_key:
        c = conn()
        row = c.execute(
            "SELECT daily_limit, daily_used FROM api_keys WHERE key=?", (agent_api_key,)
        ).fetchone()
        if row:
            limit, used = row["daily_limit"] or 100.0, row["daily_used"] or 0.0
            if used + est > limit:
                raise PermissionError("Agent LLM daily quota exceeded")
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_completion_tokens,
            "temperature": 0.0,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    p_actual = usage.get("prompt_tokens", p_tokens)
    c_actual = usage.get("completion_tokens", c_tokens)
    actual_cost = estimate_cost(model, p_actual, c_actual)
    record_usage(agent_api_key, agent_id, model, p_actual, c_actual, actual_cost)
    return {
        "text": text,
        "prompt_tokens": p_actual,
        "completion_tokens": c_actual,
        "cost": actual_cost,
    }
