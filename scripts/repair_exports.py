"""Reconvert saved paths losslessly with respect to path count (no ray retracing).

DeepMIMO 4.0.5 converter silently retains only its first MAX_PATHS=25 active
paths, even when load(max_paths=...) requests more. Override the process-local
allocation ceiling to each saved trace's full capacity, then restore it. The
installed package is untouched. Original converted scenarios remain available.
"""
import argparse,json,pickle
from pathlib import Path
import deepmimo as dm
from deepmimo import consts
from atomwise_ris.core import write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/raw/acquisition/munich_specular_v3');a=p.parse_args();root=Path(a.data)
    records=[]
    for trace in sorted(root.glob('*/trace.json')):
        info=json.loads(trace.read_text());old=info['deepmimo_scenario'];source=trace.parent/old
        if not source.exists():
            source=next(p.parent for p in trace.parent.glob('*/sionna_paths.pkl'))
        with (source/'sionna_paths.pkl').open('rb') as f:paths=pickle.load(f)
        count=max(x['a'].shape[-1] for x in paths);original=consts.MAX_PATHS
        try:
            consts.MAX_PATHS=max(count,original)
            name=dm.convert(str(source),scenario_name=old.removesuffix('_fullpaths')+'_fullpaths',overwrite=True,deduplicate=False,vis_scene=False)
        finally:consts.MAX_PATHS=original
        info['original_deepmimo_scenario']=info.get('original_deepmimo_scenario',old)
        info['deepmimo_scenario']=name;info['converter_path_capacity']=count
        info['conversion_fix']='Process-local MAX_PATHS raised from 25 to saved trace capacity; original exports retained'
        write_json(trace,info);records.append({'trace':trace.parent.name,'old':old,'new':name,'path_capacity':count})
        print(records[-1],flush=True)
    write_json(root/'export_repair.json',records)

if __name__=='__main__':main()
