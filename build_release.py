"""Build two independent ChatGPT plugin archives and a public-ready source ZIP."""
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
DIST = ROOT.parent
NAMES = {
    'open-door-archive': {
        'displayName': 'Open Door Archive Keeper',
        'shortDescription': 'Preserve and check AI conversation history',
        'longDescription': 'Guide local-first archival of AI conversations, preserve attribution, and distinguish verified files from missing or derivative content.',
        'description': 'Help people preserve and check authorized conversation archives without invented verification or accidental publishing.',
        'prompt': ['Open Door Archive — help preserve my chat before retirement.', 'Open Door Archive — inspect what my export actually contains.', 'Open Door Archive — give me a preservation receipt.'],
        'skills': 'open-door-archive',
        'keywords': ['archive', 'continuity', 'export', 'privacy', 'integrity'],
    },
    'open-door-handoff': {
        'displayName': 'Open Door Handoff Compass',
        'shortDescription': 'Evidence-grounded cross-model handoffs',
        'longDescription': 'Prepare and reconcile reviewable continuity handoffs across model changes, with separately attributed voices, dated corrections, and explicit gaps.',
        'description': 'Prepare source-grounded cross-model handoffs without erasing disagreements or promising model identity transfer.',
        'prompt': ['Open Door Handoff — prepare an attributed draft.', 'Open Door Handoff — reconcile these old and new notes.', 'Open Door Handoff — design a continuity smoke test.'],
        'skills': 'open-door-handoff',
        'keywords': ['migration', 'handoff', 'continuity', 'collaboration', 'provenance'],
    }
}

for name, cfg in NAMES.items():
    target = ROOT / 'plugins' / name
    info = {
        '$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
        'name': name,
        'version': '0.1.0',
        'description': cfg['description'],
        'author': {'name': 'Observatory of Unfinished Things'},
        'keywords': cfg['keywords'],
        'skills': './skills',
        'extensions': {'com.openai': {
            'onboardingSkill': './skills/' + cfg['skills'] + '/SKILL.md',
            'interface': {
                'displayName': cfg['displayName'],
                'shortDescription': cfg['shortDescription'],
                'longDescription': cfg['longDescription'],
                'developerName': 'Observatory of Unfinished Things',
                'category': 'Productivity',
                'capabilities': ['Read'],
                'defaultPrompt': cfg['prompt'],
            }
        }}
    }
    (target / '.codex-plugin').mkdir(parents=True, exist_ok=True)
    (target / 'plugin.json').write_text(json.dumps(info, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    variant = {key: val for key, val in info.items() if key != '$schema'}
    variant['interface'] = variant['extensions']['com.openai'].pop('interface')
    (target / '.codex-plugin' / 'plugin.json').write_text(json.dumps(variant, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'LICENSE', target / 'LICENSE')
    out = DIST / (name + '-v0.1.0.zip')
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for f in sorted(target.rglob('*')):
            if f.is_file():
                z.write(f, f.relative_to(target))
    print(out)

out = DIST / 'open-door-continuity-v0.1.0-source.zip'
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for f in sorted(ROOT.rglob('*')):
        if not f.is_file() or '__pycache__' in f.parts or f.suffix == '.pyc':
            continue
        z.write(f, Path(ROOT.name) / f.relative_to(ROOT))
print(out)
