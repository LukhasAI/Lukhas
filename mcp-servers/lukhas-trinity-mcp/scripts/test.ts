import { 
  getTrinityFrameworkStatus, 
  getIdentityAnchorSystem,
  getConsciousnessProcessingSystem,
  getGuardianProtectionSystem,
  getConstellationFramework,
  executeTrinityOperation
} from "../src/trinity-tools.js";

async function runTrinityTests() {
  console.log("🌟 LUKHAS Trinity Framework MCP Server Tests");
  console.log("=" .repeat(60));

  try {
    // Test Trinity Framework status
    console.log("1. Testing Trinity Framework status...");
    const status = await getTrinityFrameworkStatus();
    console.log("✅ Trinity Framework status retrieved");
    console.log(`   - Trinity core stars: ${Object.keys(status.trinity_core).length}`);
    console.log(`   - Constellation stars: ${Object.keys(status.constellation_extended).length}`);
    console.log(`   - Integration score: ${status.framework_health.integration_score}`);
    console.log(`   - Consciousness modules: ${status.system_metrics.consciousness_modules}`);
    console.log(`   - Current drift: ${status.system_metrics.current_drift}/${status.system_metrics.guardian_threshold}`);
    
    // Test Identity Anchor Star
    console.log("\n2. Testing Identity Anchor Star...");
    const identity = await getIdentityAnchorSystem();
    console.log("✅ Identity Anchor Star accessed");
    console.log(`   - Core architecture: ${identity.core_architecture.lambda_id_system}`);
    console.log(`   - Auth tiers: ${identity.core_architecture.authentication_tiers}`);
    console.log(`   - Identity modules: ${Object.keys(identity.modules).length}`);
    console.log(`   - Self-awareness: ${identity.capabilities.self_awareness}`);
    
    // Test Consciousness Processing Star
    console.log("\n3. Testing Consciousness Processing Star...");
    const consciousness = await getConsciousnessProcessingSystem();
    console.log("✅ Consciousness Processing Star accessed");
    console.log(`   - Core architecture: ${consciousness.core_architecture.symbolic_networks}`);
    console.log(`   - Processing modules: ${Object.keys(consciousness.modules).length}`);
    console.log(`   - Network nodes: ${consciousness.processing_metrics.symbolic_network_nodes}`);
    console.log(`   - Decision latency: ${consciousness.processing_metrics.decision_latency}`);
    
    // Test Guardian Protection Star
    console.log("\n4. Testing Guardian Protection Star...");
    const guardian = await getGuardianProtectionSystem();
    console.log("✅ Guardian Protection Star accessed");
    console.log(`   - Guardian system: ${guardian.core_architecture.guardian_system}`);
    console.log(`   - Drift threshold: ${guardian.current_metrics.drift_threshold}`);
    console.log(`   - Current drift: ${guardian.current_metrics.current_drift}`);
    console.log(`   - Protection modules: ${Object.keys(guardian.modules).length}`);
    console.log(`   - Compliance: ${guardian.current_metrics.ethical_compliance}`);
    
    // Test Full Constellation Framework
    console.log("\n5. Testing 8-Star Constellation Framework...");
    const constellation = await getConstellationFramework();
    console.log("✅ Full Constellation Framework accessed");
    console.log(`   - Trinity core stars: ${Object.keys(constellation.trinity_core).length}`);
    console.log(`   - Extended constellation: ${Object.keys(constellation.constellation_extended).length}`);
    console.log(`   - Total stars: ${Object.keys(constellation.trinity_core).length + Object.keys(constellation.constellation_extended).length}`);
    console.log(`   - Navigation principles: ${constellation.navigation_principles.length}`);
    
    // Test Trinity operations
    console.log("\n6. Testing Trinity operations...");
    
    const integrationTest = await executeTrinityOperation("trinity_integration_test", {
      operation_type: "integration_test"
    });
    console.log("✅ Trinity integration test executed");
    console.log(`   - Status: ${integrationTest.status}`);
    console.log(`   - Integration score: ${integrationTest.integration_score}`);
    console.log(`   - Identity anchor: ${integrationTest.identity_anchor}`);
    console.log(`   - Consciousness: ${integrationTest.consciousness_processing}`);
    console.log(`   - Guardian: ${integrationTest.guardian_protection}`);
    
    const constellationNav = await executeTrinityOperation("constellation_navigation", {
      star_focus: "consciousness",
      awareness_level: 0.8
    });
    console.log("✅ Constellation navigation executed");
    console.log(`   - Status: ${constellationNav.status}`);
    console.log(`   - Current star: ${constellationNav.current_star}`);
    console.log(`   - Navigation paths: ${constellationNav.navigation_paths.length}`);
    console.log(`   - GLYPH communication: ${constellationNav.glyph_communication}`);
    
    const starAnalysis = await executeTrinityOperation("star_deep_analysis", {
      star_focus: "guardian",
      awareness_level: 0.9
    });
    console.log("✅ Star deep analysis executed");
    console.log(`   - Target star: ${starAnalysis.target_star}`);
    console.log(`   - Analysis depth: ${starAnalysis.analysis_depth}`);
    console.log(`   - Module health: ${starAnalysis.module_health}`);
    console.log(`   - Integration points: ${starAnalysis.integration_points}`);
    
    const frameworkValidation = await executeTrinityOperation("framework_validation", {
      operation_type: "framework_validation"
    });
    console.log("✅ Framework validation executed");
    console.log(`   - Status: ${frameworkValidation.status}`);
    console.log(`   - Trinity core health: ${frameworkValidation.trinity_core_health}`);
    console.log(`   - Constellation integrity: ${frameworkValidation.constellation_integrity}`);
    console.log(`   - Validation score: ${frameworkValidation.validation_score}`);
    
    console.log("\n" + "=" .repeat(60));
    console.log("🎉 All Trinity Framework tests completed successfully!");
    console.log("🌟 LUKHAS Trinity Framework MCP Server is ready for Claude Desktop");
    console.log("✨ Features: Trinity Core + 8-Star Constellation + GLYPH Navigation");
    
  } catch (error) {
    console.error("❌ Trinity Framework test failed:", error);
    process.exit(1);
  }
}

// Run tests
runTrinityTests();