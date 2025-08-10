import asyncio

from core.colonies.temporal_colony import TemporalColony


async def _run(colony, task):
    await colony.start()
    result = await colony.execute_task("t1", task)
    await colony.stop()
    return result


def test_future_simulation_does_not_commit():
    colony = TemporalColony("tc1")
    res = asyncio.run(
        _run(
            colony,
            {"simulate": True, "operations": [{"type": "add_glyph", "value": "✨"}]},
        )
    )
    assert colony.current_state["glyphs"] == []
    assert res["state"]["glyphs"] == ["✨"]


def test_reversible_reasoning():
    colony = TemporalColony("tc2")

    async def run():
        await colony.start()
        await colony.execute_task(
            "a", {"operations": [{"type": "add_glyph", "value": "💡"}]}
        )
        await colony.execute_task(
            "b", {"operations": [{"type": "add_glyph", "value": "🔥"}]}
        )
        state_before = list(colony.current_state["glyphs"])
        await colony.execute_task("c", {"revert": True})
        state_after = list(colony.current_state["glyphs"])
        await colony.stop()
        return state_before, state_after

    before, after = asyncio.run(run())
    assert before == ["💡", "🔥"]
    assert after == ["💡"]
