"""Stream a fresh Portable from a pinned baseline ZIP and tested public wheels.

No live environment is modified. Unchanged compressed members are copied verbatim.
Python 3.13 zipfile internals used by the copier are covered by full CRC verification.
"""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import zipfile
from email.parser import BytesParser


def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()


def build(baseline, expected_hash, wheels, portable, output, *, release_version='v0.3.0', source=None):
    baseline, wheels, portable, output=map(Path,(baseline,wheels,portable,output))
    if digest(baseline)!=expected_hash: raise ValueError('baseline SHA-256 mismatch')
    if output.exists(): raise FileExistsError(output)
    if not re.fullmatch(r'v\d+\.\d+\.\d+',release_version): raise ValueError('invalid release version')
    changes={p.relative_to(portable).as_posix():p.read_bytes() for p in portable.rglob('*')
             if p.is_file() and '__pycache__' not in p.parts}
    for name in tuple(changes):
        if name.endswith('.bat'):
            # ASCII BAT syntax and a Japanese filename; CRLF for cmd.exe.
            changes[name]=changes[name].replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
    wheel_paths=sorted(wheels.glob('*.whl'))
    if len(wheel_paths)!=2: raise ValueError('Exactly Core and Integrations wheels required')
    versions={}
    for wheel in wheel_paths:
        changes['wheelhouse/'+wheel.name]=wheel.read_bytes()
        with zipfile.ZipFile(wheel) as archive:
            metadata_names=[n for n in archive.namelist() if n.endswith('.dist-info/METADATA')]
            if len(metadata_names)!=1: raise ValueError('ambiguous wheel metadata')
            metadata=BytesParser().parsebytes(archive.read(metadata_names[0]))
            package=metadata['Name'].replace('_','-')
            if package in versions: raise ValueError('duplicate package')
            versions[package]=metadata['Version']
            for name in archive.namelist():
                if '.data/' in name or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or ':' in name:
                    raise ValueError('unexpected wheel data layout')
                changes['runtime/Lib/site-packages/'+name]=archive.read(name)
    if set(versions)!={'docuworks-ctypes','docuworks-integrations'}: raise ValueError('unexpected wheel packages')
    version=versions['docuworks-integrations']
    if versions['docuworks-ctypes']!='1.0.0' or not re.fullmatch(r'\d+\.\d+\.\d+',version):
        raise ValueError('expected Core 1.0.0 and stable Integrations')
    init=changes['runtime/Lib/site-packages/docuworks_integrations/__init__.py'].decode('utf-8')
    if f'__version__ = "{version}"' not in init: raise ValueError('wheel/runtime version mismatch')
    if source is not None:
        source=Path(source)
        project=(source/'packages/docuworks-integrations/pyproject.toml').read_text(encoding='utf-8')
        if f'version = "{version}"' not in project: raise ValueError('source/wheel version mismatch')
        for folder in ('docs','examples'):
            for path in (source/folder).rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts:
                    changes[path.relative_to(source).as_posix()]=path.read_bytes()
    changes['README.txt']=(f'DW-OCR {release_version} Pre-release / Integrations {version}\n'
        'INPUTへXDWを入れOCR開始.batを実行、またはXDWとフォルダをドロップします。\n'
        '全ページをOCRし、赤い矩形と確認画像をOUTPUTへ保存します。\n'
        'OCRの保存結果はrunsに保持します。設定はsettings.ini。\n'
        '実行には対応するDocuWorksとNVIDIA GPUが必要です。\n'
        '文字訂正・確認用XDWはPython APIです。docsとexamplesを参照してください。\n'
        '原本重ね合わせ型・1ページ内の指定領域に対応。白紙型・検索・テンプレートは対象外です。\n'
        '既知のマーカー線幅問題は今回の矩形経路とは別課題です。\n').encode('utf-8-sig')
    changes['PROVENANCE.txt']=(f'DW-OCR {release_version} Pre-release\nBaseline archive SHA256: '+expected_hash+
        f'\nCore 1.0.0; Integrations {version}; Python 3.13.15\n'+
        '\n'.join(w.name+' SHA256 '+digest(w) for w in wheel_paths)+'\n').encode()
    changes['reference/project-wheels.json']=json.dumps({w.name:digest(w) for w in wheel_paths},indent=2).encode()
    for folder in ('INPUT','OUTPUT','runs','cache'): changes[folder+'/']=b''
    removed=[]
    with zipfile.ZipFile(baseline) as original:
        for name in original.namelist():
            if name.endswith('.bat') and name not in changes:
                data=original.read(name)
                text=data.decode('utf-8-sig')
                updated=re.sub(r'docuworks-integrations==\d+\.\d+\.\d+',f'docuworks-integrations=={version}',text)
                # No injection into existence checks, no duplicate execution flags or environment blocks.
                if updated!=text: changes[name]=updated.encode('utf-8-sig' if data.startswith(b'\xef\xbb\xbf') else 'utf-8')
        # Keep all third-party binary/model/license content, replace only own package/entrypoints.
        for name in original.namelist():
            lower=name.lower()
            if ('__pycache__' in lower or lower.endswith('.pyc') or
                lower.startswith(('wheelhouse/','runtime/lib/site-packages/docuworks_integrations',
                                  'runtime/lib/site-packages/docuworks_ctypes')) or
                lower in ('sha256sums.txt','tools_sha256sums.txt','tools_provenance.json','installed_packages.txt',
                          'pip_check.txt','readme_tools_ja.txt','public_packaging_changes.txt')):
                removed.append(name)
        with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED,allowZip64=True) as out, baseline.open('rb') as raw:
            infos=original.infolist()
            if len(infos)!=len(set(i.filename for i in infos)): raise ValueError('duplicate ZIP member')
            for index,info in enumerate(infos):
                name=info.filename
                if name in changes:
                    out.writestr(name,changes.pop(name)); continue
                if name in removed: continue
                if PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or ':' in name:
                    raise ValueError('unsafe ZIP path')
                if info.flag_bits&1: raise ValueError('encrypted baseline member')
                end=infos[index+1].header_offset if index+1<len(infos) else original.start_dir
                new=copy.copy(info); new.header_offset=out.fp.tell()
                out._writecheck(new); out._didModify=True
                raw.seek(info.header_offset)
                remaining=end-info.header_offset
                while remaining:
                    chunk=raw.read(min(8*1024*1024,remaining))
                    if not chunk: raise EOFError('truncated baseline')
                    out.fp.write(chunk); remaining-=len(chunk)
                out.filelist.append(new); out.NameToInfo[name]=new; out.start_dir=out.fp.tell()
            for name,data in sorted(changes.items()): out.writestr(name,data)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None: raise ValueError('Portable CRC failed')
        names=archive.namelist()
        dist_infos={n.split('/')[3] for n in names if n.startswith('runtime/Lib/site-packages/docuworks_integrations-')}
        if dist_infos!={f'docuworks_integrations-{version}.dist-info'}: raise ValueError('old package remains')
    return dict(sha256=digest(output),bytes=output.stat().st_size,removed=removed)


def split(archive, destination, helper_baseline):
    archive,destination,helper_baseline=map(Path,(archive,destination,helper_baseline))
    destination.mkdir()  # fresh only
    size=archive.stat().st_size; whole=digest(archive)
    chunk_size=400*1024*1024-4096
    parts=[]
    with archive.open('rb') as stream:
        index=0
        while data:=stream.read(chunk_size):
            index+=1; name=f'dw_ocr_with_code.zip.{index:03d}'
            target=destination/f'ocr_part_{index:03d}_transport.zip'
            with zipfile.ZipFile(target,'x',zipfile.ZIP_STORED) as wrapper: wrapper.writestr(name,data)
            if target.stat().st_size>400*1024*1024: raise ValueError('transport exceeds 400 MiB')
            parts.append(dict(index=index,file=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    manifest=dict(schema='docuworks-portable-split',schema_version=1,output_file='dw_ocr_with_code.zip',
                  bytes=size,sha256=whole,chunk_size_bytes=chunk_size,parts=parts)
    helpers={name:(helper_baseline/name).read_bytes() for name in ('join_parts.ps1','join_parts.bat','verify_parts.bat','LICENSE')}
    script=helpers['join_parts.ps1'].decode('utf-8-sig')
    script=re.sub(r"\$ExpectedHash = '[a-f0-9]+'",f"$ExpectedHash = '{whole}'",script)
    script=re.sub(r'\$ExpectedBytes = \[long\]\d+',f'$ExpectedBytes = [long]{size}',script)
    script=script.replace('$parts.Count -ne 8',f'$parts.Count -ne {len(parts)}').replace('$i -lt 8',f'$i -lt {len(parts)}')
    script=script.replace('Exactly 8',f'Exactly {len(parts)}').replace('all 8',f'all {len(parts)}').replace('All 8',f'All {len(parts)}')
    helpers['join_parts.ps1']=script.encode('utf-8-sig')
    helpers['split_manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    helpers['README_JOIN_JA.txt']=(f'全{len(parts)}個のtransport ZIPと結合ツールを同じフォルダへ置き、join_parts.batを実行します。\n'
        '結合後のZIPを新しい場所へ展開してください。別版の部品と混用できません。\n').encode('utf-8-sig')
    with zipfile.ZipFile(destination/'ocr_join_tools.zip','x',zipfile.ZIP_DEFLATED) as helperzip:
        for name,data in helpers.items():
            (destination/name).write_bytes(data); helperzip.writestr(name,data)
    (destination/'SHA256SUMS.txt').write_text(''.join(digest(p)+'  '+p.name+'\n' for p in sorted(destination.iterdir()) if p.is_file()),encoding='ascii')
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--baseline-sha256',required=True)
    p.add_argument('--wheels',type=Path,required=True)
    p.add_argument('--portable',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--split-dir',type=Path)
    p.add_argument('--helper-baseline',type=Path)
    p.add_argument('--release-version',default='v0.3.0')
    p.add_argument('--source',type=Path)
    a=p.parse_args()
    print(json.dumps(build(a.baseline,a.baseline_sha256,a.wheels,a.portable,a.output,release_version=a.release_version,source=a.source)),flush=True)
    if a.split_dir: print(json.dumps(split(a.output,a.split_dir,a.helper_baseline)),flush=True)
