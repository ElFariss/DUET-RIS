import json,hashlib,datetime
from pathlib import Path
root=Path('outputs/runs/coupled_wire_v1');rows=[];hashes={}
for mode in ['spatial','temporal']:
 p=root/f'benchmark_{mode}_validation.jsonl';rows.extend(json.loads(l) for l in p.read_text().splitlines());hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
methods=sorted(set(r['method'] for r in rows));feasible={}
for budget in [1,5,10,50,100]:
 selected=[r for r in rows if r['budget_ms']==budget];counts={m:sum(r['deadline_missed'] for r in selected if r['method']==m) for m in methods}
 feasible[str(budget)]={'misses_by_method':counts,'feasible':all(v==0 for v in counts.values()) and all(any(r['method']==m for r in selected) for m in methods)}
chosen=next((b for b in [10,50,100] if feasible[str(b)]['feasible']),None)
out=root/'budget_selection.json'
if out.exists():raise FileExistsError(out)
out.write_text(json.dumps({'selected_ms':chosen,'validation_feasibility':feasible,'input_hashes':hashes,'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rule':'10 ms then 50 then 100; zero observed misses for every included method; no selection using pilot scores'},indent=2)+'\n')
print('Primary budget',chosen)
