#!/usr/bin/env python3
"""Open Door Continuity: offline, non-AI, evidence-preserving archive and handoff CLI.

Stdlib only. No network, telemetry, model calls, credentials, or implicit publishing.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

FORMAT = 'open-door-archive/v0.1'
MAX_ITEMS = 500000


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as f:
        while chunk := f.read(1024 * 1024):
            size += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), size


def dump_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n'


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(obj), encoding='utf-8')


def load_json(path: Path):
    with path.open('r', encoding='utf-8-sig') as f:
        return json.load(f)


def get_chats(path: Path) -> list:
    value = load_json(path)
    if isinstance(value, list):
        chats = value
    elif isinstance(value, dict) and isinstance(value.get('conversations'), list):
        chats = value['conversations']
    else:
        raise ValueError('Unsupported export structure: expected a conversations JSON array or {"conversations": [...]}.')
    if len(chats) > MAX_ITEMS:
        raise ValueError('Export exceeds v0.1 supported item limit')
    return chats


def chat_id(chat: dict, index: int) -> str:
    return str(chat.get('id') or chat.get('conversation_id') or f'index:{index}')


def list_chats(args):
    chats = get_chats(Path(args.input))
    for index, chat in enumerate(chats):
        print(f'{chat_id(chat, index)}\t{str(chat.get("title") or "(untitled)").replace(chr(9), " ")[:120]}')
    print(f'Found {len(chats)} conversations.', file=sys.stderr)


def summarize_part(part) -> tuple[str, bool]:
    if isinstance(part, str):
        return part, False
    if isinstance(part, dict):
        # Do not invent transcripts of images/audio or claim unsupported content was converted.
        if part.get('content_type') in ('text', 'input_text') and isinstance(part.get('text'), str):
            return part['text'], False
        kind = str(part.get('content_type') or part.get('type') or 'structured')
        return f'[non-text part retained in source JSON: {kind}]', True
    return f'[non-text part retained in source JSON: {type(part).__name__}]', True


def message_text(message: dict) -> tuple[str, bool]:
    content = message.get('content') or {}
    parts = content.get('parts') if isinstance(content, dict) else None
    if isinstance(parts, list):
        results = [summarize_part(p) for p in parts]
        return '\n'.join(s for s, _ in results), any(b for _, b in results)
    if isinstance(content, dict) and isinstance(content.get('text'), str):
        return content['text'], False
    if isinstance(content, str):
        return content, False
    return '[non-text or unsupported content retained in source JSON]', True


def derive_messages(chat: dict):
    mapping = chat.get('mapping')
    if not isinstance(mapping, dict):
        return [], ['No recognized mapping; raw conversation source is still preserved.']
    current = chat.get('current_node')
    main_chain: set[str] = set()
    seen: set[str] = set()
    while current and current in mapping and current not in seen:
        main_chain.add(current)
        seen.add(current)
        current = mapping[current].get('parent')
    output = []
    for node_id, node in mapping.items():
        msg = node.get('message') if isinstance(node, dict) else None
        if not isinstance(msg, dict):
            continue
        text, unsupported = message_text(msg)
        author = msg.get('author') if isinstance(msg.get('author'), dict) else {}
        output.append({
            'node_id': node_id,
            'message_id': msg.get('id'),
            'parent_node_id': node.get('parent'),
            'child_node_ids': node.get('children') or [],
            'on_current_branch': node_id in main_chain,
            'role': author.get('role'),
            'author_name': author.get('name'),
            'create_time': msg.get('create_time'),
            'text': text,
            'contains_unsupported_parts': unsupported,
        })
    return output, []


def secure_archive_destination(dest: Path):
    dest = dest.resolve()
    if dest.exists():
        raise FileExistsError(f'Refusing to overwrite existing archive: {dest}')
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest


def finalize_archive(temp: Path, dest: Path, source: dict, extras: dict):
    files = []
    for p in sorted(temp.rglob('*')):
        if p.is_file() and p.name != 'manifest.json':
            digest, size = hash_file(p)
            files.append({'path': p.relative_to(temp).as_posix(), 'sha256': digest, 'size_bytes': size})
    manifest = {'format': FORMAT, 'created_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                'source': source, 'files': files, **extras}
    write_json(temp / 'manifest.json', manifest)
    temp.rename(dest)
    print(f'ARCHIVED: {dest}\nFILES: {len(files)}\nVerify with: python src/open_door.py verify --archive "{dest}"')


def import_chatgpt(args):
    path = Path(args.input)
    chats = get_chats(path)
    candidates = [(i, c) for i, c in enumerate(chats)
                  if (args.id is not None and chat_id(c, i) == args.id)
                  or (args.title is not None and (c.get('title') or '').casefold() == args.title.casefold())]
    if len(candidates) != 1:
        raise ValueError(f'Selection matched {len(candidates)} conversations. Use list first and supply a unique --id.')
    index, chat = candidates[0]
    dest = secure_archive_destination(Path(args.out))
    original_digest, original_size = hash_file(path)
    with tempfile.TemporaryDirectory(dir=dest.parent, prefix='.open-door-stage-') as staging:
        temp = Path(staging) / 'archive'
        temp.mkdir()
        write_json(temp / 'conversation-source.json', chat)
        entries, warnings = derive_messages(chat)
        (temp / 'messages.jsonl').write_text(''.join(json.dumps(e, ensure_ascii=False, sort_keys=True) + '\n' for e in entries), encoding='utf-8')
        write_json(temp / 'metadata.json', {'conversation_id': chat_id(chat, index), 'title': chat.get('title'),
                                          'message_count': len(entries), 'warnings': warnings,
                                          'note': 'All graph branches retained; on_current_branch marks the selected chain.'})
        finalize_archive(temp, dest,
                         {'type': 'chatgpt-json', 'filename': path.name, 'sha256': original_digest, 'size_bytes': original_size},
                         {'selection': {'conversation_id': chat_id(chat, index), 'title': chat.get('title')}})


def archive_notes(args):
    source = Path(args.input).resolve()
    if not source.is_dir():
        raise ValueError('Notes input must be a directory')
    dest = secure_archive_destination(Path(args.out))
    all_paths = sorted(p for p in source.rglob('*') if p.is_file())
    if len(all_paths) > MAX_ITEMS:
        raise ValueError('Too many files')
    with tempfile.TemporaryDirectory(dir=dest.parent, prefix='.open-door-stage-') as staging:
        temp = Path(staging) / 'archive'
        (temp / 'notes').mkdir(parents=True)
        count = 0
        for item in all_paths:
            if item.is_symlink():
                continue
            rel = item.relative_to(source)
            if any(p in ('.git', '__pycache__', '.venv') for p in rel.parts):
                continue
            if item.suffix.lower() not in ('.md', '.markdown', '.txt', '.json', '.jsonl'):
                continue
            target = temp / 'notes' / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(item, target)
            count += 1
        if not count:
            raise ValueError('No supported note files found')
        finalize_archive(temp, dest, {'type': 'notes-directory', 'source_name': source.name},
                         {'selection': {'note_count': count}})


def valid_rel_path(name: str) -> bool:
    p = Path(name)
    return bool(name) and not p.is_absolute() and '..' not in p.parts and str(p).replace('\\', '/') == name and name != 'manifest.json'


def verify_archive_path(path: Path, quiet: bool = False):
    root = path.resolve()
    manifest = load_json(root / 'manifest.json')
    errors = []
    if manifest.get('format') != FORMAT:
        errors.append('Invalid format/version')
    declared = set()
    for entry in manifest.get('files', []):
        rel = entry.get('path', '')
        if not valid_rel_path(rel) or rel in declared:
            errors.append(f'Unsafe or duplicated path: {rel!r}')
            continue
        declared.add(rel)
        file = root / rel
        if not file.is_file() or file.is_symlink():
            errors.append(f'Missing or symbolic-link file: {rel}')
            continue
        actual_hash, size = hash_file(file)
        if actual_hash != entry.get('sha256') or size != entry.get('size_bytes'):
            errors.append(f'Changed file: {rel}')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    for extra in sorted(actual - declared):
        errors.append(f'Unexpected file: {extra}')
    if not quiet:
        for e in errors:
            print('FAIL:', e)
        print('VERIFIED: all declared files match SHA-256 and size.' if not errors else 'NOT VERIFIED')
        print('Note: SHA-256 detects changes against this manifest; it does not prove who created the archive.')
    return errors, manifest


def verify(args):
    errors, _ = verify_archive_path(Path(args.archive))
    if errors:
        raise SystemExit(2)


def handoff_template(args):
    errors, manifest = verify_archive_path(Path(args.archive), quiet=True)
    if errors:
        raise ValueError('Archive failed verification: ' + '; '.join(errors))
    doc = {
        'format': 'open-door-handoff/v0.1',
        'archive_format': manifest.get('format'),
        'archive_title': manifest.get('selection', {}).get('title', ''),
        'archive_source_sha256': manifest.get('source', {}).get('sha256'),
        'collaborator_label': '',
        'prepared_by': '',
        'purpose': 'Portable working context; not a personality or consciousness transfer.',
        'claims': [
            {'id': 'example-delete-me', 'kind': 'observation', 'text': '', 'attribution': '',
             'evidence_node_ids': [], 'status': 'needs-review'}
        ],
        'open_questions': [],
        'disagreements': [],
        'next_actions': [],
        'limits': ['A different model may respond differently even with identical history.',
                   'This handoff is editable context; preserve original sources separately.'],
    }
    out = Path(args.out)
    if out.exists():
        raise FileExistsError(f'Refusing to overwrite {out}')
    write_json(out, doc)
    print(f'TEMPLATE: {out}\nFill supported claims and evidence IDs; do not invent the missing history.')


def md(s: object) -> str:
    return str(s).replace('\r', ' ').replace('\n', ' ').strip()


def render_handoff(args):
    doc = load_json(Path(args.input))
    if doc.get('format') != 'open-door-handoff/v0.1':
        raise ValueError('Not an Open Door handoff v0.1 file')
    archive_ids = None
    if args.archive:
        errors, manifest = verify_archive_path(Path(args.archive), quiet=True)
        if errors:
            raise ValueError('Cannot attest evidence IDs: archive failed verification')
        ids = set()
        msgfile = Path(args.archive) / 'messages.jsonl'
        if msgfile.exists():
            for line in msgfile.read_text(encoding='utf-8').splitlines():
                data = json.loads(line)
                ids.add(str(data.get('node_id')))
        archive_ids = ids
        if doc.get('archive_source_sha256') != manifest.get('source', {}).get('sha256'):
            raise ValueError('Handoff source hash does not match archive source')
    lines = [f'# Continuity handoff — {md(doc.get("collaborator_label") or "unassigned")}', '',
             f'**Prepared by:** {md(doc.get("prepared_by") or "unrecorded")}',
             f'**Archive:** {md(doc.get("archive_title") or "untitled")}',
             f'**Source SHA-256:** `{md(doc.get("archive_source_sha256") or "not available")}`',
             '', f'**Purpose:** {md(doc.get("purpose"))}', '',
             '> This is a portable evidence guide, not the original model, not a restored chat session, and not proof of identity.',
             '', '## Recorded observations, decisions, interpretations', '']
    for claim in doc.get('claims', []):
        if not claim.get('text'):
            continue
        refs = [str(x) for x in claim.get('evidence_node_ids', [])]
        invalid = [] if archive_ids is None else [r for r in refs if r not in archive_ids]
        status = md(claim.get('status') or 'needs-review')
        if not refs or invalid:
            status = 'UNVERIFIED' + (f' (unknown node IDs: {", ".join(invalid)})' if invalid else ' (no linked evidence)')
        kind = md(claim.get('kind') or 'unclassified')
        who = md(claim.get('attribution') or 'unattributed')
        lines += [f'- **{md(claim.get("id") or "unlabelled")}** [{kind}; {status}; attributed to {who}]: {md(claim["text"])}',
                  f'  - Evidence node IDs: {", ".join("`" + x + "`" for x in refs) if refs else "none"}']
    if not any(c.get('text') for c in doc.get('claims', [])):
        lines.append('_No supported claims have been entered._')
    for key, label in [('disagreements', 'Disagreements and revisions'),
                       ('open_questions', 'Unresolved questions'),
                       ('next_actions', 'Next actions'),
                       ('limits', 'Limitations')]:
        lines += ['', '## ' + label, '']
        values = doc.get(key) or []
        lines += [f'- {md(v)}' for v in values] if values else ['_None recorded (not evidence that none exist)._']
    lines += ['', '## Migration caveat', '',
              'Read the linked original sources before relying on a disputed claim. Keep collaborators separately attributed. Never represent this handoff as an exact copy of a previous model.', '']
    out = Path(args.out)
    if out.exists():
        raise FileExistsError(f'Refusing to overwrite {out}')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(f'RENDERED: {out}')


def compare_handoffs(args):
    old, new = load_json(Path(args.old)), load_json(Path(args.new))
    for doc in (old, new):
        if doc.get('format') != 'open-door-handoff/v0.1':
            raise ValueError('Not an Open Door handoff v0.1 file')
    older = {str(x.get('id')): x for x in old.get('claims', []) if x.get('text')}
    newer = {str(x.get('id')): x for x in new.get('claims', []) if x.get('text')}
    for key in sorted(older.keys() | newer.keys()):
        if key not in older:
            print('ADDED:', key)
        elif key not in newer:
            print('REMOVED:', key)
        elif older[key] != newer[key]:
            print('CHANGED:', key)
        else:
            print('UNCHANGED:', key)
    print('Compare marks differences only; it does not choose a truthful version or overwrite either handoff.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('list', help='List conversation IDs/titles in a ChatGPT JSON export')
    p.add_argument('--input', required=True); p.set_defaults(fn=list_chats)
    p = sub.add_parser('import-chatgpt', help='Preserve one selected ChatGPT conversation and SHA-256 manifest')
    p.add_argument('--input', required=True)
    g = p.add_mutually_exclusive_group(required=True); g.add_argument('--id'); g.add_argument('--title')
    p.add_argument('--out', required=True); p.set_defaults(fn=import_chatgpt)
    p = sub.add_parser('archive-notes', help='Archive plaintext notes without uploading')
    p.add_argument('--input', required=True); p.add_argument('--out', required=True); p.set_defaults(fn=archive_notes)
    p = sub.add_parser('verify', help='Check archived file hashes and sizes')
    p.add_argument('--archive', required=True); p.set_defaults(fn=verify)
    p = sub.add_parser('handoff-template', help='Create an editable structured handoff form')
    p.add_argument('--archive', required=True); p.add_argument('--out', required=True); p.set_defaults(fn=handoff_template)
    p = sub.add_parser('handoff-render', help='Create Markdown handoff without invented evidence')
    p.add_argument('--input', required=True); p.add_argument('--out', required=True); p.add_argument('--archive'); p.set_defaults(fn=render_handoff)
    p = sub.add_parser('handoff-compare', help='Compare two handoff versions without replacing either')
    p.add_argument('--old', required=True); p.add_argument('--new', required=True); p.set_defaults(fn=compare_handoffs)
    args = parser.parse_args(argv)
    try:
        args.fn(args)
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
