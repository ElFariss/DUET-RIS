"""Causal forecasts of impedance observations; no trajectory/future lookup."""
import numpy as np
import torch

def passive_reciprocal(z):
    z=(z+z.T)/2
    eig,vec=np.linalg.eigh(z.real)
    return (vec*np.maximum(eig,1e-6))@vec.T+1j*z.imag

def predict(history,kind,model=None,scaling=None):
    if len(history)<4:raise ValueError('Four historical observations required')
    if kind=='persistence':return history[-1].copy()
    if kind=='linear':return passive_reciprocal(2*history[-1]-history[-2])
    if kind!='gru':raise ValueError(kind)
    mean,scale,upper=scaling
    h=(history[-4:,upper[0],upper[1]].T-mean[:,None])/scale[:,None]
    x=np.stack([h.real,h.imag],-1).astype(np.float32)
    with torch.inference_mode():prediction=model(torch.from_numpy(x)).numpy()
    links=(prediction[:,0]+1j*prediction[:,1])*scale+mean
    z=np.zeros(history.shape[1:],complex);z[upper[0],upper[1]]=links;z[upper[1],upper[0]]=links
    return passive_reciprocal(z)
