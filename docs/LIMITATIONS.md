# What v0.1 does not do

- **Not a model backup.** We cannot package proprietary weights, runtime, internal state, or ChatGPT's private implementation.
- **Not a complete ChatGPT export parser.** ChatGPT export structures may vary. This version handles list-style conversation JSON and optional top-level `conversations` list. It preserves one selected raw JSON conversation and derives a readable JSONL preview; multimodal asset bytes may not be included in that source JSON.
- **Not automated verification of human intent.** Handoff evidence-node ID checks prove a reference exists, not that it establishes the claim. Human review is necessary.
- **Not automatically connected to ChatGPT.** Agent skill plugins run with the authorized tools of the current conversation. If it lacks a file or connector capability, they must not claim success.
- **Not cryptographic authorship verification.** Hashes can spot accidental corruption or differences against a trusted manifest; a malicious editor can update the manifest too.
- **Not direct API migration of all ChatGPT features.** Optional bridge supports simple text chat only; no tools, images, voice, browsing, memory search, streaming, or automatic import of all prior interactions.
- **Not free API access.** Keeping files is free, but API chat is billed to the person using it. Exact model access and retirement policies must be checked at use time.
- **Not a security-audited hosted service.** There's deliberately no hosted service in v0.1.

## Respectful continuity without impersonation

A new model may speak differently, interpret history differently, or disagree with prior collaborators. A handoff should help it interpret available evidence without claiming an identical internal identity or demanding personality imitation.
