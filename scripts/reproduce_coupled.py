"""Run the coupled pilot in a NEW workspace, preserving every existing run.

Requires separate prepared EM and training Python environments. The training
interpreter must have the project's base dependencies and Torch. EM requires
requirements-em.txt. No credentials or machine-specific paths are copied.
"""
import argparse,os,subprocess,sys,shutil,hashlib,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--em-python',required=True);p.add_argument('--train-python',required=True);p.add_argument('--workers',type=int,default=2);a=p.parse_args()
 source=Path(__file__).resolve().parents[1];dest=Path(a.workspace).resolve()
 if dest.exists():raise FileExistsError('Use a fresh destination to preserve prior experiments')
 em=str(Path(a.em_python).resolve());train=str(Path(a.train_python).resolve())
 dest.mkdir(parents=True)
 for name in ['src','scripts','configs']:shutil.copytree(source/name,dest/name,ignore=shutil.ignore_patterns('__pycache__'))
 root=dest/'outputs/runs/coupled_wire_v1';(root/'logs').mkdir(parents=True)
 env=os.environ.copy();env.update(PYTHONPATH=str(dest/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 def run(python,script,*args,allow_failed_coarse=False):
  tag=script.removesuffix('.py')+'_'+('_'.join(map(str,args)).replace('/','_') or 'default')
  print('Running',tag,flush=True)
  with (root/'logs'/f'{tag}.log').open('x') as f:
   result=subprocess.run([python,'scripts/'+script,*map(str,args)],cwd=dest,env=env,stdout=f,stderr=subprocess.STDOUT)
  if result.returncode and not (allow_failed_coarse and result.returncode==2):raise RuntimeError(f'{tag} failed: see log')
 run(em,'validate_coupled_physics.py','--side','8','--segments','21,41,81','--out','outputs/runs/coupling_halfwave64_v1',allow_failed_coarse=True)
 run(em,'gate_coupled_campaign.py')
 run(em,'generate_coupled_reference.py','--workers',a.workers)
 run(train,'prepare_coupled.py')
 for seed in [7,19,43]:
  for kind in ['mlp','attention','attention_no_physics','gru']:run(train,'train_coupled.py','--kind',kind,'--seed',seed)
 for mode in ['spatial','temporal']:run(train,'benchmark_coupled.py','--split','validation','--mode',mode)
 run(train,'select_coupled_budget.py')
 for mode in ['spatial','temporal']:run(train,'benchmark_coupled.py','--split','pilot','--mode',mode)
 run(em,'audit_coupled_mesh.py','--indices','0,32,48,52')
 run(train,'audit_coupled_actions.py');run(train,'verify_coupled_artifacts.py');run(em,'plot_coupled_geometry.py');run(em,'analyze_coupled.py');run(em,'finalize_coupled_report.py')
 print('Completed independent reproduction:',root/'REPORT.md',flush=True)
if __name__=='__main__':main()
