"""Ray-count sensitivity on train/validation nodes only, without DeepMIMO export."""
import argparse,json
from pathlib import Path
import numpy as np
from trace_munich import trace
from atomwise_ris.core import Scenario,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',default='data/raw/acquisition/munich_compute_v2');p.add_argument('--samples',default='200000,500000')
    p.add_argument('--max-paths',type=int,default=1000000);p.add_argument('--no-diffraction',action='store_true')
    p.add_argument('--tag',default='capacity_check');a=p.parse_args()
    root=Path(a.data);s=Scenario.load(root/'scenario.npz');layout=json.loads((root/'layout.json').read_text())
    idx=np.array([0,16,32,48,64])  # fixed train/validation snapshots, never pilot
    rx=s.positions[idx].reshape(-1,3);tx=np.asarray(layout['bs']);params=dict(s.metadata['ray_parameters'])
    params['max_num_paths_per_src']=a.max_paths;params['diffraction']=not a.no_diffraction
    rows=[]
    previous_bs=None;previous_h=None
    for samples in [int(x) for x in a.samples.split(',')]:
        params['samples_per_src']=samples
        new=trace(tx,np.vstack([s.cell_positions,rx]),root/f'{a.tag}_bs_{samples}',params,False)
        expected=np.vstack([s.G,s.D[idx].reshape(-1,4)])
        rel=float(np.linalg.norm(new-expected)/max(np.linalg.norm(expected),1e-30))
        direct_rel=float(np.linalg.norm(new[64:]-expected[64:])/max(np.linalg.norm(expected[64:]),1e-30))
        h=trace(s.cell_positions[:8],rx,root/f'{a.tag}_ris_{samples}',params,False)
        target=s.H[idx,:,:8].reshape(-1,8)
        hrel=float(np.linalg.norm(h-target)/max(np.linalg.norm(target),1e-30))
        rows.append({'samples_per_source':samples,'baseline_samples':s.metadata['ray_parameters']['samples_per_src'],
                     'bs_relative_l2_change':rel,'direct_relative_l2_change':direct_rel,'ris_user_relative_l2_change':hrel})
        if previous_bs is not None:
            rows[-1]['bs_change_vs_previous']=float(np.linalg.norm(new-previous_bs)/np.linalg.norm(new))
            rows[-1]['ris_change_vs_previous']=float(np.linalg.norm(h-previous_h)/np.linalg.norm(h))
        previous_bs=new;previous_h=h
    write_json(root/f'{a.tag}.json',{'indices':idx.tolist(),'rows':rows,'arguments':vars(a),
                   'limitation':'Subset ray-count sensitivity only; not a full convergence proof or material-model validation'})
    print(json.dumps(rows,indent=2))

if __name__=='__main__':main()
