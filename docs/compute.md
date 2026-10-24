# Compute and access

The active lab checkout is `~/projects/atom-wise-ris` on port 2002. It has its own Python 3.12 environment and locked dependencies. The historical `~/projects/ris-meta-feasibility` environment remains intact.

Outside the university network:

```bash
ssh faris@labkc-comm1
ssh -J faris@labkc-comm1 -p 2002 faris@gpu-labkc.ub.ac.id
ssh -J faris@labkc-comm1 -p 2003 faris@gpu-labkc.ub.ac.id
```

Credentials are managed through SSH, not research artifacts. `scripts/remote.sh` provides source push/result pull with the jump host. These operations synchronize files; they do not launch jobs, stop other workloads or push Git commits.

Observed reference hardware: Ryzen 5 5600 CPU, approximately 64 GB RAM, two RTX 3060 GPUs with 12 GB VRAM each on port 2002. The v5 campaign uses one idle GPU for sequential independent training jobs and one CPU core for the subsequent benchmark. Models are loaded before online timing. Available disk and other users' jobs must be checked before starting additional work.

The other two machines provide additional independent workers, not pooled GPU memory. Port 2003 had approximately 38 GB free and port 2001 approximately 10 GB at the earlier inspection; these are historical observations, not reserved capacity. The larger dataset is kept on port 2002.
