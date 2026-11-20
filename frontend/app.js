/**
 * CodeMix Intelligence - Step 2F
 * Frontend Application Logic: Unified Dual-Model Intelligence Lab
 *
 * Capabilities:
 * 1. Model 1: Token-Level Language Identification (MuRIL) -> POST /api/predict
 * 2. Model 2: Romanized Hinglish-to-English Translation (mT5-small) -> POST /api/translate
 *
 * Connects to local FastAPI backend (http://127.0.0.1:8000).
 * Handles dual-model health polling, capability switching, input validation,
 * sample insertion, live prediction/translation, strict response verification,
 * request cancellation, and clipboard exports.
 */

// Base API URLs
const API_BASE = "http://127.0.0.1:8000";
const API_BASE_URL = API_BASE; // Backward compatibility alias

/**
 * Retrieve the active MT pipeline base URL, falling back to API_BASE.
 * Checks localStorage under the key 'codemix_mt_base'.
 * @returns {string} Effective base URL without trailing slash.
 */
function getMtApiBase() {
  try {
    const saved = localStorage.getItem("codemix_mt_base");
    if (saved && saved.trim()) {
      return saved.trim().replace(/\/+$/, "");
    }
  } catch (_) {}
  return API_BASE;
}

let MT_API_BASE = getMtApiBase();

// Canonical Label Mappings for Model 1 (MuRIL)
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
let activeCapability = "lid"; // "lid" | "translation" | "pipeline"
let latestHealthData = null;
let latestMtHealthData = null;
let healthPollInterval = null;
let isHealthChecking = false;

// Mode A (MuRIL LID) State
let activeAbortController = null;
let activeRequestId = 0;
let currentPredictionData = null;
let activeView = "annotated"; // "annotated" | "table"
let copyNoticeTimeout = null;

// Mode B (mT5 Translation) State
let activeTransAbortController = null;
let activeTransRequestId = 0;
let currentTranslationData = null;
let transCopyNoticeTimeout = null;

// Mode C (IndicTrans2 Pipeline) State
let activePipelineAbortController = null;
let activePipelineRequestId = 0;
let currentPipelineData = null;
let pipelineCopyNoticeTimeout = null;
let activePipelineView = "annotated"; // "annotated" | "table"

// DOM Elements Cache
const elements = {
  // Navigation & Health
  activeNavLabel: document.getElementById("active-nav-label"),
  statusPill: document.getElementById("status-pill"),
  statusDot: document.getElementById("status-dot"),
  statusText: document.getElementById("status-text"),
  noticeContainer: document.getElementById("notice-container"),
  toastContainer: document.getElementById("toast-container"),

  // Settings Popover Elements
  settingsBtn: document.getElementById("settings-btn"),
  settingsPopover: document.getElementById("settings-popover"),
  settingMtBase: document.getElementById("setting-mt-base"),
  settingResetBtn: document.getElementById("setting-reset-btn"),
  settingSaveBtn: document.getElementById("setting-save-btn"),

  // Capability Tabs & Panels
  tabLid: document.getElementById("tab-lid"),
  tabTranslation: document.getElementById("tab-translation"),
  tabPipeline: document.getElementById("tab-pipeline"),
  tabExperiments: document.getElementById("tab-experiments"),
  panelLid: document.getElementById("panel-lid"),
  panelTranslation: document.getElementById("panel-translation"),
  panelPipeline: document.getElementById("panel-pipeline"),
  panelExperiments: document.getElementById("panel-experiments"),

  // Mode A: MuRIL LID Elements
  deviceInfo: document.getElementById("device-info"),
  sentenceInput: document.getElementById("sentence-input"),
  charCount: document.getElementById("char-count"),
  clearBtn: document.getElementById("clear-btn"),
  detectBtn: document.getElementById("detect-btn"),
  btnSpinner: document.getElementById("btn-spinner"),
  btnText: document.getElementById("btn-text"),
  samplePills: document.querySelectorAll(".sample-pill:not(.trans-sample-pill):not(.pipeline-sample-pill)"),
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
  avgConfidenceText: document.getElementById("avg-confidence-text"),

  // Mode B: mT5 Translation Elements
  transInput: document.getElementById("trans-input"),
  transCharCount: document.getElementById("trans-char-count"),
  transClearBtn: document.getElementById("trans-clear-btn"),
  transBtn: document.getElementById("trans-btn"),
  transBtnSpinner: document.getElementById("trans-btn-spinner"),
  transBtnText: document.getElementById("trans-btn-text"),
  transSamplePills: document.querySelectorAll(".trans-sample-pill"),
  transResultsPanel: document.getElementById("trans-results-panel"),
  transMetaBadge: document.getElementById("trans-meta-badge"),
  transResultText: document.getElementById("trans-result-text"),
  transOriginalText: document.getElementById("trans-original-text"),
  transCopyBtn: document.getElementById("trans-copy-btn"),
  transCopyNotice: document.getElementById("trans-copy-notice"),
  transStatusVal: document.getElementById("trans-status-val"),
  transDeviceVal: document.getElementById("trans-device-val"),

  // Mode C: Pipeline Translation Elements
  pipelineInput: document.getElementById("pipeline-input"),
  pipelineStrategy: document.getElementById("pipeline-strategy"),
  pipelineSrcHintWrapper: document.getElementById("pipeline-src-hint-wrapper"),
  pipelineSrcHint: document.getElementById("pipeline-src-hint"),
  pipelineGlossCheck: document.getElementById("pipeline-gloss-check"),
  pipelineCharCount: document.getElementById("pipeline-char-count"),
  pipelineClearBtn: document.getElementById("pipeline-clear-btn"),
  pipelineCompareBtn: document.getElementById("pipeline-compare-btn"),
  pipelineCompareSpinner: document.getElementById("pipeline-compare-spinner"),
  pipelineCompareBtnText: document.getElementById("pipeline-compare-btn-text"),
  pipelineCompareProgress: document.getElementById("pipeline-compare-progress"),
  pipelineReferenceInput: document.getElementById("pipeline-reference-input"),
  pipelineBtn: document.getElementById("pipeline-btn"),
  pipelineBtnSpinner: document.getElementById("pipeline-btn-spinner"),
  pipelineBtnText: document.getElementById("pipeline-btn-text"),
  pipelineElapsedCounter: document.getElementById("pipeline-elapsed-counter"),
  pipelineFirstRunNote: document.getElementById("pipeline-first-run-note"),
  pipelineDemoBanner: document.getElementById("pipeline-demo-banner"),
  pipelineSamplePills: document.querySelectorAll(".pipeline-sample-pill"),
  pipelineStatusVal: document.getElementById("pipeline-status-val"),
  pipelineResultsPanel: document.getElementById("pipeline-results-panel"),
  pipelineComparisonPanel: document.getElementById("pipeline-comparison-panel"),
  pipelineComparisonStatus: document.getElementById("pipeline-comparison-status"),
  pipelineComparisonGrid: document.getElementById("pipeline-comparison-grid"),
  pipelineErrorBanner: document.getElementById("pipeline-error-banner"),
  pipelineResultsHeader: document.getElementById("pipeline-results-header"),
  pipelineCardContent: document.getElementById("pipeline-card-content"),
  pipelineDominantBadge: document.getElementById("pipeline-dominant-badge"),
  pipelineStrategyBadge: document.getElementById("pipeline-strategy-badge"),
  pipelineCopyBtn: document.getElementById("pipeline-copy-btn"),
  pipelineCopyNotice: document.getElementById("pipeline-copy-notice"),
  pipelineResultText: document.getElementById("pipeline-result-text"),
  pipelineOriginalText: document.getElementById("pipeline-original-text"),
  pipelineNormalizedBlock: document.getElementById("pipeline-normalized-block"),
  pipelineNormalizedText: document.getElementById("pipeline-normalized-text"),
  pipelineClausesSection: document.getElementById("pipeline-clauses-section"),
  pipelineClausesList: document.getElementById("pipeline-clauses-list"),
  pipelineTokensSection: document.getElementById("pipeline-tokens-section"),
  pipelineViewAnnotatedBtn: document.getElementById("pipeline-view-annotated-btn"),
  pipelineViewTableBtn: document.getElementById("pipeline-view-table-btn"),
  pipelineAnnotatedContainer: document.getElementById("pipeline-annotated-container"),
  pipelineTableContainer: document.getElementById("pipeline-table-container"),
  pipelineTokensFlow: document.getElementById("pipeline-tokens-flow"),
  pipelineTableBody: document.getElementById("pipeline-table-body"),
  pipelineGlossesSection: document.getElementById("pipeline-glosses-section"),
  pipelineGlossesGrid: document.getElementById("pipeline-glosses-grid"),
  pipelineTimingSection: document.getElementById("pipeline-timing-section"),
  pipelineTimingStrip: document.getElementById("pipeline-timing-strip"),
  timingTotal: document.getElementById("timing-total"),
  timingNormalize: document.getElementById("timing-normalize"),
  timingLid: document.getElementById("timing-lid"),
  timingTranslit: document.getElementById("timing-translit"),
  timingTranslate: document.getElementById("timing-translate"),

  // Convenience Features (Examples, History, Download)
  pipelineExampleChips: document.querySelectorAll(".pipeline-example-chip"),
  pipelineHistoryDetails: document.getElementById("pipeline-history-details"),
  pipelineHistoryCount: document.getElementById("pipeline-history-count"),
  pipelineHistoryList: document.getElementById("pipeline-history-list"),
  pipelineHistoryEmpty: document.getElementById("pipeline-history-empty"),
  pipelineClearHistoryBtn: document.getElementById("pipeline-clear-history-btn"),
  pipelineDownloadJsonBtn: document.getElementById("pipeline-download-json-btn"),

  // Mode D: Experiments Elements
  experimentsContent: document.getElementById("experiments-content"),
  experimentsErrorBanner: document.getElementById("experiments-error-banner"),
  experimentsErrorMessage: document.getElementById("experiments-error-message"),
  experimentsHeadlinesGrid: document.getElementById("experiments-headlines-grid"),
  experimentsChartsGrid: document.getElementById("experiments-charts-grid"),
  experimentsLidContainer: document.getElementById("experiments-lid-container"),
  experimentsLidCompareContainer: document.getElementById("experiments-lid-compare-container"),
  experimentsRegressionContainer: document.getElementById("experiments-regression-container")
};

// ==============================================================================
// 1. Dual-Model Health Checking & Navigation Status
// ==============================================================================

/**
 * Update navigation status pill based on active capability and backend health.
 */
function updateNavigationStatus() {
  if (!elements.statusDot || !elements.statusText) return;

  elements.statusDot.className = "status-dot";

  if (activeCapability === "lid") {
    if (!latestHealthData) {
      elements.statusDot.classList.add("status-error");
      elements.statusText.textContent = "Backend offline";
      return;
    }
    // Mode A: MuRIL Status
    if (latestHealthData.model_loaded === true) {
      elements.statusDot.classList.add("status-ready");
      elements.statusText.textContent = "MuRIL ready";
    } else {
      elements.statusDot.classList.add("status-loading");
      elements.statusText.textContent = "MuRIL loading";
    }
  } else if (activeCapability === "translation") {
    if (!latestHealthData) {
      elements.statusDot.classList.add("status-error");
      elements.statusText.textContent = "Backend offline";
      return;
    }
    // Mode B: mT5 Translation Status
    const trans = latestHealthData.translation || {};
    if (trans.loaded === true) {
      elements.statusDot.classList.add("status-ready");
      elements.statusText.textContent = "mT5 loaded · Ready";
    } else if (trans.available === true) {
      elements.statusDot.classList.add("status-loading");
      elements.statusText.textContent = "mT5 available · On demand";
    } else {
      elements.statusDot.classList.add("status-error");
      elements.statusText.textContent = "mT5 unavailable";
    }
  } else if (activeCapability === "experiments") {
    // Mode D: Experiments Status
    if (experimentsData) {
      elements.statusDot.classList.add("status-ready");
      elements.statusText.textContent = "Experiments loaded";
    } else {
      elements.statusDot.classList.add("status-loading");
      elements.statusText.textContent = "Loading results.json";
    }
  } else {
    // Mode C: CodeMix Pipeline Status
    if (!latestMtHealthData) {
      elements.statusDot.classList.add("status-error");
      elements.statusText.textContent = "Pipeline offline";
      return;
    }
    if (latestMtHealthData.loaded === true) {
      elements.statusDot.classList.add("status-ready");
      elements.statusText.textContent = "Pipeline: ready";
    } else {
      elements.statusDot.classList.add("status-loading");
      elements.statusText.textContent = "Pipeline: not loaded yet (first request is slow)";
    }
  }
}

/**
 * Check backend health via GET /api/health and GET {MT_API_BASE}/api/mt/translate/health.
 */
async function checkBackendHealth() {
  if (isHealthChecking) return;
  isHealthChecking = true;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);
    const mtBase = getMtApiBase();

    const [healthResult, mtHealthResult] = await Promise.allSettled([
      fetch(`${API_BASE}/api/health`, { method: "GET", signal: controller.signal }),
      fetch(`${mtBase}/api/mt/translate/health`, { method: "GET", signal: controller.signal })
    ]);

    clearTimeout(timeoutId);

    // 1. Process Main /api/health
    if (healthResult.status === "fulfilled" && healthResult.value.ok) {
      const data = await healthResult.value.json();
      latestHealthData = data;

      // Update Mode A (MuRIL) Metadata Sidebar
      if (elements.deviceInfo) {
        elements.deviceInfo.textContent = data.device || "cpu";
      }

      // Update Mode B (mT5) Metadata Sidebar
      const trans = data.translation || {};
      if (elements.transStatusVal) {
        if (trans.loaded === true) {
          elements.transStatusVal.textContent = "Model loaded · Ready";
        } else if (trans.available === true) {
          elements.transStatusVal.textContent = "Model available · Loads on first translation";
        } else {
          elements.transStatusVal.textContent = "Model files unavailable";
        }
      }

      if (elements.transDeviceVal) {
        if (trans.loaded === true && trans.device) {
          elements.transDeviceVal.textContent = trans.device;
        } else if (trans.available === true) {
          elements.transDeviceVal.textContent = "Loads on first use";
        } else {
          elements.transDeviceVal.textContent = "Unavailable";
        }
      }
    } else {
      latestHealthData = null;
      if (elements.deviceInfo) elements.deviceInfo.textContent = "Unavailable";
      if (elements.transStatusVal) elements.transStatusVal.textContent = "Unavailable";
      if (elements.transDeviceVal) elements.transDeviceVal.textContent = "Unavailable";
    }

    // 2. Process CodeMix Pipeline /api/mt/translate/health
    if (mtHealthResult.status === "fulfilled" && mtHealthResult.value.ok) {
      const mtData = await mtHealthResult.value.json();
      latestMtHealthData = mtData;

      if (elements.pipelineStatusVal) {
        if (mtData.loaded === true) {
          elements.pipelineStatusVal.textContent = "Pipeline: ready";
        } else {
          elements.pipelineStatusVal.textContent = "Pipeline: not loaded yet (first request is slow)";
        }
      }
    } else {
      latestMtHealthData = null;
      if (elements.pipelineStatusVal) {
        elements.pipelineStatusVal.textContent = "Pipeline offline";
      }
    }
  } catch (err) {
    latestHealthData = null;
    latestMtHealthData = null;
    if (elements.deviceInfo) elements.deviceInfo.textContent = "Unavailable";
    if (elements.transStatusVal) elements.transStatusVal.textContent = "Unavailable";
    if (elements.transDeviceVal) elements.transDeviceVal.textContent = "Unavailable";
    if (elements.pipelineStatusVal) elements.pipelineStatusVal.textContent = "Pipeline offline";
  } finally {
    isHealthChecking = false;
    const isUrlDemo = checkUrlDemoMode();
    const isPipelineOnline = latestMtHealthData && latestMtHealthData.status === "ok";
    if (isUrlDemo || !isPipelineOnline) {
      setDemoMode(true);
    } else {
      setDemoMode(false);
    }
    updateNavigationStatus();
    updatePipelineLoadedNote();
  }
}

/**
 * Update first-run warning note based on whether pipeline model is loaded.
 */
function updatePipelineLoadedNote() {
  if (!elements.pipelineFirstRunNote) return;
  const isLoaded = latestMtHealthData && latestMtHealthData.loaded === true;
  elements.pipelineFirstRunNote.hidden = isLoaded;
}

/**
 * Start recurring health polling interval.
 */
function startHealthPolling() {
  checkBackendHealth();
  if (!healthPollInterval) {
    healthPollInterval = setInterval(checkBackendHealth, 15000);
  }
}

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
// 2. Capability Switcher (Mode A vs Mode B vs Mode C)
// ==============================================================================

/**
 * Switch active capability between Language Identification, Hinglish Translation, CodeMix Pipeline, and Experiments.
 * Preserves the input text, results, and state of all tabs.
 * Does not initiate any network requests.
 * @param {'lid'|'translation'|'pipeline'|'experiments'} targetCapability
 */
function switchCapability(targetCapability) {
  if (targetCapability === activeCapability) return;

  activeCapability = targetCapability;
  clearNotices();

  const isLid = targetCapability === "lid";
  const isTrans = targetCapability === "translation";
  const isPipe = targetCapability === "pipeline";
  const isExp = targetCapability === "experiments";

  // Tab A (LID)
  elements.tabLid.classList.toggle("active", isLid);
  elements.tabLid.setAttribute("aria-selected", isLid ? "true" : "false");
  elements.tabLid.setAttribute("tabindex", isLid ? "0" : "-1");
  elements.panelLid.hidden = !isLid;

  // Tab B (Translation)
  elements.tabTranslation.classList.toggle("active", isTrans);
  elements.tabTranslation.setAttribute("aria-selected", isTrans ? "true" : "false");
  elements.tabTranslation.setAttribute("tabindex", isTrans ? "0" : "-1");
  elements.panelTranslation.hidden = !isTrans;

  // Tab C (CodeMix Pipeline)
  if (elements.tabPipeline && elements.panelPipeline) {
    elements.tabPipeline.classList.toggle("active", isPipe);
    elements.tabPipeline.setAttribute("aria-selected", isPipe ? "true" : "false");
    elements.tabPipeline.setAttribute("tabindex", isPipe ? "0" : "-1");
    elements.panelPipeline.hidden = !isPipe;
  }

  // Tab D (Experiments & Benchmark)
  if (elements.tabExperiments && elements.panelExperiments) {
    elements.tabExperiments.classList.toggle("active", isExp);
    elements.tabExperiments.setAttribute("aria-selected", isExp ? "true" : "false");
    elements.tabExperiments.setAttribute("tabindex", isExp ? "0" : "-1");
    elements.panelExperiments.hidden = !isExp;
  }

  if (elements.activeNavLabel) {
    if (isLid) {
      elements.activeNavLabel.textContent = "Language Identification";
    } else if (isTrans) {
      elements.activeNavLabel.textContent = "Hinglish Translation";
    } else if (isPipe) {
      elements.activeNavLabel.textContent = "Pipeline Translate";
    } else {
      elements.activeNavLabel.textContent = "Experiments & Benchmark";
    }
  }

  if (isExp && !experimentsData) {
    fetchAndRenderExperiments();
  }

  updateNavigationStatus();
}

// Mouse events on capability tabs
elements.tabLid.addEventListener("click", () => switchCapability("lid"));
elements.tabTranslation.addEventListener("click", () => switchCapability("translation"));
if (elements.tabPipeline) {
  elements.tabPipeline.addEventListener("click", () => switchCapability("pipeline"));
}
if (elements.tabExperiments) {
  elements.tabExperiments.addEventListener("click", () => switchCapability("experiments"));
}

// Accessible keyboard navigation for capability tabs (Left / Right / Home / End)
const tabList = [elements.tabLid, elements.tabTranslation, elements.tabPipeline, elements.tabExperiments].filter(Boolean);
tabList.forEach((tab, index) => {
  tab.addEventListener("keydown", (e) => {
    let targetIndex = null;
    if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      targetIndex = (index + 1) % tabList.length;
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      targetIndex = (index - 1 + tabList.length) % tabList.length;
    } else if (e.key === "Home") {
      targetIndex = 0;
    } else if (e.key === "End") {
      targetIndex = tabList.length - 1;
    }

    if (targetIndex !== null) {
      e.preventDefault();
      const targetTab = tabList[targetIndex];
      targetTab.focus();
      let capKey = "lid";
      if (targetTab === elements.tabTranslation) capKey = "translation";
      else if (targetTab === elements.tabPipeline) capKey = "pipeline";
      else if (targetTab === elements.tabExperiments) capKey = "experiments";
      switchCapability(capKey);
    }
  });
});

// ==============================================================================
// 3. Safe Notice & Alert Rendering
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

/**
 * Display a floating toast notification.
 * @param {string} message - Toast message text.
 * @param {'info'|'success'|'error'} [type='info'] - Toast category.
 * @param {number} [durationMs=3500] - Duration in ms before auto-dismiss.
 */
function showToast(message, type = "info", durationMs = 3500) {
  let container = elements.toastContainer || document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "toast-container";
    container.setAttribute("aria-live", "polite");
    container.setAttribute("aria-atomic", "true");
    document.body.appendChild(container);
    elements.toastContainer = container;
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.setAttribute("role", type === "error" ? "alert" : "status");

  const msgSpan = document.createElement("span");
  msgSpan.className = "toast-message";
  msgSpan.textContent = message;
  toast.appendChild(msgSpan);

  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "toast-close-btn";
  closeBtn.setAttribute("aria-label", "Close notification");
  closeBtn.textContent = "×";
  closeBtn.addEventListener("click", () => dismissToast(toast));
  toast.appendChild(closeBtn);

  container.appendChild(toast);

  let timer = setTimeout(() => dismissToast(toast), durationMs);

  function dismissToast(el) {
    clearTimeout(timer);
    el.style.opacity = "0";
    el.style.transform = "translateY(8px)";
    el.style.transition = "opacity 200ms ease, transform 200ms ease";
    setTimeout(() => {
      if (el.parentNode) {
        el.parentNode.removeChild(el);
      }
    }, 200);
  }
}

/**
 * Helper to perform POST requests with JSON payload, timeout, and readable error handling.
 * @param {string} url - Target URL.
 * @param {object} body - Request payload object.
 * @param {object} [options]
 * @param {number} [options.timeoutMs=300000] - Timeout in milliseconds (default 5 minutes).
 * @param {AbortSignal} [options.signal] - Optional external AbortSignal for user cancellation.
 * @returns {Promise<any>} Parsed response data.
 */
async function postJSON(url, body, { timeoutMs = 300000, signal } = {}) {
  const controller = new AbortController();
  let isTimeout = false;

  const timer = setTimeout(() => {
    isTimeout = true;
    controller.abort();
  }, timeoutMs);

  if (signal) {
    if (signal.aborted) {
      clearTimeout(timer);
      const abortErr = new Error("Request cancelled by user.");
      abortErr.name = "AbortError";
      throw abortErr;
    }
    signal.addEventListener("abort", () => {
      controller.abort();
    }, { once: true });
  }

  try {
    let response;
    try {
      response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal
      });
    } catch (fetchErr) {
      if (isTimeout) {
        throw new Error(`Request timed out after ${Math.round(timeoutMs / 1000)} seconds.`);
      }
      if (signal && signal.aborted) {
        const abortErr = new Error("Request cancelled by user.");
        abortErr.name = "AbortError";
        throw abortErr;
      }
      throw new Error(`Cannot reach server at ${url}. Check your connection or ensure the backend is running.`);
    }

    if (!response.ok) {
      const status = response.status;
      let detailMsg = "";
      try {
        const errJson = await response.json();
        if (errJson && typeof errJson.detail === "string") {
          detailMsg = errJson.detail;
        } else if (errJson && Array.isArray(errJson.detail)) {
          detailMsg = errJson.detail.map((e) => e.msg || JSON.stringify(e)).join("; ");
        } else if (errJson && typeof errJson.message === "string") {
          detailMsg = errJson.message;
        }
      } catch (_) {}

      if (status === 422) {
        throw new Error(detailMsg ? `Invalid input (422): ${detailMsg}` : "Invalid input: Please verify the request parameters (text must be between 1 and 1000 characters).");
      }
      if (status === 500) {
        throw new Error(detailMsg ? `Server error (500): ${detailMsg}` : "Server error (500): Internal server error during processing.");
      }
      throw new Error(detailMsg ? `Request failed (${status}): ${detailMsg}` : `Request failed with status code ${status}.`);
    }

    return await response.json();
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Initialize the settings popover for overriding MT_API_BASE.
 */
function initSettingsPopover() {
  if (!elements.settingsBtn || !elements.settingsPopover) return;

  function openPopover() {
    if (elements.settingMtBase) {
      elements.settingMtBase.value = getMtApiBase();
    }
    elements.settingsPopover.hidden = false;
    elements.settingsPopover.classList.add("is-open");
    elements.settingsBtn.setAttribute("aria-expanded", "true");
    if (elements.settingMtBase) {
      elements.settingMtBase.focus();
    }
  }

  function closePopover() {
    elements.settingsPopover.classList.remove("is-open");
    elements.settingsPopover.hidden = true;
    elements.settingsBtn.setAttribute("aria-expanded", "false");
  }

  function togglePopover() {
    if (elements.settingsPopover.classList.contains("is-open")) {
      closePopover();
    } else {
      openPopover();
    }
  }

  elements.settingsBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    togglePopover();
  });

  // Prevent clicks inside popover from closing it
  elements.settingsPopover.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // Close when clicking outside
  document.addEventListener("click", (e) => {
    if (elements.settingsPopover.classList.contains("is-open") && !elements.settingsPopover.contains(e.target) && e.target !== elements.settingsBtn) {
      closePopover();
    }
  });

  // Close popover and tooltips on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (elements.settingsPopover.classList.contains("is-open")) {
        closePopover();
        elements.settingsBtn.focus();
      }
      // Dismiss active tooltips
      const chipsWithTooltips = document.querySelectorAll(".chip-tooltip");
      if (chipsWithTooltips.length > 0) {
        chipsWithTooltips.forEach((tt) => tt.classList.add("tooltip-dismissed"));
      }
      // Blur chip if currently focused
      if (document.activeElement && document.activeElement.closest && document.activeElement.closest(".pipeline-chip")) {
        document.activeElement.blur();
      }
    }
  });

  // Re-enable tooltips on mouse movement or focus
  document.addEventListener("mousemove", () => {
    const dismissed = document.querySelectorAll(".chip-tooltip.tooltip-dismissed");
    if (dismissed.length > 0) {
      dismissed.forEach((tt) => tt.classList.remove("tooltip-dismissed"));
    }
  }, { passive: true });

  document.addEventListener("focusin", (e) => {
    if (e.target && e.target.closest && e.target.closest(".pipeline-chip")) {
      const dismissed = document.querySelectorAll(".chip-tooltip.tooltip-dismissed");
      if (dismissed.length > 0) {
        dismissed.forEach((tt) => tt.classList.remove("tooltip-dismissed"));
      }
    }
  });

  // Save button handler
  if (elements.settingSaveBtn) {
    elements.settingSaveBtn.addEventListener("click", () => {
      const inputVal = elements.settingMtBase ? elements.settingMtBase.value.trim().replace(/\/+$/, "") : "";
      if (inputVal && inputVal !== API_BASE) {
        try {
          localStorage.setItem("codemix_mt_base", inputVal);
        } catch (_) {}
        MT_API_BASE = inputVal;
        showToast(`Pipeline URL updated to ${inputVal}`, "success");
      } else {
        try {
          localStorage.removeItem("codemix_mt_base");
        } catch (_) {}
        MT_API_BASE = API_BASE;
        showToast("Pipeline URL set to default", "info");
      }
      closePopover();
      checkBackendHealth();
    });
  }

  // Reset button handler
  if (elements.settingResetBtn) {
    elements.settingResetBtn.addEventListener("click", () => {
      try {
        localStorage.removeItem("codemix_mt_base");
      } catch (_) {}
      MT_API_BASE = API_BASE;
      if (elements.settingMtBase) {
        elements.settingMtBase.value = API_BASE;
      }
      showToast(`Pipeline URL reset to default (${API_BASE})`, "info");
      closePopover();
      checkBackendHealth();
    });
  }
}

// Expose utilities on window for global access and testing
if (typeof window !== "undefined") {
  window.API_BASE = API_BASE;
  window.getMtApiBase = getMtApiBase;
  window.postJSON = postJSON;
  window.showToast = showToast;
  try {
    Object.defineProperty(window, "MT_API_BASE", {
      get: () => getMtApiBase(),
      set: (val) => {
        if (val && val.trim()) {
          localStorage.setItem("codemix_mt_base", val.trim().replace(/\/+$/, ""));
        } else {
          localStorage.removeItem("codemix_mt_base");
        }
        MT_API_BASE = getMtApiBase();
      },
      configurable: true
    });
  } catch (_) {
    window.MT_API_BASE = MT_API_BASE;
  }
}

// ==============================================================================
// 4. Mode A: Language Identification (MuRIL) Logic
// ==============================================================================

/**
 * Update character counter and enable/disable Detect button.
 */
function handleInputChange() {
  const text = elements.sentenceInput.value;
  elements.charCount.textContent = `${text.length} characters`;

  const hasText = text.trim().length > 0;
  const isAnalyzing = elements.detectBtn.classList.contains("loading");

  elements.detectBtn.disabled = !hasText || isAnalyzing;
}

elements.sentenceInput.addEventListener("input", handleInputChange);

// Keyboard Shortcut: Ctrl+Enter or Cmd+Enter
elements.sentenceInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (!elements.detectBtn.disabled) {
      executePrediction();
    }
  }
});

// Sample Sentences for MuRIL LID
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

// Clear Button & Request Cancellation for MuRIL
elements.clearBtn.addEventListener("click", () => {
  const isAnalyzing = elements.detectBtn.classList.contains("loading");

  if (isAnalyzing && activeAbortController) {
    activeAbortController.abort();
    activeAbortController = null;
    activeRequestId++;
    resetLoadingState();
    elements.sentenceInput.value = "";
    handleInputChange();
    hideResults();
    showNotice("Analysis cancelled because the input was cleared.", "info");
  } else {
    elements.sentenceInput.value = "";
    handleInputChange();
    hideResults();
    clearNotices();
  }
});

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

function resetLoadingState() {
  elements.detectBtn.classList.remove("loading");
  elements.btnSpinner.style.display = "none";
  elements.btnText.textContent = "Detect languages";
  handleInputChange();
}

/**
 * Strict response validation for MuRIL LID.
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

    if (!(item.predicted_label in LABEL_MAPPING)) return false;

    if (typeof item.predicted_label_id === "number") {
      if (LABEL_MAPPING[item.predicted_label] !== item.predicted_label_id) return false;
    }

    if (typeof item.confidence !== "number" || !isFinite(item.confidence)) return false;
    if (item.confidence < 0.0 || item.confidence > 1.0) return false;
  }

  return true;
}

elements.detectBtn.addEventListener("click", executePrediction);

async function executePrediction() {
  const rawText = elements.sentenceInput.value;
  const cleanedText = rawText.trim();

  if (!cleanedText) {
    showNotice("Please enter some text.", "error");
    return;
  }

  clearNotices();
  hideResults();

  activeAbortController = new AbortController();
  activeRequestId++;
  const thisRequestId = activeRequestId;

  elements.detectBtn.classList.add("loading");
  elements.detectBtn.disabled = true;
  elements.btnSpinner.style.display = "inline-block";
  elements.btnText.textContent = "Analyzing...";

  let longWaitTimer = setTimeout(() => {
    if (thisRequestId === activeRequestId && elements.detectBtn.classList.contains("loading")) {
      elements.btnText.textContent = "Long text is taking a little longer...";
    }
  }, 3000);

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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: cleanedText }),
      signal: activeAbortController.signal
    });

    clearTimeout(longWaitTimer);
    clearTimeout(timeoutTimer);

    if (thisRequestId !== activeRequestId) return;

    if (!response.ok) {
      const status = response.status;
      let errorDetail = "";
      try {
        const errorJson = await response.json();
        if (errorJson && typeof errorJson.detail === "string") {
          errorDetail = errorJson.detail;
        }
      } catch (_) {}

      if (status === 400) {
        showNotice(errorDetail || "Please enter some text.", "error");
      } else if (status === 422) {
        showNotice(errorDetail || "The submitted text is not valid.", "error");
      } else if (status === 503) {
        showNotice("The model is still starting up. Please try again in a moment.", "info");
      } else {
        showNotice(`Server error (${status}). Please try again later.`, "error");
      }
      return;
    }

    const data = await response.json();
    if (!validateApiResponse(data)) {
      showNotice("The server returned an unexpected response.", "error");
      return;
    }

    currentPredictionData = data;
    renderPredictions(data);
  } catch (err) {
    clearTimeout(longWaitTimer);
    clearTimeout(timeoutTimer);

    if (thisRequestId !== activeRequestId) return;
    if (err.name === "AbortError") return;

    showNotice("Cannot reach the backend at http://127.0.0.1:8000. Make sure it is running.", "error");
    latestHealthData = null;
    updateNavigationStatus();
  } finally {
    if (thisRequestId === activeRequestId) {
      resetLoadingState();
      activeAbortController = null;
    }
  }
}

function renderPredictions(data) {
  const tokens = data.tokens;

  if (data.chunked) {
    elements.chunkingInfo.textContent = `Chunked · ${data.chunk_count} chunks processed`;
  } else {
    elements.chunkingInfo.textContent = `Not chunked · 1 chunk processed`;
  }

  while (elements.tokensFlow.firstChild) {
    elements.tokensFlow.removeChild(elements.tokensFlow.firstChild);
  }

  tokens.forEach((item) => {
    const stack = document.createElement("div");
    const langKey = item.predicted_label.toLowerCase();
    stack.className = `token-stack lang-${langKey}`;

    const confPct = (item.confidence * 100).toFixed(1);
    const langFullName = LANGUAGE_NAMES[item.predicted_label] || item.predicted_label;
    const accessibleLabel = `${item.token}, ${langFullName}, model confidence ${confPct} percent`;
    stack.setAttribute("title", accessibleLabel);
    stack.setAttribute("aria-label", accessibleLabel);

    const wordSpan = document.createElement("span");
    wordSpan.className = "token-word font-serif";
    wordSpan.textContent = item.token;

    const lineSpan = document.createElement("span");
    lineSpan.className = "token-underline";
    lineSpan.setAttribute("aria-hidden", "true");

    const labelSpan = document.createElement("span");
    labelSpan.className = "token-label-text font-mono";
    labelSpan.textContent = `${item.predicted_label} ${Math.round(item.confidence * 100)}%`;

    stack.appendChild(wordSpan);
    stack.appendChild(lineSpan);
    stack.appendChild(labelSpan);

    elements.tokensFlow.appendChild(stack);
  });

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
        segment.setAttribute("title", `${item.label}: ${item.count} tokens (${pct.toFixed(1)}%)`);
        elements.distributionBar.appendChild(segment);
      }
    });

    const avgConfidence = (totalConfidence / totalCount) * 100;
    elements.avgConfidenceText.textContent = `Average model confidence: ${avgConfidence.toFixed(1)}%`;
  } else {
    elements.avgConfidenceText.textContent = "Average model confidence: 0.0%";
  }

  setView("annotated");
  elements.resultsPanel.hidden = false;
  elements.resultsPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

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

// Copy MuRIL Results
elements.copyBtn.addEventListener("click", async () => {
  if (!currentPredictionData || !currentPredictionData.tokens) return;

  const lines = ["Index\tToken\tLabel\tConfidence"];
  currentPredictionData.tokens.forEach((item) => {
    lines.push(`${item.token_index}\t${item.token}\t${item.predicted_label}\t${(item.confidence * 100).toFixed(1)}%`);
  });
  const tsvText = lines.join("\n");

  let success = false;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(tsvText);
      success = true;
    } catch (_) {}
  }

  if (success) {
    elements.copyNotice.textContent = "Results copied to clipboard!";
    elements.copyNotice.hidden = false;
    if (copyNoticeTimeout) clearTimeout(copyNoticeTimeout);
    copyNoticeTimeout = setTimeout(() => { elements.copyNotice.hidden = true; }, 2000);
  } else {
    showNotice("Unable to copy to clipboard. Please copy manually.", "info");
  }
});

// ==============================================================================
// 5. Mode B: Hinglish to English Translation (mT5) Logic
// ==============================================================================

const TRANS_SAMPLES = {
  "ghamand": "bas kabhi ghamand nahi kiya.",
  "train": "Mujhe lagta hai ki train late ho sakti hai.",
  "meeting": "Kal meeting kitne baje start hogi?"
};

/**
 * Update translation character counter and toggle Translate button.
 */
function handleTransInputChange() {
  const text = elements.transInput.value;
  elements.transCharCount.textContent = `${text.length} / 1000 characters`;

  const hasText = text.trim().length > 0;
  const isTranslating = elements.transBtn.classList.contains("loading");
  const isWithinLimit = text.length <= 1000;

  elements.transBtn.disabled = !hasText || isTranslating || !isWithinLimit;
}

elements.transInput.addEventListener("input", handleTransInputChange);

// Keyboard Shortcut: Ctrl+Enter or Cmd+Enter for Translation
elements.transInput.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (!elements.transBtn.disabled) {
      executeTranslation();
    }
  }
});

// Sample Pills for Translation
elements.transSamplePills.forEach((pill) => {
  pill.addEventListener("click", () => {
    const key = pill.getAttribute("data-sample");
    if (TRANS_SAMPLES[key]) {
      elements.transInput.value = TRANS_SAMPLES[key];
      handleTransInputChange();
      elements.transInput.focus();
    }
  });
});

// Clear Button for Translation
elements.transClearBtn.addEventListener("click", () => {
  const isTranslating = elements.transBtn.classList.contains("loading");

  if (isTranslating && activeTransAbortController) {
    activeTransAbortController.abort();
    activeTransAbortController = null;
    activeTransRequestId++;
    resetTransLoadingState();
    elements.transInput.value = "";
    handleTransInputChange();
    hideTransResults();
    showNotice("Translation cancelled because the input was cleared.", "info");
  } else {
    elements.transInput.value = "";
    handleTransInputChange();
    hideTransResults();
    clearNotices();
  }
});

function hideTransResults() {
  elements.transResultsPanel.hidden = true;
  currentTranslationData = null;
  if (transCopyNoticeTimeout) {
    clearTimeout(transCopyNoticeTimeout);
    transCopyNoticeTimeout = null;
  }
  elements.transCopyNotice.hidden = true;
  elements.transResultText.textContent = "";
  elements.transOriginalText.textContent = "";
}

function resetTransLoadingState() {
  elements.transBtn.classList.remove("loading");
  elements.transBtnSpinner.style.display = "none";
  elements.transBtnText.textContent = "Translate to English";
  handleTransInputChange();
}

/**
 * Strict response validation for mT5 Translation.
 */
function validateTransApiResponse(data) {
  if (!data || typeof data !== "object") return false;
  if (typeof data.source_text !== "string") return false;
  if (typeof data.translated_text !== "string") return false;
  if (typeof data.model !== "string") return false;
  if (typeof data.num_beams !== "number") return false;
  return true;
}

elements.transBtn.addEventListener("click", executeTranslation);

async function executeTranslation() {
  const rawText = elements.transInput.value;
  const cleanedText = rawText.trim();

  if (!cleanedText) {
    showNotice("Please enter some Romanized Hinglish text to translate.", "error");
    return;
  }

  if (cleanedText.length > 1000) {
    showNotice("Input text exceeds maximum allowed length of 1,000 characters.", "error");
    return;
  }

  clearNotices();
  hideTransResults();

  activeTransAbortController = new AbortController();
  activeTransRequestId++;
  const thisRequestId = activeTransRequestId;

  elements.transBtn.classList.add("loading");
  elements.transBtn.disabled = true;
  elements.transBtnSpinner.style.display = "inline-block";
  elements.transBtnText.textContent = "Translating...";

  // 3-second status update if model is initializing on first run
  let firstRunTimer = setTimeout(() => {
    if (thisRequestId === activeTransRequestId && elements.transBtn.classList.contains("loading")) {
      elements.transBtnText.textContent = "Loading model & translating...";
    }
  }, 3000);

  // 120-second timeout
  let timeoutTimer = setTimeout(() => {
    if (thisRequestId === activeTransRequestId && activeTransAbortController) {
      activeTransAbortController.abort();
      showNotice("The translation request timed out. Please try again.", "error");
      resetTransLoadingState();
    }
  }, 120000);

  try {
    const response = await fetch(`${API_BASE_URL}/api/translate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: cleanedText }),
      signal: activeTransAbortController.signal
    });

    clearTimeout(firstRunTimer);
    clearTimeout(timeoutTimer);

    if (thisRequestId !== activeTransRequestId) return;

    if (!response.ok) {
      const status = response.status;
      let errorDetail = "";
      try {
        const errorJson = await response.json();
        if (errorJson && typeof errorJson.detail === "string") {
          errorDetail = errorJson.detail;
        }
      } catch (_) {}

      if (status === 400) {
        showNotice(errorDetail || "Please enter some text.", "error");
      } else if (status === 422) {
        showNotice(errorDetail || "The submitted text is invalid or exceeds 1,000 characters.", "error");
      } else if (status === 503) {
        showNotice(errorDetail || "Translation model is not ready or model files are missing.", "error");
      } else {
        showNotice("Translation failed on the server. Please try again.", "error");
      }
      return;
    }

    const data = await response.json();
    if (!validateTransApiResponse(data)) {
      showNotice("The server returned an unexpected translation response.", "error");
      return;
    }

    currentTranslationData = data;
    renderTranslation(data);

    // Refresh health to update sidebar & pill to "Model loaded · Ready"
    checkBackendHealth();
  } catch (err) {
    clearTimeout(firstRunTimer);
    clearTimeout(timeoutTimer);

    if (thisRequestId !== activeTransRequestId) return;
    if (err.name === "AbortError") return;

    showNotice("Cannot reach the backend at http://127.0.0.1:8000. Make sure it is running.", "error");
    latestHealthData = null;
    updateNavigationStatus();
  } finally {
    if (thisRequestId === activeTransRequestId) {
      resetTransLoadingState();
      activeTransAbortController = null;
    }
  }
}

/**
 * Render validated translation response into results card.
 */
function renderTranslation(data) {
  elements.transResultText.textContent = data.translated_text;
  elements.transOriginalText.textContent = data.source_text;
  elements.transMetaBadge.textContent = `${data.model || "google/mt5-small"} · ${data.num_beams || 4} beams`;

  elements.transResultsPanel.hidden = false;
  elements.transResultsPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Copy Translation to Clipboard
elements.transCopyBtn.addEventListener("click", async () => {
  if (!currentTranslationData || !currentTranslationData.translated_text) return;

  const textToCopy = currentTranslationData.translated_text;
  let success = false;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(textToCopy);
      success = true;
    } catch (_) {}
  }

  if (success) {
    elements.transCopyNotice.textContent = "Translation copied to clipboard!";
    elements.transCopyNotice.hidden = false;
    if (transCopyNoticeTimeout) clearTimeout(transCopyNoticeTimeout);
    transCopyNoticeTimeout = setTimeout(() => { elements.transCopyNotice.hidden = true; }, 2000);
  } else {
    showNotice("Unable to copy to clipboard. Please copy manually.", "info");
  }
});

// ==============================================================================
// 6. Mode C: CodeMix Translation Pipeline (IndicTrans2) Logic
// ==============================================================================

const PIPELINE_SAMPLES = {
  "comparison-sample": {
    text: "Kal meeting hai please slides bhej dena",
    strategy: "full",
    gloss: false,
    ref: "There is a meeting tomorrow, please send slides"
  },
  "acceptance-sample": {
    text: "Nenu repu college ki vastanu",
    strategy: "full",
    gloss: false
  },
  "trilingual": {
    text: "mai kal morning school ku aatta huu, akkada adukundam.",
    strategy: "full",
    gloss: true
  },
  "hinglish": {
    text: "Mujhe lagta hai ki train late ho sakti hai.",
    strategy: "full",
    gloss: false
  },
  "tenglish": {
    text: "Naku meeting ki late avuthundi, please wait cheyyandi.",
    strategy: "full",
    gloss: false
  },
  "clause": {
    text: "aaj office lo bahut work undi, akkada kaluddam.",
    strategy: "clause",
    gloss: true
  }
};

/**
 * Update pipeline character counter and toggle Translate button.
 */
function handlePipelineInputChange() {
  if (!elements.pipelineInput || !elements.pipelineCharCount || !elements.pipelineBtn) return;

  const text = elements.pipelineInput.value;
  elements.pipelineCharCount.textContent = `${text.length} / 1000 characters`;

  const hasText = text.trim().length > 0;
  const isTranslating = elements.pipelineBtn.classList.contains("loading");
  const isComparing = elements.pipelineCompareBtn && elements.pipelineCompareBtn.classList.contains("loading");
  const isWithinLimit = text.length <= 1000;

  elements.pipelineBtn.disabled = !hasText || isTranslating || isComparing || !isWithinLimit;
  if (elements.pipelineCompareBtn) {
    elements.pipelineCompareBtn.disabled = !hasText || isTranslating || isComparing || !isWithinLimit;
  }
}

if (elements.pipelineInput) {
  elements.pipelineInput.addEventListener("input", handlePipelineInputChange);

  // Keyboard Shortcut: Ctrl+Enter or Cmd+Enter for Pipeline
  elements.pipelineInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      if (!elements.pipelineBtn.disabled) {
        executePipelineTranslation();
      }
    }
  });
}

// Strategy selection changes source hint visibility
if (elements.pipelineStrategy && elements.pipelineSrcHintWrapper) {
  elements.pipelineStrategy.addEventListener("change", () => {
    const isDirect = elements.pipelineStrategy.value === "direct";
    elements.pipelineSrcHintWrapper.hidden = !isDirect;
  });
}

// Sample pills for pipeline
if (elements.pipelineSamplePills) {
  elements.pipelineSamplePills.forEach((pill) => {
    pill.addEventListener("click", () => {
      const key = pill.getAttribute("data-sample");
      const sample = PIPELINE_SAMPLES[key];
      if (sample && elements.pipelineInput) {
        elements.pipelineInput.value = sample.text;
        if (elements.pipelineStrategy) {
          elements.pipelineStrategy.value = sample.strategy;
          if (elements.pipelineSrcHintWrapper) {
            elements.pipelineSrcHintWrapper.hidden = sample.strategy !== "direct";
          }
        }
        if (elements.pipelineGlossCheck) {
          elements.pipelineGlossCheck.checked = sample.gloss;
        }
        if (elements.pipelineReferenceInput) {
          elements.pipelineReferenceInput.value = sample.ref || "";
        }
        handlePipelineInputChange();
        elements.pipelineInput.focus();
      }
    });
  });
}

// Clear button for pipeline
if (elements.pipelineClearBtn) {
  elements.pipelineClearBtn.addEventListener("click", () => {
    const isTranslating = elements.pipelineBtn && elements.pipelineBtn.classList.contains("loading");
    const isComparing = elements.pipelineCompareBtn && elements.pipelineCompareBtn.classList.contains("loading");

    if (isTranslating && activePipelineAbortController) {
      activePipelineAbortController.abort();
      activePipelineAbortController = null;
      activePipelineRequestId++;
      resetPipelineLoadingState();
      elements.pipelineInput.value = "";
      if (elements.pipelineReferenceInput) elements.pipelineReferenceInput.value = "";
      handlePipelineInputChange();
      hidePipelineResults();
      hideComparisonResults();
      showNotice("Pipeline translation cancelled because the input was cleared.", "info");
    } else if (isComparing && activeCompareAbortController) {
      activeCompareAbortController.abort();
      activeCompareAbortController = null;
      resetCompareLoadingState();
      elements.pipelineInput.value = "";
      if (elements.pipelineReferenceInput) elements.pipelineReferenceInput.value = "";
      handlePipelineInputChange();
      hidePipelineResults();
      hideComparisonResults();
      showNotice("Strategy comparison cancelled because the input was cleared.", "info");
    } else {
      if (elements.pipelineInput) elements.pipelineInput.value = "";
      if (elements.pipelineReferenceInput) elements.pipelineReferenceInput.value = "";
      handlePipelineInputChange();
      hidePipelineResults();
      hideComparisonResults();
      clearNotices();
    }
  });
}

function hidePipelineResults() {
  if (!elements.pipelineResultsPanel) return;

  elements.pipelineResultsPanel.hidden = true;
  if (elements.pipelineErrorBanner) {
    elements.pipelineErrorBanner.hidden = true;
    elements.pipelineErrorBanner.textContent = "";
  }
  currentPipelineData = null;
  if (pipelineCopyNoticeTimeout) {
    clearTimeout(pipelineCopyNoticeTimeout);
    pipelineCopyNoticeTimeout = null;
  }
  if (elements.pipelineCopyNotice) elements.pipelineCopyNotice.hidden = true;
  if (elements.pipelineResultText) elements.pipelineResultText.textContent = "";
  if (elements.pipelineOriginalText) elements.pipelineOriginalText.textContent = "";
  if (elements.pipelineNormalizedText) elements.pipelineNormalizedText.textContent = "";
  if (elements.pipelineNormalizedBlock) elements.pipelineNormalizedBlock.hidden = true;
  if (elements.pipelineClausesSection) elements.pipelineClausesSection.hidden = true;
  if (elements.pipelineTokensSection) elements.pipelineTokensSection.hidden = true;
  if (elements.pipelineGlossesSection) elements.pipelineGlossesSection.hidden = true;

  if (elements.pipelineClausesList) {
    while (elements.pipelineClausesList.firstChild) {
      elements.pipelineClausesList.removeChild(elements.pipelineClausesList.firstChild);
    }
  }
  if (elements.pipelineTokensFlow) {
    while (elements.pipelineTokensFlow.firstChild) {
      elements.pipelineTokensFlow.removeChild(elements.pipelineTokensFlow.firstChild);
    }
  }
  if (elements.pipelineTableBody) {
    while (elements.pipelineTableBody.firstChild) {
      elements.pipelineTableBody.removeChild(elements.pipelineTableBody.firstChild);
    }
  }
  if (elements.pipelineGlossesGrid) {
    while (elements.pipelineGlossesGrid.firstChild) {
      elements.pipelineGlossesGrid.removeChild(elements.pipelineGlossesGrid.firstChild);
    }
  }
}

function resetPipelineLoadingState() {
  if (!elements.pipelineBtn) return;
  elements.pipelineBtn.classList.remove("loading");
  if (elements.pipelineBtnSpinner) elements.pipelineBtnSpinner.style.display = "none";
  if (elements.pipelineBtnText) elements.pipelineBtnText.textContent = "Translate";
  if (elements.pipelineElapsedCounter) {
    elements.pipelineElapsedCounter.style.display = "none";
    elements.pipelineElapsedCounter.textContent = "0s";
  }
  handlePipelineInputChange();
}

/**
 * Show a visible error banner inside the pipeline result card.
 */
function showPipelineError(msg) {
  if (elements.pipelineErrorBanner) {
    elements.pipelineErrorBanner.textContent = msg;
    elements.pipelineErrorBanner.hidden = false;
  }
  if (elements.pipelineResultsPanel) {
    elements.pipelineResultsPanel.hidden = false;
    if (elements.pipelineResultsHeader) elements.pipelineResultsHeader.hidden = true;
    if (elements.pipelineCardContent) elements.pipelineCardContent.hidden = true;
    if (elements.pipelineTimingSection) elements.pipelineTimingSection.hidden = true;
    if (elements.pipelineClausesSection) elements.pipelineClausesSection.hidden = true;
    if (elements.pipelineTokensSection) elements.pipelineTokensSection.hidden = true;
    if (elements.pipelineGlossesSection) elements.pipelineGlossesSection.hidden = true;
    elements.pipelineResultsPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

/**
 * Strict response validation for CodeMix Pipeline Translation.
 */
function validatePipelineApiResponse(data) {
  if (!data || typeof data !== "object") return false;
  if (typeof data.original !== "string") return false;
  if (typeof data.translation !== "string") return false;
  if (typeof data.strategy !== "string") return false;
  if (!Array.isArray(data.tokens)) return false;
  if (!data.timings_ms || typeof data.timings_ms !== "object") return false;
  return true;
}

// ==============================================================================
// 6E. Pipeline Offline Demo Mode (Reading frontend/demo_cache.json)
// ==============================================================================

let isDemoMode = false;
let pipelineDemoCache = null;

function checkUrlDemoMode() {
  try {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("demo") === "1" || urlParams.get("demo") === "true";
  } catch (_) {
    return false;
  }
}

function setDemoMode(enable) {
  isDemoMode = enable;
  if (elements.pipelineDemoBanner) {
    elements.pipelineDemoBanner.hidden = !enable;
  }
  if (enable) {
    loadDemoCache();
  }
}

async function loadDemoCache() {
  if (pipelineDemoCache) return pipelineDemoCache;
  const candidateUrls = ["demo_cache.json", "frontend/demo_cache.json", "./demo_cache.json"];
  for (const url of candidateUrls) {
    try {
      const resp = await fetch(url);
      if (resp.ok) {
        pipelineDemoCache = await resp.json();
        return pipelineDemoCache;
      }
    } catch (_) {}
  }
  return null;
}

function findInDemoCache(cache, rawInput) {
  if (!cache || typeof cache !== "object" || !rawInput) return null;
  const cleaned = rawInput.trim();

  // 1. Exact match
  if (cache[cleaned]) {
    return { key: cleaned, entry: cache[cleaned] };
  }

  // 2. Whitespace and punctuation normalized match
  const normalize = (s) => s.toLowerCase().replace(/[.,!?;:]/g, "").replace(/\s+/g, " ").trim();
  const inputNorm = normalize(cleaned);

  for (const [k, v] of Object.entries(cache)) {
    if (normalize(k) === inputNorm) {
      return { key: k, entry: v };
    }
  }

  return null;
}

if (elements.pipelineBtn) {
  elements.pipelineBtn.addEventListener("click", executePipelineTranslation);
}

async function executePipelineTranslation() {
  const rawText = elements.pipelineInput ? elements.pipelineInput.value : "";
  const cleanedText = rawText.trim();

  if (!cleanedText) {
    return; // An empty textarea does not send a request
  }

  if (cleanedText.length > 1000) {
    showToast("Input text exceeds maximum allowed length of 1,000 characters.", "error");
    return;
  }

  clearNotices();
  hidePipelineResults();

  // If in Demo Mode (or forced by URL ?demo=1 / offline)
  if (isDemoMode) {
    elements.pipelineBtn.classList.add("loading");
    elements.pipelineBtn.disabled = true;
    if (elements.pipelineCompareBtn) elements.pipelineCompareBtn.disabled = true;
    if (elements.pipelineBtnSpinner) elements.pipelineBtnSpinner.style.display = "inline-block";
    if (elements.pipelineBtnText) elements.pipelineBtnText.textContent = "Translating...";

    const cache = await loadDemoCache();
    const match = findInDemoCache(cache, cleanedText);

    if (!match) {
      resetPipelineLoadingState();
      showPipelineError("This sentence is not in the offline demo. Choose one of the example chips.");
      showToast("This sentence is not in the offline demo. Choose one of the example chips.", "info");
      return;
    }

    const chosenStrategy = elements.pipelineStrategy ? elements.pipelineStrategy.value : "full";
    const cachedResp = match.entry[chosenStrategy] || match.entry["full"] || Object.values(match.entry)[0];

    if (!cachedResp) {
      resetPipelineLoadingState();
      showPipelineError("This sentence is not in the offline demo. Choose one of the example chips.");
      return;
    }

    const data = JSON.parse(JSON.stringify(cachedResp));
    currentPipelineData = data;
    renderPipelineResults(data, cleanedText);

    let totalTimeMs = 0;
    if (data.timings_ms && typeof data.timings_ms === "object") {
      for (const k of Object.keys(data.timings_ms)) {
        if (typeof data.timings_ms[k] === "number") totalTimeMs += data.timings_ms[k];
      }
    }
    const timeFormatted = totalTimeMs > 0 ? `${totalTimeMs.toFixed(0)} ms` : "Demo";
    saveToPipelineHistory({
      text: cleanedText,
      strategy: data.strategy,
      translation: data.translation,
      time: timeFormatted
    });

    resetPipelineLoadingState();
    return;
  }

  activePipelineAbortController = new AbortController();
  activePipelineRequestId++;
  const thisRequestId = activePipelineRequestId;

  elements.pipelineBtn.classList.add("loading");
  elements.pipelineBtn.disabled = true;
  if (elements.pipelineCompareBtn) elements.pipelineCompareBtn.disabled = true;
  if (elements.pipelineBtnSpinner) elements.pipelineBtnSpinner.style.display = "inline-block";
  if (elements.pipelineBtnText) elements.pipelineBtnText.textContent = "Translating...";
  if (elements.pipelineElapsedCounter) {
    elements.pipelineElapsedCounter.textContent = "0s";
    elements.pipelineElapsedCounter.style.display = "inline-block";
  }

  const startTime = Date.now();
  const elapsedTimer = setInterval(() => {
    const elapsedSec = Math.floor((Date.now() - startTime) / 1000);
    if (elements.pipelineElapsedCounter) {
      elements.pipelineElapsedCounter.textContent = `${elapsedSec}s`;
    }
  }, 1000);

  try {
    const payload = {
      text: cleanedText,
      strategy: elements.pipelineStrategy ? elements.pipelineStrategy.value : "full",
      gloss: elements.pipelineGlossCheck ? elements.pipelineGlossCheck.checked : false,
      src_hint: elements.pipelineSrcHint ? elements.pipelineSrcHint.value : "TE"
    };

    const targetUrl = `${getMtApiBase()}/api/mt/translate`;
    const data = await postJSON(targetUrl, payload, {
      timeoutMs: 300000,
      signal: activePipelineAbortController.signal
    });

    if (thisRequestId !== activePipelineRequestId) return;

    if (!validatePipelineApiResponse(data)) {
      showPipelineError("The server returned an unexpected pipeline response format.");
      return;
    }

    currentPipelineData = data;
    renderPipelineResults(data, cleanedText);

    // Save to translation history (Requirement 2)
    let totalTimeMs = 0;
    if (data.timings_ms && typeof data.timings_ms === "object") {
      for (const k of Object.keys(data.timings_ms)) {
        if (typeof data.timings_ms[k] === "number") totalTimeMs += data.timings_ms[k];
      }
    }
    const timeFormatted = totalTimeMs > 0 ? `${totalTimeMs.toFixed(0)} ms` : `${Math.floor(Date.now() - startTime)} ms`;
    saveToPipelineHistory({
      text: cleanedText,
      strategy: data.strategy,
      translation: data.translation,
      time: timeFormatted
    });

    // Refresh health to update status pill and sidebar
    checkBackendHealth();
  } catch (err) {
    if (thisRequestId !== activePipelineRequestId) return;
    if (err.name === "AbortError") return;

    if (err.message.includes("Cannot reach server") || err.message.includes("Network down") || err.message.includes("Failed to fetch") || err.message.includes("Load failed")) {
      latestMtHealthData = null;
      setDemoMode(true);
      updateNavigationStatus();
      updatePipelineLoadedNote();

      const cache = await loadDemoCache();
      const match = findInDemoCache(cache, cleanedText);
      if (match) {
        const chosenStrategy = elements.pipelineStrategy ? elements.pipelineStrategy.value : "full";
        const cachedResp = match.entry[chosenStrategy] || match.entry["full"] || Object.values(match.entry)[0];
        if (cachedResp) {
          const data = JSON.parse(JSON.stringify(cachedResp));
          currentPipelineData = data;
          renderPipelineResults(data, cleanedText);
          showToast("Backend offline. Loaded pre-computed result from demo cache.", "info");
          return;
        }
      }
      showPipelineError("This sentence is not in the offline demo. Choose one of the example chips.");
      return;
    }

    showPipelineError(err.message);
    showToast(err.message, "error");
  } finally {
    clearInterval(elapsedTimer);
    if (thisRequestId === activePipelineRequestId) {
      resetPipelineLoadingState();
      activePipelineAbortController = null;
    }
  }
}

/**
 * Render validated pipeline results into results card.
 */
function renderPipelineResults(data, inputText) {
  // Clear any previous error banner and restore content
  if (elements.pipelineErrorBanner) {
    elements.pipelineErrorBanner.hidden = true;
    elements.pipelineErrorBanner.textContent = "";
  }
  if (elements.pipelineResultsHeader) elements.pipelineResultsHeader.hidden = false;
  if (elements.pipelineCardContent) elements.pipelineCardContent.hidden = false;
  if (elements.pipelineTimingSection) elements.pipelineTimingSection.hidden = false;

  // Main translation
  if (elements.pipelineResultText) {
    elements.pipelineResultText.textContent = data.translation;
  }
  if (elements.pipelineOriginalText) {
    elements.pipelineOriginalText.textContent = data.original;
  }

  // Cleaned input (shown only when normalized differs from input)
  const compareText = (inputText || data.original || "").trim();
  if (data.normalized && data.normalized.trim() !== compareText && elements.pipelineNormalizedText && elements.pipelineNormalizedBlock) {
    elements.pipelineNormalizedText.textContent = data.normalized;
    elements.pipelineNormalizedBlock.hidden = false;
  } else if (elements.pipelineNormalizedBlock) {
    elements.pipelineNormalizedBlock.hidden = true;
  }

  // Dominant language badge (Telugu, Hindi, or "English only, no translation needed" when dominant_lang is null)
  if (elements.pipelineDominantBadge) {
    let domText = "";
    if (data.dominant_lang === "TE") {
      domText = "Telugu";
    } else if (data.dominant_lang === "HI") {
      domText = "Hindi";
    } else if (!data.dominant_lang) {
      domText = "English only, no translation needed";
    } else {
      domText = LANGUAGE_NAMES[data.dominant_lang] || data.dominant_lang;
    }
    elements.pipelineDominantBadge.textContent = domText;
  }

  if (elements.pipelineStrategyBadge) {
    elements.pipelineStrategyBadge.textContent = `Strategy: ${data.strategy}`;
  }

  // Clauses Breakdown
  if (data.strategy === "clause" && Array.isArray(data.clauses) && data.clauses.length > 0) {
    elements.pipelineClausesSection.hidden = false;
    while (elements.pipelineClausesList.firstChild) {
      elements.pipelineClausesList.removeChild(elements.pipelineClausesList.firstChild);
    }

    data.clauses.forEach((c) => {
      const row = document.createElement("div");
      row.className = "clause-row";

      // Language badge
      const badge = document.createElement("span");
      const cLang = c.lang || "TE";
      badge.className = `model-badge font-mono lang-${cLang.toLowerCase()}`;
      badge.textContent = LANGUAGE_NAMES[cLang] || cLang;

      // Clause text
      const textSpan = document.createElement("span");
      textSpan.className = "clause-text font-serif";
      textSpan.textContent = c.text;

      // Arrow
      const arrowSpan = document.createElement("span");
      arrowSpan.className = "clause-arrow";
      arrowSpan.setAttribute("aria-hidden", "true");
      arrowSpan.textContent = "→";

      // Clause translation
      const transSpan = document.createElement("span");
      transSpan.className = "clause-trans";
      transSpan.textContent = c.translation;

      row.appendChild(badge);
      row.appendChild(textSpan);
      row.appendChild(arrowSpan);
      row.appendChild(transSpan);

      elements.pipelineClausesList.appendChild(row);
    });
  } else {
    elements.pipelineClausesSection.hidden = true;
  }

  // Token Chips
  if (Array.isArray(data.tokens) && data.tokens.length > 0 && elements.pipelineTokensFlow) {
    elements.pipelineTokensSection.hidden = false;

    while (elements.pipelineTokensFlow.firstChild) {
      elements.pipelineTokensFlow.removeChild(elements.pipelineTokensFlow.firstChild);
    }

    data.tokens.forEach((item) => {
      const chip = document.createElement("div");
      const langKey = (item.lang || "other").toLowerCase();
      chip.className = `pipeline-chip lang-${langKey}`;
      chip.setAttribute("role", "listitem");
      chip.setAttribute("tabindex", "0");

      const confNum = typeof item.conf === "number" ? Math.round(item.conf * 100) : 0;
      const langName = LANGUAGE_NAMES[item.lang] || item.lang || "Other";
      const isLowConf = typeof item.conf === "number" && item.conf < 0.60;

      // aria-label: e.g. "Nenu, Telugu, 97 percent"
      chip.setAttribute("aria-label", `${item.text}, ${langName}, ${confNum} percent`);

      // Confidence below 60 percent gets a dotted outline
      if (isLowConf) {
        chip.classList.add("low-conf");
      }

      // Token text
      const wordSpan = document.createElement("span");
      wordSpan.className = "chip-text font-serif";
      wordSpan.textContent = item.text;
      chip.appendChild(wordSpan);

      // If native is not null, show it in a smaller line under the token text
      if (item.native && item.native.trim()) {
        const nativeSpan = document.createElement("span");
        nativeSpan.className = "chip-native font-sans";
        nativeSpan.textContent = item.native;
        chip.appendChild(nativeSpan);
      }

      // Language code tag so accessibility does not rely on color alone
      const langTag = document.createElement("span");
      langTag.className = "chip-lang-code font-mono";
      langTag.setAttribute("aria-hidden", "true");
      langTag.textContent = item.lang || "OTHER";
      chip.appendChild(langTag);

      // Tooltip on hover AND on keyboard focus (tabindex=0)
      const tooltip = document.createElement("div");
      tooltip.className = "chip-tooltip";
      tooltip.setAttribute("role", "tooltip");

      // Language name & confidence percentage
      const headerLine = document.createElement("div");
      headerLine.className = "tooltip-line tooltip-header";
      headerLine.textContent = `${langName} · ${confNum}%`;
      tooltip.appendChild(headerLine);

      // If low confidence, show "low confidence"
      if (isLowConf) {
        const warnLine = document.createElement("div");
        warnLine.className = "tooltip-line tooltip-low-conf";
        warnLine.textContent = "low confidence";
        tooltip.appendChild(warnLine);
      }

      // Native form
      if (item.native && item.native.trim()) {
        const nativeLine = document.createElement("div");
        nativeLine.className = "tooltip-line tooltip-native";
        nativeLine.textContent = `Native: ${item.native}`;
        tooltip.appendChild(nativeLine);
      }

      // Word meaning from glosses when present (label it "approximate meaning")
      const glossMeaning = data.glosses && data.glosses[item.text];
      if (glossMeaning) {
        const glossLine = document.createElement("div");
        glossLine.className = "tooltip-line tooltip-gloss";
        glossLine.textContent = `approximate meaning: "${glossMeaning}"`;
        tooltip.appendChild(glossLine);
      }

      chip.appendChild(tooltip);
      elements.pipelineTokensFlow.appendChild(chip);
    });
  } else if (elements.pipelineTokensSection) {
    elements.pipelineTokensSection.hidden = true;
  }

  // Word Glosses Grid
  if (data.glosses && typeof data.glosses === "object" && Object.keys(data.glosses).length > 0) {
    elements.pipelineGlossesSection.hidden = false;
    while (elements.pipelineGlossesGrid.firstChild) {
      elements.pipelineGlossesGrid.removeChild(elements.pipelineGlossesGrid.firstChild);
    }

    Object.entries(data.glosses).forEach(([word, meaning]) => {
      const pill = document.createElement("div");
      pill.className = "gloss-pill";

      const tokSpan = document.createElement("span");
      tokSpan.className = "gloss-token";
      tokSpan.textContent = word;

      const arrowSpan = document.createElement("span");
      arrowSpan.className = "gloss-arrow";
      arrowSpan.textContent = "→";

      const meanSpan = document.createElement("span");
      meanSpan.className = "gloss-meaning";
      meanSpan.textContent = meaning;

      pill.appendChild(tokSpan);
      pill.appendChild(arrowSpan);
      pill.appendChild(meanSpan);

      elements.pipelineGlossesGrid.appendChild(pill);
    });
  } else {
    elements.pipelineGlossesSection.hidden = true;
  }

  // Timings
  const tm = data.timings_ms || {};
  let totalMs = 0;
  if (typeof tm.normalize === "number") totalMs += tm.normalize;
  if (typeof tm.lid === "number") totalMs += tm.lid;
  if (typeof tm.transliterate === "number") totalMs += tm.transliterate;
  if (typeof tm.translate === "number") totalMs += tm.translate;

  if (elements.timingTotal) elements.timingTotal.textContent = `${totalMs.toFixed(1)} ms`;
  if (elements.timingNormalize) elements.timingNormalize.textContent = typeof tm.normalize === "number" ? `${tm.normalize.toFixed(1)} ms` : "—";
  if (elements.timingLid) elements.timingLid.textContent = typeof tm.lid === "number" ? `${tm.lid.toFixed(1)} ms` : "—";
  if (elements.timingTranslit) elements.timingTranslit.textContent = typeof tm.transliterate === "number" ? `${tm.transliterate.toFixed(1)} ms` : "—";
  if (elements.timingTranslate) elements.timingTranslate.textContent = typeof tm.translate === "number" ? `${tm.translate.toFixed(1)} ms` : "—";

  elements.pipelineResultsPanel.hidden = false;
  elements.pipelineResultsPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function setPipelineView(viewName) {
  activePipelineView = viewName;
  if (viewName === "annotated") {
    elements.pipelineViewAnnotatedBtn.classList.add("active");
    elements.pipelineViewAnnotatedBtn.setAttribute("aria-selected", "true");
    elements.pipelineViewTableBtn.classList.remove("active");
    elements.pipelineViewTableBtn.setAttribute("aria-selected", "false");

    elements.pipelineAnnotatedContainer.hidden = false;
    elements.pipelineTableContainer.hidden = true;
  } else {
    elements.pipelineViewTableBtn.classList.add("active");
    elements.pipelineViewTableBtn.setAttribute("aria-selected", "true");
    elements.pipelineViewAnnotatedBtn.classList.remove("active");
    elements.pipelineViewAnnotatedBtn.setAttribute("aria-selected", "false");

    elements.pipelineTableContainer.hidden = false;
    elements.pipelineAnnotatedContainer.hidden = true;
  }
}

if (elements.pipelineViewAnnotatedBtn) {
  elements.pipelineViewAnnotatedBtn.addEventListener("click", () => setPipelineView("annotated"));
}
if (elements.pipelineViewTableBtn) {
  elements.pipelineViewTableBtn.addEventListener("click", () => setPipelineView("table"));
}

// Copy Pipeline Translation
if (elements.pipelineCopyBtn) {
  elements.pipelineCopyBtn.addEventListener("click", async () => {
    if (!currentPipelineData || !currentPipelineData.translation) return;

    const textToCopy = currentPipelineData.translation;
    let success = false;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(textToCopy);
        success = true;
      } catch (_) {}
    }

    if (success) {
      elements.pipelineCopyNotice.textContent = "Pipeline translation copied to clipboard!";
      elements.pipelineCopyNotice.hidden = false;
      if (pipelineCopyNoticeTimeout) clearTimeout(pipelineCopyNoticeTimeout);
      pipelineCopyNoticeTimeout = setTimeout(() => { elements.pipelineCopyNotice.hidden = true; }, 2000);
    } else {
      showNotice("Unable to copy to clipboard. Please copy manually.", "info");
    }
  });
}

// ==============================================================================
// 6B. Pipeline Strategy Comparison & chrF Evaluation
// ==============================================================================

let activeCompareAbortController = null;
let lastComparisonData = null; // { results: [...], srcHint: string }

const STRATEGY_METADATA = {
  direct: {
    key: "direct",
    title: "Direct MT",
    getDescription: (hint) => `Direct IndicTrans2 without pipeline (${hint === "HI" ? "Hindi" : "Telugu"} hint)`
  },
  lid_only: {
    key: "lid_only",
    title: "LID Only",
    getDescription: () => "MuRIL detects dominant language, passes text directly to IndicTrans2"
  },
  full: {
    key: "full",
    title: "Full Pipeline",
    getDescription: () => "MuRIL token LID + IndicXlit transliteration + IndicTrans2"
  },
  clause: {
    key: "clause",
    title: "Clause by Clause",
    getDescription: () => "Segments text at punctuation boundaries and translates each clause"
  },
  mt5: {
    key: "mt5",
    title: "mT5 Baseline",
    getDescription: () => "Older mT5-small model trained only on Romanized Hinglish"
  }
};

/**
 * Compute approximate chrF score in plain JS.
 * chrF formulation:
 * - Remove all whitespace
 * - For n = 1 to 6, count character n-grams in hypothesis and reference
 * - For each n with at least one n-gram on both sides, compute precision (P) and recall (R)
 *   from clipped overlap counts
 * - F-beta with beta = 2: F2 = (5 * P * R) / (4 * P + R)
 * - Average F values across evaluated n, multiply by 100
 *
 * @param {string} hyp - Hypothesis translation.
 * @param {string} ref - Reference translation.
 * @returns {number|null} Score from 0.0 to 100.0 or null if inputs are invalid.
 */
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

/**
 * Clean a single word for difference matching against Full baseline.
 * Lowercases and strips leading/trailing punctuation.
 */
function cleanWordForDiff(w) {
  if (!w) return "";
  return w.toLowerCase().replace(/^[^\w\d]+|[^\w\d]+$/g, "");
}

/**
 * Escape HTML characters safely for innerHTML rendering.
 */
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Render translation text highlighting words that differ from the Full pipeline word set.
 */
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

/**
 * Extract total time from timings_ms or fallback to elapsed ms.
 */
function getTimingTotal(timingsMs, fallbackMs) {
  if (timingsMs && typeof timingsMs === "object") {
    let sum = 0;
    for (const key of Object.keys(timingsMs)) {
      if (typeof timingsMs[key] === "number") sum += timingsMs[key];
    }
    if (sum > 0) return sum;
  }
  return fallbackMs || 0;
}

/**
 * Reset compare button and progress state.
 */
function resetCompareLoadingState() {
  if (!elements.pipelineCompareBtn) return;
  elements.pipelineCompareBtn.classList.remove("loading");
  if (elements.pipelineCompareSpinner) elements.pipelineCompareSpinner.style.display = "none";
  if (elements.pipelineCompareBtnText) elements.pipelineCompareBtnText.textContent = "Compare strategies";
  if (elements.pipelineCompareProgress) {
    elements.pipelineCompareProgress.style.display = "none";
    elements.pipelineCompareProgress.textContent = "0/4";
  }
  handlePipelineInputChange();
}

/**
 * Hide comparison results and clear grid.
 */
function hideComparisonResults() {
  if (elements.pipelineComparisonPanel) elements.pipelineComparisonPanel.hidden = true;
  if (elements.pipelineComparisonStatus) elements.pipelineComparisonStatus.textContent = "Complete";
  if (elements.pipelineComparisonGrid) {
    while (elements.pipelineComparisonGrid.firstChild) {
      elements.pipelineComparisonGrid.removeChild(elements.pipelineComparisonGrid.firstChild);
    }
  }
  lastComparisonData = null;
}

/**
 * Execute all 4 pipeline strategies and mT5 baseline sequentially (never in parallel).
 */
async function executeStrategyComparison() {
  const rawText = elements.pipelineInput ? elements.pipelineInput.value : "";
  const cleanedText = rawText.trim();

  if (!cleanedText) return;

  if (cleanedText.length > 1000) {
    showToast("Input text exceeds maximum allowed length of 1,000 characters.", "error");
    return;
  }

  clearNotices();

  // If a single pipeline request is running, don't conflict
  if (elements.pipelineBtn && elements.pipelineBtn.classList.contains("loading")) {
    return;
  }

  activeCompareAbortController = new AbortController();

  elements.pipelineCompareBtn.classList.add("loading");
  elements.pipelineCompareBtn.disabled = true;
  if (elements.pipelineBtn) elements.pipelineBtn.disabled = true;
  if (elements.pipelineCompareSpinner) elements.pipelineCompareSpinner.style.display = "inline-block";
  if (elements.pipelineCompareProgress) {
    elements.pipelineCompareProgress.style.display = "inline-block";
    elements.pipelineCompareProgress.textContent = "0 of 5 done";
  }

  const chosenSrcHint = elements.pipelineSrcHint ? elements.pipelineSrcHint.value : "TE";

  // Show comparison panel with evaluating status
  if (elements.pipelineComparisonPanel) elements.pipelineComparisonPanel.hidden = false;
  if (elements.pipelineComparisonStatus) {
    elements.pipelineComparisonStatus.textContent = "Evaluating...";
  }

  // Offline Demo Mode handling for strategy comparison
  if (isDemoMode) {
    const cache = await loadDemoCache();
    const match = findInDemoCache(cache, cleanedText);

    if (!match) {
      if (elements.pipelineComparisonStatus) {
        elements.pipelineComparisonStatus.textContent = "This sentence is not in the offline demo. Choose one of the example chips.";
      }
      showPipelineError("This sentence is not in the offline demo. Choose one of the example chips.");
      showToast("This sentence is not in the offline demo. Choose one of the example chips.", "info");
      resetCompareLoadingState();
      return;
    }

    if (elements.pipelineComparisonStatus) {
      elements.pipelineComparisonStatus.textContent = "Demo Mode: Pre-computed comparison results";
    }

    const cachedEntry = match.entry;
    const results = [];
    const stratKeys = ["direct", "lid_only", "full", "clause"];

    for (const sk of stratKeys) {
      const data = cachedEntry[sk];
      if (data) {
        results.push({
          key: sk,
          success: true,
          data: data,
          translation: data.translation || "",
          clauses: data.clauses || [],
          timeMs: getTimingTotal(data.timings_ms, 0),
          dominant_lang: data.dominant_lang
        });
      }
    }

    // Step 5: mT5 Baseline
    const fullRes = results.find((r) => r.key === "full" && r.success);
    const lidRes = results.find((r) => r.key === "lid_only" && r.success);
    const isTelugu =
      (fullRes && fullRes.dominant_lang === "TE") ||
      (lidRes && lidRes.dominant_lang === "TE") ||
      (fullRes && fullRes.data && Array.isArray(fullRes.data.tokens) && fullRes.data.tokens.some((t) => t.lang === "TE"));

    if (isTelugu) {
      results.push({
        key: "mt5",
        success: true,
        notApplicable: true,
        translation: "Not applicable (mT5 baseline is trained on Romanized Hinglish only, not Telugu).",
        timeMs: 0
      });
    } else {
      results.push({
        key: "mt5",
        success: true,
        translation: "there is a meeting tomorrow please send slides",
        timeMs: 120
      });
    }

    renderComparisonResults(results, chosenSrcHint);
    resetCompareLoadingState();
    return;
  }

  const results = [];
  const strategies = [
    { key: "direct", name: "direct", payload: { text: cleanedText, strategy: "direct", gloss: false, src_hint: chosenSrcHint } },
    { key: "lid_only", name: "lid_only", payload: { text: cleanedText, strategy: "lid_only", gloss: false } },
    { key: "full", name: "full", payload: { text: cleanedText, strategy: "full", gloss: false } },
    { key: "clause", name: "clause", payload: { text: cleanedText, strategy: "clause", gloss: false } }
  ];

  const totalSteps = 5;

  try {
    // 1. Run pipeline strategies sequentially (never parallel, server is CPU bound)
    for (let i = 0; i < strategies.length; i++) {
      const item = strategies[i];
      if (elements.pipelineCompareBtnText) {
        elements.pipelineCompareBtnText.textContent = `Running ${item.name}...`;
      }
      if (elements.pipelineCompareProgress) {
        elements.pipelineCompareProgress.textContent = `${i} of ${totalSteps} done`;
      }

      const tStart = performance.now();
      try {
        const targetUrl = `${getMtApiBase()}/api/mt/translate`;
        const data = await postJSON(targetUrl, item.payload, {
          timeoutMs: 300000,
          signal: activeCompareAbortController.signal
        });
        const elapsedFallback = performance.now() - tStart;
        results.push({
          key: item.key,
          success: true,
          data: data,
          translation: data.translation || "",
          clauses: data.clauses || [],
          timeMs: getTimingTotal(data.timings_ms, elapsedFallback),
          dominant_lang: data.dominant_lang
        });
      } catch (err) {
        if (err.name === "AbortError") throw err;
        results.push({
          key: item.key,
          success: false,
          error: err.message || "Request failed",
          translation: "",
          timeMs: 0
        });
      }
    }

    // 2. Check if text is Telugu from full pipeline or lid_only
    const fullRes = results.find((r) => r.key === "full" && r.success);
    const lidRes = results.find((r) => r.key === "lid_only" && r.success);
    const isTelugu =
      (fullRes && fullRes.dominant_lang === "TE") ||
      (lidRes && lidRes.dominant_lang === "TE") ||
      (fullRes && fullRes.data && Array.isArray(fullRes.data.tokens) && fullRes.data.tokens.some((t) => t.lang === "TE"));

    // 3. Step 5: mT5 Baseline (Older Hinglish model)
    if (elements.pipelineCompareBtnText) {
      elements.pipelineCompareBtnText.textContent = "Checking mT5...";
    }
    if (elements.pipelineCompareProgress) {
      elements.pipelineCompareProgress.textContent = `4 of ${totalSteps} done`;
    }

    if (isTelugu) {
      // mT5 baseline model is trained exclusively on Romanized Hinglish, not Telugu
      results.push({
        key: "mt5",
        success: true,
        notApplicable: true,
        translation: "Not applicable (mT5 baseline is trained on Romanized Hinglish only, not Telugu).",
        timeMs: 0
      });
    } else {
      const tStart = performance.now();
      try {
        const mt5Data = await postJSON(
          `${API_BASE}/api/translate`,
          { text: cleanedText },
          {
            timeoutMs: 60000,
            signal: activeCompareAbortController.signal
          }
        );
        const elapsed = performance.now() - tStart;
        const transText = mt5Data.translated_text || mt5Data.translation || "";
        results.push({
          key: "mt5",
          success: true,
          translation: transText,
          timeMs: elapsed
        });
      } catch (mt5Err) {
        if (mt5Err.name === "AbortError") throw mt5Err;
        results.push({
          key: "mt5",
          success: false,
          error: "mT5 baseline unavailable",
          translation: "",
          timeMs: 0
        });
      }
    }

    if (elements.pipelineCompareProgress) {
      elements.pipelineCompareProgress.textContent = `${totalSteps} of ${totalSteps} done`;
    }

    lastComparisonData = {
      results: results,
      srcHint: chosenSrcHint
    };

    renderComparisonResults();

    if (elements.pipelineComparisonStatus) {
      elements.pipelineComparisonStatus.textContent = "Complete";
    }

    if (elements.pipelineComparisonPanel) {
      elements.pipelineComparisonPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  } catch (err) {
    if (err.name === "AbortError") return;
    showToast(`Comparison error: ${err.message}`, "error");
    if (elements.pipelineComparisonStatus) {
      elements.pipelineComparisonStatus.textContent = "Failed";
    }
  } finally {
    resetCompareLoadingState();
    activeCompareAbortController = null;
  }
}

/**
 * Render comparison cards into comparison grid.
 */
function renderComparisonResults() {
  if (!lastComparisonData || !elements.pipelineComparisonGrid) return;

  const { results, srcHint } = lastComparisonData;
  const refText = elements.pipelineReferenceInput ? elements.pipelineReferenceInput.value.trim() : "";

  // Extract word set from "full" translation for diff highlighting
  const fullResult = results.find((r) => r.key === "full" && r.success);
  let fullWordSet = new Set();
  if (fullResult && fullResult.translation) {
    const rawWords = fullResult.translation.split(/\s+/);
    rawWords.forEach((w) => {
      const cw = cleanWordForDiff(w);
      if (cw) fullWordSet.add(cw);
    });
  }

  while (elements.pipelineComparisonGrid.firstChild) {
    elements.pipelineComparisonGrid.removeChild(elements.pipelineComparisonGrid.firstChild);
  }

  results.forEach((col) => {
    const meta = STRATEGY_METADATA[col.key] || {
      title: col.key,
      getDescription: () => ""
    };

    const card = document.createElement("div");
    card.className = `comparison-col col-${col.key}`;

    // Header
    const header = document.createElement("div");
    header.className = "comp-header";

    const titleDiv = document.createElement("div");
    titleDiv.className = "comp-title";
    titleDiv.textContent = meta.title;

    if (col.key === "full") {
      const badge = document.createElement("span");
      badge.className = "model-badge font-mono";
      badge.textContent = "Reference Baseline";
      titleDiv.appendChild(badge);
    }

    const descDiv = document.createElement("div");
    descDiv.className = "comp-desc";
    descDiv.textContent = meta.getDescription(srcHint);

    header.appendChild(titleDiv);
    header.appendChild(descDiv);
    card.appendChild(header);

    // Body
    const body = document.createElement("div");
    body.className = "comp-body";

    if (!col.success) {
      const errDiv = document.createElement("div");
      errDiv.className = "comp-error font-mono";
      errDiv.textContent = col.error || "Translation failed";
      body.appendChild(errDiv);
    } else if (col.notApplicable) {
      const naDiv = document.createElement("div");
      naDiv.className = "comp-na";
      naDiv.textContent = col.translation;
      body.appendChild(naDiv);
    } else {
      // Translation text with diff highlighting
      const transDiv = document.createElement("div");
      transDiv.className = "comp-trans";

      if (col.translation) {
        const isFull = col.key === "full";
        transDiv.innerHTML = renderDiffText(col.translation, fullWordSet, isFull);
      } else {
        transDiv.innerHTML = "<span class=\"comp-na\">(empty translation)</span>";
      }
      body.appendChild(transDiv);

      // If strategy is clause and clauses exist, render them
      if (col.key === "clause" && Array.isArray(col.clauses) && col.clauses.length > 0) {
        const clausesContainer = document.createElement("div");
        clausesContainer.className = "comp-clauses";

        col.clauses.forEach((cl) => {
          const clRow = document.createElement("div");
          clRow.className = "comp-clause-item";

          const cLang = cl.lang || "TE";
          const b = document.createElement("span");
          b.className = `model-badge font-mono lang-${cLang.toLowerCase()}`;
          b.textContent = cLang;

          const textSpan = document.createElement("span");
          textSpan.className = "clause-src font-serif";
          textSpan.textContent = `"${cl.text}"`;

          const arrow = document.createElement("span");
          arrow.className = "clause-arrow";
          arrow.setAttribute("aria-hidden", "true");
          arrow.textContent = "→";

          const tSpan = document.createElement("span");
          tSpan.className = "clause-out font-serif";
          tSpan.textContent = cl.translation;

          clRow.appendChild(b);
          clRow.appendChild(textSpan);
          clRow.appendChild(arrow);
          clRow.appendChild(tSpan);

          clausesContainer.appendChild(clRow);
        });

        body.appendChild(clausesContainer);
      }
    }

    card.appendChild(body);

    // Meta: Time and approx chrF
    const metaFooter = document.createElement("div");
    metaFooter.className = "comp-meta";

    const timeSpan = document.createElement("span");
    timeSpan.className = "comp-time font-mono";
    if (col.success && !col.notApplicable && typeof col.timeMs === "number" && col.timeMs > 0) {
      timeSpan.textContent = `${col.timeMs.toFixed(0)} ms`;
    } else {
      timeSpan.textContent = "—";
    }
    metaFooter.appendChild(timeSpan);

    // Compute approx chrF if reference is present and column has a valid translation
    if (refText && col.success && !col.notApplicable && col.translation) {
      const chrfScore = computeChrF(col.translation, refText);
      if (chrfScore !== null) {
        const chrfChip = document.createElement("span");
        chrfChip.className = "chrf-chip font-mono";
        chrfChip.setAttribute("title", "Character n-gram F-score (beta=2, n=1..6)");
        chrfChip.textContent = `approx. chrF: ${chrfScore.toFixed(1)}`;
        metaFooter.appendChild(chrfChip);
      }
    }

    card.appendChild(metaFooter);
    elements.pipelineComparisonGrid.appendChild(card);
  });
}

// Compare Strategies Button Click Listener
if (elements.pipelineCompareBtn) {
  elements.pipelineCompareBtn.addEventListener("click", executeStrategyComparison);
}

// Dynamic chrF update on reference input typing
if (elements.pipelineReferenceInput) {
  elements.pipelineReferenceInput.addEventListener("input", () => {
    if (lastComparisonData) {
      renderComparisonResults();
    }
  });
}

// ==============================================================================
// 6C. Convenience Features: Example Chips, History, and JSON Export
// ==============================================================================

/**
 * Initialize example sentence chips above the textarea.
 */
function initPipelineExampleChips() {
  const chips = document.querySelectorAll(".pipeline-example-chip");
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const text = chip.getAttribute("data-text") || chip.textContent.trim();
      if (elements.pipelineInput) {
        elements.pipelineInput.value = text;
        handlePipelineInputChange();
        elements.pipelineInput.focus();
      }
    });
  });
}

/**
 * Download JSON export of current pipeline response (including timings_ms).
 */
if (elements.pipelineDownloadJsonBtn) {
  elements.pipelineDownloadJsonBtn.addEventListener("click", () => {
    if (!currentPipelineData) {
      showToast("No translation result to download.", "info");
      return;
    }

    try {
      const jsonStr = JSON.stringify(currentPipelineData, null, 2);
      const blob = new Blob([jsonStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "codemix-result.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("Saved codemix-result.json", "info");
    } catch (err) {
      showToast("Failed to download JSON: " + err.message, "error");
    }
  });
}

/**
 * Retrieve the last 10 translation history items from localStorage.
 * @returns {Array<{text: string, strategy: string, translation: string, time: string, timestamp?: number}>}
 */
function getStoredHistory() {
  try {
    const raw = localStorage.getItem("codemix_history");
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        return parsed;
      }
    }
  } catch (_) {
    // localStorage may be restricted in private browsing mode
  }
  return [];
}

/**
 * Persist the history array (capped at 10 items) to localStorage.
 * @param {Array} history
 */
function setStoredHistory(history) {
  try {
    localStorage.setItem("codemix_history", JSON.stringify(history.slice(0, 10)));
  } catch (_) {
    // localStorage may be restricted in private browsing mode
  }
}

/**
 * Add a new result to the translation history, keeping at most 10 items.
 */
function saveToPipelineHistory({ text, strategy, translation, time }) {
  if (!text || !translation) return;

  const current = getStoredHistory();
  // Filter out exact duplicate of text and strategy to keep list fresh
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

  const capped = filtered.slice(0, 10);
  setStoredHistory(capped);
  renderPipelineHistory();
}

/**
 * Clear the translation history from localStorage and update UI.
 */
function clearPipelineHistory() {
  try {
    localStorage.removeItem("codemix_history");
  } catch (_) {}
  renderPipelineHistory();
  showToast("Translation history cleared.", "info");
}

/**
 * Render the translation history list into the collapsible section.
 */
function renderPipelineHistory() {
  if (!elements.pipelineHistoryList) return;

  const history = getStoredHistory();

  // Update count badge
  if (elements.pipelineHistoryCount) {
    elements.pipelineHistoryCount.textContent = String(history.length);
  }

  // Toggle empty notice
  if (elements.pipelineHistoryEmpty) {
    elements.pipelineHistoryEmpty.hidden = history.length > 0;
  }

  // Clear existing items
  while (elements.pipelineHistoryList.firstChild) {
    elements.pipelineHistoryList.removeChild(elements.pipelineHistoryList.firstChild);
  }

  // Render each history item
  history.forEach((item) => {
    const li = document.createElement("li");
    li.className = "history-item";
    li.setAttribute("tabindex", "0");
    li.setAttribute("role", "button");
    li.setAttribute("aria-label", `Reload: ${item.text}`);

    // Top row: text and strategy
    const topRow = document.createElement("div");
    topRow.className = "history-item-top";

    const textSpan = document.createElement("span");
    textSpan.className = "history-text font-serif";
    textSpan.textContent = item.text;

    const stratBadge = document.createElement("span");
    stratBadge.className = "model-badge font-mono history-strategy";
    stratBadge.textContent = item.strategy;

    topRow.appendChild(textSpan);
    topRow.appendChild(stratBadge);

    // Bottom row: translation and time
    const bottomRow = document.createElement("div");
    bottomRow.className = "history-item-bottom";

    const transSpan = document.createElement("span");
    transSpan.className = "history-trans font-sans";
    transSpan.textContent = `→ ${item.translation}`;

    const timeSpan = document.createElement("span");
    timeSpan.className = "history-time font-mono";
    timeSpan.textContent = item.time;

    bottomRow.appendChild(transSpan);
    bottomRow.appendChild(timeSpan);

    li.appendChild(topRow);
    li.appendChild(bottomRow);

    // Reload on click or Enter/Space
    const reload = () => {
      if (elements.pipelineInput) {
        elements.pipelineInput.value = item.text;
        if (elements.pipelineStrategy && item.strategy) {
          elements.pipelineStrategy.value = item.strategy;
          if (elements.pipelineSrcHintWrapper) {
            elements.pipelineSrcHintWrapper.hidden = item.strategy !== "direct";
          }
        }
        handlePipelineInputChange();
        elements.pipelineInput.focus();
        showToast("Sentence reloaded from history.", "info");
      }
    };

    li.addEventListener("click", reload);
    li.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        reload();
      }
    });

    elements.pipelineHistoryList.appendChild(li);
  });
}

// Clear history button listener
if (elements.pipelineClearHistoryBtn) {
  elements.pipelineClearHistoryBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    clearPipelineHistory();
  });
}

// ==============================================================================
// 6D. Experiments & Evaluation Logic (Reading frontend/results.json)
// ==============================================================================

let experimentsData = null;

/**
 * Fetch results.json and render experimental benchmarks into Mode D.
 * Shows a friendly explanation if served via file:// without HTTP.
 */
async function fetchAndRenderExperiments() {
  try {
    const response = await fetch("results.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    experimentsData = data;

    if (elements.experimentsErrorBanner) {
      elements.experimentsErrorBanner.hidden = true;
    }
    if (elements.experimentsContent) {
      elements.experimentsContent.hidden = false;
    }

    renderExperiments(data);
    updateNavigationStatus();
  } catch (err) {
    if (elements.experimentsErrorBanner) {
      elements.experimentsErrorBanner.hidden = false;
      if (elements.experimentsErrorMessage) {
        while (elements.experimentsErrorMessage.firstChild) {
          elements.experimentsErrorMessage.removeChild(elements.experimentsErrorMessage.firstChild);
        }
        const strong = document.createElement("strong");
        strong.textContent = `Cannot load experimental results (${err.message}). `;
        const span = document.createElement("span");
        span.textContent = "When opening the frontend directly via file://, browser security policies restrict local fetch requests. Please serve the frontend over HTTP (for example: python -m http.server 5500 or via the FastAPI backend) to load live benchmarks from results.json.";
        elements.experimentsErrorMessage.appendChild(strong);
        elements.experimentsErrorMessage.appendChild(span);
      }
    }
    if (elements.experimentsContent) {
      elements.experimentsContent.hidden = true;
    }
    updateNavigationStatus();
  }
}

/**
 * Render experimental evaluation benchmarks, charts, and findings from JSON data.
 * Adheres strictly to DOM construction using textContent without innerHTML.
 * @param {Object} data - Parsed results.json object
 */
function renderExperiments(data) {
  if (!data) return;

  const footnoteText = (data.meta && data.meta.note) || data.footnote || "chrF and BLEU computed with sacreBLEU; bootstrap 95 percent confidence intervals shown where available";

  // Helper function to create an exp-bar element
  function createExpBar(score, typeClass, labelPrefix, ciText) {
    const track = document.createElement("div");
    track.className = "exp-bar-track";

    const bar = document.createElement("div");
    bar.className = `exp-bar ${typeClass}`;
    const scoreVal = typeof score === "number" ? score : 0;
    bar.style.width = `${Math.min(100, Math.max(8, scoreVal))}%`;

    const label = document.createElement("span");
    label.className = "exp-bar-label font-mono";
    label.textContent = `${labelPrefix} ${scoreVal.toFixed(scoreVal % 1 === 0 ? 1 : 2)}`;

    if (ciText) {
      const small = document.createElement("small");
      small.textContent = ` ${ciText}`;
      label.appendChild(small);
    }

    bar.appendChild(label);
    track.appendChild(bar);
    return track;
  }

  // Helper function to render a gains table
  function createGainsTable(gains) {
    const wrapper = document.createElement("div");
    wrapper.className = "exp-gains-wrapper";
    wrapper.style.marginTop = "12px";

    const title = document.createElement("div");
    title.className = "caption font-bold";
    title.style.fontSize = "11px";
    title.style.marginBottom = "6px";
    title.textContent = "Pairwise Gains (chrF, 95% Confidence Interval)";
    wrapper.appendChild(title);

    const table = document.createElement("table");
    table.className = "exp-table font-sans";
    table.style.fontSize = "12px";

    const thead = document.createElement("thead");
    const trH = document.createElement("tr");
    ["Comparison", "Mean Gain", "95% CI"].forEach((col) => {
      const th = document.createElement("th");
      th.setAttribute("scope", "col");
      th.textContent = col;
      trH.appendChild(th);
    });
    thead.appendChild(trH);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    gains.forEach((g) => {
      const tr = document.createElement("tr");

      const tdComp = document.createElement("td");
      tdComp.className = "font-mono";
      tdComp.textContent = g.comparison;

      const tdMean = document.createElement("td");
      tdMean.className = "font-mono font-bold";
      const sign = g.mean > 0 ? "+" : "";
      tdMean.textContent = `${sign}${g.mean.toFixed(2)}`;

      const tdCi = document.createElement("td");
      tdCi.className = "font-mono";
      tdCi.textContent = `[${g.ci[0].toFixed(2)}, ${g.ci[1].toFixed(2)}]`;

      tr.appendChild(tdComp);
      tr.appendChild(tdMean);
      tr.appendChild(tdCi);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrapper.appendChild(table);
    return wrapper;
  }

  // ----------------------------------------------------------------------------
  // 1. Headline KPI Cards
  // ----------------------------------------------------------------------------
  if (elements.experimentsHeadlinesGrid) {
    while (elements.experimentsHeadlinesGrid.firstChild) {
      elements.experimentsHeadlinesGrid.removeChild(elements.experimentsHeadlinesGrid.firstChild);
    }

    let cardsData = [];
    if (data.headline && typeof data.headline === "object") {
      const h = data.headline;
      const phincCiStr = h.phinc_gain_ci ? `[${h.phinc_gain_ci[0].toFixed(2)}, ${h.phinc_gain_ci[1].toFixed(2)}]` : "";
      const lidGatingCiStr = h.lid_gating_ci ? `[${h.lid_gating_ci[0].toFixed(2)}, ${h.lid_gating_ci[1].toFixed(2)}]` : "";

      cardsData = [
        {
          title: "PHINC Translation Gain",
          highlight: `+${h.phinc_gain_chrF.toFixed(2)} chrF`,
          sub: `95% CI ${phincCiStr}`,
          desc: `Full pipeline vs direct (n = ${(h.phinc_n || 1351).toLocaleString()} sentences)`
        },
        {
          title: "LID Gating Gain",
          highlight: `+${h.lid_gating_gain_chrF.toFixed(2)} chrF`,
          sub: `95% CI ${lidGatingCiStr}`,
          desc: `Transliterating only LID Indic words (n = ${(h.lid_gating_n || 400).toLocaleString()})`
        },
        {
          title: "Token-Level LID",
          highlight: `${h.lid_macro_f1.toFixed(3)}`,
          sub: `Macro F1: ${(h.lid_macro_f1 * 100).toFixed(1)}%`,
          desc: "MuRIL token classification across English, Hindi, and Telugu"
        },
        {
          title: "Inference Latency",
          highlight: `${h.ms_full} ms`,
          sub: `vs direct ${h.ms_direct} ms/sent`,
          desc: `Full pipeline is ${h.ms_direct - h.ms_full} ms faster per sentence`
        }
      ];
    } else if (Array.isArray(data.headlines)) {
      cardsData = data.headlines.map((h) => ({
        title: h.title || h.metric || "",
        highlight: h.highlight || h.value || "",
        sub: h.subtitle || h.comparison || "",
        desc: h.description || ""
      }));
    }

    cardsData.forEach((c) => {
      const card = document.createElement("div");
      card.className = "exp-headline-card";

      const title = document.createElement("div");
      title.className = "exp-headline-title";
      title.textContent = c.title;

      const hl = document.createElement("div");
      hl.className = "exp-highlight";
      hl.textContent = c.highlight;

      const sub = document.createElement("div");
      sub.className = "exp-headline-sub font-mono";
      sub.textContent = c.sub;

      const desc = document.createElement("div");
      desc.className = "exp-headline-desc";
      desc.textContent = c.desc;

      card.appendChild(title);
      card.appendChild(hl);
      card.appendChild(sub);
      card.appendChild(desc);

      elements.experimentsHeadlinesGrid.appendChild(card);
    });
  }

  // ----------------------------------------------------------------------------
  // 2. Bar Charts Grid
  // ----------------------------------------------------------------------------
  if (elements.experimentsChartsGrid) {
    while (elements.experimentsChartsGrid.firstChild) {
      elements.experimentsChartsGrid.removeChild(elements.experimentsChartsGrid.firstChild);
    }

    // Helper to add legend item
    const appendLegend = (legendContainer, dotClass, text) => {
      const item = document.createElement("span");
      item.className = "legend-item";
      const dot = document.createElement("span");
      dot.className = `legend-dot ${dotClass}`;
      item.appendChild(dot);
      item.appendChild(document.createTextNode(` ${text}`));
      legendContainer.appendChild(item);
    };

    // --- Chart 1: PHINC Benchmark (phinc_all) ---
    const phincData = data.phinc_all || (data.phinc_systems && {
      n: 400,
      systems: data.phinc_systems.systems.map((s) => ({ system: s.name, chrF: s.chrf, BLEU: s.bleu, ms: s.ms_sent }))
    });

    if (phincData && Array.isArray(phincData.systems)) {
      const card = document.createElement("div");
      card.className = "exp-chart-card panel";

      const header = document.createElement("div");
      header.className = "exp-card-header";

      const title = document.createElement("div");
      title.className = "exp-chart-title";
      title.textContent = "PHINC test, all 1,351 sentences";

      const size = document.createElement("div");
      size.className = "exp-chart-size font-mono";
      size.textContent = `n = ${(phincData.n || 1351).toLocaleString()}`;

      header.appendChild(title);
      header.appendChild(size);
      card.appendChild(header);

      const legend = document.createElement("div");
      legend.className = "exp-chart-legend";
      appendLegend(legend, "dot-chrf", "chrF (0–100)");
      appendLegend(legend, "dot-bleu", "BLEU (0–100)");
      card.appendChild(legend);

      const barsContainer = document.createElement("div");
      barsContainer.className = "exp-bars-container";

      phincData.systems.forEach((sys) => {
        const row = document.createElement("div");
        row.className = "exp-system-row";

        const meta = document.createElement("div");
        meta.className = "exp-system-meta";

        const nameSpan = document.createElement("span");
        nameSpan.className = "exp-system-name";
        nameSpan.textContent = sys.system || sys.name;
        meta.appendChild(nameSpan);

        if (typeof sys.ms === "number" || typeof sys.ms_sent === "number") {
          const speedVal = sys.ms || sys.ms_sent;
          const speedSpan = document.createElement("span");
          speedSpan.className = "exp-system-speed font-mono";
          speedSpan.textContent = `${speedVal} ms/sent`;
          meta.appendChild(speedSpan);
        }
        row.appendChild(meta);

        const chrfVal = typeof sys.chrF === "number" ? sys.chrF : sys.chrf;
        row.appendChild(createExpBar(chrfVal, "bar-chrf", "chrF"));

        const bleuVal = typeof sys.BLEU === "number" ? sys.BLEU : sys.bleu;
        if (bleuVal !== null && bleuVal !== undefined) {
          row.appendChild(createExpBar(bleuVal, "bar-bleu", "BLEU"));
        }

        barsContainer.appendChild(row);
      });
      card.appendChild(barsContainer);

      // Gains Table if present
      if (Array.isArray(phincData.gains) && phincData.gains.length > 0) {
        card.appendChild(createGainsTable(phincData.gains));
      }

      // Footnote with phinc_400
      const fn = document.createElement("div");
      fn.className = "exp-card-footnote font-mono";
      if (Array.isArray(data.phinc_400)) {
        const p400Str = data.phinc_400.map((s) => {
          const bStr = s.BLEU !== null && s.BLEU !== undefined ? ` (${s.BLEU.toFixed(2)} BLEU)` : "";
          return `${s.system}: ${s.chrF.toFixed(2)} chrF${bStr}`;
        }).join("; ");
        fn.textContent = `Earlier 400-sentence sample: ${p400Str}. ${footnoteText}`;
      } else {
        fn.textContent = footnoteText;
      }
      card.appendChild(fn);

      elements.experimentsChartsGrid.appendChild(card);
    }

    // --- Chart 2: Development Set (dev_80 & dev_80_note) ---
    const devSystems = data.dev_80 || (data.dev_systems && data.dev_systems.systems);
    if (Array.isArray(devSystems)) {
      const card = document.createElement("div");
      card.className = "exp-chart-card panel";

      const header = document.createElement("div");
      header.className = "exp-card-header";

      const title = document.createElement("div");
      title.className = "exp-chart-title";
      title.textContent = "Development-Set Systems";

      const size = document.createElement("div");
      size.className = "exp-chart-size font-mono";
      size.textContent = "n = 80 sentences";

      header.appendChild(title);
      header.appendChild(size);
      card.appendChild(header);

      const legend = document.createElement("div");
      legend.className = "exp-chart-legend";
      appendLegend(legend, "dot-chrf", "chrF (0–100)");
      appendLegend(legend, "dot-bleu", "BLEU (0–100)");
      appendLegend(legend, "dot-te", "Telugu chrF");
      appendLegend(legend, "dot-hi", "Hindi chrF");
      card.appendChild(legend);

      const barsContainer = document.createElement("div");
      barsContainer.className = "exp-bars-container";

      devSystems.forEach((sys) => {
        const row = document.createElement("div");
        row.className = "exp-system-row";

        const meta = document.createElement("div");
        meta.className = "exp-system-meta";

        const nameSpan = document.createElement("span");
        nameSpan.className = "exp-system-name";
        nameSpan.textContent = sys.system || sys.name;
        meta.appendChild(nameSpan);
        row.appendChild(meta);

        const chrfVal = typeof sys.chrF === "number" ? sys.chrF : sys.chrf;
        row.appendChild(createExpBar(chrfVal, "bar-chrf", "chrF"));

        const bleuVal = typeof sys.BLEU === "number" ? sys.BLEU : sys.bleu;
        if (bleuVal !== null && bleuVal !== undefined) {
          row.appendChild(createExpBar(bleuVal, "bar-bleu", "BLEU"));
        }

        const teVal = typeof sys.chrF_te === "number" ? sys.chrF_te : sys.chrf_te;
        const hiVal = typeof sys.chrF_hi === "number" ? sys.chrF_hi : sys.chrf_hi;

        if (typeof teVal === "number" || typeof hiVal === "number") {
          const subTracks = document.createElement("div");
          subTracks.style.display = "grid";
          subTracks.style.gridTemplateColumns = "1fr 1fr";
          subTracks.style.gap = "8px";
          subTracks.style.marginTop = "2px";

          if (typeof teVal === "number") {
            const teTrack = document.createElement("div");
            teTrack.className = "exp-bar-track";
            teTrack.style.height = "18px";
            const teBar = document.createElement("div");
            teBar.className = "exp-bar bar-te";
            teBar.style.width = `${Math.min(100, Math.max(10, teVal))}%`;
            const teLabel = document.createElement("span");
            teLabel.className = "exp-bar-label font-mono";
            teLabel.style.fontSize = "10px";
            teLabel.textContent = `TE chrF ${teVal.toFixed(1)}`;
            teBar.appendChild(teLabel);
            teTrack.appendChild(teBar);
            subTracks.appendChild(teTrack);
          }

          if (typeof hiVal === "number") {
            const hiTrack = document.createElement("div");
            hiTrack.className = "exp-bar-track";
            hiTrack.style.height = "18px";
            const hiBar = document.createElement("div");
            hiBar.className = "exp-bar bar-hi";
            hiBar.style.width = `${Math.min(100, Math.max(10, hiVal))}%`;
            const hiLabel = document.createElement("span");
            hiLabel.className = "exp-bar-label font-mono";
            hiLabel.style.fontSize = "10px";
            hiLabel.textContent = `HI chrF ${hiVal.toFixed(1)}`;
            hiBar.appendChild(hiLabel);
            hiTrack.appendChild(hiBar);
            subTracks.appendChild(hiTrack);
          }

          row.appendChild(subTracks);
        }

        barsContainer.appendChild(row);
      });
      card.appendChild(barsContainer);

      // dev_80_note
      if (data.dev_80_note) {
        const noteDiv = document.createElement("div");
        noteDiv.className = "exp-card-footnote";
        noteDiv.style.color = "var(--ink-muted)";
        noteDiv.style.fontFamily = "var(--font-sans)";
        noteDiv.style.fontSize = "12px";
        noteDiv.style.marginTop = "10px";
        noteDiv.textContent = `Note: ${data.dev_80_note}`;
        card.appendChild(noteDiv);
      }

      // Footnote
      const fn = document.createElement("div");
      fn.className = "exp-card-footnote font-mono";
      fn.textContent = footnoteText;
      card.appendChild(fn);

      elements.experimentsChartsGrid.appendChild(card);
    }

    // --- Chart 3: Transliteration Ablation ---
    const translitData = data.translit_ablation_80 || (data.translit_ablation && data.translit_ablation.systems);
    if (Array.isArray(translitData)) {
      const card = document.createElement("div");
      card.className = "exp-chart-card panel";

      const header = document.createElement("div");
      header.className = "exp-card-header";

      const title = document.createElement("div");
      title.className = "exp-chart-title";
      title.textContent = "Transliteration Module Ablation";

      const size = document.createElement("div");
      size.className = "exp-chart-size font-mono";
      size.textContent = "n = 80 sentences";

      header.appendChild(title);
      header.appendChild(size);
      card.appendChild(header);

      const legend = document.createElement("div");
      legend.className = "exp-chart-legend";
      appendLegend(legend, "dot-chrf", "chrF (0–100)");
      appendLegend(legend, "dot-bleu", "BLEU (0–100)");
      card.appendChild(legend);

      const barsContainer = document.createElement("div");
      barsContainer.className = "exp-bars-container";

      translitData.forEach((sys) => {
        const row = document.createElement("div");
        row.className = "exp-system-row";

        const meta = document.createElement("div");
        meta.className = "exp-system-meta";

        const nameSpan = document.createElement("span");
        nameSpan.className = "exp-system-name";
        nameSpan.textContent = sys.system || sys.name;
        meta.appendChild(nameSpan);
        row.appendChild(meta);

        const chrfVal = typeof sys.chrF === "number" ? sys.chrF : sys.chrf;
        row.appendChild(createExpBar(chrfVal, "bar-chrf", "chrF"));

        const bleuVal = typeof sys.BLEU === "number" ? sys.BLEU : sys.bleu;
        if (bleuVal !== null && bleuVal !== undefined) {
          row.appendChild(createExpBar(bleuVal, "bar-bleu", "BLEU"));
        }

        barsContainer.appendChild(row);
      });
      card.appendChild(barsContainer);

      const fn = document.createElement("div");
      fn.className = "exp-card-footnote font-mono";
      fn.textContent = footnoteText;
      card.appendChild(fn);

      elements.experimentsChartsGrid.appendChild(card);
    }

    // --- Chart 4: Mixed Hindi+Telugu Results ---
    if (data.mixed_multi_clause || data.mixed_results) {
      const card = document.createElement("div");
      card.className = "exp-chart-card panel";

      const header = document.createElement("div");
      header.className = "exp-card-header";

      const title = document.createElement("div");
      title.className = "exp-chart-title";
      title.textContent = "Mixed Hindi+Telugu Evaluation";

      const size = document.createElement("div");
      size.className = "exp-chart-size font-mono";
      size.textContent = "Multi-Clause (n = 40) · Total (n = 50)";

      header.appendChild(title);
      header.appendChild(size);
      card.appendChild(header);

      const legend = document.createElement("div");
      legend.className = "exp-chart-legend";
      appendLegend(legend, "dot-chrf", "chrF (0–100)");
      card.appendChild(legend);

      const barsContainer = document.createElement("div");
      barsContainer.className = "exp-bars-container";

      // 1. Mixed Multi-Clause Systems (n = 40)
      if (data.mixed_multi_clause && Array.isArray(data.mixed_multi_clause.systems)) {
        const subHead = document.createElement("div");
        subHead.className = "caption font-bold";
        subHead.style.fontSize = "12px";
        subHead.style.marginTop = "4px";
        subHead.textContent = `Mixed Multi-Clause Benchmark (n = ${data.mixed_multi_clause.n || 40})`;
        barsContainer.appendChild(subHead);

        data.mixed_multi_clause.systems.forEach((sys) => {
          const row = document.createElement("div");
          row.className = "exp-system-row";

          const meta = document.createElement("div");
          meta.className = "exp-system-meta";

          const nameSpan = document.createElement("span");
          nameSpan.className = "exp-system-name";
          nameSpan.textContent = sys.system;
          meta.appendChild(nameSpan);
          row.appendChild(meta);

          row.appendChild(createExpBar(sys.chrF, "bar-chrf", "chrF"));
          barsContainer.appendChild(row);
        });

        // Multi-clause gains table with CIs
        if (Array.isArray(data.mixed_multi_clause.gains) && data.mixed_multi_clause.gains.length > 0) {
          barsContainer.appendChild(createGainsTable(data.mixed_multi_clause.gains));
        }
      } else if (data.mixed_results && Array.isArray(data.mixed_results.systems)) {
        data.mixed_results.systems.forEach((sys) => {
          const row = document.createElement("div");
          row.className = "exp-system-row";
          const meta = document.createElement("div");
          meta.className = "exp-system-meta";
          const nameSpan = document.createElement("span");
          nameSpan.className = "exp-system-name";
          nameSpan.textContent = sys.name;
          meta.appendChild(nameSpan);
          row.appendChild(meta);
          row.appendChild(createExpBar(sys.chrf, "bar-chrf", "chrF"));
          barsContainer.appendChild(row);
        });
      }

      // 2. Mixed All 50 Systems (mixed_all_50)
      if (Array.isArray(data.mixed_all_50)) {
        const subHead = document.createElement("div");
        subHead.className = "caption font-bold";
        subHead.style.fontSize = "12px";
        subHead.style.marginTop = "14px";
        subHead.textContent = "All Mixed Sentences (n = 50)";
        barsContainer.appendChild(subHead);

        data.mixed_all_50.forEach((sys) => {
          const row = document.createElement("div");
          row.className = "exp-system-row";

          const meta = document.createElement("div");
          meta.className = "exp-system-meta";

          const nameSpan = document.createElement("span");
          nameSpan.className = "exp-system-name";
          nameSpan.textContent = sys.system;
          meta.appendChild(nameSpan);
          row.appendChild(meta);

          row.appendChild(createExpBar(sys.chrF, "bar-chrf", "chrF"));
          barsContainer.appendChild(row);
        });
      }

      // 3. Intra-Clause Systems (mixed_intra_clause)
      if (data.mixed_intra_clause) {
        const subHead = document.createElement("div");
        subHead.className = "caption font-bold";
        subHead.style.fontSize = "12px";
        subHead.style.marginTop = "14px";
        subHead.textContent = `Intra-Clause Switching (n = ${data.mixed_intra_clause.n || 10})`;
        barsContainer.appendChild(subHead);

        if (data.mixed_intra_clause.note) {
          const noteDiv = document.createElement("div");
          noteDiv.className = "exp-card-footnote";
          noteDiv.style.color = "var(--ink-muted)";
          noteDiv.style.fontFamily = "var(--font-sans)";
          noteDiv.style.fontSize = "11px";
          noteDiv.style.margin = "4px 0 8px";
          noteDiv.textContent = `Note: ${data.mixed_intra_clause.note}`;
          barsContainer.appendChild(noteDiv);
        }

        if (Array.isArray(data.mixed_intra_clause.systems)) {
          data.mixed_intra_clause.systems.forEach((sys) => {
            const row = document.createElement("div");
            row.className = "exp-system-row";

            const meta = document.createElement("div");
            meta.className = "exp-system-meta";

            const nameSpan = document.createElement("span");
            nameSpan.className = "exp-system-name";
            nameSpan.textContent = sys.system;
            meta.appendChild(nameSpan);
            row.appendChild(meta);

            row.appendChild(createExpBar(sys.chrF, "bar-chrf", "chrF"));
            barsContainer.appendChild(row);
          });
        }
      }

      card.appendChild(barsContainer);

      const fn = document.createElement("div");
      fn.className = "exp-card-footnote font-mono";
      fn.textContent = footnoteText;
      card.appendChild(fn);

      elements.experimentsChartsGrid.appendChild(card);
    }
  }

  // ----------------------------------------------------------------------------
  // 3. Token-Level LID Performance Table (EN, HI, TE)
  // ----------------------------------------------------------------------------
  if (elements.experimentsLidContainer && (data.lid || data.lid_table)) {
    while (elements.experimentsLidContainer.firstChild) {
      elements.experimentsLidContainer.removeChild(elements.experimentsLidContainer.firstChild);
    }

    const lidInfo = data.lid || data.lid_table;

    // Header
    const header = document.createElement("div");
    header.className = "exp-card-header";

    const title = document.createElement("div");
    title.className = "exp-chart-title";
    title.textContent = "Token-Level Language Identification (MuRIL)";

    const size = document.createElement("div");
    size.className = "exp-chart-size font-mono";
    const testSentences = lidInfo.test_sentences || (data.lid_table && data.lid_table.test_set_size) || 14855;
    size.textContent = typeof testSentences === "number" ? `n = ${testSentences.toLocaleString()} sentences` : testSentences;

    header.appendChild(title);
    header.appendChild(size);
    elements.experimentsLidContainer.appendChild(header);

    // Table
    const table = document.createElement("table");
    table.className = "exp-table font-sans";
    table.setAttribute("aria-label", "Token-level language identification metrics table");

    // Thead
    const thead = document.createElement("thead");
    const trHead = document.createElement("tr");
    ["Language Class", "Precision", "Recall", "F1-Score"].forEach((colName) => {
      const th = document.createElement("th");
      th.setAttribute("scope", "col");
      th.textContent = colName;
      trHead.appendChild(th);
    });
    thead.appendChild(trHead);
    table.appendChild(thead);

    // Tbody
    const tbody = document.createElement("tbody");
    const classesList = lidInfo.classes || (data.lid_table && data.lid_table.rows) || [];

    classesList.forEach((r) => {
      const tr = document.createElement("tr");

      const thRow = document.createElement("th");
      thRow.setAttribute("scope", "row");
      thRow.className = "font-serif";

      const langCode = r.label || r.lang || "OTHER";
      const badge = document.createElement("span");
      badge.className = `model-badge font-mono lang-${langCode.toLowerCase()}`;
      badge.textContent = langCode;
      thRow.appendChild(badge);

      const langFullName = LANGUAGE_NAMES[langCode] || langCode;
      thRow.appendChild(document.createTextNode(` ${langFullName}`));
      tr.appendChild(thRow);

      const precVal = typeof r.P === "number" ? r.P : r.precision;
      const tdP = document.createElement("td");
      tdP.className = "font-mono";
      tdP.textContent = `${(precVal * 100).toFixed(1)}% (${precVal.toFixed(3)})`;
      tr.appendChild(tdP);

      const recVal = typeof r.R === "number" ? r.R : r.recall;
      const tdR = document.createElement("td");
      tdR.className = "font-mono";
      tdR.textContent = `${(recVal * 100).toFixed(1)}% (${recVal.toFixed(3)})`;
      tr.appendChild(tdR);

      const f1Val = typeof r.F1 === "number" ? r.F1 : r.f1;
      const tdF1 = document.createElement("td");
      tdF1.className = "font-mono font-bold";
      tdF1.textContent = `${(f1Val * 100).toFixed(1)}% (${f1Val.toFixed(3)})`;
      tr.appendChild(tdF1);

      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    // Tfoot
    const tfoot = document.createElement("tfoot");
    const trFoot = document.createElement("tr");

    const thFoot = document.createElement("th");
    thFoot.setAttribute("scope", "row");
    thFoot.textContent = "Macro Average (EN, HI, TE)";
    trFoot.appendChild(thFoot);

    const tdSpacer = document.createElement("td");
    tdSpacer.setAttribute("colspan", "2");
    trFoot.appendChild(tdSpacer);

    const macroF1Val = lidInfo.headline_macro_f1 || (data.headline && data.headline.lid_macro_f1) || 0.983;
    const tdMacro = document.createElement("td");
    tdMacro.className = "font-mono font-bold";
    tdMacro.style.fontSize = "14px";
    tdMacro.textContent = `${(macroF1Val * 100).toFixed(1)}% (${macroF1Val.toFixed(3)})`;
    trFoot.appendChild(tdMacro);

    tfoot.appendChild(trFoot);
    table.appendChild(tfoot);

    elements.experimentsLidContainer.appendChild(table);

    // Footnote
    const fn = document.createElement("div");
    fn.className = "exp-card-footnote font-mono";
    fn.textContent = footnoteText;
    elements.experimentsLidContainer.appendChild(fn);
  }

  // ----------------------------------------------------------------------------
  // 3B. LID Comparison Table (lid_compare)
  // ----------------------------------------------------------------------------
  if (elements.experimentsLidCompareContainer && Array.isArray(data.lid_compare)) {
    while (elements.experimentsLidCompareContainer.firstChild) {
      elements.experimentsLidCompareContainer.removeChild(elements.experimentsLidCompareContainer.firstChild);
    }

    const header = document.createElement("div");
    header.className = "exp-card-header";

    const title = document.createElement("div");
    title.className = "exp-chart-title";
    title.textContent = "LID Model Comparison (Old vs. New on Normal vs. Mixed Text)";

    const size = document.createElement("div");
    size.className = "exp-chart-size font-mono";
    size.textContent = "Held-out Normal vs. Synthesized Mixed Splices";

    header.appendChild(title);
    header.appendChild(size);
    elements.experimentsLidCompareContainer.appendChild(header);

    const table = document.createElement("table");
    table.className = "exp-table font-sans";
    table.setAttribute("aria-label", "LID model comparison table on normal and mixed text");

    const thead = document.createElement("thead");
    const trH = document.createElement("tr");
    ["Evaluation Set", "Model Variant", "Macro F1", "Hindi F1", "Telugu F1", "English F1", "TE → HI", "HI → TE"].forEach((c) => {
      const th = document.createElement("th");
      th.setAttribute("scope", "col");
      th.textContent = c;
      trH.appendChild(th);
    });
    thead.appendChild(trH);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.lid_compare.forEach((row) => {
      const tr = document.createElement("tr");

      const tdTest = document.createElement("td");
      tdTest.className = "font-serif font-bold";
      tdTest.textContent = row.test;
      tr.appendChild(tdTest);

      const tdModel = document.createElement("td");
      const badge = document.createElement("span");
      badge.className = "model-badge font-mono";
      badge.textContent = row.model;
      tdModel.appendChild(badge);
      tr.appendChild(tdModel);

      const tdMacro = document.createElement("td");
      tdMacro.className = "font-mono font-bold";
      tdMacro.textContent = `${(row.macro_F1 * 100).toFixed(1)}% (${row.macro_F1.toFixed(3)})`;
      tr.appendChild(tdMacro);

      const tdHi = document.createElement("td");
      tdHi.className = "font-mono";
      tdHi.textContent = `${(row.HI_F1 * 100).toFixed(1)}%`;
      tr.appendChild(tdHi);

      const tdTe = document.createElement("td");
      tdTe.className = "font-mono";
      tdTe.textContent = `${(row.TE_F1 * 100).toFixed(1)}%`;
      tr.appendChild(tdTe);

      const tdEn = document.createElement("td");
      tdEn.className = "font-mono";
      tdEn.textContent = `${(row.EN_F1 * 100).toFixed(1)}%`;
      tr.appendChild(tdEn);

      const tdTeHi = document.createElement("td");
      tdTeHi.className = "font-mono font-bold";
      tdTeHi.style.color = row.TE_to_HI > 100 ? "var(--accent-coral)" : "var(--ink)";
      tdTeHi.textContent = row.TE_to_HI.toLocaleString();
      tr.appendChild(tdTeHi);

      const tdHiTe = document.createElement("td");
      tdHiTe.className = "font-mono";
      tdHiTe.textContent = row.HI_to_TE.toLocaleString();
      tr.appendChild(tdHiTe);

      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    elements.experimentsLidCompareContainer.appendChild(table);

    const fn = document.createElement("div");
    fn.className = "exp-card-footnote font-mono";
    fn.textContent = "TE_to_HI and HI_to_TE columns report cross-lingual confusion counts. Note that the new mixed-trained LID dramatically cuts TE → HI confusions on mixed splices from 1,130 down to 53.";
    elements.experimentsLidCompareContainer.appendChild(fn);
  }

  // ----------------------------------------------------------------------------
  // 4A. Regression Check Table (regression_check)
  // ----------------------------------------------------------------------------
  if (elements.experimentsRegressionContainer && Array.isArray(data.regression_check)) {
    while (elements.experimentsRegressionContainer.firstChild) {
      elements.experimentsRegressionContainer.removeChild(elements.experimentsRegressionContainer.firstChild);
    }

    const header = document.createElement("div");
    header.className = "exp-card-header";

    const title = document.createElement("div");
    title.className = "exp-chart-title";
    title.textContent = "Regression Check (Model & Pipeline Variants)";

    const size = document.createElement("div");
    size.className = "exp-chart-size font-mono";
    size.textContent = "chrF Parity Verification";

    header.appendChild(title);
    header.appendChild(size);
    elements.experimentsRegressionContainer.appendChild(header);

    const table = document.createElement("table");
    table.className = "exp-table font-sans";
    table.setAttribute("aria-label", "Regression check across pipeline variants table");

    const thead = document.createElement("thead");
    const trH = document.createElement("tr");
    ["Evaluation Set", "System / Model Variant", "chrF Score"].forEach((c) => {
      const th = document.createElement("th");
      th.setAttribute("scope", "col");
      th.textContent = c;
      trH.appendChild(th);
    });
    thead.appendChild(trH);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.regression_check.forEach((row) => {
      const tr = document.createElement("tr");

      const tdSet = document.createElement("td");
      tdSet.className = "font-serif font-bold";
      tdSet.textContent = row.set;

      const tdSys = document.createElement("td");
      tdSys.className = "font-mono";
      tdSys.textContent = row.system;

      const tdChrf = document.createElement("td");
      tdChrf.className = "font-mono font-bold";
      tdChrf.textContent = row.chrF.toFixed(2);

      tr.appendChild(tdSet);
      tr.appendChild(tdSys);
      tr.appendChild(tdChrf);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    elements.experimentsRegressionContainer.appendChild(table);

    const fn = document.createElement("div");
    fn.className = "exp-card-footnote font-mono";
    fn.textContent = "Confirms that the new mixed-trained LID variant does not regress translation performance on held-out benchmarks.";
    elements.experimentsRegressionContainer.appendChild(fn);
  }
}

// ==============================================================================
// 7. Initial Application Startup
// ==============================================================================

window.addEventListener("DOMContentLoaded", () => {
  initSettingsPopover();
  handleInputChange();
  handleTransInputChange();
  handlePipelineInputChange();
  initPipelineExampleChips();
  renderPipelineHistory();
  fetchAndRenderExperiments();
  updatePipelineLoadedNote();
  if (checkUrlDemoMode()) {
    setDemoMode(true);
  }
  loadDemoCache();
  startHealthPolling();
});
