# Suggestion Preloader

After every committed turn, this frontend-only plugin requests the native move
suggestions in the background while the player reads. The collapsed composer pill
shows the loading state and then announces that suggestions are ready. Opening the
composer reveals the native suggestion cards without blocking turn rendering.

The plugin is opt-in because each preload costs one additional model call. Failures
are journaled and otherwise silent. Results from an older turn or session are
discarded.

## Permissions

- `network`: calls the Tavern's authenticated `POST /session/{id}/suggest` client
  through `sdk.api`.

## Compatibility

Requires the Alex Tavern frontend plugin SDK with `sdk.ui.renderSuggestions()` and
`sdk.ui.setSuggestionsLoading()`.
