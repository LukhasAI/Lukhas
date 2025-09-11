# Auto-generated help that discovers existing targets from Makefile + mk/*.mk
# It overrides any earlier 'help' target when included at the *end* of the root Makefile.

.PHONY: help

help:
	@echo "LUKHAS Build System — Auto Help"
	@echo "================================"
	@echo ""
	@sh -c 'set -e; \
	  have() { grep -R -h -E "^$$1:" Makefile mk/*.mk 2>/dev/null | grep -q .; }; \
	  print_section() { \
	    hdr="$$1"; shift; \
	    any=0; buf=""; \
	    for tgt in "$$@"; do \
	      if have "$$tgt"; then any=1; buf="$$buf\n  $$(printf %-20s "$$tgt")"; fi; \
	    done; \
	    if [ $$any -eq 1 ]; then \
	      echo "$$hdr"; \
	      printf "$$buf\n"; \
	      echo ""; \
	    fi; \
	  }; \
	  echo "Detected sections (only showing targets that exist):"; echo ""; \
	  print_section "Setup & Installation:" \
	    install setup-hooks bootstrap organize organize-dry organize-suggest organize-watch; \
	  print_section "Development:" \
	    dev api openapi live colony-dna-smoke audit-tail lane-guard quick; \
	  print_section "Testing:" \
	    test test-cov smoke test-tier1-matriz; \
	  print_section "Advanced Testing (0.001%):" \
	    test-advanced test-property test-chaos test-metamorphic test-formal test-mutation test-performance test-oracles test-consciousness test-standalone; \
	  print_section "CI/CD:" \
	    ci-local monitor audit audit-status audit-nav audit-scan audit-nav-info audit-scan-list audit-validate api-serve api-spec check-scoped promote; \
	  print_section "Doctor & Diagnostics:" \
	    doctor doctor-strict doctor-json doctor-dup-targets doctor-dup-targets-strict; \
	  print_section "Policy & Brand:" \
	    policy policy-review policy-brand policy-tone policy-registries policy-routes policy-vocab; \
	  print_section "Security:" \
	    security security-scan security-update security-audit security-fix security-fix-vulnerabilities security-fix-issues security-fix-all \
	    security-ollama security-ollama-fix security-ollama-setup security-comprehensive-scan security-emergency-patch test-security \
	    security-autopilot security-monitor security-status security-schedule security-schedule-3h security-schedule-tonight \
	    security-schedule-list security-schedule-run; \
	  print_section "SDK:" \
	    sdk-py-install sdk-py-test sdk-ts-build sdk-ts-test; \
	  print_section "Backup & DR:" \
	    backup-local backup-s3 restore-local restore-s3 dr-drill dr-weekly dr-quarterly dr-monthly; \
	  echo "Tip: run make doctor for a quick health scan, or make doctor-strict to fail on any warnings."; \
	'