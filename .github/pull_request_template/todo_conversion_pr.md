---
name: TODO Conversion / Cleanup
about: PR for TODO deletions, issue conversions, or batch fixes
---

## TODO Cleanup/Conversion PR

**Operation:** [delete obsolete | convert to issues | fix simple TODOs | archive candidate TODOs]  
**Input inventory:** `todo_inventory.csv` (attach)  
**Mapping file (if converting to issues):** `todo_to_issue_map.json` (attach)

### Automation/Manual gates
- [ ] Proposed deletions listed in `obsolete_todos_proposal.md`
- [ ] For conversions: `create_issues.py` run in dry-run then live-mode
- [ ] For replacements: `replace_todos_with_issues.py` dry-run logs attached
- [ ] Backups created for modified files (PR should include backups or recovery notes)

### Checklist
- [ ] Unit/Smoke tests run (must pass)
- [ ] Bulk change (>100 TODOs) — requires 2 human approvals
- [ ] Candidate TODOs archival PR created (if archiving)
- [ ] `TODO_CLEANUP_AUDIT.md` updated with summary
- [ ] Maintainer approves replacements/deletions

### Risk notes
- Security/privacy/model-safety TODOs must be converted to issues (do not delete).
