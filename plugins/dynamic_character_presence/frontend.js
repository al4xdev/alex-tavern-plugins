import { t } from '/i18n.js';

/* Dynamic Character Presence — frontend.
 *
 * `Scene.present_characters` is the only source of truth; this file keeps no
 * mirror list. Per-card toggle state lives on the card itself
 * (`card.dataset.presentCharacter`) so the generic `setup.presentCharacters`
 * hook can read it back without any plugin-specific core code. */

function toggleLabel() {
    return t('character.inScene');
}

function buildToggle() {
    const label = document.createElement('label');
    label.className = 'toggle char-presence-toggle';
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.checked = true; // new/unlisted characters start present
    input.setAttribute('aria-label', toggleLabel());
    const track = document.createElement('span');
    track.className = 'toggle-track';
    const thumb = document.createElement('span');
    thumb.className = 'toggle-thumb';
    track.append(thumb);
    const copy = document.createElement('span');
    copy.className = 'toggle-label';
    copy.textContent = toggleLabel();
    label.append(input, track, copy);
    return label;
}

function mountCardToggle(card) {
    if (card.querySelector('.char-presence-toggle')) return card; // already mounted
    const toggle = buildToggle();
    const input = toggle.querySelector('input');
    card.dataset.presentCharacter = 'true';
    input.addEventListener('change', () => {
        card.dataset.presentCharacter = input.checked ? 'true' : 'false';
    });
    const head = card.querySelector('.char-card-head');
    const removeBtn = card.querySelector('.char-remove');
    head.insertBefore(toggle, removeBtn);
    return card;
}

function collectPresentCharacters(defaultPresent, { cards }) {
    const present = cards
        .filter((card) => card.querySelector('.char-presence-toggle input')?.checked !== false)
        .map((card) => card.dataset.cid);
    return [...present, 'Player'];
}

function restorePresence(presentCharacters, { cards }) {
    if (!Array.isArray(presentCharacters)) return presentCharacters;
    const presentSet = new Set(presentCharacters);
    cards.forEach((card) => {
        const input = card.querySelector('.char-presence-toggle input');
        if (!input) return;
        const isPresent = presentSet.has(card.dataset.cid);
        input.checked = isPresent;
        card.dataset.presentCharacter = isPresent ? 'true' : 'false';
    });
    return presentCharacters;
}

/* ── Mid-session compact roster control ─────────────────────────────────── */

function buildPanel(sdk) {
    let session = null; // { sessionId, revision, characters, controlledId, present }
    let busy = false;

    const root = document.createElement('div');
    root.className = 'presence-panel';
    root.hidden = true; // nothing to show until a session is loaded

    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'presence-trigger';
    trigger.textContent = t('presence.panelTitle');

    const body = document.createElement('div');
    body.className = 'presence-body';
    body.hidden = true;

    const list = document.createElement('div');
    list.className = 'presence-list';

    const status = document.createElement('p');
    status.className = 'presence-status';

    const undoBtn = document.createElement('button');
    undoBtn.type = 'button';
    undoBtn.className = 'btn btn-mini presence-undo-btn';
    undoBtn.textContent = t('presence.undoButton');

    const actions = document.createElement('div');
    actions.className = 'presence-actions';
    actions.append(undoBtn);

    body.append(list, actions, status);
    root.append(trigger, body);

    function setStatus(message, isError = false) {
        status.textContent = message || '';
        status.classList.toggle('error', isError);
    }

    function render() {
        list.replaceChildren();
        if (!session) return;
        const presentSet = new Set(session.present.filter((id) => id !== 'Player'));
        const order = Object.keys(session.characters);
        order.forEach((cid) => {
            const character = session.characters[cid];
            const row = document.createElement('label');
            row.className = 'toggle presence-row';
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.checked = presentSet.has(cid);
            const isControlled = cid === session.controlledId;
            input.disabled = busy || isControlled;
            const name = character?.mind?.name || cid;
            input.setAttribute('aria-label', `${toggleLabel()}: ${name}`);
            const track = document.createElement('span');
            track.className = 'toggle-track';
            const thumb = document.createElement('span');
            thumb.className = 'toggle-thumb';
            track.append(thumb);
            const copy = document.createElement('span');
            copy.className = 'toggle-label';
            copy.textContent = isControlled ? `${name} (${t('presence.controlled')})` : name;
            row.append(input, track, copy);
            input.addEventListener('change', () => onToggle(cid, input));
            list.append(row);
        });
    }

    async function onToggle(cid, input) {
        if (!session || busy) return;
        const order = Object.keys(session.characters);
        const presentSet = new Set(session.present.filter((id) => id !== 'Player'));
        if (input.checked) presentSet.add(cid); else presentSet.delete(cid);
        const nextList = [...order.filter((id) => presentSet.has(id)), 'Player'];

        busy = true;
        render();
        setStatus(t('presence.saving'));
        try {
            const result = await sdk.api.setPresence(session.sessionId, nextList, session.revision);
            session.present = result.present_characters;
            session.revision = result.revision;
            setStatus('');
        } catch (error) {
            setStatus(error.message, true);
        } finally {
            busy = false;
            render();
        }
    }

    undoBtn.addEventListener('click', async () => {
        if (!session || busy) return;
        busy = true;
        setStatus(t('presence.saving'));
        try {
            const result = await sdk.api.undoPresence(session.sessionId);
            if (result.restored) {
                session.present = result.present_characters;
                session.revision = result.revision;
                setStatus('');
            } else {
                setStatus(result.reason || t('presence.nothingToUndo'));
            }
        } catch (error) {
            setStatus(error.message, true);
        } finally {
            busy = false;
            render();
        }
    });

    async function refreshPanel() {
        if (!session) return;
        busy = true;
        setStatus(t('presence.loading'));
        try {
            const fresh = await sdk.api.getState(session.sessionId);
            session.characters = fresh.characters || {};
            session.controlledId = fresh.player?.controlled_character_id || null;
            session.present = fresh.scene?.present_characters || [];
            session.revision = fresh.revision;
            setStatus('');
        } catch (error) {
            setStatus(error.message, true);
        } finally {
            busy = false;
            render();
        }
    }

    trigger.addEventListener('click', async () => {
        const opening = body.hidden;
        body.hidden = !body.hidden;
        if (opening) await refreshPanel();
    });

    async function openAndFocus() {
        body.hidden = false;
        await refreshPanel();
        (list.querySelector('input:not(:disabled)') || trigger).focus({ preventScroll: true });
    }

    function ingest(gameState) {
        if (!gameState || !gameState.session_id) {
            session = null;
            root.hidden = true;
            return;
        }
        session = {
            sessionId: gameState.session_id,
            revision: gameState.revision,
            characters: gameState.characters || {},
            controlledId: gameState.player?.controlled_character_id || null,
            present: gameState.scene?.present_characters || [],
        };
        root.hidden = false;
        if (!body.hidden) render();
    }

    return { root, ingest, openAndFocus };
}

export function activate(sdk) {
    sdk.hook('setup.charCardHead', (card) => mountCardToggle(card));
    sdk.hook('setup.presentCharacters', collectPresentCharacters);
    sdk.hook('setup.restorePresence', restorePresence);

    const panel = buildPanel(sdk);
    sdk.mount('session.tools', panel.root);
    sdk.registerAction({
        name: 'presence',
        title: { en: 'Character presence', 'pt-BR': 'Presença de personagens' },
        summary: {
            en: 'Open the current scene roster and move focus to its controls.',
            'pt-BR': 'Abra o elenco da cena atual e mova o foco para seus controles.',
        },
        icon: '◉',
        aliases: { en: [], 'pt-BR': ['presenca'] },
        keywords: {
            en: ['characters', 'scene', 'roster'],
            'pt-BR': ['personagens', 'cena', 'elenco'],
        },
        scope: 'session',
    }, () => panel.openAndFocus());
    sdk.hook('session.state', (gameState) => {
        panel.ingest(gameState);
        return gameState;
    });
}
