.PHONY: api audit-tail

api:
	uvicorn lukhas_pwm.api.app:app --reload --port 8000

audit-tail:
	@mkdir -p .lukhas_audit && touch .lukhas_audit/audit.jsonl
	tail -f .lukhas_audit/audit.jsonl
