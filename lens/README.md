# ΛLens

Lightweight README for the ΛLens project (Lens symbolic dashboard and Photon contract).

Overview
--------
ΛLens is the symbolic file dashboard component of the LUKHΛS platform: it converts files and data into declarative Photon JSON documents that render dashboards, widgets and visualizations. The design is contract-first: Photon JSON (photon.schema) is the canonical UI description and Lens provides parsing, transformation and render pipelines to produce interactive dashboards (TableView, BarCompare, ForceGraph, etc.).

Key ideas
---------
- Contract-first: Photon JSON defines widgets, bindings and layout.
- Two-way editing: the Inspector allows Photon edits that re-render the UI; UI changes serialize back to Photon.
- Minimal, embeddable renderer: a small, dependency-free renderer (used by the Studio) provides HTML TableView and simple SVG BarCompare widgets for demos.
- Questioner integration planned: when bindings are missing, a guided Questioner will suggest and write bindings back into Photon.

Where things live
-----------------
- Schemas (pydantic): `lambda_products/lambda_products_pack/lambda_core/Lens/api/schemas.py`
- Example Photons used by tools and the Studio: `examples/photon_users.json` and variants under `l_lens/config/contracts/examples/` and `lukhas_website/public/lens/config/contracts/examples/`
- Small demo CSV used by the Studio: `lukhas_website/public/lens/data/users.csv`
- Validator and tools: `tools/validate_examples.py`, `tools/render_photon_minimal.py`, `tools/csv_profiler.py`
- Studio UI: `lukhas_website/app/studio/page.tsx` (loads photon JSON and CSV via `/lens/...` paths)

Quickstart (dev)
---------------
1. Run the example validator from the repo root to validate example Photon JSON against the pydantic schemas:

   python3 tools/validate_examples.py

2. Run the website Studio app for a quick preview (from `lukhas_website`):

   cd lukhas_website
   npm install
   npm run dev

   Open http://localhost:3000/studio and click "Λ Lens ▸ Load example" to render the demo Photon and CSV.

Developer notes
---------------
- The pydantic models are the source of truth for Photon validation. The validator script includes robust import fallbacks so it runs from the repo root.
- The demo CSV loader in the Studio is intentionally minimal (split-on-comma). Replace with a robust CSV parser for production.
- For unit testing, add small tests that instantiate pydantic models with fixture JSON from `examples/`.

Roadmap & references
--------------------
- See `lukhas_website/LUKHΛS_STUDIO_IMPLEMENTATION_ROADMAP.md` for the Studio and ΛLens implementation roadmap and architectural guidance.
- The archive of visionary documents and product content is in `lambda_products_pack/ARCHIVED_VISIONARY_INTEGRATION_COMPLETE.md` and `lukhas_website/LAMBDA_PRODUCTS_CONTENT.md`.
- TODO: wire a Questioner MVP to `tools/csv_profiler.py` so missing widget bindings can be suggested automatically.

Contributing
------------
- Keep Photon docs and schema in sync. When changing `schemas.py`, update `tools/validate_examples.py` and add an example JSON to `examples/` and `l_lens/config/contracts/examples/`.
- Run the repository linters and CI checks on a feature branch; this repo enforces heavy pre-commit checks so use small, focused commits.

License & governance
--------------------
Follow repo licensing and governance files at the repo root (LICENSE, CODE_OF_CONDUCT.md, CONTRIBUTING.md).
