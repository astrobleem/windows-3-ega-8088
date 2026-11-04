#!/usr/bin/env python3
"""Rebuild EGA8088 from checked source using a supplied historical toolchain.
Never downloads tools, initializes a lease, or modifies the source checkout.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,shutil,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
EXPECTED='3027415d8dc8410bd7bd42ece6e007424df049e9b739642ed3d8eb3967c79ba4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name):
 spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--toolchain',type=Path,required=True,help='Directory containing the pinned MASM.EXE, LINK4.EXE, EXE2BIN.EXE and SWINLIBC.LIB, possibly in subdirectories')
 ap.add_argument('--dosbox',type=Path,required=True,help='Existing DOSBox-X executable')
 ap.add_argument('--lease',type=Path,required=True,help='Existing nonempty shared emulator lease; never created by this script')
 ap.add_argument('--out',type=Path,required=True,help='New build directory')
 a=ap.parse_args();out=a.out.resolve();toolchain=a.toolchain.resolve()
 if out.exists():raise SystemExit('Choose a fresh --out directory')
 if not a.lease.is_file() or not a.lease.stat().st_size:raise SystemExit('--lease must already exist and be nonempty')
 manifest=json.loads((ROOT/'SOURCE-MANIFEST.json').read_text())
 for name,digest in manifest.items():
  if sha(ROOT/name)!=digest:raise SystemExit('Source checksum mismatch: '+name)
 pins=json.loads((ROOT/'TOOLCHAIN.json').read_text());found={}
 for name,digest in pins.items():
  matches=[p for p in toolchain.rglob('*') if p.is_file() and p.name.upper()==name and sha(p)==digest]
  if not matches:raise SystemExit('Missing toolchain input with expected checksum: '+name)
  found[name]=matches[0]
 out.mkdir(parents=True)
 for s,d in [('src','SRC'),('include','INC'),('resources','RES')]:shutil.copytree(ROOT/s,out/d)
 for d in ['BIN','LIB','run']:(out/d).mkdir()
 for name,p in found.items():shutil.copy2(p,out/('LIB' if name.endswith('.LIB') else 'BIN')/name)
 shutil.copy2(ROOT/'BUILD.BAT',out/'BUILD.BAT');shutil.copy2(ROOT/'MODULES.json',out/'PORT.json')
 cfg=out/'run/BUILD.CONF';cfg.write_text('[sdl]\noutput=surface\nfullscreen=false\n[dosbox]\nmachine=ega\nmemsize=16\nsplash logo=false\nshow basic information=false\n[cpu]\ncore=normal\ncputype=386\ncycles=fixed 200000\n[mixer]\nnosound=true\n[midi]\nmididevice=none\n[autoexec]\nmount R "'+str(out)+'"\nR:\nBUILD.BAT\nexit\n')
 module('guarded_dosbox').run(a.dosbox.resolve(),cfg,a.lease.resolve(),240)
 names=json.loads((ROOT/'MODULES.json').read_text())['modules'];errors=[]
 for path in [out/'SRC'/(n+'.LOG') for n in names]+[out/'SRC/LINK.LOG']+[out/'RES'/(n+'.LOG') for n in ['CONFIG','COLORTAB','FONTS']]:
  if not path.is_file():errors.append('Missing log '+str(path));continue
  s=path.read_text(errors='replace')
  if any(int(n) for n in re.findall(r'(\d+)\s+Severe\s+Errors',s)) or re.search(r'error [AL]\d+|fatal error',s,re.I):errors.append(path.name+': '+s)
 if errors:raise SystemExit('\n'.join(errors))
 for name in names:
  if not (out/'SRC'/(name+'.OBJ')).is_file() or not (out/'SRC'/(name+'.LST')).is_file():raise SystemExit('Missing object/listing: '+name)
 for name in ['CONFIG','COLORTAB','FONTS']:
  if not (out/'RES'/(name+'.BIN')).is_file():raise SystemExit('Missing resource: '+name)
 for name,report in [('ISA.json',module('AUDIT88').audit(sorted((out/'SRC').glob('*.LST')))),('REP-AUDIT.json',module('AUDITREP').audit_listings(sorted((out/'SRC').glob('*.LST')))),('LINK-CLOSURE.json',module('AUDITLINK').audit_link(out))]:
  (out/name).write_text(json.dumps(report,indent=2)+'\n')
 os.environ.update(EGA88_RESOURCES=str(out/'RES'),EGA88_WINDOWS_H=str(out/'INC/WINDOWS.H'))
 pack=module('pack_resources');records=pack.resource_records();resource=pack.write_res(records)
 if pack.read_res(resource)!=records:raise SystemExit('Resource roundtrip mismatch')
 (out/'EGA.RES').write_bytes(resource)
 binary,delta=pack.attach_ne((out/'SRC/EGA88.DRV').read_bytes(),records);(out/'EGA88.DRV').write_bytes(binary)
 digest=sha(out/'EGA88.DRV')
 result={'result':'PASS' if digest==EXPECTED else 'HASH_MISMATCH','driver_sha256':digest,'expected_sha256':EXPECTED,'driver_bytes':len(binary),'source_modules':len(names),'resource_records':len(records),'resource_header_growth':delta,'scope':'Source rebuild, 8086 instruction/listing and link-closure checks; not a new GUI or hardware test'}
 (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 if digest!=EXPECTED:raise SystemExit('Rebuilt driver differs from qualified binary')
if __name__=='__main__':main()
