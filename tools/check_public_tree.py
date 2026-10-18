"""Check this documentation-only publication candidate. No network or device I/O."""
from pathlib import Path
import json
import hashlib
import re
import sys

EXPECTED = {
    '.gitignore', 'LICENSE', 'README.md',
    'assets/README.md', 'assets/social-preview.jpg',
    'docs/architecture.md', 'docs/experiment.md', 'docs/licensing.md',
    'docs/publication.md', 'docs/upstream-license-audit.json', 'docs/code-provenance.md',
    'examples/roster.synthetic.json', 'tools/check_public_tree.py',
}
BINARY_SHA256 = {'assets/social-preview.jpg': '9ba728b8d776125a83793dc6996d65715b29f01238b3a2e0d5ea04810fbbe581'}

PATTERNS = {
    'personal_absolute_path': re.compile('/' + r'(?:Users|home)/[^\s/]+/'),
    'private_key': re.compile('-----BEGIN ' + r'(?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github_token': re.compile(r'gh[pousr]_' + r'[A-Za-z0-9]{30,}'),
    'bearer_value': re.compile(r'Bearer ' + r'[A-Za-z0-9._~-]{24,}'),
}

def inspect(root):
    errors = []
    actual = set()
    for path in root.rglob('*'):
        rel = path.relative_to(root)
        if '.git' in rel.parts:
            continue
        if path.is_symlink():
            errors.append(f'symlink: {rel}')
            continue
        if not path.is_file():
            continue
        name = rel.as_posix()
        actual.add(name)
        if name not in EXPECTED:
            errors.append(f'not allowlisted: {name}')
            continue
        if name in BINARY_SHA256:
            if hashlib.sha256(path.read_bytes()).hexdigest() != BINARY_SHA256[name]:
                errors.append(f'unreviewed binary: {name}')
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeError:
            errors.append(f'non-text: {name}')
            continue
        for label, regex in PATTERNS.items():
            if regex.search(text):
                errors.append(f'{label}: {name}')  # never print matched values
        if path.suffix == '.md':
            if text.count('```') % 2:
                errors.append(f'unbalanced code fences: {name}')
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if target.startswith(('https://', 'http://', '#')):
                    continue
                resolved = (path.parent / target.split('#')[0]).resolve()
                if root.resolve() not in resolved.parents or not resolved.is_file():
                    errors.append(f'invalid local link: {name}')
    for name in EXPECTED - actual:
        errors.append(f'missing: {name}')
    example = root / 'examples/roster.synthetic.json'
    if example.exists():
        obj = json.loads(example.read_text())
        if obj.get('exported_at') is not None or obj.get('verification', {}).get('synthetic_example') is not True:
            errors.append('example is not explicitly synthetic')
        if len(obj.get('units', [])) != 1:
            errors.append('unexpected synthetic example size')
        if obj.get('verification', {}).get('live_api_tested') is not False:
            errors.append('synthetic example must not claim live verification')
    return errors

if __name__ == '__main__':
    errors = inspect(Path(__file__).resolve().parents[1])
    print(json.dumps({'passed': not errors, 'expected_files': len(EXPECTED), 'errors': errors}, ensure_ascii=False, indent=2))
    sys.exit(bool(errors))
