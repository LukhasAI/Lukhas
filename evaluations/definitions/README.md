# Lukhas Mini-Evals

- **Format**: JSONL, one object per line:
```json
{"id":"echo-001","input":"hello lukhas","expect":{"contains":["echo","hello"]},"tools":[]}
```

- **Run**:
```bash
uvicorn lukhas.adapters.openai.api:get_app --reload &
python3 evals/run_evals.py --base-url http://localhost:8000 --cases "evals/cases/*.jsonl" --out docs/audits --threshold 0.7
```

- **Artifacts**: docs/audits/evals_report.json, docs/audits/evals_report.md (+ optional JUnit XML)
- **CI**: add as warn-only in MATRIZ Validate; flip --strict once stable.
