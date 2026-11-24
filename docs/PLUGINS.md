# Installing the two ChatGPT plugins

The `plugins/open-door-archive` and `plugins/open-door-handoff` folders are **separate plugin packages**. The supplied zip files should contain one plugin each, including its `plugin.json`, `.codex-plugin/plugin.json`, and `skills/.../SKILL.md`.

**Archive Keeper** is for collecting, reviewing and truthfully reporting what is preserved or unverified.

**Handoff Compass** is for preparing a portable narrative with evidence references and preserving disagreements.

They are **instruction-only agent plugins**. They are useful inside ChatGPT with whatever file/connector access a user grants. They do **not** create an MCP server, silently fetch private history, or let other people access your account. They do not need an OpenAI API key.

A private release may be created through Plugin Creator if that capability is available. Public distribution of the source is independent of whether a host permits listing or sharing a plugin in its directory. For an open-source copy, use the individual plugin archives and inspect `SKILL.md` before installing. If installation is unsupported on your plan or platform, the local CLI and Markdown guides still work.

Do not conflate a publicly available **GitHub source repository** with permission to see a user's personal conversations. Consent and access are separate.
