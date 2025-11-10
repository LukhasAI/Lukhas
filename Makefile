# LUKHAS AI Platform Makefile Router
# ============================================================================
# This Makefile acts as a router to provide a simplified developer experience
# while preserving the original, more complex build system.
#
# For a simplified set of common commands, see Makefile.dx.
# For the original, complete set of commands, see Makefile.lukhas.
# ============================================================================

.PHONY: help help-dx help-lukhas

# Default target
help:
	@echo "LUKHAS AI Platform Makefile"
	@echo ""
	@echo "Usage: make <command>"
	@echo ""
	@echo "A simplified developer experience is available in Makefile.dx."
	@echo "To see the available commands, run:"
	@echo ""
	@echo "    make help-dx"
	@echo ""
	@echo "To see the original, complete set of commands, run:"
	@echo ""
	@echo "    make help-lukhas"
	@echo ""

help-dx:
	@make -f Makefile.dx help

help-lukhas:
	@make -f Makefile.lukhas help

# Forward all other commands to Makefile.dx by default
%:
	@make -f Makefile.dx $@
