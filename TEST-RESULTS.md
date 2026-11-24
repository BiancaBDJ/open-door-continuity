# Local test results — 2026-11-24

**Result:** 17/17 offline tests passed on November 24, 2026.

**Environment:** Python 3, standard library only; tests against fictional ChatGPT-style export in `tests/fixtures/synthetic_conversations.json`.

**Not live tested:** private user exports, the ChatGPT API bridge, cross-provider formats, plugin tool routing in a fresh ChatGPT session, GitHub public release installation. ChatGPT plugin creation/ingestion is separately recorded as successful private registration.

Tested areas:

- Conversation export ID listing and strict selection.
- Preservation of selected conversation JSON and branching metadata.
- Non-text parts marked without inventing visual or audio content.
- SHA-256 verification, corruption detection, extraneous-file detection, path-traversal rejection.
- Existing-output overwrite rejection and missing-conversation failure.
- Offline note archival with known file extensions only.
- Empty handoff stays empty instead of fabricating facts.
- Referenced node ID existence check, source hash mismatch failure.
- Handoff comparison is read-only.
- Both independent plugin manifests and ZIP packages, skill entrypoints and absence of private conversation data.
- Optional API bridge requires explicit send acknowledgement and a user-supplied key.

**Reminder:** Passing offline tests establishes tested contract behavior, not automatic success on every real ChatGPT export or future platform version.
