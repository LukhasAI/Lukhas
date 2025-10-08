"""Stub streamlit module for tests."""

from types import SimpleNamespace


def _noop(*args, **kwargs):
    return None


def set_page_config(*args, **kwargs):
    return None


def write(*args, **kwargs):
    return None


def markdown(*args, **kwargs):
    return None


def title(*args, **kwargs):
    return None


def warning(*args, **kwargs):
    return None


def caption(*args, **kwargs):
    return None


def info(*args, **kwargs):
    return None


def success(*args, **kwargs):
    return None


def error(*args, **kwargs):
    return None


class _StreamlitSectionShim(SimpleNamespace):
    def __getattr__(self, name):
        return _noop


class _StreamlitShim:
    def __init__(self):
        self.sidebar = _StreamlitSectionShim()

    def __getattr__(self, name):
        return _noop

    def set_page_config(self, *args, **kwargs):
        return set_page_config(*args, **kwargs)

    def write(self, *args, **kwargs):
        return write(*args, **kwargs)

    def markdown(self, *args, **kwargs):
        return markdown(*args, **kwargs)

    def title(self, *args, **kwargs):
        return title(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return warning(*args, **kwargs)

    def caption(self, *args, **kwargs):
        return caption(*args, **kwargs)

    def info(self, *args, **kwargs):
        return info(*args, **kwargs)

    def success(self, *args, **kwargs):
        return success(*args, **kwargs)

    def error(self, *args, **kwargs):
        return error(*args, **kwargs)


st = _StreamlitShim()
