import { 
  getConsciousnessStatus, 
  getTrinityFramework,
  getMatrixCognitiveDNA,
  executeConsciousnessOperation
} from "../src/consciousness-tools.js";

async function runConsciousnessTests() {
  console.log("🧬 LUKHAS Consciousness MCP Server Tests");
  console.log("=" .repeat(50));

  try {
    // Test consciousness status
    console.log("1. Testing consciousness status...");
    const status = await getConsciousnessStatus();
    console.log("✅ Consciousness status retrieved");
    console.log(`   - Trinity components: ${Object.keys(status.trinity_framework).length}`);
    console.log(`   - MΛTRIZ components: ${Object.keys(status.matrix_system).length}`);
    console.log(`   - Constellation stars: ${Object.keys(status.constellation).length}`);
    
    // Test Trinity Framework
    console.log("\n2. Testing Trinity Framework access...");
    const trinity = await getTrinityFramework();
    console.log("✅ Trinity Framework accessed");
    console.log(`   - Identity: ${trinity.identity.description}`);
    console.log(`   - Consciousness: ${trinity.consciousness.description}`);
    console.log(`   - Guardian: ${trinity.guardian.description}`);
    
    // Test MΛTRIZ Cognitive DNA
    console.log("\n3. Testing MΛTRIZ Cognitive DNA...");
    const matrix = await getMatrixCognitiveDNA();
    console.log("✅ MΛTRIZ system accessed");
    console.log(`   - Total modules: ${matrix.scale.total_modules}`);
    console.log(`   - Candidate modules: ${matrix.scale.candidate_modules}`);
    console.log(`   - LUKHAS modules: ${matrix.scale.lukhas_modules}`);
    
    // Test consciousness operations
    console.log("\n4. Testing consciousness operations...");
    
    const dreamResult = await executeConsciousnessOperation("dream_processing", {
      awareness_level: 0.7
    });
    console.log("✅ Dream processing executed");
    console.log(`   - Status: ${dreamResult.status}`);
    console.log(`   - Message: ${dreamResult.message}`);
    
    const guardianResult = await executeConsciousnessOperation("guardian_check", {
      trinity_focus: "guardian"
    });
    console.log("✅ Guardian check executed");
    console.log(`   - Status: ${guardianResult.status}`);
    console.log(`   - Drift threshold: ${guardianResult.drift_threshold}`);
    console.log(`   - Current drift: ${guardianResult.current_drift}`);
    
    const memoryResult = await executeConsciousnessOperation("memory_fold_query", {
      memory_fold_limit: 800
    });
    console.log("✅ Memory fold query executed");
    console.log(`   - Status: ${memoryResult.status}`);
    console.log(`   - Cascade prevention: ${memoryResult.cascade_prevention}`);
    
    const reasoningResult = await executeConsciousnessOperation("symbolic_reasoning", {
      awareness_level: 0.9
    });
    console.log("✅ Symbolic reasoning executed");
    console.log(`   - Status: ${reasoningResult.status}`);
    console.log(`   - Reasoning depth: ${reasoningResult.reasoning_depth}`);
    
    console.log("\n" + "=" .repeat(50));
    console.log("🎉 All consciousness tests completed successfully!");
    console.log("🧬 LUKHAS Consciousness MCP Server is ready for Claude Desktop");
    
  } catch (error) {
    console.error("❌ Consciousness test failed:", error);
    process.exit(1);
  }
}

// Run tests
runConsciousnessTests();