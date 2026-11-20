const assert = require('assert');

// 1. Test chrF computation
function computeChrF(hyp, ref) {
  if (!hyp || !ref) return null;
  const h = hyp.replace(/\s+/g, "").toLowerCase();
  const r = ref.replace(/\s+/g, "").toLowerCase();
  if (!h || !r) return null;

  let sumF = 0;
  let validCount = 0;

  for (let n = 1; n <= 6; n++) {
    const totalH = h.length - n + 1;
    const totalR = r.length - n + 1;
    if (totalH <= 0 || totalR <= 0) continue;

    const hGrams = {};
    for (let i = 0; i <= h.length - n; i++) {
      const g = h.substring(i, i + n);
      hGrams[g] = (hGrams[g] || 0) + 1;
    }

    const rGrams = {};
    for (let i = 0; i <= r.length - n; i++) {
      const g = r.substring(i, i + n);
      rGrams[g] = (rGrams[g] || 0) + 1;
    }

    let overlap = 0;
    for (const [g, count] of Object.entries(hGrams)) {
      if (rGrams[g]) {
        overlap += Math.min(count, rGrams[g]);
      }
    }

    const p = overlap / totalH;
    const rec = overlap / totalR;
    const denom = 4 * p + rec;
    const f2 = denom > 0 ? (5 * p * rec) / denom : 0;

    sumF += f2;
    validCount++;
  }

  if (validCount === 0) return 0;
  return (sumF / validCount) * 100;
}

// 2. Diff rendering logic
function cleanWordForDiff(w) {
  if (!w) return "";
  return w.toLowerCase().replace(/^[^\w\d]+|[^\w\d]+$/g, "");
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function renderDiffText(text, fullWordSet, isFullColumn) {
  if (!text) return "";
  if (isFullColumn || !fullWordSet || fullWordSet.size === 0) {
    return escapeHtml(text);
  }

  const tokens = text.split(/(\s+)/);
  return tokens
    .map((token) => {
      if (!token.trim()) {
        return escapeHtml(token);
      }
      const clean = cleanWordForDiff(token);
      if (clean && !fullWordSet.has(clean)) {
        return `<mark class="diff-word">${escapeHtml(token)}</mark>`;
      }
      return escapeHtml(token);
    })
    .join("");
}

console.log("--- Testing chrF ---");
const perfect = computeChrF("hello world", "hello world");
assert.strictEqual(perfect, 100);
console.log("chrF perfect match:", perfect);

const disjoint = computeChrF("abcdef", "123456");
assert.strictEqual(disjoint, 0);
console.log("chrF disjoint match:", disjoint);

const emptyRef = computeChrF("some hypothesis", "");
assert.strictEqual(emptyRef, null);

const acceptanceHypFull = "there is a meeting tomorrow please send slides";
const acceptanceHypDirect = "tomorrow is the meeting please slides bhej dena";
const acceptanceRef = "There is a meeting tomorrow, please send slides";

const fullScore = computeChrF(acceptanceHypFull, acceptanceRef);
const directScore = computeChrF(acceptanceHypDirect, acceptanceRef);
console.log("Full pipeline chrF:", fullScore.toFixed(1));
console.log("Direct MT chrF:", directScore.toFixed(1));
assert(fullScore > directScore, "Full strategy should have higher chrF than Direct strategy");
assert(fullScore > 85, "Full strategy chrF should be > 85");

console.log("\n--- Testing Diff Highlighting ---");
const fullWords = acceptanceHypFull.split(/\s+/).map(cleanWordForDiff).filter(Boolean);
const fullWordSet = new Set(fullWords);

const diffHtml = renderDiffText(acceptanceHypDirect, fullWordSet, false);
console.log("Diff HTML for Direct column:\n", diffHtml);
assert(diffHtml.includes('<mark class="diff-word">bhej</mark>'), "bhej should be highlighted");
assert(diffHtml.includes('<mark class="diff-word">dena</mark>'), "dena should be highlighted");
assert(!diffHtml.includes('<mark class="diff-word">tomorrow</mark>'), "tomorrow is in Full, should not be highlighted");
assert(!diffHtml.includes('<mark class="diff-word">meeting</mark>'), "meeting is in Full, should not be highlighted");

const fullColHtml = renderDiffText(acceptanceHypFull, fullWordSet, true);
assert(!fullColHtml.includes('class="diff-word"'), "Full column should have no diff highlights");
console.log("Full column diff check passed: zero marks present.");

console.log("\n--- Testing Telugu detection for mT5 ---");
function checkTelugu(fullRes, lidRes) {
  return (fullRes && fullRes.dominant_lang === "TE") ||
         (lidRes && lidRes.dominant_lang === "TE") ||
         (fullRes && fullRes.data && Array.isArray(fullRes.data.tokens) && fullRes.data.tokens.some((t) => t.lang === "TE"));
}

assert.strictEqual(checkTelugu({ dominant_lang: "TE" }, {}), true);
assert.strictEqual(checkTelugu({ dominant_lang: "HI" }, { dominant_lang: "TE" }), true);
assert.strictEqual(checkTelugu({ dominant_lang: "HI", data: { tokens: [{ lang: "TE" }] } }, {}), true);
assert.strictEqual(checkTelugu({ dominant_lang: "HI", data: { tokens: [{ lang: "HI" }, { lang: "EN" }] } }, {}), false);
console.log("Telugu detection checks passed.");

console.log("\nAll unit tests passed successfully!");

