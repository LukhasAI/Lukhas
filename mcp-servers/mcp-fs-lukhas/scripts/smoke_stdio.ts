import { statRel, listDir, searchFiles, getFile, readRange } from "../src/fsTools.js";

async function main() {
  console.log("STAT .");
  console.log(await statRel("."));

  console.log("\nLIST .");
  const lst = await listDir(".");
  console.log(lst.slice(0, 10));

  console.log("\nSEARCH 'EQNOX OR DriftScore'");
  console.log(await searchFiles("EQNOX OR DriftScore", "**/*.{md,txt,ts,tsx,js,py,json}", 5));

  console.log("\nGET README.md (first 200 chars)");
  const file = await getFile("README.md").catch(() => ({ text: "(no README.md here)" } as any));
  console.log((file.text || "").slice(0, 200));

  console.log("\nREAD_RANGE README.md [0..1024]");
  const rr = await readRange("README.md", 0, 1024).catch(() => ({ chunk: "(no README.md here)" } as any));
  console.log((rr as any).chunk);
}

main().catch(e => { console.error(e); process.exit(1); });