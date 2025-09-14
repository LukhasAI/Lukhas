# Test targets (core & advanced)
.PHONY: test test-cov smoke test-tier1-matriz test-advanced test-property test-chaos test-metamorphic test-formal test-mutation test-performance test-oracles test-consciousness test-standalone
test: ## Run full test suite
	pytest tests/ -v --junitxml=test-results.xml

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=lukhas --cov=candidate --cov=bridge --cov=core --cov=serve --cov-report=html --cov-report=xml --cov-report=term --junitxml=test-results.xml

smoke:
	python3 scripts/testing/smoke_check.py

test-tier1-matriz: ## Run MATRIZ Tier-1 tests (fast, blocking smoke)
	PYTHONPATH=. python3 -m pytest -q -m tier1 tests_new/matriz

test-advanced:
	@echo "🧬 Running Advanced Testing Suite (0.001% Methodology)..."
	python3 rl/run_advanced_tests.py --verbose

test-property:
	@echo "🔬 Running Property-Based Tests..."
	pytest rl/tests/test_consciousness_properties.py -v -m property_based --tb=short

test-chaos:
	@echo "🌪️ Running Chaos Engineering Tests..."
	pytest rl/tests/test_chaos_consciousness.py -v -m chaos_engineering --tb=short

test-metamorphic:
	@echo "🔄 Running Metamorphic Tests..."
	pytest rl/tests/test_metamorphic_consciousness.py -v -m metamorphic --tb=short

test-formal:
	@echo "⚖️ Running Formal Verification Tests..."
	pytest rl/tests/test_formal_verification.py -v -m formal_verification --tb=short

test-mutation:
	@echo "🧬 Running Mutation Tests..."
	pytest rl/tests/test_mutation_testing.py -v -m mutation_testing --tb=short

test-performance:
	@echo "📊 Running Performance Regression Tests..."
	pytest rl/tests/test_performance_regression.py -v -m performance_regression --tb=short

test-oracles:
	@echo "🔮 Running Generative Oracle Tests..."
	pytest rl/tests/test_generative_oracles.py -v -m generative_oracles --tb=short

test-consciousness:
	@echo "🧠 Running Complete Consciousness Testing Suite..."
	pytest tests/consciousness/ rl/tests/ -v -m consciousness --tb=short

test-standalone:
	@echo "🚀 Running Standalone Advanced Test Suite..."
	python3 test_advanced_suite_standalone.py