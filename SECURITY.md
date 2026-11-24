# Security and privacy

## Threat model

The most likely failures are: publicly exposing personal conversations, accidental disclosure of credentials, misattributing quotes, corrupted backups, overconfident AI-generated memories, and unexpected paid API usage.

**Controls in this release**

- Offline archive tools use only Python's standard library; they have no network or telemetry functions.
- Import selects a single conversation by ID or unique exact title to avoid silently exporting every conversation.
- The selected original JSON object is preserved in reserialized form in `conversation-source.json` (not byte-identical to the source export), while `messages.jsonl` provides a derived readable view with branches marked.
- Files are SHA-256 hashed and checked; existing archives and handoffs are never overwritten.
- Only known plaintext extensions are copied by `archive-notes`; symlinks are skipped.
- Example fixtures are synthetic and contain no real user conversations.
- The optional API bridge requires a model ID, environment key and `--yes-send`, refuses silently oversized handoffs, avoids logging the chat and does not retry automatically.

## Important limitations

- Private archive files themselves are not encrypted. Choose a secure local destination and encrypted backups.
- The integrity manifest is **not digitally signed**; anyone who can rewrite both archive and manifest can counterfeit a consistent bundle.
- A hash match of a handoff's source file does not verify the truth of interpreted claims; human review remains necessary.
- External tools, including ChatGPT plugins, can only access current-session authorized content and may involve separate provider data handling.
- No public support volunteer needs a complete archive or API key to debug the CLI. Use synthetic reproductions.

## Reporting issues

Open a GitHub issue containing **only synthetic reproduction steps**. Never share secret keys, private memory files, complete exports, or sensitive screenshots.
