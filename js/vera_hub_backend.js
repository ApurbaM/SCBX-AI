/**
 * EcliptOS Vera Hub — browser backend connector (configurable).
 *
 * Configure (pick one):
 * - URL query: ?veraHub=https://your-host/api
 * - localStorage: veraHubBaseUrl, veraHubApiKey (optional Bearer / X-API-Key)
 * - Repo default: js/vera_hub_config.js → window.__VERA_HUB_DEFAULT_BASE__
 * - Disconnect vs default: clearing URL in Configure sets veraHubDisabled=1 (see resolveBase)
 *
 * Expected cockpit metrics (first successful GET wins), try in order:
 *   GET {base}/api/v1/cockpit/metrics?personaId=&horizon=
 *   GET {base}/cockpit/metrics?personaId=&horizon=
 *   GET {base}/metrics/cockpit?persona=
 *
 * Response shape (flexible): { computed: { inquiryContain, avgRespSec, ... } }
 *   or { metrics: {...} } or flat numeric fields.
 *
 * Ontology (optional): GET {base}/api/v1/ontology  or {base}/ontology/graph
 *   → { ontology: { nodes, edges } } or { nodes, edges }
 *
 * CORS: Vera Hub must allow this origin, or serve the HTML from the same host / use a reverse proxy.
 */
(function (global) {
  "use strict";

  var overlay = null;
  var ontologyOverlay = null;
  var status = { state: "off", detail: "", lastSync: null };
  var debounceTimer = null;
  var lastSyncKey = "";

  function defaultBaseFromConfig() {
    try {
      var d = global.__VERA_HUB_DEFAULT_BASE__;
      if (d == null || String(d).trim() === "") return "";
      return String(d).trim().replace(/\/+$/, "");
    } catch (e) {
      return "";
    }
  }

  function resolveBase() {
    try {
      var q = new URLSearchParams(location.search).get("veraHub");
      if (q != null && String(q).trim() !== "") return String(q).trim().replace(/\/+$/, "");
    } catch (e) {}
    try {
      if (localStorage.getItem("veraHubDisabled") === "1") return "";
    } catch (e0) {}
    try {
      var s = localStorage.getItem("veraHubBaseUrl");
      if (s != null && String(s).trim() !== "") return String(s).trim().replace(/\/+$/, "");
    } catch (e2) {
      return "";
    }
    return defaultBaseFromConfig();
  }

  function resolveKey() {
    try {
      return (localStorage.getItem("veraHubApiKey") || "").trim();
    } catch (e) {
      return "";
    }
  }

  function timeoutMs() {
    var t = parseInt(localStorage.getItem("veraHubTimeoutMs") || "", 10);
    return !isNaN(t) && t >= 3000 ? t : 15000;
  }

  function fetchJson(path, method, body) {
    var base = resolveBase();
    if (!base) return Promise.reject(new Error("Vera Hub base URL not set"));
    var url = base + (path.charAt(0) === "/" ? path : "/" + path);
    var headers = { Accept: "application/json" };
    var key = resolveKey();
    if (key) {
      headers["Authorization"] = "Bearer " + key;
      headers["X-API-Key"] = key;
    }
    if (body != null) {
      headers["Content-Type"] = "application/json";
    }
    var ctrl = new AbortController();
    var tid = setTimeout(function () {
      ctrl.abort();
    }, timeoutMs());
    return fetch(url, {
      method: method || "GET",
      headers: headers,
      body: body != null ? JSON.stringify(body) : undefined,
      signal: ctrl.signal,
      credentials: "omit"
    })
      .then(function (r) {
        clearTimeout(tid);
        if (!r.ok) throw new Error(r.status + " " + r.statusText);
        return r.json();
      })
      .catch(function (e) {
        clearTimeout(tid);
        throw e;
      });
  }

  function normalizeMetrics(data) {
    if (!data || typeof data !== "object") return null;
    var c = data.computed || data.metrics || data.data || data;
    if (!c || typeof c !== "object") return null;
    var keys = [
      "inquiryContain",
      "avgRespSec",
      "taskCompletion",
      "callDeflect",
      "fcr",
      "dauUplift",
      "timeSpent",
      "revenueUplift",
      "nps",
      "receptionist",
      "butler",
      "banker"
    ];
    var out = {};
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      var v = c[k];
      if (typeof v === "number" && !isNaN(v)) out[k] = v;
    }
    return Object.keys(out).length ? out : null;
  }

  function normalizeOntology(data) {
    if (!data || typeof data !== "object") return null;
    var o = data.ontology || data.graph || data;
    if (!o || !Array.isArray(o.nodes) || !Array.isArray(o.edges)) return null;
    return { nodes: o.nodes, edges: o.edges };
  }

  function syncCockpitMetrics(ctx) {
    var base = resolveBase();
    if (!base) {
      overlay = null;
      status = { state: "off", detail: "Using local mock metrics.", lastSync: null };
      return Promise.resolve();
    }
    status = { state: "syncing", detail: base, lastSync: status.lastSync };
    var personaId = (ctx && ctx.personaId) || "";
    var horizon = (ctx && ctx.horizon) || "day";
    var paths = [
      "/api/v1/cockpit/metrics?personaId=" + encodeURIComponent(personaId) + "&horizon=" + encodeURIComponent(horizon),
      "/cockpit/metrics?personaId=" + encodeURIComponent(personaId) + "&horizon=" + encodeURIComponent(horizon),
      "/metrics/cockpit?persona=" + encodeURIComponent(personaId) + "&horizon=" + encodeURIComponent(horizon)
    ];
    var chain = Promise.reject(new Error("try next"));
    for (var p = 0; p < paths.length; p++) {
      (function (path) {
        chain = chain.catch(function () {
          return fetchJson(path, "GET", null);
        });
      })(paths[p]);
    }
    return chain
      .then(function (data) {
        overlay = normalizeMetrics(data);
        status = {
          state: overlay ? "ok" : "error",
          detail: overlay ? "Metrics merged from Vera Hub." : "Response had no numeric metrics fields.",
          lastSync: new Date().toISOString()
        };
      })
      .catch(function (e) {
        overlay = null;
        status = {
          state: "error",
          detail: e && e.name === "AbortError" ? "Request timed out." : String(e.message || e),
          lastSync: null
        };
      });
  }

  function syncOntology() {
    var base = resolveBase();
    if (!base) {
      ontologyOverlay = null;
      return Promise.resolve(null);
    }
    var paths = ["/api/v1/ontology", "/ontology/graph", "/ontology"];
    var chain = Promise.reject(new Error("try next"));
    for (var i = 0; i < paths.length; i++) {
      (function (path) {
        chain = chain.catch(function () {
          return fetchJson(path, "GET", null);
        });
      })(paths[i]);
    }
    return chain
      .then(function (data) {
        ontologyOverlay = normalizeOntology(data);
        return ontologyOverlay;
      })
      .catch(function () {
        ontologyOverlay = null;
        return null;
      });
  }

  function scheduleDashboardSync(ctx, onDone) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      var key = (ctx.personaId || "") + "|" + (ctx.horizon || "");
      syncCockpitMetrics(ctx).then(function () {
        lastSyncKey = key;
        if (typeof onDone === "function") onDone();
      });
    }, 400);
  }

  function configure() {
    if (typeof prompt !== "function") return;
    var cur =
      (function () {
        try {
          var q = new URLSearchParams(location.search).get("veraHub");
          if (q != null && String(q).trim() !== "") return String(q).trim().replace(/\/+$/, "");
        } catch (e) {}
        try {
          var s = localStorage.getItem("veraHubBaseUrl");
          if (s != null && String(s).trim() !== "") return String(s).trim().replace(/\/+$/, "");
        } catch (e2) {}
        return defaultBaseFromConfig();
      })();
    var u = prompt(
      "EcliptOS Vera Hub base URL (https://… , no trailing slash).\nLeave empty to use mock data (skips repo default in vera_hub_config.js).",
      cur || ""
    );
    if (u === null) return;
    u = String(u).trim().replace(/\/+$/, "");
    try {
      if (u) {
        localStorage.setItem("veraHubBaseUrl", u);
        localStorage.removeItem("veraHubDisabled");
      } else {
        localStorage.removeItem("veraHubBaseUrl");
        if (defaultBaseFromConfig()) localStorage.setItem("veraHubDisabled", "1");
        else localStorage.removeItem("veraHubDisabled");
      }
    } catch (e) {}
    var k = prompt(
      "API key (optional; sent as Authorization Bearer and X-API-Key).\nLeave empty to remove stored key.",
      ""
    );
    if (k !== null) {
      try {
        k = String(k).trim();
        if (k) localStorage.setItem("veraHubApiKey", k);
        else localStorage.removeItem("veraHubApiKey");
      } catch (e2) {}
    }
    overlay = null;
    lastSyncKey = "";
    status = { state: "off", detail: "", lastSync: null };
  }

  function getOverlay() {
    return overlay;
  }

  function getOntologyOverlay() {
    return ontologyOverlay;
  }

  function getStatus() {
    return status;
  }

  global.VeraHubBackend = {
    resolveBase: resolveBase,
    defaultBaseFromConfig: defaultBaseFromConfig,
    resolveKey: resolveKey,
    getOverlay: getOverlay,
    getOntologyOverlay: getOntologyOverlay,
    getStatus: getStatus,
    syncCockpitMetrics: syncCockpitMetrics,
    syncOntology: syncOntology,
    scheduleDashboardSync: scheduleDashboardSync,
    configure: configure,
    normalizeMetrics: normalizeMetrics,
    normalizeOntology: normalizeOntology
  };
})(typeof window !== "undefined" ? window : this);
