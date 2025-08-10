#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: final_validation.py
# MODULE: core.final_validation
# DESCRIPTION: Performs a final, comprehensive validation of the LUKHAS AGI Automatic
#              Testing and Logging System, focusing on key features and performance.
# DEPENDENCIES: asyncio, sys, time, os, pathlib, logging, core.automatic_testing_system
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import asyncio
import os
import sys
import time
from pathlib import Path

# Initialize logger for ΛTRACE

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony

logger = logging.getLogger("ΛTRACE.core.final_validation")
# Basic configuration for the logger if no handlers are present
if not logging.getLogger("ΛTRACE").handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - ΛTRACE: %(message)s",
    )

logger.info("ΛTRACE: Initializing final_validation script.")

# Adjust Python path to import from the 'core' module correctly if script is run from elsewhere
# or to ensure 'core.automatic_testing_system' can be found.
current_script_path = Path(__file__).resolve()
# Assuming this script is in 'core/', so 'core.automatic_testing_system' should be importable
# If 'core' is not in PYTHONPATH, its parent directory might need to be added.
# For this setup, direct import 'from .automatic_testing_system' or 'from core.automatic_testing_system'
# should work if the script is run correctly relative to the project structure.
# We'll assume 'core' is part of a package or the parent is in sys.path for now.

# Human-readable comment: Main asynchronous function to run all validation checks.


async def main() -> bool:
    """Main validation function to test the Automatic Testing System."""
    logger.info("ΛTRACE: Starting final_validation main function.")
    logger.info("🚀 LUKHAS AGI AUTOMATIC TESTING & LOGGING SYSTEM")
    logger.info("🎯 Final Comprehensive Validation")
    logger.info("=" * 70)

    original_dir = Path.cwd()
    logger.debug(f"ΛTRACE: Original working directory: {original_dir}")
    overall_success = True

    try:
        # Test 1: Module Import
        logger.info("ΛTRACE: Test 1: Module Import started.")
        logger.info("\n📦 Test 1: Module Import")
        logger.info("-" * 30)
        ats_module_imported = False
        try:
            # Explicitly import from core.automatic_testing_system
            from core.automatic_testing_system import AutomaticTestingSystem
            from core.automatic_testing_system import capture
            from core.automatic_testing_system import TestOperation

            logger.info(
                "ΛTRACE: Successfully imported components from core.automatic_testing_system."
            )
            logger.info(
                "✅ Successfully imported all autotest components from core.automatic_testing_system"
            )
            logger.info("   📋 Available: run(), watch(), report(), capture()")
            logger.info("   🏗️  Classes: AutomaticTestingSystem, TestOperation")
            ats_module_imported = True
        except ImportError as e:
            logger.critical(
                f"ΛTRACE: Import failed for core.automatic_testing_system: {e}",
                exc_info=True,
            )
            logger.error(f"❌ Import failed: {e}")
            logger.error(
                "   Ensure 'core' directory is in PYTHONPATH or script is run from project root."
            )
            return False  # Critical failure
        except Exception as e:  # Catch any other unexpected import error
            logger.critical(
                f"ΛTRACE: Unexpected error during import: {e}", exc_info=True
            )
            logger.error(f"❌ Unexpected import error: {e}")
            return False

        # Test 2: System Initialization
        logger.info("ΛTRACE: Test 2: System Initialization started.")
        logger.info("\n🔧 Test 2: System Initialization")
        logger.info("-" * 30)
        autotest_instance: Optional[AutomaticTestingSystem] = None
        try:
            # Use a workspace path relative to this script for testing purposes.
            # Example: project_root/test_workspace/final_validation_ws
            # For simplicity here, using a subdir of the script's location.
            test_workspace = Path(__file__).parent / "final_validation_workspace"
            test_workspace.mkdir(parents=True, exist_ok=True)
            logger.info(
                f"ΛTRACE: Test workspace for final_validation: {test_workspace}"
            )

            autotest_instance = AutomaticTestingSystem(
                workspace_path=test_workspace,  # Use a dedicated test workspace
                enable_ai_analysis=True,
                enable_performance_monitoring=True,
            )
            logger.info(
                f"ΛTRACE: AutomaticTestingSystem initialized. Workspace: {autotest_instance.workspace_path}, AI: {autotest_instance.enable_ai_analysis}, PerfMon: {autotest_instance.enable_performance_monitoring}"
            )
            logger.info("✅ AutomaticTestingSystem initialized")
            logger.info(f"   📁 Workspace: {autotest_instance.workspace_path}")
            logger.info(
                f"   🤖 AI Analysis: {'Enabled' if autotest_instance.ai_analyzer else 'Disabled'}"
            )
            logger.info(
                f"   📊 Performance Monitoring: {'Enabled' if autotest_instance.performance_monitor else 'Disabled'}"
            )
        except Exception as e:
            logger.error(
                f"ΛTRACE: AutomaticTestingSystem initialization failed: {e}",
                exc_info=True,
            )
            logger.error(f"❌ Initialization failed: {e}")
            overall_success = False
            # Continue if possible, but note the failure. Some subsequent tests might
            # fail.

        if (
            not overall_success
        ):  # If initialization failed, skip tests requiring an instance
            logger.warning(
                "ΛTRACE: Skipping further tests due to initialization failure."
            )
            logger.warning(
                "\n⚠️ Skipping further tests due to system initialization failure."
            )
            return False

        # Test 3: Basic Operation Capture
        logger.info("ΛTRACE: Test 3: Basic Operation Capture started.")
        logger.info("\n🔄 Test 3: Basic Operation Capture")
        logger.info("-" * 30)
        captured_operation_for_ai_test: Optional[TestOperation] = None
        try:
            # Test with direct method of the instance
            # TODO: Use sys.executable for python calls to ensure consistency, or
            # configured python path
            test_command = "echo 'LUKHAS AGI Testing System Active (final_validation)'"
            logger.debug(f"ΛTRACE: Capturing command: {test_command}")
            captured_operation_for_ai_test = (
                await autotest_instance.capture_terminal_operation(
                    command_str=test_command,
                    operation_type_str="final_validation_echo",
                )
            )

            logger.info(
                f"ΛTRACE: Operation capture completed. Status: {captured_operation_for_ai_test.status}, Duration: {captured_operation_for_ai_test.duration_ms:.2f}ms"
            )
            logger.info(
                f"✅ Operation completed: {captured_operation_for_ai_test.status}"
            )
            logger.info(
                f"   ⏱️  Duration: {captured_operation_for_ai_test.duration_ms:.2f}ms"
            )
            logger.info(
                f"   📤 Output: '{captured_operation_for_ai_test.output.strip()}'"
            )
            logger.info(f"   🔢 Exit Code: {captured_operation_for_ai_test.exit_code}")

            # Performance validation
            if captured_operation_for_ai_test.duration_ms < 100:
                logger.info("ΛTRACE: Echo performance target met (<100ms).")
                logger.info("   🎯 ✅ Performance target achieved (< 100ms)")
            elif captured_operation_for_ai_test.duration_ms < 500:
                logger.warning(
                    f"ΛTRACE: Echo performance acceptable (<500ms): {captured_operation_for_ai_test.duration_ms:.2f}ms."
                )
                logger.info("   🎯 ⚠️  Performance acceptable (< 500ms)")
            else:
                logger.error(
                    f"ΛTRACE: Echo performance needs improvement: {captured_operation_for_ai_test.duration_ms:.2f}ms."
                )
                logger.error("   🎯 ❌ Performance needs improvement")
                # Not failing the overall test for this, but it's a concern.
        except Exception as e:
            logger.error(f"ΛTRACE: Operation capture failed: {e}", exc_info=True)
            logger.error(f"❌ Operation capture failed: {e}")
            overall_success = False

        # Test 4: One-Line API Functions
        logger.info("ΛTRACE: Test 4: One-Line API Functions started.")
        logger.info("\n🎯 Test 4: One-Line API Functions")
        logger.info("-" * 30)
        try:
            # Test global capture function
            logger.debug("ΛTRACE: Testing global capture() function.")
            logger.info("   Testing capture()...")
            start_time_api = time.perf_counter()  # Use perf_counter for more precision
            # TODO: Use sys.executable for python calls to ensure consistency
            one_line_cmd = f"{sys.executable} -c \"import sys; print(f'One-line API test successful. Python: {{sys.version_info.major}}.{{sys.version_info.minor}}')\""
            logger.debug(f"ΛTRACE: Global capture command: {one_line_cmd}")
            op_api = await capture(command_to_run=one_line_cmd)  # Uses global instance
            duration_api = (time.perf_counter() - start_time_api) * 1000

            logger.info(
                f"ΛTRACE: Global capture() Status: {op_api.status}, Duration: {duration_api:.2f}ms, Output: '{op_api.output.strip()}'"
            )
            logger.info(
                f"   ✅ capture() - Status: {op_api.status}, Duration: {duration_api:.2f}ms"
            )
            logger.info(f"      Output: '{op_api.output.strip()}'")
            if op_api.status != "completed":
                overall_success = False
                logger.error(
                    f"ΛTRACE: Global capture() did not complete successfully. Error: {op_api.error}"
                )
        except Exception as e:
            logger.error(
                f"ΛTRACE: One-line API test (capture) failed: {e}",
                exc_info=True,
            )
            logger.error(f"   ❌ One-line API test failed: {e}")
            overall_success = False

        # Test 5: Performance Stress Test (brief)
        logger.info("ΛTRACE: Test 5: Performance Stress Test started.")
        logger.info("\n⚡ Test 5: Performance Stress Test")
        logger.info("-" * 30)
        stress_commands = [
            "echo 'Stress test 1 (final_validation)'",
            f"{sys.executable} -c \"import time; time.sleep(0.001); print('Stress test 2 (final_validation)')\"",
            "echo 'Stress test 3 (final_validation)'",]
        stress_durations: List[float] = []
        stress_successful_ops = 0

        for i, cmd in enumerate(stress_commands, 1):
            logger.debug(f"ΛTRACE: Stress test command {i}: {cmd}")
            try:
                op_stress = await autotest_instance.capture_terminal_operation(
                    command_str=cmd,
                    operation_type_str=f"final_validation_stress_{i}",
                    timeout_val_seconds=5,
                )
                stress_durations.append(op_stress.duration_ms)
                if op_stress.status == "completed":
                    stress_successful_ops += 1
                logger.info(
                    f"ΛTRACE: Stress op {i} status: {op_stress.status},"
                    duration: {op_stress.duration_ms: .2f}ms"
                )
                logger.info(
                    f"   Operation {i}: {op_stress.duration_ms:.2f}ms - {op_stress.status}"
                )
            except Exception as e:
                logger.error(f"ΛTRACE: Stress operation {i} failed: {e}", exc_info=True)
                logger.error(f"   Operation {i}: FAILED - {e}")
                # Not necessarily failing overall_success, depends on how many succeed

        if stress_durations:
            avg_stress_dur = sum(stress_durations) / len(stress_durations)
            max_stress_dur = max(stress_durations)
            min_stress_dur = min(stress_durations)
            stress_success_rate = (stress_successful_ops / len(stress_commands)) * 100
            logger.info(
                f"ΛTRACE: Stress Stats - Avg: {avg_stress_dur:.2f}ms, Max: {max_stress_dur:.2f}ms, Min: {min_stress_dur:.2f}ms, Success: {stress_success_rate:.1f}%"
            )
            logger.info("\n   📊 Performance Statistics (Stress Test):")
            logger.info(f"      📈 Average: {avg_stress_dur:.2f}ms")
            logger.info(f"      ✅ Success Rate: {stress_success_rate:.1f}%")
            if stress_success_rate < 100:
                logger.warning(
                    f"ΛTRACE: Stress test success rate below 100% ({stress_success_rate:.1f}%)."
                )
                # overall_success = False # Decide if this is a failure condition
        else:
            logger.error("ΛTRACE: No stress test durations collected.")
            logger.warning("   ⚠️ No stress test durations collected.")
            overall_success = False

        # Test 6: AI Analysis (if available and previous op captured)
        logger.info("ΛTRACE: Test 6: AI Analysis started.")
        logger.info("\n🤖 Test 6: AI Analysis")
        logger.info("-" * 30)
        if autotest_instance.ai_analyzer:
            if captured_operation_for_ai_test:
                try:
                    analysis = autotest_instance.ai_analyzer.analyze_operation(
                        captured_operation_for_ai_test
                    )
                    logger.info(
                        f"ΛTRACE: AI analysis completed. Category: {analysis.get('performance_category', 'N/A')}, Success Prob: {analysis.get('predicted_success_probability', 0):.2f}"
                    )
                    logger.info("   ✅ AI analysis completed")
                    logger.info(
                        f"      📊 Performance Category: {analysis.get('performance_category', 'unknown')}"
                    )
                except Exception as e:
                    logger.error(f"ΛTRACE: AI analysis error: {e}", exc_info=True)
                    logger.warning(f"   ⚠️  AI analysis error: {e}")
                    # Not failing overall test for this
            else:
                logger.warning(
                    "ΛTRACE: Skipping AI analysis as target operation was not captured."
                )
                logger.warning(
                    "   ⚠️  Skipping AI analysis (target operation not captured)."
                )
        else:
            logger.info("ΛTRACE: AI analysis not available (disabled in instance).")
            logger.info("   ℹ️  AI analysis not available (disabled in instance).")

        # Test 7: Performance Monitoring (if available)
        logger.info("ΛTRACE: Test 7: Performance Monitoring started.")
        logger.info("\n📊 Test 7: Performance Monitoring")
        logger.info("-" * 30)
        if autotest_instance.performance_monitor:
            try:
                metrics = autotest_instance.performance_monitor.capture_metrics()
                logger.info(
                    f"ΛTRACE: Performance metrics captured: CPU {metrics.get('cpu_percent_system', 'N/A')}%, Mem {metrics.get('memory_percent_system', 'N/A')}%"
                )
                logger.info("   ✅ Performance monitoring active")
                logger.info(
                    f"      💻 CPU Usage(System): {metrics.get('cpu_percent_system',
                                                              'N/A'): .1f} %"
                )
                logger.info(
                    f"      💾 Memory Usage (System): {metrics.get('memory_percent_system', 'N/A'):.1f}%"
                )
            except Exception as e:
                logger.error(
                    f"ΛTRACE: Performance monitoring error: {e}", exc_info=True
                )
                logger.warning(f"   ⚠️  Performance monitoring error: {e}")
                # Not failing overall test for this
        else:
            logger.info(
                "ΛTRACE: Performance monitoring not available (disabled in instance)."
            )
            logger.info(
                "   ℹ️  Performance monitoring not available (disabled in instance)."
            )

        # Final Results Output
        logger.info("ΛTRACE: Final validation summary generation.")
        logger.info("\n" + "=" * 70)
        logger.info("🏁 VALIDATION RESULTS")
        logger.info("=" * 70)
        if overall_success:
            logger.info("ΛTRACE: ALL TESTS PASSED SUCCESSFULLY!")
            logger.info("✅ ✅ ✅ ALL TESTS PASSED SUCCESSFULLY! ✅ ✅ ✅")
            logger.info(
                "\n🎉 LUKHAS AGI Automatic Testing & Logging System is FULLY OPERATIONAL"
            )
            # Further positive print statements can be kept as is from original.
        else:
            logger.error("ΛTRACE: ONE OR MORE TESTS FAILED.")
            logger.error(
                "❌ ❌ ❌ ONE OR MORE TESTS FAILED. Please review logs. ❌ ❌ ❌"
            )

        return overall_success

    except Exception as e_critical:
        logger.critical(
            f"ΛTRACE: CRITICAL ERROR during final_validation main function: {e_critical}",
            exc_info=True,
        )
        logger.critical(f"\n❌ CRITICAL ERROR: {e_critical}")
        return False
    finally:
        # Clean up test workspace if created, or other cleanup tasks
        if "test_workspace" in locals() and test_workspace.exists():
            try:
                # Basic cleanup, for more complex scenarios, shutil.rmtree might be
                # needed
                for item in test_workspace.iterdir():
                    if item.is_file():
                        item.unlink()
                # test_workspace.rmdir() # Remove directory if empty, careful with this
                logger.info(
                    f"ΛTRACE: Basic cleanup of test workspace {test_workspace} attempted."
                )
            except Exception as e_cleanup:
                logger.error(
                    f"ΛTRACE: Error during test workspace cleanup: {e_cleanup}",
                    exc_info=True,
                )

        os.chdir(original_dir)  # Restore original directory
        logger.debug(f"ΛTRACE: Restored original working directory: {original_dir}")
        logger.info("ΛTRACE: final_validation main function finished.")


# Human-readable comment: Main execution block when script is run directly.
if __name__ == "__main__":
    logger.info("ΛTRACE: final_validation.py executed as __main__.")

    # Python version check

    # Run validation
    final_status_success: bool = False
    try:
        logger.info("ΛTRACE: Invoking asyncio.run(main()).")
        final_status_success = asyncio.run(main())
        logger.info(
            f"ΛTRACE: Main validation completed. Overall success: {final_status_success}"
        )
        logger.info(
            f"\n🏁 Final Result: {'SUCCESS' if final_status_success else 'FAILURE'}"
        )
        sys.exit(0 if final_status_success else 1)

    except KeyboardInterrupt:
        logger.warning("ΛTRACE: Validation interrupted by user (KeyboardInterrupt).")
        logger.warning("\n⚠️  Validation interrupted by user.")
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e_global:  # Catch-all for unexpected errors at the top level
        logger.critical(
            f"ΛTRACE: Validation crashed with unhandled exception: {e_global}",
            exc_info=True,
        )
        logger.critical(f"\n❌ Validation crashed: {e_global}")
        sys.exit(2)  # General error exit code

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: final_validation.py
# VERSION: 1.1.0
# TIER SYSTEM: Not applicable (Validation Script)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Validates core functionalities of the Automatic Testing System including
#               module import, system initialization, operation capture, one-line API calls,
#               performance stress testing, AI analysis, and performance monitoring.
# FUNCTIONS: main
# CLASSES: None (imports ATS classes for testing)
# DECORATORS: None
# DEPENDENCIES: asyncio, sys, time, os, pathlib, logging, traceback, core.automatic_testing_system
# INTERFACES: Command-line execution (__main__ block).
# ERROR HANDLING: Catches exceptions during test execution, logs them, and reports overall success/failure.
#                 Sets system exit code based on validation outcome.
# LOGGING: ΛTRACE_ENABLED for detailed tracing of the validation script's execution flow and test outcomes.
# AUTHENTICATION: Not applicable.
# HOW TO USE:
#   Run as a standalone Python script: python core/final_validation.py
#   Ensure 'core.automatic_testing_system' is importable (e.g., 'core' in PYTHONPATH or run from project root).
# INTEGRATION NOTES: This script serves as a comprehensive health check for the
#                    Automatic Testing System. It should be run to confirm system integrity
#                    after changes or in CI/CD pipelines.
# MAINTENANCE: Update test cases and assertions as the Automatic Testing System evolves.
#              Ensure paths and commands (e.g., use of sys.executable) are robust.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════