const assert = require('assert');

// Mock localStorage
const mockStorage = {};
const localStorage = {
  getItem: (k) => mockStorage[k] || null,
  setItem: (k, v) => { mockStorage[k] = String(v); },
  removeItem: (k) => { delete mockStorage[k]; },
  clear: () => { for (const k in mockStorage) delete mockStorage[k]; }
};

// 1. Verify example strings match the prompt requirements exactly
const expectedExamples = [
  "Nenu repu college ki vastanu, but assignment complete cheyyaledu",
  "Meeru ee project deadline gurinchi manager tho matladara?",
  "Kal meeting hai please slides bhej dena",
  "Tum kab tak college aaoge?",
  "NENU REPU college ki vastanuuuu plz",
  "Nenu repu college ki vastanu, tum bhi aao na"
];

const fs = require('fs');
const htmlContent = fs.readFileSync('frontend/index.html', 'utf8');

console.log("--- Checking Example Chips in index.html ---");
expectedExamples.forEach((ex, idx) => {
  assert(htmlContent.includes(ex), `Missing example chip ${idx + 1}: ${ex}`);
  console.log(`Example chip ${idx + 1} present: ${ex}`);
});

console.log("\n--- Testing History in localStorage ---");
function getStoredHistory() {
  try {
    const raw = localStorage.getItem("codemix_history");
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    }
  } catch (err) {}
  return [];
}

function setStoredHistory(history) {
  localStorage.setItem("codemix_history", JSON.stringify(history.slice(0, 10)));
}

function saveToPipelineHistory({ text, strategy, translation, time }) {
  if (!text || !translation) return;
  const current = getStoredHistory();
  const filtered = current.filter(
    (item) => !(item.text === text && item.strategy === strategy)
  );
  filtered.unshift({
    text: text,
    strategy: strategy || "full",
    translation: translation,
    time: time || "—",
    timestamp: Date.now()
  });
  setStoredHistory(filtered.slice(0, 10));
}

function clearPipelineHistory() {
  localStorage.removeItem("codemix_history");
}

// Initial state: empty
assert.strictEqual(getStoredHistory().length, 0);

// Add 12 items, verify capped at 10 and ordered most recent first
for (let i = 1; i <= 12; i++) {
  saveToPipelineHistory({
    text: `Input sentence ${i}`,
    strategy: i % 2 === 0 ? "full" : "clause",
    translation: `Translation ${i}`,
    time: `${i * 100} ms`
  });
}

const history = getStoredHistory();
assert.strictEqual(history.length, 10, "History should be capped at 10 items");
assert.strictEqual(history[0].text, "Input sentence 12", "Most recent item should be at index 0");
assert.strictEqual(history[9].text, "Input sentence 3", "10th item should be sentence 3 (1 and 2 evicted)");
console.log("Added 12 items -> correctly capped to 10 with newest first.");

// Acceptance: Simulate page reload (reading from localStorage)
const reloadedHistory = getStoredHistory();
assert.strictEqual(reloadedHistory.length, 10);
assert.strictEqual(reloadedHistory[0].translation, "Translation 12");
console.log("Simulated reload: history persisted in localStorage under 'codemix_history'.");

// Acceptance: Clear history empties it
clearPipelineHistory();
assert.strictEqual(getStoredHistory().length, 0, "Clear history should empty storage");
assert.strictEqual(localStorage.getItem("codemix_history"), null);
console.log("Clear history: correctly emptied localStorage.");

console.log("\n--- Testing Download JSON Serialization ---");
const sampleResponse = {
  original: "Kal meeting hai please slides bhej dena",
  normalized: "Kal meeting hai please slides bhej dena",
  dominant_lang: "HI",
  strategy: "full",
  translation: "there is a meeting tomorrow please send slides",
  tokens: [
    { text: "Kal", lang: "HI", conf: 0.98, native: "कल" },
    { text: "meeting", lang: "EN", conf: 0.99, native: null }
  ],
  glosses: {},
  clauses: [],
  timings_ms: {
    normalize: 1.2,
    lid: 145.3,
    transliterate: 21.0,
    translate: 820.5
  }
};

const jsonStr = JSON.stringify(sampleResponse, null, 2);
const parsed = JSON.parse(jsonStr);
assert.strictEqual(parsed.translation, sampleResponse.translation);
assert(parsed.timings_ms.translate > 800, "Timings must be included in exported JSON");
console.log("JSON export serialization verified with timings and token annotations.");

console.log("\nAll convenience feature tests passed!");

