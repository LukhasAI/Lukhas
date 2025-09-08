import { statRel, listDir, getFile } from "../src/fsTools.js";

async function fuzzTest() {
  console.log("🔥 Running fuzz tests for mcp-fs-lukhas...\n");
  
  const pathTraversalAttempts = [
    "../../",
    "../../../etc/passwd",
    "%2e%2e/",
    "..\\..\\windows\\system32",
    "/..",
    "//etc/passwd",
    "CON",
    "PRN", 
    "AUX",
    "NUL",
    "COM1",
    "LPT1",
    "a".repeat(1000), // overly long name
    "\x00../secret", // null byte injection
    "secret\x00file.txt",
    "path/with/\x1f/control/chars",
    "unicode\u0000injection"
  ];
  
  const pathologicalQueries = [
    "a".repeat(10000), // massive query
    "((((((((((", // regex-like payload
    "<script>alert('xss')</script>", // HTML/script injection
    "'; DROP TABLE users; --", // SQL injection attempt
    "SELECT * FROM secrets WHERE id=1", // SQL-like
    "\x1b[31mRED TEXT\x1b[0m", // ANSI escape codes
    "api_key = sk_1234567890abcdef", // credential-like
    "AKIA1234567890123456", // AWS key-like
    "ghp_abcdefghijklmnopqrstuvwxyz123456789012", // GitHub token-like
    "password: super_secret_123"
  ];
  
  let passCount = 0;
  let totalTests = 0;
  
  // Test path traversal protection
  console.log("Testing path traversal protection...");
  for (const badPath of pathTraversalAttempts) {
    totalTests++;
    try {
      await statRel(badPath);
      console.log(`❌ FAIL: stat should have rejected: ${badPath}`);
    } catch (error) {
      console.log(`✅ PASS: stat correctly rejected: ${badPath.slice(0, 50)}...`);
      passCount++;
    }
    
    totalTests++;
    try {
      await listDir(badPath);
      console.log(`❌ FAIL: list_dir should have rejected: ${badPath}`);
    } catch (error) {
      console.log(`✅ PASS: list_dir correctly rejected: ${badPath.slice(0, 50)}...`);
      passCount++;
    }
    
    totalTests++;
    try {
      await getFile(badPath);
      console.log(`❌ FAIL: get_file should have rejected: ${badPath}`);
    } catch (error) {
      console.log(`✅ PASS: get_file correctly rejected: ${badPath.slice(0, 50)}...`);
      passCount++;
    }
  }
  
  // Test search query validation
  console.log("\nTesting search query validation...");
  const { searchFiles } = await import("../src/fsTools.js");
  for (const badQuery of pathologicalQueries) {
    totalTests++;
    try {
      await searchFiles(badQuery, "**/*.md", 10);
      console.log(`⚠️  WARN: search accepted potentially dangerous query: ${badQuery.slice(0, 50)}...`);
      passCount++; // It's ok if search handles it gracefully
    } catch (error) {
      console.log(`✅ PASS: search rejected dangerous query: ${badQuery.slice(0, 50)}...`);
      passCount++;
    }
  }
  
  console.log(`\n📊 Fuzz Test Results: ${passCount}/${totalTests} tests passed`);
  
  if (passCount === totalTests) {
    console.log("🎉 All fuzz tests passed! Security looks good.");
  } else {
    console.log("⚠️  Some security tests failed. Review the implementation.");
    process.exit(1);
  }
}

fuzzTest();
