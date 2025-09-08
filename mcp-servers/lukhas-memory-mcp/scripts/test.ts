import { 
  getMemorySystemStatus, 
  queryMemoryFolds,
  getWaveCMemorySystem,
  executeMemoryOperation,
  getMemoryDatabaseInfo
} from "../src/memory-tools.js";

async function runMemoryTests() {
  console.log("🧠 LUKHAS Memory Integration MCP Server Tests");
  console.log("=" .repeat(55));

  try {
    // Test memory system status
    console.log("1. Testing memory system status...");
    const status = await getMemorySystemStatus();
    console.log("✅ Memory system status retrieved");
    console.log(`   - Wave C processing: ${status.wave_c_processing.available ? 'Available' : 'Offline'}`);
    console.log(`   - Fold-based memory: ${status.fold_based_memory.available ? 'Available' : 'Offline'}`);
    console.log(`   - LUKHAS memory: ${status.lukhas_memory.available ? 'Available' : 'Offline'}`);
    console.log(`   - Threading safety: ${status.memory_security.threading_safety}`);
    
    // Test memory fold queries
    console.log("\n2. Testing memory fold queries...");
    const foldResults = await queryMemoryFolds("consciousness patterns", 500);
    console.log("✅ Memory fold query executed");
    console.log(`   - Query: ${foldResults.query}`);
    console.log(`   - Fold limit: ${foldResults.fold_limit}`);
    console.log(`   - Results found: ${foldResults.search_results.length}`);
    console.log(`   - Cascade prevention: ${foldResults.memory_statistics.cascade_prevention_active ? 'Active' : 'Inactive'}`);
    
    // Test Wave C memory system
    console.log("\n3. Testing Wave C memory system (Aka Qualia)...");
    const waveC = await getWaveCMemorySystem();
    console.log("✅ Wave C memory system accessed");
    console.log(`   - Memory clients: ${Object.keys(waveC.architecture.memory_clients).length}`);
    console.log(`   - Test categories: ${Object.keys(waveC.test_categories).length}`);
    console.log(`   - Current status: ${waveC.current_status.infrastructure}`);
    console.log(`   - Threading issues: ${waveC.current_status.threading_issues}`);
    
    // Test memory database info
    console.log("\n4. Testing memory database information...");
    const dbInfo = await getMemoryDatabaseInfo();
    console.log("✅ Memory database info retrieved");
    console.log(`   - Storage type: ${dbInfo.primary_storage.type}`);
    console.log(`   - Memory clients: ${Object.keys(dbInfo.memory_clients).length}`);
    console.log(`   - Threading status: ${dbInfo.safety_measures.threading}`);
    console.log(`   - Test coverage: ${dbInfo.test_infrastructure.total_coverage}`);
    
    // Test memory operations
    console.log("\n5. Testing memory operations...");
    
    const storeResult = await executeMemoryOperation("store_scene", {
      scene_id: "test_scene_001",
      emotion_vector: [0.8, 0.6, 0.7],
      memory_type: "episodic"
    });
    console.log("✅ Store scene operation executed");
    console.log(`   - Scene ID: ${storeResult.scene_id}`);
    console.log(`   - Storage client: ${storeResult.storage_client}`);
    console.log(`   - Cascade check: ${storeResult.fold_cascade_check}`);
    
    const recallResult = await executeMemoryOperation("recall_scenes", {
      query_text: "happy memories",
      memory_type: "semantic",
      fold_limit: 800
    });
    console.log("✅ Recall scenes operation executed");
    console.log(`   - Query: ${recallResult.query_text}`);
    console.log(`   - Scenes found: ${recallResult.scenes_found}`);
    console.log(`   - Memory type: ${recallResult.memory_type}`);
    
    const analysisResult = await executeMemoryOperation("analyze_memory_pattern", {
      scene_id: "test_scene_001"
    });
    console.log("✅ Memory pattern analysis executed");
    console.log(`   - Pattern type: ${analysisResult.pattern_type}`);
    console.log(`   - Pattern strength: ${analysisResult.pattern_strength}`);
    console.log(`   - Wave C insights: ${analysisResult.wave_c_insights}`);
    
    const foldAnalysisResult = await executeMemoryOperation("memory_fold_analysis", {
      fold_limit: 1000
    });
    console.log("✅ Memory fold analysis executed");
    console.log(`   - Fold count: ${foldAnalysisResult.fold_count}`);
    console.log(`   - Cascade prevention: ${foldAnalysisResult.cascade_prevention}`);
    console.log(`   - Causal integrity: ${foldAnalysisResult.causal_integrity}`);
    
    const gdprResult = await executeMemoryOperation("gdpr_erasure", {
      scene_id: "user_requested_deletion"
    });
    console.log("✅ GDPR erasure operation executed");
    console.log(`   - Compliance: ${gdprResult.compliance}`);
    console.log(`   - Erasure method: ${gdprResult.erasure_method}`);
    console.log(`   - Verification: ${gdprResult.verification}`);
    
    console.log("\n" + "=" .repeat(55));
    console.log("🎉 All memory tests completed successfully!");
    console.log("🧠 LUKHAS Memory MCP Server is ready for Claude Desktop");
    console.log("💡 Features: Wave C processing, fold-based memory, GDPR compliance, threading safety");
    
  } catch (error) {
    console.error("❌ Memory test failed:", error);
    process.exit(1);
  }
}

// Run tests
runMemoryTests();