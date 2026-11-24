# Data format v0.1

An archive folder contains:

- `manifest.json`: format version, timestamp, source file SHA-256 if available, each derived file path, size and SHA-256.
- `conversation-source.json`: the selected conversation object as JSON (normalized serialization, *not byte-for-byte* extracted from the entire source export), when importing ChatGPT JSON.
- `messages.jsonl`: derived per-message records with node ID, parent, children, role, time, readable text, `on_current_branch`, and `contains_unsupported_parts`.
- `metadata.json`: conversation ID/title, extraction warnings, count.
- `notes/`: archived plaintext sources when using `archive-notes`.

The original downloaded ZIP or `conversations.json` is *not* copied into the archive; keep it separately, because its SHA-256 is the provenance anchor. Files such as images and audio may be represented by references only in source JSON; preserve the original export separately and review actual contents. Do not interpret reordered graph nodes as a chronological linear conversation; use links and timestamps.

`handoff.json` is a manually reviewed document with: `format`, `archive_source_sha256`, `collaborator_label`, `prepared_by`, `purpose`, `claims[]` (id, kind, text, attribution, evidence_node_ids, status), `disagreements[]`, `open_questions[]`, `next_actions[]`, `limits[]`.

A local `handoff-render` with `--archive` verifies the original source hash and existence of node IDs for claims, but it does **not** semantically verify whether the quoted node actually establishes a given claim. Human judgment or an explicitly scoped AI evidence review is still required.
