/* Creme Theme — warm ivory/terracotta palette in the Anthropic editorial style.
 *
 * Pure stylesheet injection: the core dark theme stays untouched on disk and this
 * plugin appends one <style> element after it, so equal-specificity rules win by
 * source order. Section one retints the design-system custom properties; section
 * two re-covers every core rule that hardcodes a dark color instead of reading a
 * variable (audited against core style.css — see tests/test_frontend.py, which
 * fails if core grows a new :root variable this theme does not override).
 */

const STYLE_ID = 'dev-alex-tavern-theme-creme';

const THEME_CSS = `
/* ═══════════ 1. Design-system variables ═══════════ */
:root {
    color-scheme: light;

    /* Surfaces — ivory page, lighter cards for elevation */
    --bg-0: #F0EEE6;
    --bg-1: #F6F4ED;
    --bg-2: #FAF9F5;
    --surface: rgba(252, 250, 245, 0.78);
    --surface-solid: #F7F5EE;
    --surface-hi: rgba(255, 255, 255, 0.88);
    --glass-border: rgba(32, 29, 24, 0.09);
    --glass-border-hi: rgba(32, 29, 24, 0.17);

    /* Text — warm ink */
    --text-1: #201D18;
    --text-2: #524C42;
    --text-3: #8A8375;

    /* Accent — book-cloth terracotta → coral gradient */
    --accent: #BC5B3D;
    --accent-2: #D97757;
    --accent-glow: rgba(202, 100, 66, 0.25);
    --accent-grad: linear-gradient(135deg, #BC5B3D 0%, #D97757 100%);

    --danger: #B23A4C;
    --success: #3E8460;

    /* Character palette — saturated but ink-dark, readable on cream */
    --c-0: #3D6DB4;
    --c-1: #8A5FB8;
    --c-2: #3E8460;
    --c-3: #B57F2E;
    --c-4: #C2588B;
    --c-5: #2E8C96;
}

/* ═══════════ 2. Rules that hardcode dark colors ═══════════ */

/* Page glow: coral + kraft washes instead of indigo/violet */
html, body {
    background:
        radial-gradient(1200px 600px at 75% -10%, rgba(217, 119, 87, 0.10), transparent 60%),
        radial-gradient(900px 500px at 10% 110%, rgba(212, 162, 127, 0.14), transparent 55%),
        var(--bg-0);
    background-attachment: fixed;
}

/* Buttons */
.btn:hover { background: rgba(235, 230, 218, 0.95); }
.btn-ghost:hover { background: rgba(188, 91, 61, 0.08); }
.input-expand-btn:hover { background: rgba(235, 230, 218, 0.95); }
#setup-close-btn { background: rgba(32, 29, 24, 0.04); }

.btn-danger-ghost { color: #A32E40; border-color: rgba(178, 58, 76, 0.30); }
.btn-danger-ghost:hover { color: #7E1F2F; background: rgba(178, 58, 76, 0.10); }
.btn-danger {
    border-color: rgba(178, 58, 76, 0.7);
    background: linear-gradient(135deg, #A83648, #C74E60);
    box-shadow: 0 4px 18px rgba(178, 58, 76, 0.22);
}
.btn-danger:hover { background: linear-gradient(135deg, #B23A4C, #D25A6C); }

/* Plugin Center trigger + shell */
.plugin-center-trigger {
    color: #A04E2F;
    border-color: rgba(188, 91, 61, 0.30);
    background: radial-gradient(circle at 50% 35%, rgba(217, 119, 87, 0.16), transparent 70%);
}
.overlay { background: rgba(46, 40, 31, 0.42); }
.modal {
    background: linear-gradient(180deg, rgba(252, 250, 245, 0.97), rgba(244, 241, 232, 0.98));
    box-shadow: 0 30px 80px rgba(64, 52, 37, 0.28), 0 0 0 1px rgba(188, 91, 61, 0.07);
}
.plugin-tab.active { color: #A04E2F; border-bottom-color: #BC5B3D; }
.plugin-update-count { background: #BC5B3D; color: #FFF9F2; }

.experience-hero {
    border: 1px solid rgba(188, 91, 61, 0.24);
    background:
        radial-gradient(circle at 85% 15%, rgba(217, 119, 87, 0.20), transparent 38%),
        linear-gradient(125deg, rgba(240, 227, 210, 0.85), rgba(250, 247, 240, 0.90));
}
.experience-kicker { color: #A04E2F; }
.experience-card, .plugin-card, .activity-row { background: rgba(32, 29, 24, 0.03); }
.experience-card.active { border-color: rgba(62, 132, 96, 0.32); }
.experience-active-badge {
    border: 1px solid rgba(62, 132, 96, 0.42);
    background: rgba(62, 132, 96, 0.10);
    color: #2E6E4E;
}
.experience-visual { background: linear-gradient(135deg, #E7D3BE, #D3DECE); }
.experience-visual span, .plugin-permissions span {
    border: 1px solid rgba(32, 29, 24, 0.12);
    background: rgba(252, 250, 245, 0.82);
}
.plugin-trust-note { color: #8A6A1F; }
.plugin-card.active { border-color: rgba(62, 132, 96, 0.32); }
.plugin-card.has-update {
    border-color: rgba(188, 91, 61, 0.5);
    box-shadow: inset 3px 0 #BC5B3D;
}
.plugin-update-badge {
    border: 1px solid rgba(188, 91, 61, 0.4);
    background: rgba(188, 91, 61, 0.10);
    color: #A04E2F;
}
.plugin-update-badge.conflict { border-color: rgba(178, 125, 32, 0.45); color: #8A6A1F; }
.plugin-meta { color: #96867A; }
.plugin-release-rail { background: rgba(188, 91, 61, 0.07); }
.plugin-release-rail i { background: linear-gradient(90deg, #C9B39A, #BC5B3D); }
.plugin-release-rail strong { color: #A04E2F; }
.plugin-version-row { background: rgba(32, 29, 24, 0.04); }
.plugin-version-row code { color: #7A6A5A; }
.plugin-version-row.active > span { color: #2E6E4E; }

.plugin-confirm-layer { background: rgba(46, 40, 31, 0.46); }
.plugin-confirm-panel {
    border: 1px solid rgba(188, 91, 61, 0.30);
    background:
        radial-gradient(circle at 90% 0%, rgba(217, 119, 87, 0.14), transparent 34%),
        #FAF8F1;
    box-shadow: 0 28px 70px rgba(64, 52, 37, 0.26);
}
.plugin-confirm-kicker { color: #A04E2F; }
.plugin-confirm-list li { background: rgba(32, 29, 24, 0.03); }
.plugin-confirm-list li > div span { color: #96867A; }
.plugin-confirm-status { color: #2E6E4E; }
.plugin-confirm-status.danger { color: #A32E40; }

/* Compaction */
.compaction-control {
    background:
        radial-gradient(circle at 92% 0%, rgba(217, 119, 87, 0.12), transparent 36%),
        var(--bg-1);
}
.compaction-warning-box {
    border: 1px solid rgba(178, 125, 32, 0.35);
    background: rgba(178, 125, 32, 0.07);
}
.compaction-threshold input[type='range']::-webkit-slider-runnable-track {
    background: linear-gradient(90deg, var(--success), var(--accent) 68%, #B57F2E);
}
.compaction-threshold input[type='range']::-moz-range-track {
    background: linear-gradient(90deg, var(--success), var(--accent) 68%, #B57F2E);
}
.compaction-threshold input[type='range']::-webkit-slider-thumb {
    box-shadow: 0 0 0 2px var(--accent), 0 3px 10px rgba(64, 52, 37, 0.28);
}
.compaction-threshold input[type='range']::-moz-range-thumb {
    box-shadow: 0 0 0 2px var(--accent), 0 3px 10px rgba(64, 52, 37, 0.28);
}

/* Setup sections */
.section { background: rgba(32, 29, 24, 0.02); }
.app-preferences-section {
    border-color: rgba(61, 109, 180, 0.30);
    background: rgba(61, 109, 180, 0.06);
}
.ai-engine-section {
    background:
        linear-gradient(135deg, rgba(188, 91, 61, 0.07), transparent 48%),
        rgba(32, 29, 24, 0.02);
}
.engine-status {
    border: 1px solid rgba(62, 132, 96, 0.40);
    background: rgba(62, 132, 96, 0.08);
}
.engine-status.cloud {
    color: #2F5E9E;
    border-color: rgba(61, 109, 180, 0.42);
    background: rgba(61, 109, 180, 0.08);
}
.provider-card { background: rgba(255, 255, 255, 0.60); }
.provider-card.active {
    background: rgba(188, 91, 61, 0.08);
    box-shadow: inset 0 0 0 1px rgba(188, 91, 61, 0.18), 0 8px 28px rgba(64, 52, 37, 0.12);
}
.provider-orbit-cloud { color: #3D6DB4; }
.provider-panel { background: rgba(255, 255, 255, 0.55); }
.reasoning-lock {
    border: 1px solid rgba(61, 109, 180, 0.22);
    background: rgba(61, 109, 180, 0.06);
}
.reasoning-lock-icon { color: #2F5E9E; }
.reasoning-lock-copy { color: #2F5E9E; }
.reasoning-lock strong { color: #24497C; }
.session-char-tag { background: rgba(188, 91, 61, 0.12); }
.char-card-head { background: rgba(188, 91, 61, 0.06); }
.setup-error {
    border: 1px solid rgba(178, 58, 76, 0.40);
    background: rgba(178, 58, 76, 0.07);
}
.char-preset-row {
    border: 1px solid rgba(61, 109, 180, 0.22);
    background: linear-gradient(135deg, rgba(61, 109, 180, 0.06), rgba(138, 95, 184, 0.05));
}
.char-avatar-preview { border: 1px solid rgba(138, 95, 184, 0.45); }

/* Messages */
.msg-narrator { background: rgba(32, 29, 24, 0.03); }
.msg-player {
    background: linear-gradient(135deg, rgba(188, 91, 61, 0.12), rgba(188, 91, 61, 0.05));
    border-color: rgba(188, 91, 61, 0.30);
}
.msg-transform-badge { border: 1px solid rgba(188, 91, 61, 0.35); }
.msg-transformed { border-color: rgba(188, 91, 61, 0.48); }
.debug-block-head { background: rgba(188, 91, 61, 0.08); }
.stop-btn:hover { background: rgba(178, 58, 76, 0.12); }
.retry-banner { border: 1px solid rgba(178, 58, 76, 0.5); }

/* Slash palette + command panel */
.slash-trigger {
    border-color: rgba(217, 119, 87, 0.42);
    background: rgba(188, 91, 61, 0.08);
    color: #A04E2F;
    box-shadow: inset 0 0 18px rgba(188, 91, 61, 0.05);
}
.slash-trigger:hover, .slash-trigger:focus-visible {
    border-color: #C97D5B;
    box-shadow: 0 0 0 3px rgba(188, 91, 61, 0.16), inset 0 0 18px rgba(188, 91, 61, 0.10);
}
.slash-mode .slash-trigger, .slash-mode #input-speech {
    border-color: #C06A48;
    color: #8F4630;
    box-shadow: 0 0 0 1px rgba(217, 119, 87, 0.18), 0 0 24px rgba(188, 91, 61, 0.10);
}
.slash-suggestions {
    border: 1px solid rgba(217, 119, 87, 0.48);
    background: linear-gradient(155deg, rgba(252, 250, 245, 0.985), rgba(245, 241, 232, 0.99));
    box-shadow: 0 24px 60px rgba(64, 52, 37, 0.22), 0 0 32px rgba(188, 91, 61, 0.09);
    scrollbar-color: rgba(188, 91, 61, 0.45) transparent;
}
.slash-option::after {
    background:
        radial-gradient(circle at 100% 50%, #BC5B3D 0 1px, #D97757 1.5px 2.5px, transparent 3px),
        radial-gradient(circle at 82% 18%, rgba(217, 119, 87, 0.9) 0 1px, transparent 1.5px),
        radial-gradient(circle at 70% 82%, rgba(188, 91, 61, 0.85) 0 1px, transparent 1.5px),
        linear-gradient(90deg, transparent, rgba(188, 91, 61, 0.08) 22%, rgba(217, 119, 87, 0.72) 100%);
    filter: drop-shadow(0 0 4px rgba(217, 119, 87, 0.7));
}
.slash-option[aria-selected="true"], .slash-option:hover {
    background: linear-gradient(90deg, rgba(188, 91, 61, 0.14), rgba(217, 119, 87, 0.06));
    box-shadow: inset 2px 0 rgba(160, 78, 47, 0.72);
}
.slash-option-icon { color: #A04E2F; }
.slash-option code { color: #A04E2F; }
.slash-option-origin { color: #96867A; }
.slash-catalog-notice { color: #8A6A1F; }
.command-panel {
    border: 1px solid rgba(217, 119, 87, 0.55);
    background: linear-gradient(145deg, rgba(252, 249, 243, 0.98), rgba(246, 241, 232, 0.99));
    box-shadow: inset 0 0 0 1px rgba(217, 119, 87, 0.08);
    scrollbar-color: rgba(188, 91, 61, 0.45) transparent;
}
.command-sigil { background: rgba(188, 91, 61, 0.14); color: #A04E2F; }
.command-origin { color: #96867A; }
@keyframes commandSigilSet {
    0% { opacity: 0; transform: rotate(-18deg) scale(.72); box-shadow: 0 0 0 rgba(188, 91, 61, 0); }
    62% { opacity: 1; transform: rotate(3deg) scale(1.06); box-shadow: 0 0 20px rgba(188, 91, 61, .30); }
    100% { opacity: 1; transform: none; box-shadow: 0 0 0 rgba(188, 91, 61, 0); }
}

/* Action popup */
.action-popup { box-shadow: 0 8px 28px rgba(64, 52, 37, 0.22); }
.action-popup:has(.action-popup-secondary.open) {
    border-color: rgba(217, 119, 87, 0.32);
    background: linear-gradient(155deg, rgba(252, 250, 245, 0.99), rgba(245, 241, 232, 0.99));
    box-shadow: 0 18px 44px rgba(64, 52, 37, 0.24), 0 0 24px rgba(188, 91, 61, 0.07);
}
.action-popup:has(.action-popup-secondary.open) .action-popup-secondary {
    border: 1px solid rgba(217, 119, 87, 0.16);
    background: rgba(32, 29, 24, 0.03);
}
.action-popup:has(.action-popup-secondary.open) .action-btn {
    border: 1px solid rgba(32, 29, 24, 0.07);
    background: rgba(32, 29, 24, 0.025);
}

/* Empty stage + openings */
.empty-stage-mark { color: #B3684C; }
.empty-stage-mark::before { background: linear-gradient(transparent, rgba(188, 91, 61, 0.55), transparent); }
.empty-stage-mark::after {
    border: 1px solid rgba(188, 91, 61, 0.26);
    background: radial-gradient(circle, rgba(188, 91, 61, 0.11), transparent 66%);
}
.empty-kicker { color: #96867A; }
.empty-scroll-cue > span:first-child { color: #B3684C; }
.opening-carousel {
    border: 1px solid rgba(188, 91, 61, 0.22);
    background: linear-gradient(155deg, rgba(188, 91, 61, 0.07), var(--surface) 48%);
    box-shadow: 0 16px 45px rgba(64, 52, 37, 0.12);
}
.opening-heading { color: #A04E2F; }
.opening-card {
    background:
        radial-gradient(circle at 12% 18%, rgba(217, 119, 87, 0.10), transparent 34%),
        var(--surface-solid);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}
.opening-card-mark { color: #BC5B3D; }
.opening-dot.active { background: #BC5B3D; }

/* Toasts + banners */
.toast { box-shadow: 0 12px 40px rgba(64, 52, 37, 0.24); }
.toast.error { border-color: rgba(178, 58, 76, 0.5); }
.toast.success { border-color: rgba(62, 132, 96, 0.5); }
.toast.version-warning-toast { border-color: rgba(178, 125, 32, 0.5); }
.tip-banner {
    background: rgba(178, 125, 32, 0.07);
    border: 1px dashed rgba(178, 125, 32, 0.35);
}
.tip-banner:hover {
    background: rgba(178, 125, 32, 0.11);
    border-color: rgba(178, 125, 32, 0.5);
}
.whisper-popup { box-shadow: 0 6px 18px rgba(64, 52, 37, 0.20); }
`;

export function activate(sdk) {
    const doc = sdk.unsafe.document;
    doc.getElementById(STYLE_ID)?.remove();
    const style = doc.createElement('style');
    style.id = STYLE_ID;
    style.textContent = THEME_CSS;
    doc.head.append(style);
    sdk.observe('unsafe', { action: 'theme.stylesheet.inject', style_id: STYLE_ID });
}
