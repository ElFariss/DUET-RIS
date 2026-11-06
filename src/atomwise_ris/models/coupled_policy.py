"""Matched shared-MLP and atom-attention residual mutation policies."""
import torch
from torch import nn

class CoupledPolicy(nn.Module):
    architecture_version = 'coupled_policy_residual_v1'

    def __init__(self,features=16,kind='attention',physics=True):
        super().__init__();self.kind=kind;self.physics=physics
        if kind=='attention':
            self.input=nn.Linear(features,32)
            layer=nn.TransformerEncoderLayer(32,4,64,0.,activation='gelu',batch_first=True)
            self.encoder=nn.TransformerEncoder(layer,2,enable_nested_tensor=False)
            self.head=nn.Linear(32,1)
            nn.init.zeros_(self.head.weight);nn.init.zeros_(self.head.bias)
        else:
            self.mlp=nn.Sequential(nn.Linear(features*3,96),nn.GELU(),nn.Linear(96,96),nn.GELU(),nn.Linear(96,1))
            nn.init.zeros_(self.mlp[-1].weight);nn.init.zeros_(self.mlp[-1].bias)
    def forward(self,x,analytical):
        if not self.physics:
            x=x.clone();x[:,:,4:15]=0
        if self.kind=='attention':y=self.head(self.encoder(self.input(x))).squeeze(-1)
        else:
            mean=x.mean(1,keepdim=True).expand_as(x)
            selected=(x*x[:,:,-1:]).sum(1,keepdim=True).expand_as(x)
            y=self.mlp(torch.cat([x,mean,selected],-1)).squeeze(-1)
        return analytical+y

class LinkGRU(nn.Module):
    """Shared temporal predictor for complex network entries, not future labels."""
    architecture_version = 'linear_velocity_residual_v2'

    def __init__(self,width=16):
        super().__init__();self.gru=nn.GRU(4,width,batch_first=True);self.head=nn.Linear(width,2)
        nn.init.zeros_(self.head.weight);nn.init.zeros_(self.head.bias)
    def forward(self,x):
        # Causal linear baseline extrapolation from last two historical frames
        linear=2*x[:,-1]-x[:,-2]
        # Velocity / first difference history for curvature learning
        delta=torch.cat([torch.zeros_like(x[:,:1]),x[:,1:]-x[:,:-1]],1)
        y,_=self.gru(torch.cat([x,delta],-1))
        return linear+0.25*torch.tanh(self.head(y[:,-1]))
