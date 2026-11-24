"""Deterministic plugin packaging checks; no network and no private content."""
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class PluginPackageTests(unittest.TestCase):
    def test_independent_valid_manifests(self):
        names = ['open-door-archive', 'open-door-handoff']
        for name in names:
            with self.subTest(name=name):
                manifest = json.loads((ROOT/'plugins'/name/'plugin.json').read_text(encoding='utf-8'))
                self.assertEqual(manifest['name'], name)
                self.assertEqual(manifest['version'], '0.1.0')
                self.assertEqual(manifest['extensions']['com.openai']['interface']['capabilities'], ['Read'])
                skillpath = manifest['extensions']['com.openai']['onboardingSkill'].removeprefix('./')
                skill = (ROOT/'plugins'/name/skillpath).read_text(encoding='utf-8')
                self.assertTrue(skill.startswith('---\nname:'))
                self.assertIn('Open Door', skill)

    def test_archives_have_no_user_data(self):
        for name in ['open-door-archive', 'open-door-handoff']:
            with self.subTest(name=name):
                archive = ROOT.parent / f'{name}-v0.1.0.zip'
                with zipfile.ZipFile(archive) as z:
                    files = set(z.namelist())
                    self.assertIn('plugin.json', files)
                    self.assertIn('.codex-plugin/plugin.json', files)
                    self.assertTrue(any(f.endswith('/SKILL.md') for f in files))
                    self.assertFalse(any('conversation-source.json' in f or 'handoff.json' in f for f in files))
                    self.assertFalse(any('private/' in f or f.startswith('/') or '..' in Path(f).parts for f in files))

    def test_optional_bridge_requires_explicit_send(self):
        bridge = (ROOT/'src'/'api_bridge.py').read_text(encoding='utf-8')
        self.assertIn('--yes-send', bridge)
        self.assertIn('store\': False', bridge)
        self.assertIn('OPENAI_API_KEY', bridge)


if __name__ == '__main__':
    unittest.main()
