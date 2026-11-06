"""Causal forecasts of impedance observations; no trajectory/future lookup."""
import numpy as np
import torch

def require_forecast_checkpoint(checkpoint, expected_version='linear_velocity_residual_v2'):
    """Fail closed when checkpoint semantics are absent or differ from inference code."""
    version=checkpoint.get('architecture_version')
    if version != expected_version:
        raise RuntimeError(f'Forecast checkpoint architecture {version!r} is incompatible; expected {expected_version!r}')


def passive_reciprocal(z):
    z=(z+z.T)/2
    zr=z.real
    try:
        np.linalg.cholesky(zr-1e-6*np.eye(zr.shape[0]))
        return zr+1j*z.imag
    except np.linalg.LinAlgError:
        eig,vec=np.linalg.eigh(zr)
        return (vec*np.maximum(eig,1e-6))@vec.T+1j*z.imag

def predict(history,kind,model=None,scaling=None):
    if len(history)<4:raise ValueError('Four historical observations required')
    if kind=='persistence':return history[-1].copy()
    if kind=='linear':return passive_reciprocal(2*history[-1]-history[-2])
    if kind!='gru':raise ValueError(kind)
    mean,scale,upper=scaling[:3]
    active_mask=scaling[3] if len(scaling)>3 and scaling[3] is not None else (scale>0.01)
    linear_z=2*history[-1]-history[-2]
    dyn_idx=np.flatnonzero(active_mask)
    if len(dyn_idx)==0:
        return passive_reciprocal(linear_z)
    u0=upper[0][dyn_idx];u1=upper[1][dyn_idx]
    h=(history[-4:,u0,u1].T-mean[dyn_idx,None])/scale[dyn_idx,None]
    x=np.stack([h.real,h.imag],-1).astype(np.float32)
    with torch.inference_mode():
        pred=model(torch.from_numpy(x)).numpy()
    linear_x=2*x[:,-1]-x[:,-2]
    residual=(pred-linear_x)*scale[dyn_idx,None]
    res_c=residual[:,0]+1j*residual[:,1]
    z=linear_z.copy()
    diagonal=u0==u1
    z[u0[diagonal],u1[diagonal]]+=res_c[diagonal]
    off_diagonal=~diagonal
    z[u0[off_diagonal],u1[off_diagonal]]+=res_c[off_diagonal]
    z[u1[off_diagonal],u0[off_diagonal]]+=res_c[off_diagonal]
    return passive_reciprocal(z)
