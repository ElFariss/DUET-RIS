import numpy as np
import torch
from torch import nn

class EditPolicy(nn.Module):
    def __init__(self,features,kind='attention',physics=True,conditioning=True):
        super().__init__();self.kind=kind;self.physics=physics;self.conditioning=conditioning
        self.features=features
        if kind=='attention':
            self.input=nn.Linear(features,32)
            layer=nn.TransformerEncoderLayer(32,4,dim_feedforward=64,dropout=0.,batch_first=True,norm_first=False,activation='gelu')
            self.encoder=nn.TransformerEncoder(layer,2,enable_nested_tensor=False)
            self.head=nn.Linear(32,1)
        elif kind=='mlp':
            self.mlp=nn.Sequential(nn.Linear(features*3,96),nn.GELU(),nn.Linear(96,96),nn.GELU(),nn.Linear(96,1))
        else:raise ValueError(kind)

    def forward(self,x,analytical):
        # Last six columns: gain, first marker, population frequency, recent edit,
        # and two current rates (K=2 initial study only).
        if not self.conditioning:
            x=x.clone();x[:,:,-5]=0
        if not self.physics:
            x=x.clone();x[:,:,4:-6]=0  # response and complex contribution features
        if self.kind=='attention':
            residual=self.head(self.encoder(self.input(x))).squeeze(-1)
        else:
            mean=x.mean(1,keepdim=True).expand_as(x)
            marker=x[:,:,-5:-4]
            selected=(x*marker).sum(1,keepdim=True).expand_as(x)
            residual=self.mlp(torch.cat([x,mean,selected],-1)).squeeze(-1)
        return analytical+residual

    def callable_cpu(self):
        self.eval();self.cpu()
        def infer(x,analytical):
            with torch.inference_mode():
                return self(torch.from_numpy(x)[None],torch.as_tensor(analytical,dtype=torch.float32)[None])[0].numpy()
        return infer
