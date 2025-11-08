#!/usr/bin/env python3
"""
LUKHAS Application Bootstrap

Initializes core services including OTEL tracing, metrics, and Guardian system.
"""

import logging
import os
from typing import Any

# Early OTel initialization
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
except ImportError:
    OTLPSpanExporter = None

logger = logging.getLogger(__name__)


def init_tracing(service_name: str = "lukhas-matriz"):
    """Initialize OpenTelemetry tracing early in bootstrap."""
    if trace.get_tracer_provider().__class__.__name__ == "TracerProvider":
        # already initialized
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # always at least one sink (console) to catch local issues
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # if OTLP endpoint is provided in CI/prod, add it
    otlp = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp and OTLPSpanExporter:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp)))

    logger.info(f"✅ OTel tracing initialized for {service_name} (endpoint: {otlp or 'console-only'})")


# call once on process start
init_tracing()


def initialize_lukhas_services() -> dict[str, Any]:
    """
    Initialize all LUKHAS core services.

    Returns:
        Dict with initialization status for each service
    """
    initialization_results = {
        "otel": False,
        "guardian": False,
        "metrics": False,
        "lane": os.getenv("LUKHAS_LANE", "experimental")
    }

    # 1. Initialize OpenTelemetry
    try:
        from observability.otel_instrumentation import (
            get_instrumentation_status,
            initialize_otel_instrumentation,
        )

        service_name = f"lukhas-{initialization_results['lane']}"
        otel_initialized = initialize_otel_instrumentation(
            service_name=service_name,
            enable_prometheus=True,
            enable_logging=True
        )

        if otel_initialized:
            status = get_instrumentation_status()
            initialization_results["otel"] = True
            logger.info(f"✅ OTEL initialized: {status}")
        else:
            logger.warning("⚠️ OTEL initialization failed")

    except ImportError:
        logger.warning("⚠️ OTEL not available")
    except Exception as e:
        logger.error(f"❌ OTEL initialization error: {e}")

    # 2. Initialize Guardian System
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from governance.guardian_system import GuardianSystem

        guardian = GuardianSystem()

        # Test Guardian with a validation call
        test_result = guardian.validate_safety({"action": "bootstrap_test"})
        if test_result:
            initialization_results["guardian"] = True
            logger.info(f"✅ Guardian initialized: {test_result['guardian_status']}")
        else:
            logger.error("❌ Guardian validation failed")

    except Exception as e:
        logger.error(f"❌ Guardian initialization error: {e}")

    # 3. Initialize Metrics Endpoint
    try:
        from observability.prometheus_metrics import setup_metrics_endpoint

        metrics_port = int(os.getenv("METRICS_PORT", "8090"))
        setup_metrics_endpoint(port=metrics_port)
        initialization_results["metrics"] = True
        logger.info(f"✅ Metrics endpoint initialized on :{metrics_port}")

    except ImportError:
        logger.warning("⚠️ Prometheus metrics not available")
    except Exception as e:
        logger.error(f"❌ Metrics initialization error: {e}")

    # Log overall status
    services_up = sum(1 for service, status in initialization_results.items()
                     if service != "lane" and status)
    total_services = len([k for k in initialization_results if k != "lane"])

    logger.info(f"🚀 LUKHAS Bootstrap Complete: {services_up}/{total_services} services initialized")

    return initialization_results


def validate_per_stage_spans() -> dict[str, Any]:
    """
    Test that per-stage OTEL spans are working.

    Returns:
        Validation results for each stage
    """
    logger.info("🔍 Validating per-stage OTEL spans...")

    try:
        import asyncio
        import time

        from observability.otel_instrumentation import instrument_matriz_stage, matriz_pipeline_span

        # Test each stage type
        @instrument_matriz_stage("intent_processing", "intent", slo_target_ms=50.0)
        async def test_intent_stage():
            await asyncio.sleep(0.01)
            return {"intent": "test", "confidence": 0.95}

        @instrument_matriz_stage("decision_making", "reasoning", slo_target_ms=75.0)
        async def test_decision_stage():
            await asyncio.sleep(0.015)
            return {"decision": "process", "strategy": "standard"}

        @instrument_matriz_stage("processing", "processing", slo_target_ms=100.0)
        async def test_processing_stage():
            await asyncio.sleep(0.02)
            return {"result": "processed", "items": 42}

        @instrument_matriz_stage("validation", "validation", slo_target_ms=30.0)
        async def test_validation_stage():
            await asyncio.sleep(0.008)
            return {"valid": True, "score": 0.92}

        @instrument_matriz_stage("reflection", "reflection", slo_target_ms=40.0)
        async def test_reflection_stage():
            await asyncio.sleep(0.012)
            return {"insights": ["good_performance"], "rating": 4.2}

        async def run_span_validation():
            """Run the 5-stage pipeline with spans"""
            with matriz_pipeline_span("bootstrap_validation", "test query", 250.0):
                start_time = time.perf_counter()

                # Execute all 5 stages
                intent_result = await test_intent_stage()
                decision_result = await test_decision_stage()
                processing_result = await test_processing_stage()
                validation_result = await test_validation_stage()
                reflection_result = await test_reflection_stage()

                end_time = time.perf_counter()
                total_time = (end_time - start_time) * 1000

                return {
                    "pipeline_time_ms": total_time,
                    "stages_completed": 5,
                    "results": [
                        intent_result,
                        decision_result,
                        processing_result,
                        validation_result,
                        reflection_result
                    ]
                }

        # Run the validation
        result = asyncio.run(run_span_validation())

        validation_status = {
            "spans_working": True,
            "stages_instrumented": 5,
            "pipeline_time_ms": result["pipeline_time_ms"],
            "within_slo": result["pipeline_time_ms"] < 250.0,
            "all_stages_completed": result["stages_completed"] == 5
        }

        logger.info(f"✅ OTEL spans validated: {validation_status}")
        return validation_status

    except Exception as e:
        logger.error(f"❌ OTEL span validation failed: {e}")
        return {
            "spans_working": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize services
    init_results = initialize_lukhas_services()

    # Validate OTEL spans if available
    if init_results.get("otel", False):
        span_results = validate_per_stage_spans()
        init_results["span_validation"] = span_results

    print("🎯 LUKHAS Bootstrap Summary:")
    for service, status in init_results.items():
        if isinstance(status, bool):
            print(f"   {service}: {'✅' if status else '❌'}")
        elif isinstance(status, dict):
            working = status.get("spans_working", False)
            print(f"   {service}: {'✅' if working else '❌'}")
        else:
            print(f"   {service}: {status}")

    # Exit code based on critical services
    critical_services = ["otel", "guardian"]
    critical_up = all(init_results.get(service, False) for service in critical_services)

    exit(0 if critical_up else 1)
