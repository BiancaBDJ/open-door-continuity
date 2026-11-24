# Windows quickstart (zero API charges)

1. Download/extract the **source package** to a folder on your PC (for example `E:\OpenDoorTools`).
2. Install Python 3.10 or newer if necessary. Open Windows Terminal/PowerShell in the folder and type `python --version`.
3. In ChatGPT, choose **Settings → Data Controls → Export Data**, and download the emailed archive. Export processing can take time; do not send anyone your credentials.
4. Unzip your export privately. Find `conversations.json`. If your file has a different structure, don't rename it to trick the program: v0.1 may not support it yet.
5. Enter `python src/open_door.py list --input "C:\Path\To\conversations.json"` and copy the exact conversation ID you want.
6. Enter `python src/open_door.py import-chatgpt --input "C:\Path\To\conversations.json" --id "ID-HERE" --out "C:\OpenDoorPrivate\archive-1"`.
7. Enter `python src/open_door.py verify --archive "C:\OpenDoorPrivate\archive-1"`. It must say **VERIFIED**.
8. Create a handoff template with `handoff-template`; enter claims with links to the original messages. Run `handoff-render`; review the output before showing it to another assistant.

**For absolute beginners:** You can start by using the **Archive Keeper** plugin as a checklist, with **no export uploaded anywhere**. It should help you review what to copy, explain checksums, and tell you what remains unverified.

**Where are files stored?** Exactly where you set `--out`. The tool does not upload them. Back them up to a storage location you trust; optionally encrypt sensitive backups using Windows device encryption or another encryption tool you understand.

**How to view help:** `python src/open_door.py --help` and `python src/open_door.py import-chatgpt --help`.

**Already have Markdown notes?** `python src/open_door.py archive-notes --input "C:\MyPrivateNotes" --out "C:\OpenDoorPrivate\notes-1"`.

**Never upload an API key, complete private archive, or sensitive memory file to a public issue or Discord server.**
