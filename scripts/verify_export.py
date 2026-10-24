"""Audit public DeepMIMO conversion against saved Sionna CIRs."""
import argparse
from pathlib import Path
import json
import numpy as np
from scipy.spatial import cKDTree
import deepmimo as dm
from deepmimo.datasets.dataset import Dataset,MacroDataset
from atomwise_ris.core import write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--trace',default='data/munich_pilot/smoke')
    p.add_argument('--name',default='sionna_export');a=p.parse_args()
    z=np.load(Path(a.trace)/'paths.npz');ds=dm.load(a.name,max_paths=100000)
    def flatten(x):
        if isinstance(x,MacroDataset):return flatten(x.datasets)
        if isinstance(x,Dataset):
            if 'power' in x:return [x]
        if isinstance(x,dict):return [v for child in x.values() for v in flatten(child)]
        if isinstance(x,(list,tuple)):return [v for child in x for v in flatten(child)]
        return []
    items=flatten(ds)
    results=[]
    for i,x in enumerate(items):
        if not hasattr(x,'keys') or 'power' not in x:continue
        f=float(x.rt_params.frequency)
        # Exported phase is interaction phase before propagation delay. Unlike
        # paths.cir(), it needs the carrier delay exactly once when reconstructing.
        h=np.nansum(10**(x.power.astype(float)/20)*np.exp(1j*np.deg2rad(x.phase.astype(float))-2j*np.pi*f*x.delay.astype(float)),axis=-1)
        # DeepMIMO sorts unique transmitter coordinates, so tx_idx is NOT the
        # original Sionna insertion index (the rotated RIS row reverses order).
        tx_distance,tx=cKDTree(z['tx']).query(np.asarray(x.tx_pos).reshape(-1,3)[0])
        rx_distance,rx=cKDTree(z['rx']).query(np.asarray(x.rx_pos).reshape(-1,3))
        if tx_distance>1e-4 or np.max(rx_distance)>1e-4 or len(set(rx))!=len(rx):
            raise AssertionError('Exported physical node matching failed')
        tx=int(tx);expected=z['channel'][rx,tx]
        error=float(np.linalg.norm(h-expected)/max(np.linalg.norm(expected),1e-30))
        params=dm.ChannelParameters()
        params.bs_antenna.shape=np.array([1,1]);params.ue_antenna.shape=np.array([1,1]);params.freq_domain=0
        params.num_paths=x.power.shape[1]
        generated=x.compute_channels(params)
        raw_generated=generated.sum(-1).reshape(-1)
        gen_error=float(np.linalg.norm(raw_generated-expected)/max(np.linalg.norm(expected),1e-30))
        results.append({'tx':tx,'deepmimo_tx_idx':int(x.txrx['tx_idx']),
                        'coordinate_match_max_m':float(max(tx_distance,np.max(rx_distance))),
                        'manual_relative_l2_error':error,'deepmimo_channel_shape':list(generated.shape),
                        'default_deepmimo_summed_taps_error':gen_error,
                        'frequency_hz':f,'actual_diffraction_metadata':bool(x.rt_params.raw_params['diffraction'])})
    write_json(Path(a.trace)/'deepmimo_parity.json',results);print(json.dumps(results,indent=2))
    if len(results)!=z['channel'].shape[1] or any(v['manual_relative_l2_error']>.01 for v in results):
        raise AssertionError('DeepMIMO export parity check failed')

if __name__=='__main__':main()
