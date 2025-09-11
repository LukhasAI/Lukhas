# Auto-discovered help with inline descriptions (targets can add "## Description")
.PHONY: help
help:
	@echo "LUKHAS Build System — Auto Help"
	@echo "================================"
	@echo ""
	@sh -c '\
	  set -e; \
	  # Return 0 if a target exists in Makefile or mk/*.mk
	  have() { grep -R -h -E "^[[:alnum:]_.-]+:" Makefile mk/*.mk 2>/dev/null | cut -d: -f1 | grep -qx "$$1"; }; \
	  # Extract first inline description after "##"
	  desc() { \
	    grep -R -h -E "^$$1:[^#]*##" Makefile mk/*.mk 2>/dev/null \
	      | sed -n "1s/.*##[[:space:]]*//p"; \
	  }; \
	  # Print a section only if at least one target exists
	  print_section() { \
	    hdr="$$1"; shift; any=0; \
	    for tgt in "$$@"; do if have "$$tgt"; then any=1; break; fi; done; \
	    [ $$any -eq 1 ] || return 0; \
	    echo "$$hdr"; \
	    for tgt in "$$@"; do \
	      if have "$$tgt"; then \
	        d=$$(desc "$$tgt"); \
	        if [ -n "$$d" ]; then \
	          printf "  %-22s - %s\n" "$$tgt" "$$d"; \
	        else \
	          printf "  %-22s\n" "$$tgt"; \
	        fi; \
	      fi; \
	    done; \
	    echo ""; \
	  }; \
	  echo "Detected sections (only existing targets shown):"; echo ""; \
	  print_section "Setup & Installation:" \
	    install setup-hooks bootstrap organize organize-dry organize-suggest organize-watch; \
	  print_section "Development:" \
	    dev api openapi live colony-dna-smoke audit-tail lane-guard quick; \
	  print_section "Testing:" \
	    test test-cov smoke test-legacy test-tier1-matriz; \
	  print_section "Advanced Testing (0.001%):" \
	    test-advanced test-property test-chaos test-metamorphic test-formal test-mutation test-performance test-oracles test-consciousness test-standalone; \
	  print_section "CI/CD:" \
	    ci-local monitor audit audit-status audit-nav audit-scan audit-nav-info audit-scan-list audit-validate api-serve api-spec check-scoped promote pc-all; \
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
	  echo "Tip: add inline descriptions with ## after target names"; \
	'