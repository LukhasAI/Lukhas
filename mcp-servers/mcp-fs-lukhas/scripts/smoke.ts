import { getFile, listDir, searchFiles, statRel } from "../src/fsTools.js";

async function smokeTest() {
  console.log("🧪 Running smoke tests for mcp-fs-lukhas...\n");
  
  try {
    // Test 1: stat on root
    console.log("1. Testing stat on root...");
    const statResult = await statRel(".");
    console.log(`✅ stat('.') -> ${JSON.stringify(statResult, null, 2)}\n`);
    
    // Test 2: list_dir on src (if exists) else root
    console.log("2. Testing list_dir...");
    let listResult;
    try {
      listResult = await listDir("src");
      console.log(`✅ list_dir('src') -> Found ${listResult.length} entries\n`);
    } catch {
      listResult = await listDir(".");
      console.log(`✅ list_dir('.') -> Found ${listResult.length} entries\n`);
    }
    
    // Test 3: search for "TODO OR FIXME"
    console.log("3. Testing search...");
    const searchResult = await searchFiles("TODO OR FIXME", "**/*.{md,ts,js,py}", 5);
    console.log(`✅ search('TODO OR FIXME') -> Found ${searchResult.length} matches\n`);
    
    // Test 4: get_file on README.md
    console.log("4. Testing get_file...");
    const fileResult = await getFile("README.md");
    console.log(`✅ get_file('README.md') -> ${fileResult.size} bytes, redacted: ${fileResult.redacted || false}\n`);
    
    console.log("🎉 All smoke tests passed!");
    
  } catch (error) {
    console.error("❌ Smoke test failed:", error);
    process.exit(1);
  }
}

smokeTest();
