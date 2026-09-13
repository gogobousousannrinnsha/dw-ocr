"""Export buildable MIT project source, retaining the established public notices."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import re
import xml.etree.ElementTree as ET


def export(repo, baseline_public, output, *, release_version='v0.3.0'):
    repo, baseline_public, output=map(Path,(repo,baseline_public,output))
    if not re.fullmatch(r'v\d+\.\d+\.\d+', release_version):
        raise ValueError('invalid Portable release version')
    metadata=(repo/'packages/docuworks-integrations/pyproject.toml').read_text(encoding='utf-8')
    version=re.search(r'^version = "([^"]+)"$',metadata,re.M).group(1)
    runtime=(repo/'packages/docuworks-integrations/docuworks_integrations/__init__.py').read_text(encoding='utf-8')
    if f'__version__ = "{version}"' not in runtime or not re.fullmatch(r'\d+\.\d+\.\d+',version):
        raise ValueError('stable package and runtime versions must match')
    if output.exists(): raise FileExistsError(output)
    output.mkdir(parents=True)
    for name in ('LICENSE','LICENSE_NOTICE.md','THIRD_PARTY_NOTICES.md'):
        shutil.copyfile(baseline_public/name,output/name)
    for name in ('docuworks-ctypes','docuworks-integrations'):
        source=repo/'packages'/name
        destination=output/'packages'/name
        shutil.copytree(source,destination,ignore=shutil.ignore_patterns(
            '__pycache__','*.pyc','*.egg-info','build','dist','.pytest_cache','integration-artifacts'))
        metadata=destination/'pyproject.toml'
        text=metadata.read_text(encoding='utf-8').replace('license = {text = "Proprietary"}',
                                                        'license = {text = "MIT"}')
        metadata.write_text(text,encoding='utf-8')
        shutil.copyfile(baseline_public/'LICENSE',destination/'LICENSE')
    for folder in ('portable','requirements','docs','examples','scripts'):
        if folder=='docs' and (baseline_public/folder).is_dir():
            shutil.copytree(baseline_public/folder,output/folder)
        shutil.copytree(repo/folder,output/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    # Preserve already published compatibility entry points; do not regenerate their shell syntax.
    for name in ('ocr_rectangles.bat','text_maps.bat'):
        shutil.copyfile(baseline_public/'portable'/name,output/'portable'/name)
    # Historical development records stay recognizable as redacted records;
    # operational clone instructions point to the public repository instead.
    for path in (output/'docs').rglob('*'):
        if path.is_file() and path.suffix=='.xml':
            tree=ET.parse(path)
            for element in tree.iter():
                for key in ('hostname','file'): element.attrib.pop(key,None)
            tree.write(path,encoding='utf-8',xml_declaration=True)
        if not path.is_file() or path.suffix not in ('.md','.json'): continue
        text=path.read_text(encoding='utf-8')
        if path.name=='INSTALLED_PACKAGES.md':
            text=re.sub(r'\| docuworks-integrations \| [^|]+ \|',f'| docuworks-integrations | {version} |',text)
        pattern=r'https://github\.com/[A-Za-z0-9_-]+/docuworks-ocr(?:\.git)?'
        if path.name=='SIMPLE_GUIDE.md':
            text=re.sub(pattern,'https://github.com/gogobousousannrinnsha/dw-ocr.git',text)
        else:
            text=re.sub(pattern,'REDACTED_PRIVATE_REPOSITORY',text)
            text=re.sub(r'`[A-Za-z0-9_-]+/docuworks-ocr`','`REDACTED_PRIVATE_REPOSITORY`',text)
        path.write_text(text,encoding='utf-8')
    (output/'README.md').write_text(f'# DW-OCR {release_version}\n\n'
        f'Integrations {version} / Core 1.0.0。Pre-release。\n\n'
        '[利用・移行・API手順](docs/UNIFIED_0.6.0.md)\n\n'
        '[文字訂正](docs/CORRECTIONS_0.7.0.md) / '
        '[確認用XDW](docs/REVIEW_XDW_REGIONS_0.7.0.md)\n\n'
        '通常のOCR入口は従来どおりです。訂正・確認用XDWはPython APIとして提供します。\n\n'
        'ソースのビルド: `python -m build packages/docuworks-integrations`\n'
        'Coreも同様にpackages/docuworks-ctypesからビルドします。\n',encoding='utf-8')
    # Public requirements must refer to this export's local packages, never a private URL.
    files=[]
    for path in sorted(output.rglob('*')):
        if path.is_file():
            data=path.read_bytes()
            files.append(dict(path=path.relative_to(output).as_posix(),bytes=len(data),
                              sha256=hashlib.sha256(data).hexdigest()))
    (output/'source-manifest.json').write_text(json.dumps(dict(files=files),indent=2)+'\n',encoding='utf-8')
    return files


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--baseline-public',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--release-version',default='v0.3.0')
    a=p.parse_args(); print(len(export(a.repo,a.baseline_public,a.output,release_version=a.release_version)))
