"""Stub pytest-asyncio plugin for configuration support."""

import asyncio
import inspect


def pytest_addoption(parser):
    parser.addini(
        "asyncio_default_fixture_loop_scope",
        "Stub option provided by test environment",
        default="function",
    )
    parser.addini(
        "asyncio_mode",
        "Stub asyncio mode option",
        default="auto",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: stub marker for async tests")


def pytest_pyfunc_call(pyfuncitem):
    test_function = pyfuncitem.obj
    if asyncio.iscoroutinefunction(test_function):
        signature = inspect.signature(test_function)
        kwargs = {name: pyfuncitem.funcargs[name] for name in signature.parameters if name in pyfuncitem.funcargs}
        asyncio.run(test_function(**kwargs))
        return True
    return None
