# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: autotest_validation.py
# MODULE: core.autotest_validation
# DESCRIPTION: Validation script for the LUKHAS AGI Automatic Testing System.
#              It performs comprehensive testing of all features of the testing system.
# DEPENDENCIES: asyncio, sys, os, pathlib, logging, automatic_testing_system
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import asyncio
import sys
import os
from pathlib import Path
import structlog # For ΛTRACE logging
import traceback # For logging critical errors

# Initialize ΛTRACE logger for this validation script using structlog
logger = structlog.get_logger("ΛTRACE.core.autotest_validation")

# Basic configuration for structlog if this script is run standalone
# and no higher-level configuration (e.g. from core/__init__.py during tests) has been done.
if not structlog.is_configured():
    structlog.configure(
        processors=[
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    # Re-get logger to apply this config if it was just set
    logger = structlog.get_logger("ΛTRACE.core.autotest_validation")

logger.info("ΛTRACE: Initializing autotest_validation script.")

# Adjust Python path to import from the parent directory ('core')
# This allows 'from automatic_testing_system import ...' to work when this script is in 'core'.
# More robust solutions might involve setting PYTHONPATH or proper packaging.
# ΛNOTE: The following sys.path manipulation assumes this validation script is located within a subdirectory (e.g., 'core') of the main project, and it prepends the project's root directory to sys.path to allow direct imports like 'from core.automatic_testing_system'. This is common for test scripts but might need adjustment if the file structure or execution context changes. Consider using relative imports if feasible or a more structured test runner that handles paths.
current_script_path = Path(__file__).resolve()
project_root_path = current_script_path.parent.parent # Assuming this script is in core/
sys.path.insert(0, str(project_root_path))
logger.debug(f"ΛTRACE: Added '{project_root_path}' to sys.path for imports.")

# Import components from the Automatic Testing System
try:
    from core.automatic_testing_system import ( # Assuming it's in core.automatic_testing_system
        AutomaticTestingSystem,
        TestOperation, # Not directly used here but good to confirm import
        TestSession,   # Not directly used here
        PerformanceMonitor, # Not directly used here
        AITestAnalyzer,    # Not directly used here
        run, watch, report, capture # These are the one-line API functions
    )
    logger.info("ΛTRACE: Successfully imported components from core.automatic_testing_system.")
    logger.info("✅ Successfully imported LUKHAS Automatic Testing System components.")
except ImportError as e:
    logger.critical(f"ΛTRACE: Import failed for automatic_testing_system components: {e}", exc_info=True)
    logger.error(f"❌ Import failed: {e}. Ensure 'automatic_testing_system.py' is in the 'core' directory or PYTHONPATH is set correctly.")
    sys.exit(1)
except Exception as e_gen: # Catch any other exception during import phase
    logger.critical(f"ΛTRACE: General exception during import phase: {e_gen}", exc_info=True)
    logger.error(f"❌ A general error occurred during imports: {e_gen}")
    sys.exit(1)

# Async function to test basic functionality
async def test_basic_functionality() -> bool:
    """Tests the fundamental initialization and operation capture of the AutomaticTestingSystem."""
    test_name = "Basic Functionality"
    logger.info(f"ΛTRACE: Starting test suite: {test_name}")
    logger.info(f"\n🧪 Testing {test_name}")
    logger.info("=" * 50)
    all_steps_passed = True

    # Step 1: Initialize AutomaticTestingSystem
    logger.info("ΛTRACE: Step 1: Initializing AutomaticTestingSystem instance.")
    logger.info("1. Initializing AutomaticTestingSystem...")
    autotest_instance: Optional[AutomaticTestingSystem] = None
    try:
        # Assuming the script runs from 'core' directory, so parent is project root.
        # If script is run from project root, Path.cwd() might be more appropriate.
        # For consistency, let's use a path relative to this script file.
        # ΛNOTE: `workspace_for_test` is set to the parent of the script's directory (assumed project root). This path is used by AutomaticTestingSystem. Consider making this configurable if tests need to run against different workspace roots.
        workspace_for_test = Path(__file__).parent.parent
        autotest_instance = AutomaticTestingSystem(
            workspace_path=workspace_for_test, # Example: Use project root as workspace
            enable_ai_analysis=True, # Explicitly enable for test
            enable_performance_monitoring=True # Explicitly enable for test
        )
        logger.info(f"ΛTRACE: AutomaticTestingSystem initialized successfully. Workspace: {workspace_for_test}")
        logger.info("   ✅ System initialized successfully.")
    except Exception as e:
        logger.error(f"ΛTRACE: Initialization of AutomaticTestingSystem failed: {e}", exc_info=True)
        logger.error(f"   ❌ Initialization failed: {e}")
        return False # Critical failure, cannot proceed

    # Step 2: Capture a simple terminal operation
    logger.info("ΛTRACE: Step 2: Testing terminal operation capture.")
    logger.info("2. Testing terminal operation capture...")
    captured_op_for_ai: Optional[TestOperation] = None # To store for AI analysis test
    try:
        captured_op_for_ai = await autotest_instance.capture_terminal_operation(
            command_str="echo 'Hello from core.common Test Validation!'", # Renamed arg
            operation_type_str="validation_echo_test", # Renamed arg
            timeout_val_seconds=10 # Renamed arg
        )
        logger.info(f"ΛTRACE: Terminal operation capture completed. Status: {captured_op_for_ai.status}, Duration: {captured_op_for_ai.duration_ms:.2f}ms.")
        logger.info(f"   ✅ Operation completed: {captured_op_for_ai.status}")
        logger.info(f"   ⏱️  Duration: {captured_op_for_ai.duration_ms:.2f}ms")
        logger.info(f"   📤 Output: {captured_op_for_ai.output.strip()}")

        if captured_op_for_ai.duration_ms < 100: # Performance check
            logger.info("ΛTRACE: Performance target for echo test met (<100ms).")
            logger.info("   🎯 Performance target met (< 100ms).")
        else:
            logger.warning(f"ΛTRACE: Performance target for echo test missed ({captured_op_for_ai.duration_ms:.2f}ms).")
            logger.warning(f"   ⚠️  Performance target missed ({captured_op_for_ai.duration_ms:.2f}ms).")
            # Not failing the test for this, just a warning.
    except Exception as e:
        logger.error(f"ΛTRACE: Terminal operation capture failed: {e}", exc_info=True)
        logger.error(f"   ❌ Terminal capture failed: {e}")
        all_steps_passed = False

    # Step 3: Test performance monitoring (if enabled and instance exists)
    logger.info("ΛTRACE: Step 3: Testing performance monitoring.")
    logger.info("3. Testing performance monitoring...")
    try:
        if autotest_instance and autotest_instance.performance_monitor:
            metrics = autotest_instance.performance_monitor.capture_metrics()
            logger.info(f"ΛTRACE: Performance metrics captured: CPU System {metrics.get('cpu_percent_system', 'N/A'):.1f}%, Memory System {metrics.get('memory_percent_system', 'N/A'):.1f}%")
            logger.info(f"   ✅ Metrics captured: CPU System {metrics.get('cpu_percent_system', 'N/A'):.1f}%")
            logger.info(f"   💾 Memory System: {metrics.get('memory_percent_system', 'N/A'):.1f}%")
        else:
            logger.warning("ΛTRACE: Performance monitoring disabled or autotest_instance not available.")
            logger.warning("   ⚠️  Performance monitoring disabled or system not initialized.")
    except Exception as e:
        logger.error(f"ΛTRACE: Performance monitoring test failed: {e}", exc_info=True)
        logger.error(f"   ❌ Performance monitoring failed: {e}")
        # Not critical enough to fail the whole suite, but noted.

    # Step 4: Test AI analysis (if enabled, instance and operation exist)
    logger.info("ΛTRACE: Step 4: Testing AI analysis.")
    logger.info("4. Testing AI analysis...")
    try:
        if autotest_instance and autotest_instance.ai_analyzer and captured_op_for_ai:
            analysis_results = autotest_instance.ai_analyzer.analyze_operation(captured_op_for_ai)
            logger.info(f"ΛTRACE: AI analysis completed. Category: {analysis_results.get('performance_category', 'unknown')}, Success Prob: {analysis_results.get('predicted_success_probability', 0):.2f}")
            logger.info(f"   ✅ AI analysis completed.")
            logger.info(f"   🎯 Performance category: {analysis_results.get('performance_category', 'unknown')}")
            logger.info(f"   📊 Predicted success probability: {analysis_results.get('predicted_success_probability', 0):.2f}")
        elif not captured_op_for_ai :
             logger.warning("ΛTRACE: AI analysis skipped as previous capture operation failed.")
             logger.warning("   ⚠️  AI analysis skipped due to previous capture failure.")
        else:
            logger.warning("ΛTRACE: AI analysis disabled or autotest_instance not available.")
            logger.warning("   ⚠️  AI analysis disabled or system not initialized.")
    except Exception as e:
        logger.error(f"ΛTRACE: AI analysis test failed: {e}", exc_info=True)
        logger.error(f"   ❌ AI analysis failed: {e}")
        # Not critical to fail suite.

    logger.info(f"ΛTRACE: Test suite '{test_name}' finished. Overall result: {'PASSED' if all_steps_passed else 'FAILED'}")
    return all_steps_passed

# Async function to test one-line API
async def test_one_line_api() -> bool:
    """Tests the simplified one-line API functions (run, capture, report) from the module."""
    test_name = "One-Line API"
    logger.info(f"ΛTRACE: Starting test suite: {test_name}")
    logger.info(f"\n🎯 Testing {test_name}")
    logger.info("=" * 50)
    all_steps_passed = True

    # Step 1: Test autotest.run() with "basic" test type
    logger.info("ΛTRACE: Step 1: Testing global autotest.run('basic').")
    logger.info("1. Testing autotest.run() with basic tests...")
    run_results: Optional[Dict[str,Any]] = None
    try:
        run_results = await run(test_type_str="basic") # Using renamed arg
        logger.info(f"ΛTRACE: autotest.run('basic') completed. Status: {run_results.get('status')}, Session ID: {run_results.get('session_id')}")
        logger.info(f"   ✅ Test run completed: {run_results.get('status')}")
        logger.info(f"   📋 Session ID: {run_results.get('session_id')}")
        if 'summary_results' in run_results and isinstance(run_results['summary_results'], dict): # Check type
            logger.info(f"   📊 Test type from summary: {run_results['summary_results'].get('test_suite_type', 'unknown')}")
    except Exception as e:
        logger.error(f"ΛTRACE: autotest.run('basic') failed: {e}", exc_info=True)
        logger.error(f"   ❌ Test run failed: {e}")
        all_steps_passed = False

    # Step 2: Test autotest.capture()
    logger.info("ΛTRACE: Step 2: Testing global autotest.capture().")
    logger.info("2. Testing autotest.capture()...")
    try:
        captured_op = await capture(command_to_run="python --version") # Using renamed arg
        logger.info(f"ΛTRACE: autotest.capture() completed. Status: {captured_op.status}, Duration: {captured_op.duration_ms:.2f}ms.")
        logger.info(f"   ✅ Capture completed: {captured_op.status}")
        logger.info(f"   ⏱️  Duration: {captured_op.duration_ms:.2f}ms")
        if "Python" in captured_op.output: # Basic check for output content
             logger.info("ΛTRACE: Python version detected in capture output.")
             logger.info(f"   🐍 Python version detected in output.")
        else:
             logger.warning("ΛTRACE: Python version string not found in capture output.")
             logger.warning(f"   ⚠️ Python version string not found in output: {captured_op.output[:100]}")
    except Exception as e:
        logger.error(f"ΛTRACE: autotest.capture() failed: {e}", exc_info=True)
        logger.error(f"   ❌ Capture failed: {e}")
        all_steps_passed = False

    # Step 3: Test autotest.report()
    logger.info("ΛTRACE: Step 3: Testing global autotest.report().")
    logger.info("3. Testing autotest.report()...")
    try:
        # Use session ID from the 'run' test if available and successful
        session_id_for_report = run_results.get('session_id') if run_results and run_results.get('status') == 'completed' else None
        logger.debug(f"ΛTRACE: Generating report for session ID: {session_id_for_report if session_id_for_report else 'most recent'}")

        report_output = await report(session_id_str=session_id_for_report) # Using renamed arg
        logger.info(f"ΛTRACE: autotest.report() completed. Status: {report_output.get('status')}")
        logger.info(f"   ✅ Report generated: {report_output.get('status')}")

        if report_output.get('status') == 'report_generated_successfully':
            logger.info(f"ΛTRACE: Report file location: {report_output.get('report_file_location')}")
            logger.info(f"   📁 Report file: {report_output.get('report_file_location')}")
            # Further checks on report_content_summary can be added here
        elif report_output.get('status') == 'no_sessions_available':
            logger.warning("ΛTRACE: Report generation skipped as no sessions were available (possibly prior run failed).")
            logger.warning("   ⚠️ No sessions available for report (prior run might have failed).")
        else:
            logger.error(f"ΛTRACE: Report generation had issues: {report_output}")
            logger.warning(f"   ⚠️ Report generation status: {report_output.get('status')}, Error: {report_output.get('error_details', report_output.get('error'))}")
            # Not failing the whole suite for a report generation issue if tests ran.

    except Exception as e:
        logger.error(f"ΛTRACE: autotest.report() failed with exception: {e}", exc_info=True)
        logger.error(f"   ❌ Report generation failed: {e}")
        # Potentially set all_steps_passed = False here if report is critical

    logger.info(f"ΛTRACE: Test suite '{test_name}' finished. Overall result: {'PASSED' if all_steps_passed else 'FAILED'}")
    return all_steps_passed

# Async function to test performance validation
async def test_performance_validation() -> bool:
    """Runs multiple operations to test performance consistency and analysis."""
    test_name = "Performance Validation"
    logger.info(f"ΛTRACE: Starting test suite: {test_name}")
    logger.info(f"\n⚡ Testing {test_name}")
    logger.info("=" * 50)

    captured_ops_list: List[TestOperation] = []
    logger.info("1. Running multiple short operations for performance analysis...")
    test_cmds = [
        "echo 'Performance test echo 1'",
        "python -c \"print('Performance output from Python')\"",
        "ls -la . > /dev/null" if os.name != 'nt' else "dir > NUL", # OS-dependent listing
        "python -c \"import time; time.sleep(0.01); print('Tiny sleep done.')\"", # Small sleep
        "echo 'Performance test echo final'"
    ]

    for idx, cmd_str in enumerate(test_cmds, 1):
        logger.debug(f"ΛTRACE: Running perf validation command {idx}: {cmd_str}")
        try:
            op = await capture(command_to_run=cmd_str, timeout_duration_seconds=5) # Using renamed args
            captured_ops_list.append(op)
            status_symbol = "✅" if op.status == 'completed' else "❌"
            logger.info(f"   {status_symbol} Test {idx} ('{cmd_str[:30]}...'): {op.duration_ms:.2f}ms, Status: {op.status}")
            logger.info(f"ΛTRACE: Perf validation command {idx} status: {op.status}, duration: {op.duration_ms:.2f}ms.")
        except Exception as e:
            logger.error(f"ΛTRACE: Perf validation command {idx} ('{cmd_str}') failed: {e}", exc_info=True)
            logger.error(f"   ❌ Test {idx} ('{cmd_str}') failed: {e}")
            # Continue with other commands even if one fails

    if not captured_ops_list:
        logger.error("ΛTRACE: No operations were successfully captured for performance validation.")
        return False

    # Analyze aggregated performance statistics
    op_durations = [op.duration_ms for op in captured_ops_list if op.status == 'completed' and op.duration_ms is not None and op.duration_ms > 0]
    successful_ops_count = len([op for op in captured_ops_list if op.status == 'completed'])

    if op_durations:
        avg_duration_val = np.mean(op_durations) if np else sum(op_durations)/len(op_durations)
        max_duration_val = max(op_durations)
        min_duration_val = min(op_durations)
        success_rate_val = (successful_ops_count / len(captured_ops_list)) * 100

        logger.info(f"ΛTRACE: Performance Stats - AvgDur: {avg_duration_val:.2f}ms, MaxDur: {max_duration_val:.2f}ms, MinDur: {min_duration_val:.2f}ms, Success: {success_rate_val:.1f}%")
        logger.info(f"\n   📊 Performance Statistics:")
        logger.info(f"   📈 Average duration: {avg_duration_val:.2f}ms")
        logger.info(f"   ⬆️  Maximum duration: {max_duration_val:.2f}ms")
        logger.info(f"   ⬇️  Minimum duration: {min_duration_val:.2f}ms")
        logger.info(f"   ✅ Success rate: {success_rate_val:.1f}%")

        sub_100ms_ops_count = len([d for d in op_durations if d < 100])
        sub_100ms_percent = (sub_100ms_ops_count / len(op_durations)) * 100 if op_durations else 0
        logger.info(f"ΛTRACE: Sub-100ms operations: {sub_100ms_ops_count}/{len(op_durations)} ({sub_100ms_percent:.1f}%)")
        logger.info(f"   🎯 Sub-100ms operations: {sub_100ms_ops_count}/{len(op_durations)} ({sub_100ms_percent:.1f}%)")

        if sub_100ms_percent >= 75: # Adjusted target
            logger.info("ΛTRACE: Performance target (>=75% sub-100ms) met or exceeded.")
            logger.info("   🏆 EXCELLENT: Meeting sub-100ms performance targets!")
        else:
            logger.warning("ΛTRACE: Performance target (>=75% sub-100ms) NOT met.")
            logger.warning("   ⚠️  NEEDS IMPROVEMENT: Consider optimization for sub-100ms operations.")
        return sub_100ms_percent >= 75 # Test passes if target met
    else:
        logger.warning("ΛTRACE: No valid durations collected for performance statistics.")
        logger.warning("   ⚠️ No valid durations to calculate performance statistics.")
        return False # No successful ops with duration to analyze

# Async function to test error handling
async def test_error_handling() -> bool:
    """Tests the system's error handling for invalid commands and timeouts."""
    test_name = "Error Handling"
    logger.info(f"ΛTRACE: Starting test suite: {test_name}")
    logger.info(f"\n🛡️ Testing {test_name}")
    logger.info("=" * 50)
    all_steps_passed = True

    # Test 1: Invalid command execution
    logger.info("ΛTRACE: Step 1: Testing invalid command handling.")
    logger.info("1. Testing invalid command handling...")
    try:
        invalid_cmd_op = await capture(command_to_run="this_is_not_a_real_command_xyz123abc")
        if invalid_cmd_op.status == 'failed' and invalid_cmd_op.exit_code != 0 : # More specific check
            logger.info(f"ΛTRACE: Invalid command handled as 'failed' with exit code {invalid_cmd_op.exit_code}. Error: {invalid_cmd_op.error[:100]}...")
            logger.info("   ✅ Invalid command properly handled as failed.")
            logger.info(f"   📝 Error message (first 100 chars): {invalid_cmd_op.error[:100]}...")
        else:
            logger.error(f"ΛTRACE: Invalid command not properly detected as failed. Status: {invalid_cmd_op.status}, ExitCode: {invalid_cmd_op.exit_code}")
            logger.warning(f"   ⚠️  Invalid command not properly detected. Status: {invalid_cmd_op.status}, ExitCode: {invalid_cmd_op.exit_code}")
            all_steps_passed = False
    except Exception as e: # Should be caught by capture
        logger.error(f"ΛTRACE: Exception during invalid command test: {e}", exc_info=True)
        logger.error(f"   ❌ Exception during invalid command test: {type(e).__name__}")
        all_steps_passed = False

    # Test 2: Timeout handling
    logger.info("ΛTRACE: Step 2: Testing timeout handling.")
    logger.info("2. Testing timeout handling...")
    # Command that sleeps longer than timeout
    sleep_command = "sleep 5" if os.name != 'nt' else "timeout /t 5 /nobreak > NUL"
    try:
        timeout_op = await capture(command_to_run=sleep_command, timeout_duration_seconds=2)
        if timeout_op.status == 'timeout':
            logger.info(f"ΛTRACE: Timeout properly handled. Duration: {timeout_op.duration_ms:.0f}ms (expected ~2000ms).")
            logger.info("   ✅ Timeout properly handled.")
            logger.info(f"   ⏰ Duration: {timeout_op.duration_ms:.0f}ms (expected ~2000ms)")
        else:
            logger.error(f"ΛTRACE: Timeout not properly handled. Status: {timeout_op.status}, Duration: {timeout_op.duration_ms}ms.")
            logger.warning(f"   ⚠️  Timeout not properly handled: {timeout_op.status}")
            all_steps_passed = False
    except Exception as e: # Should be caught by capture
        logger.error(f"ΛTRACE: Exception during timeout test: {e}", exc_info=True)
        logger.error(f"   ❌ Exception during timeout test: {type(e).__name__}")
        all_steps_passed = False

    logger.info(f"ΛTRACE: Test suite '{test_name}' finished. Overall result: {'PASSED' if all_steps_passed else 'FAILED'}")
    return all_steps_passed

# Main async function to run all validation tests
async def main_validation_runner(): # Renamed
    """Main function to orchestrate and run all validation test suites."""
    logger.info("ΛTRACE: Starting main validation runner for Automatic Testing System.")
    logger.info("🚀 LUKHAS AGI Automatic Testing System - Full Validation Suite 🚀")
    logger.info("=" * 60)
    logger.info("This script will now perform a comprehensive validation of the testing system's capabilities...")

    validation_suite_results: List[Tuple[str, bool]] = []

    try:
        # Execute each test suite
        res_basic = await test_basic_functionality()
        validation_suite_results.append(("Basic Functionality Validation", res_basic))

        res_api = await test_one_line_api()
        validation_suite_results.append(("One-Line API Validation", res_api))

        res_perf = await test_performance_validation()
        validation_suite_results.append(("Performance Metrics Validation", res_perf))

        res_error = await test_error_handling()
        validation_suite_results.append(("Error Handling Validation", res_error))

    except Exception as e_critical:
        logger.critical(f"ΛTRACE: CRITICAL ERROR during main validation execution: {e_critical}", exc_info=True)
        logger.critical(f"\n❌ A critical error occurred during the validation process: {e_critical}")
        # No need to print traceback here if logger does it.
        return False # Indicate overall failure

    # Summarize results
    logger.info("ΛTRACE: All validation test suites completed. Generating summary.")
    logger.info("\n" + "=" * 60)
    logger.info("🏁 OVERALL VALIDATION SUMMARY 🏁")
    logger.info("=" * 60)

    num_passed_suites = sum(1 for _, result_flag in validation_suite_results if result_flag)
    total_suites_run = len(validation_suite_results)

    for suite_name, result_flag in validation_suite_results:
        status_indicator = "✅ PASSED" if result_flag else "❌ FAILED"
        logger.info(f"{status_indicator}: {suite_name}")
        logger.info(f"ΛTRACE: Validation Suite '{suite_name}' result: {'PASSED' if result_flag else 'FAILED'}")

    logger.info(f"\n📊 Final Tally: {num_passed_suites} out of {total_suites_run} validation suites passed.")
    logger.info(f"ΛTRACE: Final Tally - Passed: {num_passed_suites}, Total: {total_suites_run}.")

    if num_passed_suites == total_suites_run:
        logger.info("🎉 CONGRATULATIONS! All validation suites passed. The Automatic Testing System appears robust.")
        logger.info("ΛTRACE: All validation suites PASSED.")
        return True
    else:
        logger.warning("⚠️ ATTENTION: One or more validation suites failed. Please review the logs and output for details.")
        logger.warning("ΛTRACE: One or more validation suites FAILED.")
        return False

# Entry point for direct script execution
if __name__ == "__main__":
    logger.info("ΛTRACE: autotest_validation.py executed directly as __main__.")

    # Python version check
    if sys.version_info < (3, 7): # Async/await syntax requires 3.5+, but many libraries target 3.7+
        logger.critical("ΛTRACE: Python 3.7+ is required for this validation script due to async/await usage and type hinting.")
        logger.error("❌ This script requires Python 3.7 or higher.")
        sys.exit(1)

    # Run the main validation runner
    logger.info("ΛTRACE: Invoking main_validation_runner.")
    overall_success_status = asyncio.run(main_validation_runner())
    logger.info(f"ΛTRACE: main_validation_runner finished. Overall success: {overall_success_status}.")

    # Exit with appropriate status code (0 for success, 1 for failure)
    sys.exit(0 if overall_success_status else 1)

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: autotest_validation.py
# VERSION: 1.1.0 # Assuming evolution from a prior version
# TIER SYSTEM: Not applicable (Validation Script)
# ΛTRACE INTEGRATION: ENABLED (Script-level logging for validation process)
# CAPABILITIES: Validates AutomaticTestingSystem initialization, operation capture,
#               one-line API functions, performance analysis, and error handling.
# FUNCTIONS: test_basic_functionality, test_one_line_api, test_performance_validation,
#            test_error_handling, main_validation_runner.
# CLASSES: None defined in this file (imports ATS classes).
# DECORATORS: None.
# DEPENDENCIES: asyncio, sys, os, pathlib, logging, traceback,
#               core.automatic_testing_system.
# INTERFACES: Command-line execution (__main__ block).
# ERROR HANDLING: Catches exceptions during test execution and reports overall success/failure.
# LOGGING: ΛTRACE_ENABLED for tracing the validation script's execution.
# AUTHENTICATION: Not applicable.
# HOW TO USE:
#   Run as a standalone script: python core/autotest_validation.py
#   Ensure automatic_testing_system.py is in the parent 'core' directory or PYTHONPATH.
# INTEGRATION NOTES: This script is crucial for verifying the integrity and functionality
#                    of the AutomaticTestingSystem. It should be run after any significant
#                    changes to the testing system itself.
# MAINTENANCE: Update test cases as new features are added to AutomaticTestingSystem.
#              Ensure paths and commands used in tests are valid in the execution environment.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
