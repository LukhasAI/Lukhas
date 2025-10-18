.PHONY: context-migrate-frontmatter context-coverage

context-migrate-frontmatter: ## Add YAML front-matter to lukhas_context.md (in manifests/**)
	python3 scripts/migrate_context_front_matter.py

context-coverage: ## Check lukhas_context.md coverage and front-matter presence
	python3 scripts/context_coverage_bot.py --manifests manifests --min $${MIN_COV:-0.95}
