import streamlit as st
"""API package with versioned interfaces."""

API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

SUPPORTED_VERSIONS = ["v1"]
VERSION_DEPRECATION: dict[str, str] = {}
