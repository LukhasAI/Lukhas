from lukhas.orchestration.kernel_bus import KernelBus


def test_kernel_bus_emit_and_status_dry_run():
    KernelBus()
res = bus.emit("unit_test_event", {"ok": True})
assert res["ok"] is True
status = bus.get_status()
assert status["ok"] is True
assert status["mode"] == "dry_run"
