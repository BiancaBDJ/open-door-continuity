# Verification protocol

Record provenance separately for the original file and any derived rendering. When a local CLI computes SHA-256 for source bytes, record filename, byte length, digest, and when and where it was computed. The archive manifest lists each saved file's SHA-256 and size.

If the output says VERIFIED, the listed file bytes match this manifest at that moment. This is **not** a digital signature, and later alterations to both files and manifest are possible. If the archive includes a non-text part in the original JSON, the readable JSONL may show a placeholder. Do not say the actual media bytes were captured unless explicitly verified.

Possible statuses:

- **VERIFIED AGAINST MANIFEST:** exact file hashes match.
- **SAVED — NOT VERIFIED:** a copy exists but readback/hash comparison was not completed.
- **DERIVED VIEW ONLY:** text extract exists without raw evidence.
- **UNAVAILABLE:** source not accessible or missing.
- **INTEGRITY FAILURE:** missing, extra, or changed files.

Never invent a hash, readback, receipt, file count, or a successful remote action.
