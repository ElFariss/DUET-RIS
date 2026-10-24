"""Generate actual 5.53-GHz Munich propagation and export each trace to DeepMIMO.

All antennas/cells are explicit singleton nodes, so no far-field synthetic-array
phase approximation is made inside the RIS panel. Gamma is absent in RT and
applied exactly once by Evaluator. RIS cells are virtual probes, not scene meshes.
"""
import argparse
import inspect
import json
import os
from pathlib import Path
import time
import pickle
import importlib.metadata
import numpy as np
import sionna.rt as rt
import mitsuba as mi
import deepmimo as dm
from deepmimo import consts as dm_consts
from deepmimo.exporters.sionna_exporter import sionna_exporter
from atomwise_ris.core import Scenario, C0, sha256, write_json, source_versions

def asarray(x):
    return np.asarray(x.numpy() if hasattr(x,'numpy') else x)

def channels(paths):
    # cir() returns carrier-phase coefficients; do not multiply by exp(-j*fc*tau) again.
    a,tau=paths.cir(normalize_delays=False,out_type='numpy')
    # [rx,rx_ant,tx,tx_ant,path,time], all singleton antennas and one time step.
    if a.ndim != 6:raise RuntimeError(f'Unexpected CIR shape {a.shape}')
    return a[:,0,:,0,:,0].sum(-1).astype(np.complex128),a,tau

def base_scene():
    scene=rt.load_scene(rt.scene.munich);scene.frequency=5.53e9
    ant=rt.PlanarArray(num_rows=1,num_cols=1,vertical_spacing=.5,horizontal_spacing=.5,pattern='iso',polarization='V')
    scene.tx_array=ant;scene.rx_array=ant
    return scene

def trace(tx,rx,out,params,export=True):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    s=base_scene()
    for i,p in enumerate(tx):s.add(rt.Transmitter(f'tx_{i}',position=p.tolist()))
    for i,p in enumerate(rx):s.add(rt.Receiver(f'rx_{i}',position=p.tolist()))
    start=time.perf_counter();paths=rt.PathSolver()(scene=s,**params)
    h,a,tau=channels(paths)
    np.savez_compressed(out/'paths.npz',channel=h,a=a,tau=tau,tx=tx,rx=rx)
    info={'seconds':time.perf_counter()-start,'tx_count':len(tx),'rx_count':len(rx),
          'nonzero_links':int(np.count_nonzero(abs(h)>0)),'total_links':h.size,'a_shape':list(a.shape),
          'parameters':params}
    if export:
        export_dir=out/(out.parent.name+'_'+out.name);sionna_exporter(s,paths,params,str(export_dir))
        # DeepMIMO 4.0.5 hardcodes the diffraction alias to False, even though
        # Sionna RT 2.0.1 accepts diffraction=True. Correct only this metadata.
        rp=export_dir/'sionna_rt_params.pkl'
        with rp.open('rb') as f: exported_params=pickle.load(f)
        exported_params['diffraction']=bool(params.get('diffraction',False))
        with rp.open('wb') as f:pickle.dump(exported_params,f)
        info['exporter_compatibility_fix']='Preserved requested diffraction flag instead of hardcoded False alias'
        # DeepMIMO's converter owns its scenario directory; use a project-local root.
        previous_max=dm_consts.MAX_PATHS
        try:
            dm_consts.MAX_PATHS=max(previous_max,a.shape[-2])
            name=dm.convert(str(export_dir),overwrite=True,deduplicate=False,vis_scene=False)
        finally:
            dm_consts.MAX_PATHS=previous_max
        info['converter_path_capacity']=a.shape[-2]
        info['conversion_deduplicate']=False
        info['deepmimo_scenario']=name
        ds=dm.load(name,max_paths=100000)
        info['deepmimo_loaded']=True
        info['deepmimo_type']=type(ds).__name__
    write_json(out/'trace.json',info);print(json.dumps(info),flush=True)
    return h

def free_space_check(out):
    s=rt.load_scene();s.frequency=5.53e9
    s.tx_array=s.rx_array=rt.PlanarArray(num_rows=1,num_cols=1,vertical_spacing=.5,horizontal_spacing=.5,pattern='iso',polarization='V')
    s.add(rt.Transmitter('t',position=[0,0,2]));s.add(rt.Receiver('r',position=[10,0,2]))
    p=rt.PathSolver()(scene=s,max_depth=0,los=True,samples_per_src=1000,seed=7)
    h,a,tau=channels(p);expected=(C0/5.53e9)/(4*np.pi*10)*np.exp(-2j*np.pi*5.53e9*10/C0)
    relative=float(abs(h.item()-expected)/abs(expected))
    # Polarization basis can contribute a common sign; report it explicitly.
    ratio=h.item()/expected
    info={'actual_real':h.item().real,'actual_imag':h.item().imag,'expected_real':expected.real,
          'expected_imag':expected.imag,'relative_complex_error':relative,
          'magnitude_relative_error':float(abs(abs(h.item())/abs(expected)-1)),
          'phase_offset_degrees':float(np.angle(ratio,deg=True)),'delay_seconds':np.asarray(tau).reshape(-1).tolist()}
    if info['magnitude_relative_error']>1e-4 or relative>5e-3:
        raise RuntimeError(f'Free-space phase/normalization failed: {info}')
    write_json(out/'free_space_check.json',info)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='data/raw/acquisition/munich_specular_v3')
    ap.add_argument('--trajectories',type=int,default=24);ap.add_argument('--steps',type=int,default=4)
    ap.add_argument('--samples',type=int,default=100000);ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--source-batch',type=int,default=8)
    ap.add_argument('--max-paths',type=int,default=1000000)
    ap.add_argument('--no-diffraction',action='store_true')
    ap.add_argument('--skip-export',action='store_true');args=ap.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    free_space_check(out)
    params=dict(max_depth=3,los=True,specular_reflection=True,diffuse_reflection=False,
                diffraction=not args.no_diffraction,refraction=False,samples_per_src=args.samples,
                max_num_paths_per_src=args.max_paths,synthetic_array=False,seed=7)
    if args.smoke:
        trace(np.array([[-210.,73.,105.]]),np.array([[40.,20.,1.5],[20.,50.,1.5]]),out/'smoke',params,not args.skip_export)
        return
    # Fixed design chosen before objective evaluation; no label-driven placement.
    bs=np.array([-210.,73.,105.])+np.column_stack([np.zeros(4),(np.arange(4)-1.5)*(C0/5.53e9)/2,np.zeros(4)])
    center=np.array([65.,20.,3.])
    # Vertical 8x8 panel, 20 mm horizontal pitch and 13 mm vertical pitch.
    # Horizontal normal faces the BS; normal-incidence scalar response is extrapolated.
    normal=np.array([-210.,73.,0.])-np.array([65.,20.,0.]);normal/=np.linalg.norm(normal)
    tangent=np.array([-normal[1],normal[0],0.])
    cells=np.array([center+(j-3.5)*.020*tangent+(i-3.5)*.013*np.array([0.,0.,1.]) for i in range(8) for j in range(8)])
    # Disjoint rectangular spatial blocks, assigned BEFORE rays/labels. Two users
    # move together inside each block. Block boundaries include a guard interval.
    nt=args.trajectories;steps=args.steps
    if nt!=24:raise ValueError('The registered pilot spatial layout has exactly 24 trajectories')
    scene=base_scene()
    def outdoor(p):
        hit=scene.mi_scene.ray_intersect(mi.Ray3f(mi.Point3f(float(p[0]),float(p[1]),1000),mi.Vector3f(0,0,-1)))
        return bool(asarray(hit.is_valid())[0]) and float(asarray(hit.p)[2,0])<.5
    if not outdoor(center):raise RuntimeError('RIS center is not outdoors')
    candidates=[np.array([18+8*j,12+8*i,1.5]) for i in range(10) for j in range(6)]
    accepted=[];rejected=[]
    for c in candidates:
        corners=[c+[-1.2,-.3,0],c+[-1.2,.3,0],c+[1.2,.4,0],c+[1.2,1.,0]]
        valid=all(outdoor(p) and np.dot(p-center,normal)>0 for p in corners)
        (accepted if valid else rejected).append(c)
    if len(accepted)<nt:raise RuntimeError(f'Only {len(accepted)} valid spatial blocks')
    block_centers=np.array(accepted[:nt])
    split_by_block=np.array(['train']*12+['validation']*6+['pilot']*6)
    positions=[];trajectory=[];splits=[]
    for t,c in enumerate(block_centers):
        for step in range(steps):
            offset=(step-(steps-1)/2)*.15
            positions.append([c+[-1.2,offset,0],c+[1.2,offset+.7,0]])
            trajectory.append(t);splits.append(split_by_block[t])
    pos=np.asarray(positions)
    layout={'bs':bs.tolist(),'ris_center':center.tolist(),'panel_normal':normal.tolist(),
            'cells':cells.tolist(),'users':pos.tolist(),'trajectory':trajectory,'split':splits,
            'chosen_before_channels':True,'guard_m':4.0,
            'outdoor_selection':'Downward ray must hit ground below 0.5 m at every trajectory corner; positive panel-front dot product',
            'rejected_block_centers':np.asarray(rejected).tolist(),'candidate_order':'Increasing y, then x; first 24 outdoor blocks',
            'front_side_cosines':((pos-center)@normal/np.linalg.norm(pos-center,axis=-1)).tolist()}
    write_json(out/'layout.json',layout)
    # Per-transmitter batches keep exporter RAM and GPU path capacity bounded.
    gd=trace(bs,np.vstack([cells,pos.reshape(-1,3)]),out/'bs',params,not args.skip_export)
    g=gd[:64];direct=gd[64:].reshape(len(pos),2,4)
    hs=[]
    for j in range(0,64,args.source_batch):
        h=trace(cells[j:j+args.source_batch],pos.reshape(-1,3),out/f'ris_{j:02}',params,not args.skip_export)
        hs.append(h)
    h=np.concatenate(hs,axis=1).reshape(len(pos),2,64)
    versions={n:importlib.metadata.version(n) for n in ['numpy','torch','sionna-rt','deepmimo','mitsuba','drjit']}
    scene_path=Path(rt.scene.munich)
    # Dataset includes geometry source hashes; the distributable scene ships with pinned sionna-rt.
    source_hashes={str(p.relative_to(scene_path.parent)):sha256(p) for p in sorted(scene_path.parent.rglob('*')) if p.is_file()}
    # 1-MHz equivalent narrowband receiver, 7-dB NF, 290 K thermal noise.
    noise=1.380649e-23*290*1e6*10**(.7)
    metadata={'frequency_hz':5.53e9,'power_w':.1,'noise_w':noise,'noise_bandwidth_hz':1e6,'noise_figure_db':7,
              'cell_area_m2':.020*.013,'versions':versions,'scene_sha256':source_hashes,'ray_parameters':params,
              'source':'Sionna built-in Munich, newly ray traced, DeepMIMO export',
              'response_approximation':'Independent scalar cells, co-polar V, angle independent; uniform-surface response extrapolated',
              'aperture_normalization':'Cascade of isotropic voltage gains times 4*pi*cell_area/lambda^2',
              'phase_convention':'Sionna CIR carrier phase retained; transfer matrices have no additional conjugation',
              'precoder':'Propagation independent of precoder; consult evaluator run metadata',
              'split_unit':'Disjoint spatial block containing entire two-user trajectory',
              'pilot_is_development':True,'untouched_final_test_generated':False,
              'diffuse_reflection':False,'reason':'Explicit RT settings; see separate convergence audits',
              'layout_sha256':sha256(out/'layout.json')}
    metadata['represented_frequency_hz']=float(asarray(scene.frequency)[0])
    metadata['deepmimo_export_completed']=not args.skip_export
    metadata['coefficient_origin']='Sionna CIR; companion DeepMIMO export is verified separately'
    metadata['source_sha256']=source_versions()
    Scenario(g,h,direct,pos,cells,np.asarray(trajectory),np.asarray(splits),metadata).save(out/'scenario.npz')
    print('SCENARIO_COMPLETE',out/'scenario.npz',flush=True)

if __name__=='__main__':main()
