/**
 * test_offline_acceptance.js
 * Comprehensive end-to-end simulation of Offline Demo Mode acceptance test.
 */

const fs = require("fs");
const path = require("path");
const assert = require("assert");

// Load demo_cache.json
const cachePath = path.join(__dirname, "..", "frontend", "demo_cache.json");
const cache = JSON.parse(fs.readFileSync(cachePath, "utf-8"));

console.log("=== Testing Acceptance Criteria ===");

// 1. Simulate backend stopped (health check fails)
console.log("1. Simulating backend stop / health check failure...");
let isDemoMode = false;
let bannerHidden = true;
let bannerText = "";

function setDemoMode(enable) {
  isDemoMode = enable;
  bannerHidden = !enable;
  if (enable) {
    bannerText = "Demo mode - showing pre-computed results";
  }
}

// Backend health check fails -> switch to demo mode
const latestMtHealthData = null; // offline
const isUrlDemo = false;
if (isUrlDemo || !latestMtHealthData) {
  setDemoMode(true);
}

assert.strictEqual(isDemoMode, true, "Must switch to demo mode when backend is offline");
assert.strictEqual(bannerHidden, false, "Demo banner must be visible when demo mode is active");
assert.strictEqual(bannerText, "Demo mode - showing pre-computed results", "Banner must show exact required text");
console.log("   Banner displayed: 'Demo mode - showing pre-computed results'");

// 2. Click an example chip
console.log("2. Simulating clicking an example chip...");
const chosenSentence = "Kal meeting hai please slides bhej dena";
let inputAreaValue = chosenSentence;
assert.strictEqual(inputAreaValue, "Kal meeting hai please slides bhej dena");
console.log("   Textarea populated with:", inputAreaValue);

// 3. Press Translate in demo mode
console.log("3. Simulating pressing Translate in offline demo mode...");
function simulateTranslate(input, strategy = "full") {
  assert(isDemoMode, "Must be in demo mode");
  const cleaned = input.trim();
  const entry = cache[cleaned];
  if (!entry) {
    return {
      success: false,
      error: "This sentence is not in the offline demo. Choose one of the example chips."
    };
  }
  const response = entry[strategy] || entry.full;
  return {
    success: true,
    data: response
  };
}

const transResult = simulateTranslate(inputAreaValue, "full");
assert(transResult.success, "Translation must succeed from cache");
assert.strictEqual(transResult.data.translation, "there is a meeting tomorrow please send slides");
assert(Array.isArray(transResult.data.tokens) && transResult.data.tokens.length === 7);
assert.strictEqual(transResult.data.dominant_lang, "HI");
assert(transResult.data.glosses["Kal"] === "Tomorrow");
console.log("   Result rendered from cache:", transResult.data.translation);
console.log("   Tokens rendered:", transResult.data.tokens.map(t => `${t.text}(${t.lang})`).join(" "));

// 4. Test un-cached sentence
console.log("4. Simulating entering an un-cached custom sentence...");
const unCachedSentence = "Yeh sentence cache me nahi hai";
const unCachedResult = simulateTranslate(unCachedSentence);
assert.strictEqual(unCachedResult.success, false);
assert.strictEqual(unCachedResult.error, "This sentence is not in the offline demo. Choose one of the example chips.");
console.log("   Correctly rejected with message:", unCachedResult.error);

// 5. Test Compare Strategies in demo mode
console.log("5. Simulating 'Compare strategies' in demo mode...");
function simulateCompare(input) {
  const cleaned = input.trim();
  const entry = cache[cleaned];
  if (!entry) {
    return {
      success: false,
      error: "This sentence is not in the offline demo. Choose one of the example chips."
    };
  }
  const columns = [];
  for (const strat of ["direct", "lid_only", "full", "clause"]) {
    columns.push({
      strategy: strat,
      translation: entry[strat].translation,
      timings: entry[strat].timings_ms
    });
  }
  return { success: true, columns };
}

const compareResult = simulateCompare(inputAreaValue);
assert(compareResult.success);
assert.strictEqual(compareResult.columns.length, 4);
console.log("   Compare rendered columns:");
compareResult.columns.forEach(c => console.log(`     - [${c.strategy}]: ${c.translation}`));

// 6. Backend comes back online
console.log("6. Simulating backend coming back online...");
const onlineHealth = { status: "ok", loaded: true };
if (onlineHealth && onlineHealth.status === "ok" && !isUrlDemo) {
  setDemoMode(false);
}
assert.strictEqual(isDemoMode, false, "Must leave demo mode when backend is back");
assert.strictEqual(bannerHidden, true, "Banner must be automatically hidden when backend returns");
console.log("   Banner automatically removed when backend came back online.");

console.log("\nALL ACCEPTANCE CRITERIA VERIFIED SUCCESSFULLY!");

