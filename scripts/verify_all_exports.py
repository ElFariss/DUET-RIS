import argparse,json,subprocess,sys
from pathlib import Path
from atomwise_ris.core import write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/raw/acquisition/munich_specular_v3');a=p.parse_args();root=Path(a.data)
    summaries=[]
    for path in sorted(root.glob('*/trace.json')):
        meta=json.loads(path.read_text())
        if not meta.get('deepmimo_loaded'):continue
        subprocess.run([sys.executable,'scripts/verify_export.py','--trace',str(path.parent),'--name',meta['deepmimo_scenario']],check=True)
        records=json.loads((path.parent/'deepmimo_parity.json').read_text())
        summaries.append({'trace':path.parent.name,'transmitters':len(records),
                          'max_relative_l2_error':max(v['manual_relative_l2_error'] for v in records)})
    if len(summaries)!=9 or sum(x['transmitters'] for x in summaries)!=68:raise AssertionError('Incomplete exports')
    write_json(root/'all_exports_verified.json',{'checks':summaries,'conversion':'Explicit carrier phase from exported interaction phase and delay',
                           'limit_relative_l2':.01,'scope':'All four BS and 64 RIS transmitters; raw float32 delays limit phase precision'})

if __name__=='__main__':main()
