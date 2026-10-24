"""Publication-exportable figures from simulated geometry and network matrices."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from atomwise_ris.physics.network import CoupledNetwork
root=Path('outputs/runs/coupled_wire_v1');out=root/'figures';out.mkdir(parents=True,exist_ok=True)
data=Path('data/processed/coupled_wire_v1');ds=np.load(data/'frame_0000.npz');p=ds['centers'];z=ds['z'];rows=json.loads((data/'scenario.json').read_text())['rows'];gate=json.loads((root/'physics_gate.json').read_text());loads=np.array(gate['loads_real_ohm'])+1j*np.array(gate['loads_imag_ohm'])
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
fig=plt.figure(figsize=(12,5.4));ax=fig.add_subplot(121,projection='3d')
verts=[[(0,-.112,.88),(0,.112,.88),(0,.112,1.12),(0,-.112,1.12)]]
ax.add_collection3d(Poly3DCollection(verts,facecolors='#94a3b8',alpha=.17,edgecolors='#334155'))
for i,(x,y,zz) in enumerate(p[:64]):ax.plot([x,x],[y,y],[zz-.012,zz+.012],color='#2563eb',lw=2)
ax.scatter(*p[64:68].T,c='#dc2626',marker='^',s=42,label='4 BS ports')
for u,color in enumerate(['#16a34a','#9333ea']):
 trajectory=np.array([r['users_m'][u] for r in rows if r['trajectory']==0]);ax.plot(*trajectory.T,color=color,lw=2,label=f'UE {u+1}, 0–300 ms');ax.scatter(*trajectory[0],color=color,s=35)
ax.text(0,0,1.15,'8 × 8 wire surface',ha='center');ax.set(xlabel='x (m)',ylabel='y (m)',zlabel='z (m)',title='Actual simulated geometry');ax.view_init(23,-55);ax.legend(loc='upper left',bbox_to_anchor=(-.04,.98),fontsize=8);ax.set_box_aspect((1.1,1.4,.65))
ax2=fig.add_subplot(122,projection='3d');off=np.abs(z[:64,:64]).copy();np.fill_diagonal(off,0);strength=off.sum(1)
y=p[:64,1].reshape(8,8)*1000;zz=(p[:64,2].reshape(8,8)-1)*1000
surf=ax2.plot_surface(y,zz,strength.reshape(8,8),cmap='viridis',edgecolor='white',linewidth=.3)
ax2.set(xlabel='Horizontal position (mm)',ylabel='Vertical position (mm)',zlabel='Σ mutual |Z| (Ω)',title='Position-dependent electromagnetic coupling');ax2.view_init(28,-50)
fig.colorbar(surf,ax=ax2,shrink=.6,pad=.12,label='Coupling magnitude sum (Ω)')
fig.suptitle('5.53 GHz PEC wire reference — free space, no substrate or human blockers',fontsize=12)
fig.subplots_adjust(left=.01,right=.93,bottom=.05,top=.86,wspace=.12)
for ext in ['png','pdf']:fig.savefig(out/f'geometry_3d.{ext}',bbox_inches='tight')
plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(11,4.5));im=axs[0].imshow(np.abs(z[:64,:64]-np.diag(np.diag(z[:64,:64]))),cmap='magma');axs[0].set(title='Off-diagonal port impedance',xlabel='Element index',ylabel='Element index');fig.colorbar(im,ax=axs[0],label='|Zij| (Ω)')
ev=CoupledNetwork(z,loads);blind=CoupledNetwork(z,loads,w=ev.w,coupled=False);rng=np.random.default_rng(113);a=[];b=[]
for _ in range(250):
 bits=rng.integers(0,2,64);a.append(float(ev.score(ev.channel(bits)@ev.w)));b.append(float(blind.score(blind.channel(bits)@ev.w)))
axs[1].scatter(a,b,s=12,alpha=.5);lo=min(a+b);hi=max(a+b);axs[1].plot([lo,hi],[lo,hi],color='black',ls='--',lw=1);axs[1].set(title='Same 250 bit patterns, two channel models',xlabel='Fully coupled rate (bit/s/Hz)',ylabel='Coupling-blind predicted rate (bit/s/Hz)');fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(out/f'coupling_effect.{ext}')
(root/'coupling_effect.json').write_text(json.dumps({'frame':0,'patterns':250,'full_mean':float(np.mean(a)),'blind_mean':float(np.mean(b)),'mean_absolute_rate_prediction_error':float(np.mean(np.abs(np.array(a)-b))),'note':'Train-frame model-mismatch diagnostic, not held-out controller performance'},indent=2)+'\n')
