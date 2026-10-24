import argparse,json
from pathlib import Path
import numpy as np
from atomwise_ris.core import Scenario,ResponseModel,Evaluator,sha256,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--scenario',required=True);p.add_argument('--compare',default=None);a=p.parse_args()
    path=Path(a.scenario);s=Scenario.load(path);r=ResponseModel.from_table('data/processed/responses/opensourceris_v1.csv',5.53e9)
    layout=json.loads((path.parent/'layout.json').read_text())
    rng=np.random.default_rng(837);max_error=0.
    for idx in range(len(s.H)):
        e=Evaluator.from_scenario(s,idx,r);b=rng.integers(2,size=e.n,dtype=np.int8)
        full=e.full_field(b);max_error=max(max_error,float(np.max(abs(e.field(b)-full))))
        q=np.tile(b,(e.n,1));q[np.arange(e.n),np.arange(e.n)]^=1
        np.testing.assert_allclose(e.flip_fields(b),e.full_field(q),rtol=1e-10,atol=1e-15)
    counts={str(split):int(len(np.unique(s.trajectory[s.split==split]))) for split in np.unique(s.split)}
    front=np.array(layout['front_side_cosines']);assert (front>0).all()
    report={'scenario_sha256':sha256(path),'split_trajectory_counts':counts,'snapshots':len(s.H),
            'nonzero_fraction':{k:float(np.mean(abs(getattr(s,k))>0)) for k in ['G','H','D']},
            'cached_field_max_absolute_error':max_error,'front_side_cosine_min':float(front.min()),
            'front_side_cosine_max':float(front.max()),'rear_side_users':int(np.sum(front<=0)),
            'response_phase_contrast_degrees':float(abs(np.angle(r.gamma[1]/r.gamma[0],deg=True))),
            'physical_validity':'Mathematical checks passed; independent-cell/oblique response remains an approximation'}
    if a.compare:
        other=Scenario.load(a.compare)
        report['companion_comparison']={k:float(np.linalg.norm(getattr(s,k)-getattr(other,k))/np.linalg.norm(getattr(s,k))) for k in ['G','H','D']}
        report['companion_path']=a.compare;report['companion_sha256']=sha256(a.compare)
    write_json(path.parent/'audit.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
