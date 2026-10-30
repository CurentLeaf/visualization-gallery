from pathlib import Path
import json, random, csv
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import missingno as msno
p=Path('site');p.mkdir(exist_ok=True)
rng=random.Random(42);rows=[];draws=[]
for i in range(12):
    r=dict(report=f'R-{i+1:02}',source=f'Sensor {chr(65+i%3)}',estimate=round(19+i*.35,2),sd=round(.35+(i%4)*.25,2),age_hours=i*3,verification='Reviewed' if i%3==0 else 'Unreviewed',location=None if i%4==0 else ['North','East','West'][i%3],reviewer='Reviewer A' if i%3==0 else None)
    rows.append(r)
    draws.extend({'report':r['report'],'value':rng.gauss(r['estimate'],r['sd'])} for _ in range(500))
(p/'reports.json').write_text(json.dumps(rows,indent=2))
with open('draws.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['report','value']);w.writeheader();w.writerows(draws)
fields=pd.DataFrame(rows)[['source','estimate','age_hours','location','reviewer']]
ax=msno.matrix(fields,figsize=(10,4),fontsize=10,sparkline=False)
ax.figure.savefig(p/'missingness.png',bbox_inches='tight',dpi=140);plt.close(ax.figure)
ax=msno.bar(fields,figsize=(10,4),fontsize=10)
ax.figure.savefig(p/'missingness-bars.png',bbox_inches='tight',dpi=140);plt.close(ax.figure)
ax=msno.heatmap(fields[['location','reviewer']],figsize=(7,4),fontsize=10)
ax.figure.savefig(p/'missingness-heatmap.png',bbox_inches='tight',dpi=140);plt.close(ax.figure)
assert len(rows)==12 and len(draws)==6000
