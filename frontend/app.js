/**
 * CodeMix Intelligence - Step 33C
 * Frontend Application Logic: "Linguist's Lab" × "Minimal Light"
 *
 * Connects to the local FastAPI backend (http://127.0.0.1:8000).
 * Handles model health polling, input validation, sample insertion,
 * live token prediction, response validation, annotated/table rendering,
 * distribution calculations, request cancellation, and clipboard export.
 */

// Global API Base URL (single source of truth)
const API_BASE_URL = "http://127.0.0.1:8000";

// Canonical Label Mappings
const LABEL_MAPPING = {
  EN: 0,
  HI: 1,
  TE: 2,
  OTHER: 3
};

const LANGUAGE_NAMES = {
  EN: "English",
  HI: "Hindi",
  TE: "Telugu",
  OTHER: "Other"
};

// Application State
let activeAbortController = null;
let activeRequestId = 0;
let healthPollInterval = null;
let isHealthChecking = false;
let currentPredictionData = null;
let activeView = "annotated"; // "annotated" | "table"

// DOM Elements Cache
const elements = {
  statusPill: document.getElementById("status-pill"),
  statusDot: document.getElementById("status-dot"),
  statusText: document.getElementById("status-text"),
  deviceInfo: document.getElementById("device-info"),
  noticeContainer: document.getElementById("notice-container"),
  sentenceInput: document.getElementById("sentence-input"),
  charCount: document.getElementById("char-count"),
  clearBtn: document.getElementById("clear-btn"),
  detectBtn: document.getElementById("detect-btn"),
  btnSpinner: document.getElementById("btn-spinner"),
  btnText: document.getElementById("btn-text"),
  samplePills: document.querySelectorAll(".sample-pill"),
  resultsPanel: document.getElementById("results-panel"),
  chunkingInfo: document.getElementById("chunking-info"),
  viewAnnotatedBtn: document.getElementById("view-annotated-btn"),
  viewTableBtn: document.getElementById("view-table-btn"),
  annotatedContainer: document.getElementById("annotated-container"),
  tableContainer: document.getElementById("table-container"),
  tokensFlow: document.getElementById("tokens-flow"),
  tableBody: document.getElementById("table-body"),
  copyBtn: document.getElementById("copy-btn"),
  copyNotice: document.getElementById("copy-notice"),
  statTotal: document.getElementById("stat-total"),
  statEn: document.getElementById("stat-en"),
  statHi: document.getElementById("stat-hi"),
  statTe: document.getElementById("stat-te"),
  statOther: document.getElementById("stat-other"),
  distributionBar: document.getElementById("distribution-bar"),
  avgConfidenceText: document.getElementById("avg-confidence-text")
};

// ==============================================================================
// 1. Health Checking & System Status
// ==============================================================================

/**
 * Update the navigation status pill and device metadata.
 * @param {'ready'|'loading'|'offline'} state
 * @param {string} [deviceText]
 */
function updateStatusPill(state, deviceText) {
  elements.statusDot.className = "status-dot";

  if (state === "ready") {
    elements.statusDot.classList.add("status-ready");
    elements.statusText.textContent = "Model ready";
  } else if (state === "loading") {
    elements.statusDot.classList.add("status-loading");
    elements.statusText.textContent = "Model loading";
  } else {
    elements.statusDot.classList.add("status-error");
    elements.statusText.textContent = "Backend offline";
  }

  if (deviceText !== undefined) {
    elements.deviceInfo.textContent = deviceText;
  }
}

/**
 * Check backend health via GET /api/health.
 */
async function checkBackendHealth() {
  if (isHealthChecking) return;
  isHealthChecking = true;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);

    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      if (data && data.model_loaded === true) {
        updateStatusPill("ready", data.device || "cpu");
      } else {
        updateStatusPill("loading", data.device || "Loading...");
      }
    } else {
      updateStatusPill("offline", "Unavailable");
    }
  } catch (err) {
    updateStatusPill("offline", "Unavailable");
  } finally {
    isHealthChecking = false;
  }
}

/**
 * Start health polling interval.
 */
function startHealthPolling() {
  checkBackendHealth();
  if (!healthPollInterval) {
    healthPollInterval = setInterval(checkBackendHealth, 15000);
  }
}

/**
 * Pause health polling when document is hidden to conserve resources.
 */
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    if (healthPollInterval) {
      clearInterval(healthPollInterval);
      healthPollInterval = null;
    }
  } else {
    startHealthPolling();
  }
});

// ==============================================================================
// 2. Safe Notice & Alert Rendering
// ==============================================================================

/**
 * Display an inline notice block using safe DOM manipulation.
 * @param {string} message - Text message to display.
 * @param {'error'|'info'} [type='error'] - Notice type.
 */
function showNotice(message, type = "error") {
  clearNotices();

  const box = document.createElement("div");
  box.className = `notice-box notice-${type}`;
  box.setAttribute("role", type === "error" ? "alert" : "status");

  const textSpan = document.createElement("span");
  textSpan.textContent = message;

  box.appendChild(textSpan);
  elements.noticeContainer.appendChild(box);
}

/**
 * Clear all visible notices.
 */
function clearNotices() {
  while (elements.noticeContainer.firstChild) {
    elements.noticeContainer.removeChild(elements.noticeContainer.firstChild);
  }
}

// ==============================================================================
// 3. Input Handling & Character Counter
// ==============================================================================

/**
 * Update character counter and enable/disable Detect button.
 */
function handleInputChange() {
  const text = elements.sentenceInput.value;
  elements.charCount.textContent = `${text.length} characters`;

  // Enable Detect button only if non-whitespace text is present and not currently analyzing
  const hasText = text.trim().length > 0;
  const isAnalyzing = elements.detectBtn.classList.contains("loading");

  elements.detectBtn.disabled = !hasText || isAnalyzing;
}

elements.sentenceInput.addEventListener("input", handleInputChange);

// Keyboard Shortcut: Ctrl+Enter (Win/Linux) or Cmd+Enter (Mac) to detect languages
elements.sentenceInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (!elements.detectBtn.disabled) {
      executePrediction();
    }
  }
});

// ==============================================================================
// 4. Sample Sentences
// ==============================================================================

const LONG_PARAGRAPH_BASE = "Hello dost, nenu repu morning office ki vastanu kaani meeting start cheyyandi please. Mujhe lagta hai ki train late ho sakti hai, isliye thoda wait karo. Mariyu project report submit cheyyadam chala important, so work complete cheyali. Kal hum sab milkar discuss karenge and updates final karenge. Please inform everyone in the team so that no one misses the discussion. ";

const SAMPLE_TEXTS = {
  "te-en": "Naku meeting ki late avuthundi, please wait cheyyandi.",
  "hi-en": "Mujhe meeting ke liye late ho raha hai, please wait karo.",
  "tri": "Hello dost, nenu kal meeting ke liye office ki vastanu.",
  "long": LONG_PARAGRAPH_BASE.repeat(5).trim()
};

elements.samplePills.forEach((pill) => {
  pill.addEventListener("click", () => {
    const key = pill.getAttribute("data-sample");
    if (SAMPLE_TEXTS[key]) {
      elements.sentenceInput.value = SAMPLE_TEXTS[key];
      handleInputChange();
      elements.sentenceInput.focus();
    }
  });
});

// ==============================================================================
// 5. Clear Button & Request Cancellation
// ==============================================================================

elements.clearBtn.addEventListener("click", () => {
  const isAnalyzing = elements.detectBtn.classList.contains("loading");

  if (isAnalyzing && activeAbortController) {
    // 1. Abort the running request
    activeAbortController.abort();
    activeAbortController = null;

    // 2. Invalidate active request ID so any late response is discarded
    activeRequestId++;

    // 3. Reset loading UI
    resetLoadingState();

    // 4. Empty textarea and reset character count
    elements.sentenceInput.value = "";
    handleInputChange();

    // 5. Hide results
    hideResults();

    // 6. Display specified cancellation notice
    showNotice("Analysis cancelled because the input was cleared.", "info");
  } else {
    // Normal idle clear
    elements.sentenceInput.value = "";
    handleInputChange();
    hideResults();
    clearNotices();
  }
});

/**
 * Hide and clear the results panel.
 */
function hideResults() {
  elements.resultsPanel.hidden = true;
  currentPredictionData = null;
  setView("annotated");
  if (copyNoticeTimeout) {
    clearTimeout(copyNoticeTimeout);
    copyNoticeTimeout = null;
  }
  elements.copyNotice.hidden = true;
  while (elements.tokensFlow.firstChild) {
    elements.tokensFlow.removeChild(elements.tokensFlow.firstChild);
  }
  while (elements.tableBody.firstChild) {
    elements.tableBody.removeChild(elements.tableBody.firstChild);
  }
  while (elements.distributionBar.firstChild) {
    elements.distributionBar.removeChild(elements.distributionBar.firstChild);
  }
}

/**
 * Reset Detect button to normal idle state.
 */
function resetLoadingState() {
  elements.detectBtn.classList.remove("loading");
  elements.btnSpinner.style.display = "none";
  elements.btnText.textContent = "Detect languages";
  handleInputChange();
}

// ==============================================================================
// 6. Response Validation (Strict)
// ==============================================================================

/**
 * Strictly validate the structure and content of the API response.
 * Never maps an unknown label to OTHER; rejects corrupted data.
 * @param {any} data
 * @returns {boolean}
 */
function validateApiResponse(data) {
  if (!data || typeof data !== "object") return false;
  if (typeof data.text !== "string") return false;
  if (!Array.isArray(data.tokens)) return false;
  if (typeof data.chunked !== "boolean") return false;
  if (typeof data.chunk_count !== "number" || data.chunk_count < 1) return false;
  if (typeof data.model !== "string") return false;

  for (let i = 0; i < data.tokens.length; i++) {
    const item = data.tokens[i];
    if (!item || typeof item !== "object") return false;
    if (typeof item.token_index !== "number" || item.token_index !== i) return false;
    if (typeof item.token !== "string") return false;

    // Allowed labels check: strictly EN, HI, TE, OTHER
    if (!(item.predicted_label in LABEL_MAPPING)) {
      console.error(`Invalid label detected: ${item.predicted_label}`);
      return false;
    }

    // Label ID check
    if (typeof item.predicted_label_id === "number") {
      if (LABEL_MAPPING[item.predicted_label] !== item.predicted_label_id) {
        console.error(`Label ID mismatch: ${item.predicted_label} vs ${item.predicted_label_id}`);
        return false;
      }
    }

    // Confidence scale check: must be finite number in [0.0, 1.0]
    if (typeof item.confidence !== "number" || !isFinite(item.confidence)) return false;
    if (item.confidence < 0.0 || item.confidence > 1.0) return false;
  }

  return true;
}

// ==============================================================================
// 7. Prediction Flow & Execution
// ==============================================================================

elements.detectBtn.addEventListener("click", executePrediction);

async function executePrediction() {
  const rawText = elements.sentenceInput.value;
  const cleanedText = rawText.trim();

  if (!cleanedText) {
    showNotice("Please enter some text.", "error");
    return;
  }

  // Clear previous notices & hide old results
  clearNotices();
  hideResults();

  // Create AbortController and track request ID
  activeAbortController = new AbortController();
  activeRequestId++;
  const thisRequestId = activeRequestId;

  // Set loading state
  elements.detectBtn.classList.add("loading");
  elements.detectBtn.disabled = true;
  elements.btnSpinner.style.display = "inline-block";
  elements.btnText.textContent = "Analyzing...";

  // Timer 1: 3-second long text notice
  let longWaitTimer = setTimeout(() => {
    if (thisRequestId === activeRequestId && elements.detectBtn.classList.contains("loading")) {
      elements.btnText.textContent = "Long text is taking a little longer...";
    }
  }, 3000);

  // Timer 2: 120-second client-side timeout
  let timeoutTimer = setTimeout(() => {
    if (thisRequestId === activeRequestId && activeAbortController) {
      activeAbortController.abort();
      showNotice("The request timed out. Please try again with a shorter sentence.", "error");
      resetLoadingState();
    }
  }, 120000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: cleanedText }),
      signal: activeAbortController.signal
    });

    clearTimeout(longWaitTimer);
    clearTimeout(timeoutTimer);

    // If request was cancelled or superseded by a newer one, discard
    if (thisRequestId !== activeRequestId) return;

    if (!response.ok) {
      const status = response.status;
      let errorDetail = "";
      try {
        const errorJson = await response.json();
        if (errorJson && typeof errorJson.detail === "string") {
          errorDetail = errorJson.detail;
        } else if (errorJson && Array.isArray(errorJson.detail)) {
          errorDetail = errorJson.detail.map((d) => d.msg || "").join("; ");
        }
      } catch (_) {}

      if (status === 400) {
        showNotice(errorDetail || "Please enter some text.", "error");
      } else if (status === 422) {
        showNotice(
          errorDetail || "The submitted text is not valid. Please check the input and try again.",
          "error"
        );
      } else if (status === 503) {
        showNotice("The model is still starting up. Please try again in a moment.", "info");
        updateStatusPill("loading");
      } else {
        showNotice(`Server error (${status}). Please try again later.`, "error");
      }

      checkBackendHealth();
      return;
    }

    const data = await response.json();

    // Verify response integrity
    if (!validateApiResponse(data)) {
      showNotice("The server returned an unexpected response.", "error");
      return;
    }

    // Render genuine validated predictions
    currentPredictionData = data;
    renderPredictions(data);
  } catch (err) {
    clearTimeout(longWaitTimer);
    clearTimeout(timeoutTimer);

    if (thisRequestId !== activeRequestId) return;

    if (err.name === "AbortError") {
      // Aborted either by user clear or timeout; already handled
      return;
    }

    showNotice(
      "Cannot reach the backend at http://127.0.0.1:8000. Make sure it is running.",
      "error"
    );
    updateStatusPill("offline");
    checkBackendHealth();
  } finally {
    if (thisRequestId === activeRequestId) {
      resetLoadingState();
      activeAbortController = null;
    }
  }
}

// ==============================================================================
// 8. Results Rendering (Annotated View, Table View, Statistics)
// ==============================================================================

/**
 * Render validated predictions into both annotated and table views.
 * @param {object} data - Validated API response.
 */
function renderPredictions(data) {
  const tokens = data.tokens;

  // 1. Chunking Info in Results Header
  if (data.chunked) {
    elements.chunkingInfo.textContent = `Chunked · ${data.chunk_count} chunks processed`;
  } else {
    elements.chunkingInfo.textContent = `Not chunked · 1 chunk processed`;
  }

  // 2. Render Annotated View (Signature Vertical Stacks)
  while (elements.tokensFlow.firstChild) {
    elements.tokensFlow.removeChild(elements.tokensFlow.firstChild);
  }

  tokens.forEach((item) => {
    const stack = document.createElement("div");
    const langKey = item.predicted_label.toLowerCase();
    stack.className = `token-stack lang-${langKey}`;

    const confPct = (item.confidence * 100).toFixed(1);
    const langFullName = LANGUAGE_NAMES[item.predicted_label] || item.predicted_label;

    // Accessible title and ARIA label
    const accessibleLabel = `${item.token}, ${langFullName}, model confidence ${confPct} percent`;
    stack.setAttribute("title", accessibleLabel);
    stack.setAttribute("aria-label", accessibleLabel);

    // 1. Token Text
    const wordSpan = document.createElement("span");
    wordSpan.className = "token-word font-serif";
    wordSpan.textContent = item.token;

    // 2. Coloured Underline
    const lineSpan = document.createElement("span");
    lineSpan.className = "token-underline";
    lineSpan.setAttribute("aria-hidden", "true");

    // 3. Language Label Text
    const labelSpan = document.createElement("span");
    labelSpan.className = "token-label-text font-mono";
    labelSpan.textContent = `${item.predicted_label} ${Math.round(item.confidence * 100)}%`;

    stack.appendChild(wordSpan);
    stack.appendChild(lineSpan);
    stack.appendChild(labelSpan);

    elements.tokensFlow.appendChild(stack);
  });

  // 3. Render Table View
  while (elements.tableBody.firstChild) {
    elements.tableBody.removeChild(elements.tableBody.firstChild);
  }

  tokens.forEach((item) => {
    const row = document.createElement("tr");

    const tdIndex = document.createElement("td");
    tdIndex.className = "font-mono";
    tdIndex.textContent = String(item.token_index);

    const tdToken = document.createElement("td");
    tdToken.className = "td-token";
    tdToken.textContent = item.token;

    const tdLabel = document.createElement("td");
    const langKey = item.predicted_label.toLowerCase();
    tdLabel.className = `td-label lang-${langKey}`;
    tdLabel.textContent = item.predicted_label;

    const tdConf = document.createElement("td");
    tdConf.className = "td-conf";
    tdConf.textContent = `${(item.confidence * 100).toFixed(1)}%`;

    row.appendChild(tdIndex);
    row.appendChild(tdToken);
    row.appendChild(tdLabel);
    row.appendChild(tdConf);

    elements.tableBody.appendChild(row);
  });

  // 4. Calculate Statistics
  const totalCount = tokens.length;
  let countEn = 0;
  let countHi = 0;
  let countTe = 0;
  let countOther = 0;
  let totalConfidence = 0.0;

  tokens.forEach((item) => {
    totalConfidence += item.confidence;
    if (item.predicted_label === "EN") countEn++;
    else if (item.predicted_label === "HI") countHi++;
    else if (item.predicted_label === "TE") countTe++;
    else if (item.predicted_label === "OTHER") countOther++;
  });

  elements.statTotal.textContent = String(totalCount);
  elements.statEn.textContent = String(countEn);
  elements.statHi.textContent = String(countHi);
  elements.statTe.textContent = String(countTe);
  elements.statOther.textContent = String(countOther);

  // 5. Render Proportional Distribution Bar
  while (elements.distributionBar.firstChild) {
    elements.distributionBar.removeChild(elements.distributionBar.firstChild);
  }

  if (totalCount > 0) {
    const distribution = [
      { key: "en", label: "English", count: countEn },
      { key: "hi", label: "Hindi", count: countHi },
      { key: "te", label: "Telugu", count: countTe },
      { key: "other", label: "Other", count: countOther }
    ];

    distribution.forEach((item) => {
      if (item.count > 0) {
        const pct = (item.count / totalCount) * 100;
        const segment = document.createElement("div");
        segment.className = `dist-segment seg-${item.key}`;
        segment.style.width = `${pct}%`;
        segment.setAttribute(
          "title",
          `${item.label}: ${item.count} tokens (${pct.toFixed(1)}%)`
        );
        elements.distributionBar.appendChild(segment);
      }
    });

    // 6. Average Model Confidence
    const avgConfidence = (totalConfidence / totalCount) * 100;
    elements.avgConfidenceText.textContent = `Average model confidence: ${avgConfidence.toFixed(1)}%`;
  } else {
    elements.avgConfidenceText.textContent = "Average model confidence: 0.0%";
  }

  // Ensure Annotated view is the default whenever new results render
  setView("annotated");

  // 7. Make Results Panel Visible
  elements.resultsPanel.hidden = false;
  elements.resultsPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ==============================================================================
// 9. View Toggle (Annotated | Table)
// ==============================================================================

/**
 * Switch results presentation view.
 * @param {'annotated'|'table'} viewName
 */
function setView(viewName) {
  activeView = viewName;
  if (viewName === "annotated") {
    elements.viewAnnotatedBtn.classList.add("active");
    elements.viewAnnotatedBtn.setAttribute("aria-selected", "true");
    elements.viewTableBtn.classList.remove("active");
    elements.viewTableBtn.setAttribute("aria-selected", "false");

    elements.annotatedContainer.hidden = false;
    elements.tableContainer.hidden = true;
  } else {
    elements.viewTableBtn.classList.add("active");
    elements.viewTableBtn.setAttribute("aria-selected", "true");
    elements.viewAnnotatedBtn.classList.remove("active");
    elements.viewAnnotatedBtn.setAttribute("aria-selected", "false");

    elements.tableContainer.hidden = false;
    elements.annotatedContainer.hidden = true;
  }
}

elements.viewAnnotatedBtn.addEventListener("click", () => setView("annotated"));
elements.viewTableBtn.addEventListener("click", () => setView("table"));

// ==============================================================================
// 10. Copy Results to Clipboard
// ==============================================================================

let copyNoticeTimeout = null;

elements.copyBtn.addEventListener("click", async () => {
  if (!currentPredictionData || !currentPredictionData.tokens) return;

  const lines = ["Index\tToken\tLabel\tConfidence"];
  currentPredictionData.tokens.forEach((item) => {
    lines.push(
      `${item.token_index}\t${item.token}\t${item.predicted_label}\t${(item.confidence * 100).toFixed(1)}%`
    );
  });
  const tsvText = lines.join("\n");

  let success = false;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(tsvText);
      success = true;
    } catch (_) {}
  }

  // Fallback for older browsers or restricted permissions
  if (!success) {
    const tempTextarea = document.createElement("textarea");
    tempTextarea.value = tsvText;
    tempTextarea.style.position = "fixed";
    tempTextarea.style.left = "-9999px";
    document.body.appendChild(tempTextarea);
    tempTextarea.select();
    try {
      success = document.execCommand("copy");
    } catch (_) {}
    document.body.removeChild(tempTextarea);
  }

  if (success) {
    elements.copyNotice.textContent = "Results copied to clipboard!";
    elements.copyNotice.hidden = false;
    if (copyNoticeTimeout) {
      clearTimeout(copyNoticeTimeout);
    }
    copyNoticeTimeout = setTimeout(() => {
      elements.copyNotice.hidden = true;
    }, 2000);
  } else {
    showNotice("Unable to copy to clipboard. Please copy manually.", "info");
  }
});

// ==============================================================================
// 11. Initial Application Startup
// ==============================================================================

window.addEventListener("DOMContentLoaded", () => {
  handleInputChange();
  startHealthPolling();
});
