/**
 * EcliptOS Vera Hub — default endpoint for this prototype checkout.
 *
 * Set to your real API root (no trailing slash). Examples:
 *   https://vera-hub.your-org.com
 *   https://your-org.com/ecliptos/vera/api
 *
 * Precedence (highest first): URL ?veraHub=… → localStorage.veraHubBaseUrl → this default.
 * To force mock data after a default is set here, use CXO “Configure endpoint” and clear the URL
 * (stores veraHubDisabled so this default is skipped until you save a URL again).
 */
window.__VERA_HUB_DEFAULT_BASE__ = "";
