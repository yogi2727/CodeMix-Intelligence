/**
 * test_demo_mode.js
 * Verification of Offline Demo Mode (P7) in CodeMix Intelligence.
 */

const fs = require("fs");
const path = require("path");
const assert = require("assert");

console.log("=== 1. Checking frontend/demo_cache.json ===");
const cachePath = path.join(__dirname, "..", "frontend", "demo_cache.json");
assert(fs.existsSync(cachePath), "demo_cache.json must exist in frontend/");

const cache = JSON.parse(fs.readFileSync(cachePath, "utf-8"));
const exampleSentences = [
  "Nenu repu college ki vastanu, but assignment complete cheyyaledu",
  "Meeru ee project deadline gurinchi manager tho matladara?",
  "Kal meeting hai please slides bhej dena",
  "Tum kab tak college aaoge?",
  "NENU REPU college ki vastanuuuu plz",
  "Nenu repu college ki vastanu, tum bhi aao na"
];

for (const sent of exampleSentences) {
  assert(cache[sent], `Sentence must be cached: "${sent}"`);
  const entry = cache[sent];
  assert(entry.direct, `direct strategy must exist for "${sent}"`);
  assert(entry.lid_only, `lid_only strategy must exist for "${sent}"`);
  assert(entry.full, `full strategy must exist for "${sent}"`);
  assert(entry.clause, `clause strategy must exist for "${sent}"`);

  // Verify response fields
  for (const strat of ["direct", "lid_only", "full", "clause"]) {
    const res = entry[strat];
    assert.strictEqual(typeof res.translation, "string", `translation must be string for ${strat}`);
    assert(res.translation.length > 0, `translation must not be empty for ${strat}`);
    assert(res.timings_ms && typeof res.timings_ms === "object", `timings_ms must exist for ${strat}`);
    if (strat !== "direct") {
      assert(Array.isArray(res.tokens), `tokens must be an array for ${strat}`);
      assert(res.dominant_lang === "TE" || res.dominant_lang === "HI", `dominant_lang must be TE or HI for ${strat}`);
    }
  }
}
console.log("All 6 example sentences verified with direct, lid_only, full, and clause responses!");

console.log("\n=== 2. Checking HTML Demo Banner ===");
const htmlContent = fs.readFileSync(path.join(__dirname, "..", "frontend", "index.html"), "utf-8");
assert(htmlContent.includes('id="pipeline-demo-banner"'), "index.html must have #pipeline-demo-banner");
assert(htmlContent.includes("Demo mode - showing pre-computed results"), "index.html must contain exact banner text");

console.log("\n=== 3. Checking CSS Demo Banner Styles ===");
const cssContent = fs.readFileSync(path.join(__dirname, "..", "frontend", "styles.css"), "utf-8");
assert(cssContent.includes(".pipeline-demo-banner"), "styles.css must have .pipeline-demo-banner");
assert(cssContent.includes(".pipeline-demo-banner[hidden]"), "styles.css must handle [hidden] state");

console.log("\n=== 4. Checking Demo Mode Logic in app.js ===");
const appJsContent = fs.readFileSync(path.join(__dirname, "..", "frontend", "app.js"), "utf-8");

assert(appJsContent.includes("checkUrlDemoMode"), "app.js must implement checkUrlDemoMode");
assert(appJsContent.includes("setDemoMode"), "app.js must implement setDemoMode");
assert(appJsContent.includes("loadDemoCache"), "app.js must implement loadDemoCache");
assert(appJsContent.includes("findInDemoCache"), "app.js must implement findInDemoCache");
assert(appJsContent.includes("This sentence is not in the offline demo. Choose one of the example chips."),
  "app.js must show exact missing message for non-cached sentences");

console.log("\n=== 5. Simulating Cache Matching Logic ===");
function findInDemoCache(demoCache, rawInput) {
  if (!demoCache || typeof demoCache !== "object" || !rawInput) return null;
  const cleaned = rawInput.trim();
  if (demoCache[cleaned]) return { key: cleaned, entry: demoCache[cleaned] };
  const normalize = (s) => s.toLowerCase().replace(/[.,!?;:]/g, "").replace(/\s+/g, " ").trim();
  const inputNorm = normalize(cleaned);
  for (const [k, v] of Object.entries(demoCache)) {
    if (normalize(k) === inputNorm) return { key: k, entry: v };
  }
  return null;
}

// Test exact match
const matchExact = findInDemoCache(cache, "Kal meeting hai please slides bhej dena");
assert(matchExact, "Exact sentence must match");
assert.strictEqual(matchExact.entry.full.translation, "there is a meeting tomorrow please send slides");

// Test slight punctuation/spacing variance
const matchVar = findInDemoCache(cache, "Nenu repu college ki vastanu but assignment complete cheyyaledu");
assert(matchVar, "Sentence without comma must still match");

// Test unknown sentence
const matchUnknown = findInDemoCache(cache, "This is an un-cached random sentence for testing");
assert.strictEqual(matchUnknown, null, "Unknown sentence must return null");

console.log("Cache lookup logic verified successfully!");

console.log("\nAll unit tests for Offline Demo Mode (P7) passed!");

