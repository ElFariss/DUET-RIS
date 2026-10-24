"""Exact passive multiport termination and rank-one/rank-two RIS edits.

Port order: RIS cells, four BS ports, two UE ports. All external ports use
50-ohm real references; H maps incident BS power waves to received UE waves.
No empirical aperture multiplier or OpenSourceRIS gamma is used here.
"""
from dataclasses import dataclass
import numpy as np
from atomwise_ris.channels.precoding import precoder

@dataclass
class NetworkState:
    bits: np.ndarray
    inverse: np.ndarray
    field: np.ndarray

class CoupledNetwork:
    def __init__(self,z,loads,w=None,coupled=True):
        self.n=len(z)-6;self.loads=np.asarray(loads);self.z=np.asarray(z).copy()
        if not coupled:
            # Model mismatch ablation only: ground-truth evaluation stays coupled.
            rr=self.z[:self.n,:self.n];rr[:]=np.diag(np.diag(rr))
        n=self.n;e=self.z[n:,n:]+50*np.eye(6);ei=np.linalg.inv(e)
        self.a=self.z[:n,:n]-self.z[:n,n:]@ei@self.z[n:,:n]
        self.c=-100*(ei@self.z[n:,:n])[-2:]
        self.f=(self.z[:n,n:]@ei)[:,:4]
        self.d=-100*ei[-2:,:4]
        self.w=precoder(self.channel(np.zeros(n,dtype=np.int8))) if w is None else w
        self.fw=self.f@self.w;self.dw=self.d@self.w
        self.noise=1.380649e-23*290*1e6*10**(.7)
        self.pairs=np.array(np.triu_indices(n,1)).T
    def channel(self,bits):
        return self.d+self.c@np.linalg.solve(self.a+np.diag(self.loads[np.asarray(bits,int)]),self.f)
    def state(self,bits):
        b=np.asarray(bits,np.int8).copy();inv=np.linalg.inv(self.a+np.diag(self.loads[b]))
        return NetworkState(b,inv,self.dw+self.c@inv@self.fw)
    def score(self,fields):
        power=np.abs(fields)**2;signal=np.diagonal(power,axis1=-2,axis2=-1)
        interference=np.maximum(0.,power.sum(-1)-signal)
        return np.log2(1+signal/(self.noise+interference)).min(-1)
    def moves(self,state,pairs=False):
        t=state.inverse;l=self.c@t;r=t@self.fw
        delta=self.loads[1-state.bits]-self.loads[state.bits]
        den=1/delta+np.diag(t)
        if not pairs:
            fields=state.field[None]-np.einsum('ki,ij->ikj',l,r)/den[:,None,None]
        else:
            i,j=self.pairs.T
            det=den[i]*den[j]-t[i,j]*t[j,i]
            ui=(den[j,None]*r[i]-t[i,j,None]*r[j])/det[:,None]
            uj=(den[i,None]*r[j]-t[j,i,None]*r[i])/det[:,None]
            fields=state.field[None]-l[:,i].T[:,:,None]*ui[:,None,:]-l[:,j].T[:,:,None]*uj[:,None,:]
        return np.asarray(self.score(fields))
    def flip(self,state,indices):
        ix=np.asarray(indices,dtype=int).reshape(-1)
        if len(set(ix.tolist()))!=len(ix):raise ValueError('Distinct flips required')
        delta=self.loads[1-state.bits[ix]]-self.loads[state.bits[ix]]
        small=np.diag(1/delta)+state.inverse[np.ix_(ix,ix)]
        inv=state.inverse-state.inverse[:,ix]@np.linalg.solve(small,state.inverse[ix])
        b=state.bits.copy();b[ix]=1-b[ix]
        return NetworkState(b,inv,self.dw+self.c@inv@self.fw)
    def features(self,state,first=-1):
        n=self.n;gain=self.moves(state)-self.score(state.field)
        t=state.inverse;l=self.c@t;r=t@self.fw
        # Analytical full-network score, port interaction and geometry features.
        coords=np.column_stack((np.arange(n)%8,np.arange(n)//8))/7
        interaction=np.abs(t).sum(1)-np.abs(np.diag(t))
        features=np.column_stack([state.bits,coords,gain,np.real(np.diag(t)),np.imag(np.diag(t)),
           interaction,l.real.T,l.imag.T,r.real,r.imag,np.arange(n)==first])
        return features.astype(np.float32),gain
