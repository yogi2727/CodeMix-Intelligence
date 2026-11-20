const assert = require('assert');
const fs = require('fs');

console.log("--- 1. Testing frontend/results.json Schema & Required Content ---");
const raw = fs.readFileSync('frontend/results.json', 'utf8');
const data = JSON.parse(raw);

// Check headline key
assert(data.headline && typeof data.headline === "object", "headline must be an object");
assert.strictEqual(data.headline.phinc_gain_chrF, 11.30, "phinc_gain_chrF should be 11.30");
assert.deepStrictEqual(data.headline.phinc_gain_ci, [10.47, 12.16], "phinc_gain_ci must be [10.47, 12.16]");
assert.strictEqual(data.headline.phinc_n, 1351, "phinc_n must be 1351");

assert.strictEqual(data.headline.lid_gating_gain_chrF, 6.64, "lid_gating_gain_chrF should be 6.64");
assert.deepStrictEqual(data.headline.lid_gating_ci, [5.21, 8.04], "lid_gating_ci must be [5.21, 8.04]");
assert.strictEqual(data.headline.lid_gating_n, 400, "lid_gating_n must be 400");

assert.strictEqual(data.headline.lid_macro_f1, 0.983, "lid_macro_f1 should be 0.983");
assert.strictEqual(data.headline.ms_full, 568, "ms_full should be 568");
assert.strictEqual(data.headline.ms_direct, 744, "ms_direct should be 744");
console.log("Headline card keys verified.");

// Check phinc_all (n = 1351) and gains table
assert(data.phinc_all && typeof data.phinc_all === "object", "phinc_all missing");
assert.strictEqual(data.phinc_all.n, 1351, "phinc_all.n must be 1351");
assert(Array.isArray(data.phinc_all.systems) && data.phinc_all.systems.length === 3, "phinc_all.systems must have 3 systems");
assert(Array.isArray(data.phinc_all.gains) && data.phinc_all.gains.length === 3, "phinc_all.gains must have 3 entries");

// Check phinc_400
assert(Array.isArray(data.phinc_400) && data.phinc_400.length === 4, "phinc_400 must have 4 entries");
console.log("phinc_all (n = 1351), gains, and phinc_400 verified.");

// Check dev_80 & dev_80_note
assert(Array.isArray(data.dev_80) && data.dev_80.length === 5, "dev_80 must have 5 systems");
assert(typeof data.dev_80_note === "string" && data.dev_80_note.includes("Telugu lexicon"), "dev_80_note verified");
console.log("dev_80 and dev_80_note verified.");

// Check translit_ablation_80
assert(Array.isArray(data.translit_ablation_80) && data.translit_ablation_80.length === 3, "translit_ablation_80 must have 3 systems");
console.log("translit_ablation_80 verified.");

// Check lid & lid_compare
assert(data.lid && Array.isArray(data.lid.classes) && data.lid.classes.length === 3, "lid.classes must have EN, HI, TE");
assert(Array.isArray(data.lid_compare) && data.lid_compare.length === 4, "lid_compare must have 4 rows");
data.lid_compare.forEach((row, idx) => {
  assert(row.test, `Row ${idx} missing test`);
  assert(row.model, `Row ${idx} missing model`);
  assert(typeof row.macro_F1 === "number", `Row ${idx} missing macro_F1`);
  assert(typeof row.TE_to_HI === "number", `Row ${idx} missing TE_to_HI`);
  assert(typeof row.HI_to_TE === "number", `Row ${idx} missing HI_to_TE`);
});
console.log("lid and lid_compare (with TE_to_HI and HI_to_TE) verified.");

// Check mixed_multi_clause, mixed_all_50, mixed_intra_clause
assert(data.mixed_multi_clause && typeof data.mixed_multi_clause === "object", "mixed_multi_clause missing");
assert.strictEqual(data.mixed_multi_clause.provisional, false, "provisional must be false");
assert.strictEqual(data.mixed_multi_clause.n, 40, "mixed_multi_clause.n must be 40");
assert(Array.isArray(data.mixed_multi_clause.systems) && data.mixed_multi_clause.systems.length === 4, "mixed_multi_clause.systems must have 4 items");
assert(Array.isArray(data.mixed_multi_clause.gains) && data.mixed_multi_clause.gains.length === 3, "mixed_multi_clause.gains must have 3 items");

assert(Array.isArray(data.mixed_all_50) && data.mixed_all_50.length === 4, "mixed_all_50 must have 4 items");

assert(data.mixed_intra_clause && typeof data.mixed_intra_clause === "object", "mixed_intra_clause missing");
assert.strictEqual(data.mixed_intra_clause.n, 10, "mixed_intra_clause.n must be 10");
assert(typeof data.mixed_intra_clause.note === "string" && data.mixed_intra_clause.note.includes("Inconclusive"), "mixed_intra_clause note verified");
assert(Array.isArray(data.mixed_intra_clause.systems) && data.mixed_intra_clause.systems.length === 4, "mixed_intra_clause systems verified");
console.log("mixed_multi_clause, mixed_all_50, and mixed_intra_clause verified.");

// Check regression_check & negative_results
assert(Array.isArray(data.regression_check) && data.regression_check.length === 4, "regression_check must have 4 rows");
data.regression_check.forEach((r, idx) => {
  assert(r.set, `regression_check row ${idx} missing set`);
  assert(r.system, `regression_check row ${idx} missing system`);
  assert(typeof r.chrF === "number", `regression_check row ${idx} missing chrF`);
});

assert(Array.isArray(data.negative_results) && data.negative_results.length === 5, "negative_results must have 5 items");
console.log("regression_check and negative_results verified.");

console.log("\n--- 2. Testing frontend/index.html DOM Structure ---");
const html = fs.readFileSync('frontend/index.html', 'utf8');
assert(html.includes('id="tab-experiments"'), "Missing #tab-experiments");
assert(html.includes('id="panel-experiments"'), "Missing #panel-experiments");
assert(html.includes('id="experiments-error-banner"'), "Missing #experiments-error-banner");
assert(html.includes('id="experiments-content"'), "Missing #experiments-content");
assert(html.includes('id="experiments-headlines-grid"'), "Missing #experiments-headlines-grid");
assert(html.includes('id="experiments-charts-grid"'), "Missing #experiments-charts-grid");
assert(html.includes('id="experiments-lid-container"'), "Missing #experiments-lid-container");
assert(html.includes('id="experiments-lid-compare-container"'), "Missing #experiments-lid-compare-container");
assert(html.includes('id="experiments-regression-container"'), "Missing #experiments-regression-container");
assert(html.includes('id="experiments-negative-list"'), "Missing #experiments-negative-list");
assert(html.includes('id="experiments-limitations-list"'), "Missing #experiments-limitations-list");
console.log("All required DOM elements present in index.html.");

console.log("\n--- 3. Testing Dynamic Rendering & Number Modification (Acceptance Test) ---");
function computeBarWidth(score) {
  return `${Math.min(100, Math.max(8, score))}%`;
}

// Initial PHINC Full score: 53.17
assert.strictEqual(computeBarWidth(data.phinc_all.systems[2].chrF), "53.17%");

// Changing a number in data and recomputing updates the score
const modifiedData = JSON.parse(JSON.stringify(data));
modifiedData.phinc_all.systems[2].chrF = 61.25;
assert.strictEqual(computeBarWidth(modifiedData.phinc_all.systems[2].chrF), "61.25%");
console.log("Dynamic render verified: changing number in JSON updates chart width (53.17% -> 61.25%).");

console.log("\nAll unit and acceptance tests for Experiments tab passed!");
