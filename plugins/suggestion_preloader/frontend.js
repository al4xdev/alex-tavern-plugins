/* Preloads move suggestions right after each committed turn, while the player
   is still reading the narration — so opening the input bar finds them ready.
   Costs one extra model call per turn, which is why this is an opt-in plugin. */

export function activate(sdk) {
    let inFlight = false;
    let turnSerial = 0;

    sdk.hook('turn.output', (data, context) => {
        const serial = ++turnSerial; // a newer turn makes this preload stale
        const sessionId = context?.state?.sessionId;
        if (sessionId && !inFlight) {
            inFlight = true;
            // Fire-and-forget AFTER returning data — rendering never waits on this.
            queueMicrotask(async () => {
                try {
                    sdk.ui.setSuggestionsLoading(true);
                    const result = await sdk.api.suggest(sessionId);
                    // Drop stale results: session switched or another turn committed.
                    // A manual "Suggest" racing this call is harmless — both carry
                    // fresh suggestions for the same turn; the last one wins.
                    if (serial === turnSerial && context?.state?.sessionId === sessionId) {
                        sdk.ui.renderSuggestions(result.suggestions);
                    }
                } catch (error) {
                    sdk.observe('frontend.suggest.preload-error', { error: String(error) });
                } finally {
                    sdk.ui.setSuggestionsLoading(false);
                    inFlight = false;
                }
            });
        }
        return data; // unchanged — this hook is a pure observer
    });
}
