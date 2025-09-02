## Contract Examples (save these exact files)

Below are minimal, schema-valid examples for the ΛLens MVP loop. Copy each block into the indicated path so the editor and renderers can run immediately.

### 1) job_users.json → l_lens/config/contracts/examples/job_users.json
```json
{
  "source_uri": "file:///data/users.csv",
  "source_type": "data",
  "policies": { "LLM_off": true, "redact_on": true, "offline_only": true },
  "target_forms": ["web2d"],
  "lid_context": { "user_id": "demo", "user_tier": "default" }
}
```

### 2) photon_users.json → l_lens/config/contracts/examples/photon_users.json
```json
{
  "photon_version": "1.0.0",
  "title": "Users Lens",
  "nodes": [
    { "id": "n_table", "kind": "TableView", "label": "Users Table",
      "properties": { "columns": ["name","email","created_at"] },
      "data_binding": { "type": "static", "value": "csv:/data/users.csv" } },
    { "id": "n_chart", "kind": "BarCompare", "label": "Signups per Month",
      "properties": { "x": "created_at:month", "y": "count" },
      "data_binding": { "type": "static", "value": "csv:/data/users.csv" } }
  ],
  "edges": [
    { "id": "e1", "source": "n_table", "target": "n_chart", "kind": "derives", "label": "Aggregation" }
  ],
  "layout": { "positions_2d": { "n_table": {"x":80,"y":120}, "n_chart": {"x":520,"y":120} } }
}
```

### 3) widget_presets.json → l_lens/config/contracts/examples/widget_presets.json
```json
{
  "presets": [
    {
      "id": "TableView",
      "label": "Table",
      "description": "Tabular data view",
      "icon": "table",
      "properties_schema": {
        "type": "object",
        "properties": {
          "columns": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
          "pageSize": { "type": "integer", "minimum": 5, "default": 20 }
        },
        "required": ["columns"]
      }
    },
    {
      "id": "BarCompare",
      "label": "Bar Chart",
      "description": "Compare categories over a measure",
      "icon": "bar-chart",
      "properties_schema": {
        "type": "object",
        "properties": {
          "x": { "type": "string" },
          "y": { "type": "string" },
          "stacked": { "type": "boolean", "default": false }
        },
        "required": ["x", "y"]
      }
    }
  ]
}
```

Next steps to validate

- Validate each file against `job.schema.json`, `photon.schema.json`, and `widget.schema.json`.
- Feed `photon_users.json` to `web2d_renderer.py` and confirm Table + Bar render.
- Keep `LLM_off=true` for this run; parsers should not require LLMs.