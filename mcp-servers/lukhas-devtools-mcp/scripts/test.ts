import { 
  getTestInfrastructureStatus, 
  getCodeAnalysisStatus,
  getT4AuditStatus,
  getDevelopmentUtilities,
  executeDevToolsOperation,
  getModuleStructure
} from "../src/devtools.js";

async function runDevToolsTests() {
  console.log("🛠️ LUKHAS Development Tools MCP Server Tests");
  console.log("=" .repeat(65));

  try {
    // Test testing infrastructure status
    console.log("1. Testing infrastructure status...");
    const testStatus = await getTestInfrastructureStatus();
    console.log("✅ Testing infrastructure status retrieved");
    console.log(`   - Total tests: ${testStatus.comprehensive_testing.total_tests}`);
    console.log(`   - Test categories: ${Object.keys(testStatus.comprehensive_testing.test_categories).length}`);
    console.log(`   - Current status: ${testStatus.comprehensive_testing.current_status}`);
    console.log(`   - Passing tests: ${testStatus.test_execution.passing_tests}`);
    console.log(`   - Infrastructure health: ${testStatus.infrastructure_health.system_stability}`);
    
    // Test code analysis status
    console.log("\n2. Testing code analysis status...");
    const codeAnalysis = await getCodeAnalysisStatus();
    console.log("✅ Code analysis status retrieved");
    console.log(`   - Total errors (pre-fix): ${codeAnalysis.ruff_analysis.total_errors}`);
    console.log(`   - Error reduction: ${codeAnalysis.ruff_analysis.error_reduction}`);
    console.log(`   - Current Ruff errors: ${codeAnalysis.ruff_analysis.current_status}`);
    console.log(`   - MyPy errors: ${codeAnalysis.mypy_analysis.current_errors}`);
    console.log(`   - Lane guard: ${codeAnalysis.code_quality.lane_guard}`);
    
    // Test T4 audit status
    console.log("\n3. Testing T4 audit status...");
    const t4Status = await getT4AuditStatus();
    console.log("✅ T4 audit status retrieved");
    console.log(`   - Current phase: ${t4Status.current_phase}`);
    console.log(`   - Coverage: ${t4Status.coverage_metrics.current_coverage} (target: ${t4Status.coverage_metrics.target_coverage})`);
    console.log(`   - Ruff errors: ${t4Status.coverage_metrics.ruff_errors}`);
    console.log(`   - Tests passing: ${t4Status.coverage_metrics.tests_passing}`);
    console.log(`   - STEPS_2 progress: ${t4Status.progress_summary.steps_2_progress}`);
    
    // Test development utilities
    console.log("\n4. Testing development utilities...");
    const devUtils = await getDevelopmentUtilities();
    console.log("✅ Development utilities retrieved");
    console.log(`   - Core Makefile commands: ${devUtils.makefile_targets.core_commands.length}`);
    console.log(`   - Development commands: ${devUtils.makefile_targets.development_commands.length}`);
    console.log(`   - Quality commands: ${devUtils.makefile_targets.quality_commands.length}`);
    console.log(`   - Analysis tools: ${Object.keys(devUtils.analysis_tools).length}`);
    
    // Test module structure
    console.log("\n5. Testing module structure exploration...");
    const rootStructure = await getModuleStructure();
    console.log("✅ Module structure retrieved");
    console.log(`   - Root path: ${rootStructure.path}`);
    console.log(`   - Structure items: ${rootStructure.structure.length}`);
    console.log(`   - Total modules: ${rootStructure.consciousness_architecture.total_modules}`);
    console.log(`   - Candidate modules: ${rootStructure.consciousness_architecture.candidate_modules}`);
    console.log(`   - LUKHAS modules: ${rootStructure.consciousness_architecture.lukhas_modules}`);
    
    const candidateStructure = await getModuleStructure("candidate/");
    console.log("✅ Candidate structure explored");
    console.log(`   - Candidate items: ${candidateStructure.structure.length}`);
    
    // Test development operations
    console.log("\n6. Testing development operations...");
    
    const testRun = await executeDevToolsOperation("run_tests", {
      test_category: "integration"
    });
    console.log("✅ Test run operation executed");
    console.log(`   - Status: ${testRun.status}`);
    console.log(`   - Test category: ${testRun.test_category}`);
    console.log(`   - Total tests: ${testRun.total_tests}`);
    console.log(`   - Infrastructure: ${testRun.infrastructure_status}`);
    
    const codeAnalysisOp = await executeDevToolsOperation("code_analysis", {
      analysis_type: "ruff"
    });
    console.log("✅ Code analysis operation executed");
    console.log(`   - Analysis type: ${codeAnalysisOp.analysis_type}`);
    console.log(`   - Improvements: ${codeAnalysisOp.improvements}`);
    console.log(`   - Priority fixes: ${codeAnalysisOp.priority_fixes}`);
    
    const auditCheck = await executeDevToolsOperation("audit_status", {
      audit_phase: "steps_2"
    });
    console.log("✅ Audit status check executed");
    console.log(`   - Current phase: ${auditCheck.current_phase}`);
    console.log(`   - Audit phase: ${auditCheck.audit_phase}`);
    console.log(`   - Quality target: ${auditCheck.quality_target}`);
    
    const infraCheck = await executeDevToolsOperation("infrastructure_check", {});
    console.log("✅ Infrastructure check executed");
    console.log(`   - Status: ${infraCheck.status}`);
    console.log(`   - Critical fixes: ${infraCheck.critical_fixes.length}`);
    console.log(`   - MCP readiness: ${infraCheck.mcp_readiness}`);
    
    const devMetrics = await executeDevToolsOperation("development_metrics", {});
    console.log("✅ Development metrics gathered");
    console.log(`   - Total modules: ${devMetrics.metrics.total_modules}`);
    console.log(`   - Error reduction: ${devMetrics.metrics.error_reduction}`);
    console.log(`   - MCP servers: ${devMetrics.metrics.mcp_servers}`);
    console.log(`   - System readiness: ${devMetrics.metrics.system_readiness}`);
    
    console.log("\n" + "=" .repeat(65));
    console.log("🎉 All development tools tests completed successfully!");
    console.log("🛠️ LUKHAS Development Tools MCP Server is ready for Claude Desktop");
    console.log("📊 Features: T4 Audit + Testing Infrastructure + Code Analysis + Module Exploration");
    
  } catch (error) {
    console.error("❌ Development tools test failed:", error);
    process.exit(1);
  }
}

// Run tests
runDevToolsTests();