"""Reproducible color-curve extraction; calibration read from original figure axes."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from atomwise_ris.core import write_json, sha256

ROOT=Path(__file__).resolve().parents[1]

def extract(file,state,phase=False):
    im=np.asarray(Image.open(file).convert('RGB')).astype(int)
    r,g,b=im.transpose(2,0,1)
    mask=(b>180)&(r<100)&(g<100) if state=='off' else (r>180)&(g<100)&(b<100)
    x0,x1=(142,682) if phase else (128,669)
    # Exclude legend and wrap's vertical line. Vertical phase wrap is interpolated
    # in unwrapped phase, never by averaging the +180/-180 edge.
    mask[:32]=False; mask[480:]=False
    if phase: mask[383:,450:]=False; mask[:,443:448]=False
    else: mask[410:,436:]=False
    xs=[];ys=[]
    for x in range(x0+1,x1):
        y=np.flatnonzero(mask[:,x])
        if len(y) and y.max()-y.min()<12:
            xs.append(x);ys.append(np.median(y))
    f=5.1+(np.asarray(xs)-x0)/(x1-x0)*.8
    v=180-(np.asarray(ys)-31)/449*360 if phase else -(np.asarray(ys)-31)/449*10
    if phase: v=np.rad2deg(np.unwrap(np.deg2rad(v)))
    return f,v

def main():
    src=ROOT/'data/raw/opensourceris-and-upstream';out=ROOT/'data/processed/responses';out.mkdir(exist_ok=True)
    freq=np.round(np.arange(5.15,5.8751,.005),6)
    columns=[freq];fig,axs=plt.subplots(1,2,figsize=(10,3.5))
    for phase in (False,True):
        for state,color in [('off','blue'),('on','red')]:
            f,v=extract(src/('phase.png' if phase else 'magnitude.png'),state,phase)
            val=np.interp(freq,f,v);columns.append(val)
            axs[int(phase)].plot(freq,val,color=color,label=state)
    np.savetxt(out/'opensourceris_v1.csv',np.array(columns).T,delimiter=',',fmt='%.8f',
               header='frequency_ghz,off_db,on_db,off_deg,on_deg',comments='')
    for ax,label in zip(axs,['Magnitude (dB)','Unwrapped phase (degrees)']):
        ax.set(xlabel='Frequency (GHz)',ylabel=label);ax.axvline(5.53,color='gray',ls=':');ax.legend();ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'digitization_check.png',dpi=180)
    write_json(out/'opensourceris_v1.json',{
      'source':'https://github.com/mheinri/OpenSourceRIS','commit':'7982a576a5edd389edfd81ece9a1f6675c7c545e',
      'measurement':'Uniform 16x16 panel, all OFF/all ON, normal incidence/reflection, metal-plate normalized',
      'scope':'Measurement-informed independent-cell approximation; mixed patterns and angle response unvalidated',
      'polarization':'Co-polarized scalar V approximation; cross-polar response not supplied',
      'cell_width_m':.020,'cell_height_m':.013,'cell_area_m2':.00026,
      'calibration':{'magnitude_axes_pixels':[128,669,31,480],'phase_axes_pixels':[142,682,31,480],
                     'frequency_ghz':[5.1,5.9],'magnitude_db':[0,-10],'phase_deg':[180,-180]},
      'digitization_bound':{'horizontal_pixels':2,'vertical_pixels':2,'frequency_hz':3e6,'magnitude_db':.05,'phase_deg':1.61},
      'sensitivity_envelope':{'digitization_db':.10,'digitization_deg':2,'model_db':1,'model_deg':15,
                              'note':'Model envelope is a stress test, not a measured confidence interval'},
      'image_sha256':{n:sha256(src/n) for n in ['magnitude.png','phase.png','cell.png']},
      'phase_reference':'Published metal-reference phase; unknown common registration phase must be stress-tested',
      'license':'MIT repository; retain attribution; plots attributed to Heinrichs et al.'})
    from atomwise_ris.core import ResponseModel
    r=ResponseModel.from_table(out/'opensourceris_v1.csv',5.53e9)
    print(json.dumps({'gamma_real':r.gamma.real.tolist(),'gamma_imag':r.gamma.imag.tolist(),
                      'magnitude_db':(20*np.log10(abs(r.gamma))).tolist(),'phase_deg':np.angle(r.gamma,deg=True).tolist()}))

if __name__=='__main__': main()
