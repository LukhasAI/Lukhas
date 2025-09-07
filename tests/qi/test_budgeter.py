import os
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from candidate.qi.ops import budgeter as budgeter_mod


def test_plan_and_check_defaults(tmp_path):
    # ΛTAG: budget_test
    budgeter_mod.STATE = str(tmp_path)
    budgeter_mod.BUDGET_FILE = os.path.join(budgeter_mod.STATE, "budget_state.json")
    budgeter_mod.CONF_FILE = os.path.join(budgeter_mod.STATE, "budget_config.json")

    b = budgeter_mod.Budgeter()
    plan = b.plan(text="hello", model="default")
    assert plan["tokens_planned"] > 0
    assert plan["energy_wh"] > 0
    verdict = b.check(user_id=None, task=None, plan=plan)
    assert verdict["ok"]
    b.commit(
        user_id="u",
        task="t",
        actual_tokens=plan["tokens_planned"],
        latency_ms=plan["latency_est_ms"],
    )
    assert b.state["runs"]
