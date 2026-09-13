"""Run correction/review tests using only the freshly extracted sdist's files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

from publication_policy import path_error, content_error, MAX_FILE_BYTES, MAX_ARCHIVE_BYTES


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def verify(archive, output):
    archive, output = Path(archive).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    unpacked = output / 'source'
    unpacked.mkdir()
    with tarfile.open(archive, 'r:gz') as handle:
        seen = set()
        total = 0
        for member in handle:
            if member.isdir():
                continue
            if not member.isfile() or member.name in seen or path_error(member.name):
                raise ValueError('unsafe or duplicate sdist member')
            seen.add(member.name)
            total += member.size
            if member.size > MAX_FILE_BYTES or total > MAX_ARCHIVE_BYTES or len(seen) > 5000:
                raise ValueError('sdist size limit exceeded')
            with handle.extractfile(member) as stream:
                data = stream.read()
            if content_error(data):
                raise ValueError('non-distributable sdist member')
            path = unpacked / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    source = unpacked / archive.name.removesuffix('.tar.gz')
    if not (source / 'tests/conftest.py').is_file():
        raise ValueError('sdist must supply tests/conftest.py')
    before = hashes(unpacked)
    env = dict(os.environ, PYTHONPATH=str(source), PYTHONDONTWRITEBYTECODE='1',
               DOCUWORKS_INTEGRATIONS_TEST_TMP=str(output / 'temp'))
    probe = 'import docuworks_integrations as p; from pathlib import Path; import sys; assert Path(p.__file__).is_relative_to(Path(sys.argv[1]))'
    subprocess.run([sys.executable, '-c', probe, str(source)], cwd=output, env=env, check=True)
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_corrections.py',
                             'tests/test_review_xdw.py', 'tests/test_review_xdw_regions.py', '-q', '-p', 'no:cacheprovider',
                             '--junitxml=' + str(output / 'junit.xml')], cwd=source, env=env)
    after = hashes(unpacked)
    added = set(after) - set(before)
    cache_only = all('__pycache__' in Path(name).parts and name.endswith('.pyc') for name in added)
    unchanged = all(after.get(name) == value for name, value in before.items()) and cache_only
    report = dict(exit_code=result.returncode, source_unchanged=unchanged,
                  supplemental_files_added=False, archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                  python=sys.version, source_files=len(before), generated_cache_files=len(added))
    (output / 'verification.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    if result.returncode or not unchanged:
        raise RuntimeError('sdist tests failed or extracted source changed')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.archive, args.output), indent=2))
