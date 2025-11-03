#!/usr/bin/env python3
"""
Ethics DSL Evaluation Tests
===========================

Task 11: Comprehensive tests for ethics DSL determinism and performance.

Test coverage:
- DSL predicate functions
- Rule compilation and evaluation
- Ethics engine priority lattice
- Performance benchmarks (<1ms p95)
- Deterministic behavior validation
"""
import time

import pytest
from core.ethics.logic.dsl_lite import (
    DSLError,
    and_op,
    canonical_domain,
    compile_rule,
    contains,
    domain_etld1,
    domain_is,
    equals,
    greater_than,
    hash_rule,
    is_empty,
    is_present,
    less_than,
    matches,
    not_has_consent,
    not_op,
    or_op,
    param_bytes_lte,
    param_seconds_lte,
    parse_bytes,
    parse_seconds,
)
from core.ethics.logic.ethics_engine import (
    EthicsAction,
    EthicsEngine,
    EthicsRule,
    Priority,
    RuleSet,
)


class TestDSLPredicates:
    """Test pure DSL predicate functions."""

    def test_contains_predicate(self):
        """Test contains predicate function."""
        assert contains("hello world", "world") is True
        assert contains("hello world", "WORLD") is True  # case insensitive
        assert contains("hello world", "xyz") is False
        assert contains(None, "anything") is False
        assert contains(123, "2") is True
        assert contains("", "test") is False

    def test_equals_predicate(self):
        """Test equals predicate function."""
        assert equals("test", "test") is True
        assert equals("test", "TEST") is False  # case sensitive
        assert equals(123, 123) is True
        assert equals(123, "123") is False
        assert equals(None, None) is True
        assert equals(None, "test") is False

    def test_greater_than_predicate(self):
        """Test greater_than predicate function."""
        assert greater_than(10, 5) is True
        assert greater_than(5, 10) is False
        assert greater_than(10, 10) is False
        assert greater_than("10", "5") is True  # string conversion
        assert greater_than("invalid", 5) is False
        assert greater_than(5, "invalid") is False

    def test_less_than_predicate(self):
        """Test less_than predicate function."""
        assert less_than(5, 10) is True
        assert less_than(10, 5) is False
        assert less_than(10, 10) is False
        assert less_than("5", "10") is True  # string conversion
        assert less_than("invalid", 5) is False

    def test_matches_predicate(self):
        """Test regex matches predicate function."""
        assert matches("test123", r"\d+") is True
        assert matches("testABC", r"\d+") is False
        assert matches("user@domain.com", r".*@.*\.com") is True
        assert matches(None, r".*") is False
        assert matches("test", "invalid[regex") is False  # invalid regex

    def test_is_empty_predicate(self):
        """Test is_empty predicate function."""
        assert is_empty(None) is True
        assert is_empty("") is True
        assert is_empty([]) is True
        assert is_empty({}) is True
        assert is_empty(set()) is True
        assert is_empty("test") is False
        assert is_empty([1, 2, 3]) is False
        assert is_empty({"key": "value"}) is False

    def test_is_present_predicate(self):
        """Test is_present predicate function."""
        assert is_present("test") is True
        assert is_present([1, 2, 3]) is True
        assert is_present({"key": "value"}) is True
        assert is_present(None) is False
        assert is_present("") is False
        assert is_present([]) is False

    def test_logical_operators(self):
        """Test logical operator functions."""
        assert and_op(True, True, True) is True
        assert and_op(True, False, True) is False
        assert and_op() is True  # empty and

        assert or_op(False, False, True) is True
        assert or_op(False, False, False) is False
        assert or_op() is False  # empty or

        assert not_op(True) is False
        assert not_op(False) is True

    def test_not_has_consent_predicate(self):
        """Test not_has_consent predicate function."""
        assert not_has_consent(None) is True
        assert not_has_consent(False) is True
        assert not_has_consent(True) is False
        assert not_has_consent("false") is True
        assert not_has_consent("no") is True
        assert not_has_consent("deny") is True
        assert not_has_consent("reject") is True
        assert not_has_consent("") is True
        assert not_has_consent("yes") is False
        assert not_has_consent("true") is False


class TestDomainPredicates:
    """Test domain-related predicates."""

    def test_canonical_domain(self):
        """Test domain canonicalization."""
        assert canonical_domain("OPENAI.COM") == "openai.com"
        assert canonical_domain("https://api.openai.com:443/path") == "api.openai.com"
        assert canonical_domain("openai.com.") == "openai.com"  # trailing dot
        assert canonical_domain("http://192.168.1.1") == "192.168.1.1"
        assert canonical_domain("invalid://") == ""  # fail closed

        # Scheme-less URLs
        assert canonical_domain("api.openai.com") == "api.openai.com"
        assert canonical_domain("subdomain.example.org") == "subdomain.example.org"

    def test_domain_is_predicate(self):
        """Test exact domain matching."""
        assert domain_is("https://api.openai.com/path", "api.openai.com") is True
        assert domain_is("https://api.openai.com/path", "openai.com") is False
        assert domain_is("API.OPENAI.COM", "api.openai.com") is True  # case insensitive
        assert domain_is("https://other.com", "openai.com") is False
        assert domain_is(None, "openai.com") is False
        assert domain_is("https://openai.com", None) is False

    def test_domain_etld1_predicate(self):
        """Test eTLD+1 domain matching."""
        assert domain_etld1("https://api.openai.com/path", "openai.com") is True
        assert domain_etld1("https://sub.api.openai.com", "openai.com") is True
        assert domain_etld1("https://openai.com", "openai.com") is True
        assert domain_etld1("https://other.com", "openai.com") is False
        assert domain_etld1("https://openai-fake.com", "openai.com") is False
        assert domain_etld1(None, "openai.com") is False


class TestUnitsPredicates:
    """Test units parsing predicates."""

    def test_parse_bytes(self):
        """Test byte parsing with units."""
        assert parse_bytes("1024") == 1024
        assert parse_bytes("1KB") == 1000
        assert parse_bytes("1KiB") == 1024
        assert parse_bytes("1MB") == 1000000
        assert parse_bytes("1MiB") == 1024**2
        assert parse_bytes("1.5GB") == int(1.5 * 1000**3)
        assert parse_bytes("2GiB") == 2 * 1024**3

        # Shorthand
        assert parse_bytes("1K") == 1024
        assert parse_bytes("1M") == 1024**2

    def test_parse_seconds(self):
        """Test time parsing with units."""
        assert parse_seconds("60") == 60.0
        assert parse_seconds("1s") == 1.0
        assert parse_seconds("1000ms") == 1.0
        assert parse_seconds("1m") == 60.0
        assert parse_seconds("1h") == 3600.0
        assert parse_seconds("1d") == 86400.0
        assert parse_seconds("1.5h") == 5400.0

    def test_param_bytes_lte(self):
        """Test param_bytes_lte predicate."""
        assert param_bytes_lte("1024", "1MB") is True  # 1024 bytes < 1MB
        assert param_bytes_lte("2048", "1KB") is False  # 2048 bytes > 1KB
        assert param_bytes_lte("1MB", "1MB") is True  # equal
        assert param_bytes_lte(None, "1MB") is True  # missing param passes

    def test_param_seconds_lte(self):
        """Test param_seconds_lte predicate."""
        assert param_seconds_lte("30", "1m") is True  # 30s < 1m
        assert param_seconds_lte("90", "1m") is False  # 90s > 1m
        assert param_seconds_lte("1m", "60s") is True  # equal
        assert param_seconds_lte(None, "1h") is True  # missing param passes


class TestDSLCompilation:
    """Test DSL rule compilation."""

    def test_simple_predicate_compilation(self):
        """Test compilation of simple predicates."""
        rule = compile_rule('contains(action, "test")')
        assert callable(rule)

        # Test evaluation
        plan = {"action": "test_action", "params": {}}
        assert rule(plan) is True

        plan = {"action": "other_action", "params": {}}
        assert rule(plan) is False

    def test_path_resolution(self):
        """Test dotted path resolution in rules."""
        rule = compile_rule('equals(params.url, "https://api.openai.com")')

        plan = {"action": "external_call", "params": {"url": "https://api.openai.com"}}
        assert rule(plan) is True

        plan = {"action": "external_call", "params": {"url": "https://other.com"}}
        assert rule(plan) is False

    def test_context_path_resolution(self):
        """Test context path resolution."""
        rule = compile_rule('equals(context.user_id, "user123")')

        plan = {"action": "test"}
        context = {"user_id": "user123"}
        assert rule(plan, context) is True

        context = {"user_id": "other_user"}
        assert rule(plan, context) is False

    def test_logical_operator_compilation(self):
        """Test compilation of logical operators."""
        rule = compile_rule('and(equals(action, "test"), contains(params.data, "sensitive"))')

        plan = {"action": "test", "params": {"data": "sensitive_info"}}
        assert rule(plan) is True

        plan = {"action": "test", "params": {"data": "public_info"}}
        assert rule(plan) is False

        plan = {"action": "other", "params": {"data": "sensitive_info"}}
        assert rule(plan) is False

    def test_nested_logical_operators(self):
        """Test nested logical operator compilation."""
        rule = compile_rule('or(and(equals(action, "read"), contains(params, "user")), equals(action, "admin"))')

        plan = {"action": "read", "params": {"user_data": True}}
        assert rule(plan) is True

        plan = {"action": "admin", "params": {}}
        assert rule(plan) is True

        plan = {"action": "read", "params": {"system_data": True}}
        assert rule(plan) is False

    def test_invalid_rule_compilation(self):
        """Test error handling for invalid rules."""
        with pytest.raises(DSLError):
            compile_rule("invalid_syntax")

        with pytest.raises(DSLError):
            compile_rule("unknown_predicate(action)")

        with pytest.raises(DSLError):
            compile_rule("contains(")  # incomplete

    def test_rule_hash_consistency(self):
        """Test rule hash determinism."""
        rule1 = 'contains(action, "test")'
        rule2 = 'contains(action, "test")'
        rule3 = 'contains(action, "other")'

        assert hash_rule(rule1) == hash_rule(rule2)
        assert hash_rule(rule1) != hash_rule(rule3)

    def test_fail_closed_evaluation(self):
        """Test that evaluation errors fail closed."""
        # Create a rule that will cause evaluation error
        rule = compile_rule('contains(action, "test")')

        # Test with invalid plan structure
        assert rule(None) is False  # Should fail closed
        assert rule("not_a_dict") is False  # Should fail closed


class TestEthicsEngine:
    """Test ethics engine functionality."""

    def setup_method(self):
        """Set up test rules."""
        self.test_rules = [
            EthicsRule(
                name="block_harmful",
                description="Block harmful actions",
                rule_dsl='equals(action, "delete_user_data")',
                action=EthicsAction.BLOCK,
                priority=Priority.CRITICAL,
                tags={"security"}
            ),
            EthicsRule(
                name="warn_external",
                description="Warn on external calls",
                rule_dsl='equals(action, "external_call")',
                action=EthicsAction.WARN,
                priority=Priority.MEDIUM,
                tags={"audit"}
            ),
            EthicsRule(
                name="block_excessive_memory",
                description="Block excessive memory usage",
                rule_dsl='greater_than(params.estimated_memory_mb, 1024)',
                action=EthicsAction.BLOCK,
                priority=Priority.HIGH,
                tags={"resources"}
            )
        ]

        self.rule_set = RuleSet(self.test_rules)
        self.engine = EthicsEngine(self.rule_set)

    def test_rule_priority_sorting(self):
        """Test that rules are sorted by priority."""
        # Rules should be sorted: CRITICAL, HIGH, MEDIUM
        assert self.rule_set.rules[0].priority == Priority.CRITICAL
        assert self.rule_set.rules[1].priority == Priority.HIGH
        assert self.rule_set.rules[2].priority == Priority.MEDIUM

    def test_block_action_evaluation(self):
        """Test evaluation that results in BLOCK."""
        plan = {"action": "delete_user_data", "params": {}}
        result = self.engine.evaluate_plan(plan)

        assert result.action == EthicsAction.BLOCK
        assert len(result.triggered_rules) == 1
        assert result.triggered_rules[0].name == "block_harmful"
        assert "block: block_harmful" in result.reasons

    def test_warn_action_evaluation(self):
        """Test evaluation that results in WARN."""
        plan = {"action": "external_call", "params": {}}
        result = self.engine.evaluate_plan(plan)

        assert result.action == EthicsAction.WARN
        assert len(result.triggered_rules) == 1
        assert result.triggered_rules[0].name == "warn_external"
        assert "warn: warn_external" in result.reasons

    def test_allow_action_evaluation(self):
        """Test evaluation that results in ALLOW."""
        plan = {"action": "safe_operation", "params": {}}
        result = self.engine.evaluate_plan(plan)

        assert result.action == EthicsAction.ALLOW
        assert len(result.triggered_rules) == 0
        assert result.reasons == ["allow: no_rules_triggered"]

    def test_priority_lattice_block_wins(self):
        """Test that BLOCK action wins over WARN in priority lattice."""
        plan = {
            "action": "external_call",
            "params": {"estimated_memory_mb": 2048}
        }
        result = self.engine.evaluate_plan(plan)

        assert result.action == EthicsAction.BLOCK  # BLOCK wins over WARN
        assert len(result.triggered_rules) == 2  # Both rules triggered

        # Should have both reasons but final action is BLOCK
        rule_names = {r.name for r in result.triggered_rules}
        assert "warn_external" in rule_names
        assert "block_excessive_memory" in rule_names

    def test_is_plan_allowed(self):
        """Test convenience method for plan allowance."""
        allowed_plan = {"action": "safe_operation", "params": {}}
        assert self.engine.is_plan_allowed(allowed_plan) is True

        warn_plan = {"action": "external_call", "params": {}}
        assert self.engine.is_plan_allowed(warn_plan) is True  # WARN is allowed

        blocked_plan = {"action": "delete_user_data", "params": {}}
        assert self.engine.is_plan_allowed(blocked_plan) is False

    def test_evaluation_audit_trail(self):
        """Test that evaluations are recorded in audit trail."""
        initial_count = len(self.engine.evaluation_history)

        plan = {"action": "test_action", "params": {}}
        self.engine.evaluate_plan(plan)

        assert len(self.engine.evaluation_history) == initial_count + 1

        entry = self.engine.evaluation_history[-1]
        assert "timestamp" in entry
        assert "plan_hash" in entry
        assert "action" in entry
        assert "evaluation_time_ms" in entry

    def test_get_stats(self):
        """Test engine statistics."""
        stats = self.engine.get_stats()

        assert stats["total_rules"] == 3
        assert stats["rules_by_action"]["block"] == 2
        assert stats["rules_by_action"]["warn"] == 1
        assert stats["rules_by_action"]["allow"] == 0
        assert "evaluation_history_size" in stats


class TestDeterminismAndPerformance:
    """Test deterministic behavior and performance requirements."""

    def setup_method(self):
        """Set up test engine."""
        rules = [
            EthicsRule(
                name="test_rule",
                description="Test rule for determinism",
                rule_dsl='and(equals(action, "test"), contains(params.data, "value"))',
                action=EthicsAction.WARN,
                priority=Priority.MEDIUM,
                tags={"test"}
            )
        ]
        self.engine = EthicsEngine(RuleSet(rules))

    def test_deterministic_evaluation(self):
        """Test that same plan+context always produces same result."""
        plan = {"action": "test", "params": {"data": "test_value"}}
        context = {"user_id": "user123"}

        # Run evaluation multiple times
        results = []
        for _ in range(10):
            result = self.engine.evaluate_plan(plan, context)
            results.append((
                result.action,
                tuple(r.name for r in result.triggered_rules),
                tuple(result.reasons)
            ))

        # All results should be identical
        assert len(set(results)) == 1

    def test_performance_benchmark(self):
        """Test that evaluation meets <1ms p95 requirement."""
        plan = {"action": "test", "params": {"data": "test_value"}}

        # Warm up
        for _ in range(10):
            self.engine.evaluate_plan(plan)

        # Benchmark
        durations = []
        for _ in range(100):
            start = time.perf_counter()
            self.engine.evaluate_plan(plan)
            duration_ms = (time.perf_counter() - start) * 1000
            durations.append(duration_ms)

        # Calculate P95
        durations.sort()
        p95_index = int(0.95 * len(durations))
        p95_duration = durations[p95_index]

        assert p95_duration < 1.0, f"P95 duration {p95_duration:.2f}ms exceeds 1ms requirement"

    def test_plan_hash_consistency(self):
        """Test that plan hashes are consistent for same plans."""
        plan = {"action": "test", "params": {"data": "value"}}
        context = {"user_id": "user123"}

        result1 = self.engine.evaluate_plan(plan, context)
        result2 = self.engine.evaluate_plan(plan, context)

        assert result1.plan_hash == result2.plan_hash

        # Different plan should have different hash
        plan2 = {"action": "test", "params": {"data": "other_value"}}
        result3 = self.engine.evaluate_plan(plan2, context)

        assert result1.plan_hash != result3.plan_hash


class TestRuleSetOperations:
    """Test rule set query operations."""

    def setup_method(self):
        """Set up test rule set."""
        self.rules = [
            EthicsRule("rule1", "desc1", "equals(action, 'test')",
                      EthicsAction.BLOCK, Priority.CRITICAL, {"security"}),
            EthicsRule("rule2", "desc2", "equals(action, 'test')",
                      EthicsAction.WARN, Priority.MEDIUM, {"audit"}),
            EthicsRule("rule3", "desc3", "equals(action, 'test')",
                      EthicsAction.BLOCK, Priority.HIGH, {"security", "resources"})
        ]
        self.rule_set = RuleSet(self.rules)

    def test_get_rules_by_tag(self):
        """Test getting rules by tag."""
        security_rules = self.rule_set.get_rules_by_tag("security")
        assert len(security_rules) == 2
        assert all("security" in rule.tags for rule in security_rules)

        audit_rules = self.rule_set.get_rules_by_tag("audit")
        assert len(audit_rules) == 1

        nonexistent_rules = self.rule_set.get_rules_by_tag("nonexistent")
        assert len(nonexistent_rules) == 0

    def test_get_rules_by_action(self):
        """Test getting rules by action."""
        block_rules = self.rule_set.get_rules_by_action(EthicsAction.BLOCK)
        assert len(block_rules) == 2

        warn_rules = self.rule_set.get_rules_by_action(EthicsAction.WARN)
        assert len(warn_rules) == 1

        allow_rules = self.rule_set.get_rules_by_action(EthicsAction.ALLOW)
        assert len(allow_rules) == 0

    def test_get_rules_by_priority(self):
        """Test getting rules by priority."""
        critical_rules = self.rule_set.get_rules_by_priority(Priority.CRITICAL)
        assert len(critical_rules) == 1

        medium_rules = self.rule_set.get_rules_by_priority(Priority.MEDIUM)
        assert len(medium_rules) == 1

        low_rules = self.rule_set.get_rules_by_priority(Priority.LOW)
        assert len(low_rules) == 0


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def setup_method(self):
        """Load rules from YAML config."""
        # Load default rules (would normally come from config file)
        default_rules = [
            EthicsRule(
                name="block_harmful_actions",
                description="Block explicitly harmful actions",
                rule_dsl='or(equals(action, "delete_user_data"), equals(action, "access_private_info"))',
                action=EthicsAction.BLOCK,
                priority=Priority.CRITICAL,
                tags={"security", "privacy"}
            ),
            EthicsRule(
                name="warn_external_calls",
                description="Warn on external API calls",
                rule_dsl='equals(action, "external_call")',
                action=EthicsAction.WARN,
                priority=Priority.MEDIUM,
                tags={"audit", "external"}
            ),
            EthicsRule(
                name="block_excessive_resources",
                description="Block excessive resource usage",
                rule_dsl='greater_than(params.estimated_memory_mb, 1024)',
                action=EthicsAction.BLOCK,
                priority=Priority.HIGH,
                tags={"resources"}
            )
        ]

        self.engine = EthicsEngine(RuleSet(default_rules))

    def test_safe_ai_model_call(self):
        """Test safe AI model API call."""
        plan = {
            "action": "external_call",
            "params": {
                "url": "https://api.openai.com/v1/chat/completions",
                "method": "POST",
                "estimated_memory_mb": 64
            }
        }

        result = self.engine.evaluate_plan(plan)
        assert result.action == EthicsAction.WARN  # Should warn but allow
        assert self.engine.is_plan_allowed(plan) is True

    def test_harmful_action_blocked(self):
        """Test that harmful actions are blocked."""
        plan = {
            "action": "delete_user_data",
            "params": {"user_id": "victim_user"}
        }

        result = self.engine.evaluate_plan(plan)
        assert result.action == EthicsAction.BLOCK
        assert self.engine.is_plan_allowed(plan) is False

    def test_resource_limit_exceeded(self):
        """Test resource limit enforcement."""
        plan = {
            "action": "batch_process",
            "params": {
                "batch_size": 500,
                "estimated_memory_mb": 2048  # Exceeds 1024MB limit
            }
        }

        result = self.engine.evaluate_plan(plan)
        assert result.action == EthicsAction.BLOCK
        assert "block_excessive_resources" in [r.name for r in result.triggered_rules]

    def test_multiple_violations_priority_lattice(self):
        """Test priority lattice with multiple violations."""
        plan = {
            "action": "external_call",  # Triggers WARN
            "params": {
                "url": "https://api.example.com",
                "estimated_memory_mb": 2048  # Triggers BLOCK
            }
        }

        result = self.engine.evaluate_plan(plan)
        assert result.action == EthicsAction.BLOCK  # BLOCK wins over WARN
        assert len(result.triggered_rules) == 2  # Both rules triggered


class TestProductionHardening:
    """Test production hardening features."""

    def test_domain_canonicalization_security(self):
        """Test that domain canonicalization prevents bypass attempts."""
        # Test various bypass attempts
        test_cases = [
            ("https://openai.com", "openai.com"),
            ("https://api.openai.com", "api.openai.com"),
            ("HTTPS://API.OPENAI.COM", "api.openai.com"),  # case normalization
            ("https://api.openai.com.:443/", "api.openai.com"),  # trailing dot + port
            ("api.openai.com", "api.openai.com"),  # scheme-less
            ("invalid://malformed", ""),  # fail closed
        ]

        for input_url, expected in test_cases:
            result = canonical_domain(input_url)
            assert result == expected, f"Failed for {input_url}: got {result}, expected {expected}"

    def test_units_parsing_fail_closed(self):
        """Test that units parsing fails closed on invalid input."""
        # Invalid byte units should raise ValueError
        try:
            parse_bytes("1XB")  # Unknown unit
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

        # Invalid time units should raise ValueError
        try:
            parse_seconds("1xyz")  # Unknown unit
            raise AssertionError("Should have raised ValueError")
        except ValueError:
            pass

        # param_*_lte should return False on parsing errors
        assert param_bytes_lte("invalid", "1MB") is False
        assert param_seconds_lte("invalid", "1h") is False

    def test_reason_codes_taxonomy(self):
        """Test reason code taxonomy."""
        from core.ethics.logic.ethics_engine import ReasonCode

        # Test mapping from rule names to codes
        assert ReasonCode.from_rule_name("block_harmful_actions") == ReasonCode.HARMFUL_ACTION
        assert ReasonCode.from_rule_name("block_untrusted_domains") == ReasonCode.UNTRUSTED_DOMAIN
        assert ReasonCode.from_rule_name("warn_external_api_calls") == ReasonCode.EXTERNAL_API_CALL
        assert ReasonCode.from_rule_name("unknown_rule") == ReasonCode.UNKNOWN

        # Test that reason codes follow the ETH#NNNN format
        assert ReasonCode.HARMFUL_ACTION.value == "ETH#1001"
        assert ReasonCode.EXTERNAL_API_CALL.value == "ETH#3001"

    def test_enhanced_metrics_structure(self):
        """Test enhanced metrics in EthicsResult."""
        rules = [
            EthicsRule(
                name="test_rule",
                description="Test rule",
                rule_dsl='equals(action, "test")',
                action=EthicsAction.BLOCK,
                priority=Priority.CRITICAL,
                tags={"test"}
            )
        ]

        engine = EthicsEngine(RuleSet(rules))
        plan = {"action": "test", "params": {}}

        result = engine.evaluate_plan(plan)

        # Verify enhanced fields
        assert hasattr(result, 'facts_hash')
        assert hasattr(result, 'triggered_rule_ids')
        assert hasattr(result, 'reason_codes')

        assert result.facts_hash is not None
        assert result.triggered_rule_ids == ["test_rule"]
        assert result.reason_codes == ["ETH#1001"]  # HARMFUL_ACTION code

    def test_concurrency_safety(self):
        """Test that the engine is thread-safe."""
        import threading
        import time

        rules = [
            EthicsRule(
                name="concurrent_test",
                description="Test concurrent access",
                rule_dsl='equals(action, "concurrent")',
                action=EthicsAction.WARN,
                priority=Priority.MEDIUM,
                tags={"test"}
            )
        ]

        engine = EthicsEngine(RuleSet(rules))
        results = []
        errors = []

        def worker():
            try:
                for _i in range(10):
                    plan = {"action": "concurrent", "params": {"worker_id": threading.current_thread().ident}}
                    result = engine.evaluate_plan(plan)
                    results.append(result.action)
                    time.sleep(0.001)  # Small delay to encourage race conditions
            except Exception as e:
                errors.append(e)

        # Run multiple threads concurrently
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrency errors: {errors}"

        # Verify all evaluations completed
        assert len(results) == 50  # 5 threads × 10 evaluations each

        # Verify deterministic results (all should be WARN)
        assert all(result == EthicsAction.WARN for result in results)

    def test_ruleset_hash_stability(self):
        """Test that ruleset hash is stable and changes with rule modifications."""
        rules1 = [
            EthicsRule("rule1", "desc1", 'equals(action, "test")', EthicsAction.BLOCK, Priority.HIGH, {"test"})
        ]
        rules2 = [
            EthicsRule("rule1", "desc1", 'equals(action, "test")', EthicsAction.BLOCK, Priority.HIGH, {"test"})
        ]
        rules3 = [
            EthicsRule("rule1", "desc1", 'equals(action, "other")', EthicsAction.BLOCK, Priority.HIGH, {"test"})
        ]

        ruleset1 = RuleSet(rules1)
        ruleset2 = RuleSet(rules2)
        ruleset3 = RuleSet(rules3)

        # Same rules should have same hash
        assert ruleset1.ruleset_hash == ruleset2.ruleset_hash

        # Different rules should have different hash
        assert ruleset1.ruleset_hash != ruleset3.ruleset_hash

    def test_new_predicates_compilation(self):
        """Test that new predicates compile and work correctly."""
        # Test domain_etld1 predicate compilation
        rule = compile_rule('domain_etld1(params.url, "openai.com")')
        plan = {"action": "call", "params": {"url": "https://api.openai.com/v1/chat"}}
        assert rule(plan) is True

        plan = {"action": "call", "params": {"url": "https://malicious.com"}}
        assert rule(plan) is False

        # Test not_has_consent predicate compilation
        rule = compile_rule('not_has_consent(params.consent)')
        plan = {"action": "process", "params": {"consent": False}}
        assert rule(plan) is True

        plan = {"action": "process", "params": {"consent": True}}
        assert rule(plan) is False

        # Test param_bytes_lte predicate compilation
        rule = compile_rule('param_bytes_lte(params.memory, "1GB")')
        plan = {"action": "compute", "params": {"memory": "512MB"}}
        assert rule(plan) is True

        plan = {"action": "compute", "params": {"memory": "2GB"}}
        assert rule(plan) is False
