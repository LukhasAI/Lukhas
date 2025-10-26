# Context Extractor Skill

Systematically extract, validate and normalize `lukhas_context.md` files; create stubs where missing; produce a centralized `context_index.json` describing ownership, dependencies, intended module structure, test coverage, and risk notes for each directory.

## Reasoning

1. Walk the repo tree and find all `lukhas_context.md` files. If absent for a directory with source code, produce a well-formed stub containing required metadata fields.

2. Normalize context files to a canonical schema (name, purpose, owner, dependencies, CI, public API, tests, deployment, ethical_notes). This allows other CLAUDE skills to rely on a predictable structure.

3. Validate contexts with existing scripts (e.g., `scripts/validate_context_files.sh`) and produce a context_index.json summarizing completeness and gaps for maintainers to triage.

4. If ambiguous or missing fields are detected, the skill emits a small interactive checklist and a recommended textual prompt to present to module owners for clarification.

5. Automate with a GitHub Action to keep contexts in-sync and to surface missing contexts on PRs (fail fast).

## Actions

### Artifacts delivered:
- `scripts/context_extractor.py` which builds `context_index.json` and creates stubs for missing contexts.
- A canonical `lukhas_context.schema.md` that describes required fields and examples.
- A recommended GitHub Action (see `workflow_enforcer`) to run the extractor on PRs.

### Example `lukhas_context.schema.md` (required fields):

```md
# lukhas_context.md schema (LUKHΛS canonical)

fields:
- name: short human-friendly module name
- purpose: 1-paragraph description of intent and responsibilities
- owner: GitHub handle and email
- public_api: list of public functions/classes with brief descriptions
- dependencies: other LUKHΛS modules or external libs
- tests: path to tests that exercise the module
- deploy: deployment notes or 'local' if not deployed
- ethical_notes: short note when module touches consciousness/ethics
- last_updated: ISO date
```

### Example `scripts/context_extractor.py` core (abbreviated):

```python
import os, json, datetime
SCHEMA_KEYS = ['name','purpose','owner','public_api','dependencies','tests','deploy','ethical_notes','last_updated']
def read_context(path):
    try:
        with open(path,'r',encoding='utf-8') as fh: return fh.read()
    except Exception: return None
def make_stub(dirpath):
    stub = {k: '' for k in SCHEMA_KEYS}
    stub['name'] = os.path.basename(dirpath)
    stub['purpose'] = 'STUB: describe module purpose.'
    stub['owner'] = 'owner@lukhas'
    stub['last_updated'] = datetime.date.today().isoformat()
    with open(os.path.join(dirpath,'lukhas_context.md'),'w',encoding='utf-8') as fh: fh.write(json.dumps(stub,indent=2))
def main(root='.'):
    index = {}
    for d,_,files in os.walk(root):
        if 'lukhas_context.md' in files:
            ctx = read_context(os.path.join(d,'lukhas_context.md'))
            index[d] = {'present':True,'summary':ctx[:400]}
        else:
            # heuristics: if dir contains .py or package, create stub
            if any(f.endswith('.py') for f in files):
                make_stub(d)
                index[d] = {'present':False,'action':'stub_created'}
    with open('context_index.json','w',encoding='utf-8') as fh: json.dump(index,fh,indent=2)
if __name__=='__main__': main()
```

### Run & Integration:
- Dry-run: `python3 scripts/context_extractor.py` (no destructive ops).
- Apply: commit the stubs and request module owners to fill them in.
- Use `scripts/validate_context_files.sh` to lint contexts before merging.

## Context References

- `/docs/CONTEXT_FILES.md`
- `/scripts/context_coverage_bot.py`
- `/scripts/validate_context_files.sh`
- `/context_files.txt`
