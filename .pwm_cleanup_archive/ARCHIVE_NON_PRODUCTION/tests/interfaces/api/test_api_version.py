from interfaces.api import API_PREFIX, API_VERSION


def test_api_version_constants():
    assert API_VERSION == "v1"
    assert f"/api/{API_VERSION}" == API_PREFIX
