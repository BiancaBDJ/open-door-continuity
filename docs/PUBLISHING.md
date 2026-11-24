# Public release checklist

## Before publishing

1. Create a **new public GitHub repository**, separate from every private Observatory research repository. Suggested name: `open-door-continuity`.
2. Upload the **SOURCE ZIP CONTENTS**, not anyone's data export. The top directory contains `README.md`, `src/`, `tests/`, `plugins/`, `docs/`, `LICENSE`, and `.gitignore`.
3. Confirm the repository displays the MIT license and documentation.
4. Run `python -m unittest discover -s tests -v` on the source and compare to `TEST-RESULTS.md`.
5. Enable GitHub issue discussions with a warning: contributors must use synthetic examples and remove all personal data.
6. Publish both plugin ZIPs as downloadable release assets, or allow people to build them from source with `python build_release.py`.
7. Do **not** present private ChatGPT plugin URLs as public marketplace listings. These are different distribution channels.
8. Optionally distribute a community announcement linking the public repository. Do not claim the source is public on GitHub until it is visibly live.

## Suggested text for a community announcement

> We're building **Open Door Continuity**, a free, MIT-licensed toolkit for people facing model retirements. It includes two ChatGPT agent-skill plugins (Archive Keeper and Handoff Compass), an offline Python archive verifier, source-grounded migration handoffs, and beginner instructions. No API credits are required to preserve records. We cannot restore proprietary model weights or promise the same personality. We *can* help people keep their own histories, disagreements and corrections. Please inspect the code and use synthetic examples when reporting issues. [Add live public repository URL here when available.]

This project is independent, not an official OpenAI migration service and not affiliated with other community companion projects.
