# Private-by-default safety

- A user's ChatGPT export can contain personal, health, financial, family and other intimate information. Never publish it to GitHub, Discord or an issue tracker for debugging.
- Prefer local-only workflows. If a cloud connector is proposed, state destination and what data will leave the user's device before requesting consent.
- Never request passwords, API keys or payment card information in chat.
- For demonstrations use synthetic source files. If an error requires assistance, ask for an error *message* after removing paths, names and secrets, not the entire private export.
- Separate independently named collaborators and preserve revisions rather than blending them for convenience.
