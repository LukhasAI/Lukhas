from tools.check_openapi_drift import compute_openapi_diff, deep_schema_diff


def test_compute_openapi_diff_detects_added_and_removed_paths():
    saved = {
        "paths": {
            "/stable": {
                "get": {
                    "responses": {
                        "200": {"description": "Stable", "content": {}}
                    }
                }
            },
            "/removed": {
                "post": {
                    "responses": {
                        "201": {"description": "Created", "content": {}}
                    }
                }
            },
        }
    }
    live = {
        "paths": {
            "/stable": {
                "get": {
                    "responses": {
                        "200": {"description": "Stable", "content": {}}
                    }
                }
            },
            "/added": {
                "get": {
                    "responses": {
                        "200": {"description": "Added", "content": {}}
                    }
                }
            },
        }
    }

    summary = compute_openapi_diff(saved, live)

    assert summary["drift_detected"] is True
    assert summary["paths"]["added"] == ["/added"]
    assert summary["paths"]["removed"] == ["/removed"]
    assert summary["paths"]["modified"] == {}


def test_compute_openapi_diff_reports_method_and_response_changes():
    saved = {
        "paths": {
            "/delta": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Old",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "count": {"type": "integer"},
                                        },
                                        "required": ["name"],
                                    }
                                }
                            },
                        }
                    }
                }
            }
        }
    }
    live = {
        "paths": {
            "/delta": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Old",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "count": {"type": "number"},
                                            "status": {"type": "string"},
                                        },
                                        "required": ["name", "status"],
                                    }
                                }
                            },
                        },
                        "404": {
                            "description": "Missing",
                            "content": {},
                        },
                    }
                },
                "post": {
                    "responses": {
                        "201": {"description": "Created", "content": {}}
                    }
                },
            }
        }
    }

    summary = compute_openapi_diff(saved, live)

    assert summary["drift_detected"] is True
    modified_path = summary["paths"]["modified"]["/delta"]
    assert modified_path["added_methods"] == ["post"]
    responses = modified_path["modified_methods"]["get"]["responses"]
    assert responses["added"] == ["404"]

    modified_entries = responses["modified"][0]
    assert modified_entries["status"] == "200"
    diff_paths = {diff["path"] for diff in modified_entries["differences"]}
    assert "responses.200.content.application/json.schema.properties.count.type" in diff_paths
    assert "responses.200.content.application/json.schema.properties.status" in diff_paths
    assert (
        "responses.200.content.application/json.schema.required"
        in diff_paths
    )


def test_deep_schema_diff_handles_scalar_and_list_changes():
    saved = {"type": "object", "required": ["id"], "nullable": False}
    live = {"type": "object", "required": ["id", "name"], "nullable": True}

    diffs = deep_schema_diff(saved, live, "schema")

    diff_map = {entry["path"]: entry for entry in diffs}

    assert diff_map["schema.required"]["change"] == "modified"
    assert diff_map["schema.nullable"]["change"] == "modified"
