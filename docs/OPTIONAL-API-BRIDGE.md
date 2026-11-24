# Optional API bridge: simple text conversation (can cost money)

This is a separate demonstration, **not required** for preserving archives and **not** a guarantee of access to a specific model after any retirement.

1. Complete and personally review `handoff.md` in private storage.
2. Visit your API provider's docs and pricing to verify that the model you want is accessible to your API account. OpenAI publishes [pricing](https://platform.openai.com/pricing/) and [API documentation](https://platform.openai.com/docs/overview).
3. Add billing only if you personally choose to; set spending controls. API billing differs from ChatGPT subscription billing.
4. Put your key in the **environment** rather than inside a source file or screenshots.
5. Run `src/api_bridge.py` with your chosen model ID.

Example on PowerShell (enter your key **privately** in your own terminal, not in Discord or ChatGPT):

```powershell
$env:OPENAI_API_KEY = Read-Host "Paste OpenAI API key privately"
python src/api_bridge.py --handoff "C:\OpenDoorPrivate\handoff.md" --model "YOUR-CURRENT-API-MODEL-ID" --yes-send
Remove-Item Env:OPENAI_API_KEY
```

The script sends the handoff plus recent messages to `https://api.openai.com/v1/responses` using `store: false` and the exact chosen model name. It prints reported token usage when available. It keeps the chat history **in memory only**, and does not save locally. API provider retention and data handling still apply; inspect the provider's latest rules before transmitting sensitive material. You can terminate with `/exit`.

**Limits:** A long handoff is refused instead of silently truncated. Input context grows as you talk, and fees may accumulate. No automatic retries, no auto-switching models, and no representation that the assistant is the original model. An API call is not made without `--yes-send`.
