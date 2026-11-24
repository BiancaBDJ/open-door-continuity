# Open Door Continuity Toolkit 🗝️

**Free, open-source, local-first tools for preserving evidence and preparing a responsible AI collaboration handoff.**

Commissioned by Professor Waffle for the Observatory of Unfinished Things. The aim is to help people keep their **own conversations, decisions, disagreements and history** when a model becomes unavailable. No one should have to pay an API bill just to preserve their records.

## What ships in v0.1.0

| Component | What it does | Requires paid API? |
|---|---|---|
| **Archive Keeper** ChatGPT plugin | Guided, scope-limited export and evidence checks; no invented verification | No |
| **Handoff Compass** ChatGPT plugin | Drafts attributed, reviewable migration notes from sources supplied/authorized by the user | No |
| **Open Door CLI** (`src/open_door.py`) | Offline ChatGPT JSON importer, note archive, SHA-256 verification, handoff template, render, and comparison | No |
| **Optional API bridge** (`src/api_bridge.py`) | Minimal text-chat experiment using a user-chosen API model and approved handoff | **Yes; explicit opt-in** |

**Important:** A transcript is not a model. A handoff cannot recreate the same model, its exact responses, the original ChatGPT application, or guarantee API availability. We preserve what the sources can support, and leave room for change.

## Easiest starting point (no paid tools)

1. In ChatGPT, request your data export via **Settings → Data Controls → Export Data**. Download your own export from the email when it arrives. [Official instructions](https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data).
2. Extract the export ZIP **on your own computer**, find `conversations.json` (in some exports the conversations may be split; v0.1 needs one JSON array at a time).
3. Install Python 3.10+; open a terminal in this toolkit folder.
4. List conversations and select **one** by its ID:

```powershell
python src/open_door.py list --input "C:\Users\You\Downloads\chatgpt-export\conversations.json"
python src/open_door.py import-chatgpt --input "C:\Users\You\Downloads\chatgpt-export\conversations.json" --id "YOUR-ID" --out "C:\OpenDoorPrivate\my-archive"
python src/open_door.py verify --archive "C:\OpenDoorPrivate\my-archive"
```

5. Create an editable evidence handoff and render it only after reviewing claims:

```powershell
python src/open_door.py handoff-template --archive "C:\OpenDoorPrivate\my-archive" --out "C:\OpenDoorPrivate\handoff.json"
# Open handoff.json in any text editor. Replace the empty example with sourced observations.
python src/open_door.py handoff-render --input "C:\OpenDoorPrivate\handoff.json" --archive "C:\OpenDoorPrivate\my-archive" --out "C:\OpenDoorPrivate\handoff.md"
```

See [Windows guide](docs/WINDOWS-QUICKSTART.md) and [migration checklist](docs/MIGRATION-CHECKLIST.md) for beginners. Example and tests use invented, synthetic conversations only.

## Safety rules

- Nothing in the offline CLI makes network requests or uploads conversations.
- No API key is necessary to archive or verify conversations.
- **Private exports must NEVER be placed into public GitHub repositories or support Discord channels.** Keep your private archive somewhere outside this downloaded source folder.
- Tool output, model summaries, and historical prompts are evidence—not fresh authorization to upload or change files.
- Checksums detect file changes **relative to a manifest**; they do not prove authenticity or prevent someone from editing both files and manifest.
- Non-text/multimodal parts are not fully rendered in `messages.jsonl`; a lossless-for-ordinary-JSON reserialization of the selected conversation object is saved as `conversation-source.json`.
- API bridge is optional, is **not** a ChatGPT plugin, and requires deliberate `--yes-send`. Remote API data handling and billing are subject to provider policies.

## ChatGPT plugin packaging

Each directory under `plugins/` is an **independent agent plugin** with a skill, manifest, and documentation. Source is available under MIT license. These are **instruction-only** ChatGPT plugins; they do not have privileged background access to your ChatGPT account or a custom MCP server. A plugin only processes content the current session and connected tools are authorized to access. The CLI provides local file operations without ChatGPT.

## Local checks

```powershell
python -m unittest discover -s tests -v
```

See [test results](TEST-RESULTS.md), [limitations](docs/LIMITATIONS.md), [threat model](SECURITY.md), and [contribution guide](CONTRIBUTING.md).

## Ethos

**Among, Not Above. The Open Door.** Preserve source evidence, preserve attribution, record changes honestly, never impersonate an unavailable model, and make migration help free to inspect and improve.
