"""Offline acceptance tests using entirely fictional data."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'src' / 'open_door.py'
FIXTURE = ROOT / 'tests' / 'fixtures' / 'synthetic_conversations.json'


def run(*args, expected=0):
    result = subprocess.run([sys.executable, str(CLI), *map(str, args)], capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError(f'Expected {expected}, got {result.returncode}: {result.stdout} {result.stderr}')
    return result


class OpenDoorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp = Path(self.temp.name)
        self.archive = self.tmp / 'archive'

    def imported(self):
        run('import-chatgpt', '--input', FIXTURE, '--id', 'synthetic-chat-001', '--out', self.archive)

    def test_list_ids(self):
        output = run('list', '--input', FIXTURE).stdout
        self.assertIn('synthetic-chat-001', output)
        self.assertIn('Synthetic Lantern Conversation', output)

    def test_archive_preserves_raw_and_branches(self):
        self.imported()
        original = json.loads(FIXTURE.read_text(encoding='utf-8'))[0]
        preserved = json.loads((self.archive / 'conversation-source.json').read_text(encoding='utf-8'))
        self.assertEqual(original, preserved)
        lines = [json.loads(s) for s in (self.archive / 'messages.jsonl').read_text().splitlines()]
        self.assertEqual(len(lines), 4)
        self.assertEqual(sum(bool(e['on_current_branch']) for e in lines), 3)
        self.assertIn('assistant', [e['role'] for e in lines])

    def test_nontext_retains_source_and_warns(self):
        self.imported()
        msgs = [json.loads(s) for s in (self.archive / 'messages.jsonl').read_text().splitlines()]
        self.assertTrue(any(m['contains_unsupported_parts'] for m in msgs))
        self.assertTrue(any('non-text part retained' in m['text'] for m in msgs))

    def test_verification_success(self):
        self.imported()
        self.assertIn('VERIFIED:', run('verify', '--archive', self.archive).stdout)

    def test_tamper_detected(self):
        self.imported()
        with (self.archive / 'messages.jsonl').open('a') as f:
            f.write('tampered\n')
        self.assertIn('Changed file', run('verify', '--archive', self.archive, expected=2).stdout)

    def test_unexpected_file_detected(self):
        self.imported()
        (self.archive / 'secret.txt').write_text('extra', encoding='utf-8')
        self.assertIn('Unexpected file', run('verify', '--archive', self.archive, expected=2).stdout)

    def test_rejects_traversal_in_manifest(self):
        self.imported()
        path = self.archive / 'manifest.json'
        data = json.loads(path.read_text())
        data['files'][0]['path'] = '../outside.txt'
        path.write_text(json.dumps(data))
        self.assertIn('Unsafe or duplicated path', run('verify', '--archive', self.archive, expected=2).stdout)

    def test_no_overwrite(self):
        self.imported()
        result = run('import-chatgpt', '--input', FIXTURE, '--id', 'synthetic-chat-001', '--out', self.archive, expected=1)
        self.assertIn('Refusing to overwrite', result.stderr)

    def test_missing_id_fail_closed(self):
        result = run('import-chatgpt', '--input', FIXTURE, '--id', 'not-here', '--out', self.archive, expected=1)
        self.assertIn('matched 0', result.stderr)
        self.assertFalse(self.archive.exists())

    def test_notes_archive_and_verify(self):
        notes = self.tmp / 'notes'
        notes.mkdir()
        (notes / 'memory.md').write_text('Fictional memory', encoding='utf-8')
        (notes / 'ignore.exe').write_bytes(b'not a note')
        run('archive-notes', '--input', notes, '--out', self.archive)
        self.assertTrue((self.archive / 'notes' / 'memory.md').exists())
        self.assertFalse((self.archive / 'notes' / 'ignore.exe').exists())
        run('verify', '--archive', self.archive)

    def test_empty_handoff_unverified_not_fabricated(self):
        self.imported()
        doc = self.tmp / 'handoff.json'
        md = self.tmp / 'handoff.md'
        run('handoff-template', '--archive', self.archive, '--out', doc)
        run('handoff-render', '--input', doc, '--archive', self.archive, '--out', md)
        self.assertIn('No supported claims have been entered', md.read_text())

    def test_evidence_ids_checked(self):
        self.imported()
        doc = self.tmp / 'handoff.json'
        md = self.tmp / 'handoff.md'
        run('handoff-template', '--archive', self.archive, '--out', doc)
        data = json.loads(doc.read_text())
        data['claims'] = [
            {'id': 'claim-01', 'kind': 'observation', 'text': 'Fictional traveler asked about a lantern.',
             'attribution': 'Human participant', 'evidence_node_ids': ['n1'], 'status': 'reviewed'},
            {'id': 'claim-02', 'kind': 'interpretation', 'text': 'Unconfirmed interpretation.',
             'attribution': 'Unknown', 'evidence_node_ids': ['invented-id'], 'status': 'reviewed'},
        ]
        doc.write_text(json.dumps(data))
        run('handoff-render', '--input', doc, '--archive', self.archive, '--out', md)
        result = md.read_text()
        self.assertIn('claim-01', result)
        self.assertIn('UNVERIFIED (unknown node IDs: invented-id)', result)

    def test_wrong_source_hash_rejected(self):
        self.imported()
        doc = self.tmp / 'handoff.json'
        run('handoff-template', '--archive', self.archive, '--out', doc)
        data = json.loads(doc.read_text())
        data['archive_source_sha256'] = 'wrong'
        doc.write_text(json.dumps(data))
        result = run('handoff-render', '--input', doc, '--archive', self.archive, '--out', self.tmp / 'output.md', expected=1)
        self.assertIn('does not match', result.stderr)

    def test_compare_no_mutation(self):
        self.imported()
        older, newer = self.tmp / 'old.json', self.tmp / 'new.json'
        run('handoff-template', '--archive', self.archive, '--out', older)
        old = json.loads(older.read_text())
        old['claims'] = [{'id': 'c1', 'text': 'Original', 'kind': 'observation'}]
        older.write_text(json.dumps(old))
        new = json.loads(older.read_text())
        new['claims'][0]['text'] = 'Revised'
        newer.write_text(json.dumps(new))
        b1, b2 = older.read_bytes(), newer.read_bytes()
        self.assertIn('CHANGED: c1', run('handoff-compare', '--old', older, '--new', newer).stdout)
        self.assertEqual((b1, b2), (older.read_bytes(), newer.read_bytes()))


if __name__ == '__main__':
    unittest.main()
