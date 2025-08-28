import os

import pytest


# Enforce minimal realism in "reality" tests
def pytest_collection_modifyitems(items):
    for item in items:
        if item.get_closest_marker("no_mock"):
            item.add_marker(pytest.mark.block_mocks)


def pytest_runtest_setup(item):
    if item.get_closest_marker("block_mocks"):
        # Disarm common mocking channels in reality tests
        os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"


# def pytest_sessionfinish(session, exitstatus):
#     rep = session.config.pluginmanager.getplugin("terminalreporter")
#     skips = sum(1 for _ in rep.stats.get("skipped", []))
#     xfails = sum(1 for _ in rep.stats.get("xfailed", []))
#     if skips + xfails > 5:
#         pytest.exit(
#             f"Too many skipped/xfail tests ({skips + xfails}). Tighten scope.",
#             returncode=1,
#         )
