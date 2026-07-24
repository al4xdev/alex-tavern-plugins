# Creme Theme

A curated palette theme in the Anthropic editorial style: ivory and cream surfaces,
warm ink text, and a book-cloth terracotta → coral accent gradient in place of the
core indigo/violet on near-black.

The core dark theme ships untouched. This plugin's frontend entrypoint appends one
`<style>` element after `style.css`, so equal-specificity rules win by source order:

- **Section 1** retints the design-system custom properties (`--bg-*`, `--surface*`,
  `--text-*`, `--accent*`, semantic and character colors) and declares
  `color-scheme: light` so native controls follow.
- **Section 2** re-covers every core rule that hardcodes a dark color instead of
  reading a variable — modals, plugin center, slash palette, command panel, provider
  cards, toasts, and the tinted `commandSigilSet` keyframe.

Enable the plugin to apply the theme; disable it (and reload) to return to the dark
default. There is no configuration.

## Curation notes

- Frontend-only; declares the `unsafe` permission because it reaches
  `sdk.unsafe.document` to inject the stylesheet, and journals that access with
  `sdk.observe('unsafe', …)`.
- `tests/test_frontend.py` reads the sibling core checkout's `style.css` and fails
  when core grows a new `:root` palette variable or a new hardcoded dark rule this
  theme does not override — coverage drift is caught at review time, not by users.
- Accent text tones (`#A04E2F` on cream, white on the accent gradient) keep WCAG AA
  contrast; character colors are darkened to stay readable on ivory.
