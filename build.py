from pathlib import Path
import json, random, csv, math, statistics, re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import missingno as msno
p=Path('site');p.mkdir(exist_ok=True)
rng=random.Random(42)
specs=[('A','Fixed station','direct sensor',8,.35,'normal','North'),('B','Mobile station','direct sensor',5,1.1,'normal','East'),('C','Manual observer','human entry',4,.7,'skewed','West'),('D','Remote estimate','model derived',3,1.4,'bimodal','North'),('E','Partner relay','relayed report',2,.8,'normal','East'),('F','Archive feed','historical import',2,1.8,'skewed','West')]
sources=[];rows=[];draws=[]
for letter,name,kind,count,spread,shape,site in specs:
    sid='S-'+letter
    sources.append(dict(source_id=sid,name=name,kind=kind,report_count=count,site=site,distribution_assumption=shape,collection_method={'direct sensor':'Synthetic instrument reading','human entry':'Synthetic manually transcribed observation','model derived':'Synthetic remote model output','relayed report':'Synthetic partner redistribution','historical import':'Synthetic archived record'}[kind],update_pattern='Historical batch' if letter=='F' else 'Intermittent' if letter in 'CE' else 'Periodic',known_limitations={'A':'Stable but limited to one site','B':'Movement creates variable measurement conditions','C':'Transcription and timestamp gaps are intentionally simulated','D':'Two plausible model regimes; not a calibrated posterior','E':'Reuses observations from source A; not independent','F':'Old records and incomplete metadata'}[letter],synthetic=True))
    for j in range(count):
        idx=len(rows)+1;rid=f'R-{idx:02}';center=20+{'North':0,'East':2,'West':-1}[site]+rng.gauss(0,1.3)
        age=round(rng.uniform(72,180) if letter=='F' else rng.uniform(0,60),1)
        values=[]
        for k in range(600):
            z=rng.gauss(0,1) if shape=='normal' else rng.expovariate(1)-1 if shape=='skewed' else rng.choice([-1.5,1.5])+rng.gauss(0,.35)
            values.append(center+spread*z)
        status='Reviewed' if letter=='A' or j%3==0 else 'Pending' if j%3==1 else 'Unreviewed'
        parent=f'R-{j+1:02}' if letter=='E' else None
        r=dict(report=rid,source=name,source_id=sid,source_type=kind,estimate=round(statistics.mean(values),3),sd=round(statistics.stdev(values),3),distribution_shape=shape,age_hours=age,verification=status,location=None if letter=='C' and j%2==0 else site,reviewer='Reviewer '+str(j%3+1) if status=='Reviewed' else None,collection_time=None if letter=='C' and j%2==0 else f'T-minus {age} hours',calibration_record=None if letter in 'CF' or j%4==2 else 'CAL-'+letter,translation_status=None if letter=='F' else 'Not applicable',upstream_report=parent,lineage_status='Relayed from '+parent if parent else 'No upstream report in this synthetic dataset',processing_steps=['Synthetic collection','Unit normalization','Review recorded' if status=='Reviewed' else 'Review pending','Display'],claim_group='Claim-'+site,synthetic=True)
        rows.append(r);draws.extend(dict(report=rid,value=v) for v in values)
(p/'reports.json').write_text(json.dumps(rows,indent=2));(p/'sources.json').write_text(json.dumps(sources,indent=2))
(p/'data-notes.json').write_text(json.dumps(dict(synthetic=True,reports=len(rows),sources=len(sources),seed=42,draws_per_report=600,interpretation='All distributions and metadata are invented. Normal, shifted-exponential, and two-component mixture draws demonstrate shapes, not calibrated confidence. Claims are grouping labels, not statistically fused estimates. Source E redistributes source A reports; no independent corroboration is implied.'),indent=2))
with open('draws.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['report','value']);w.writeheader();w.writerows(draws)
fields=pd.DataFrame(rows)[['source','estimate','age_hours','location','reviewer','collection_time','calibration_record','translation_status']]
for name,func,data,kwargs in [('missingness.png',msno.matrix,fields,dict(sparkline=False)),('missingness-bars.png',msno.bar,fields,{}),('missingness-heatmap.png',msno.heatmap,fields[['location','reviewer','collection_time','calibration_record','translation_status']],{})]:
    ax=func(data,figsize=(11,6),fontsize=9,**kwargs);ax.figure.savefig(p/name,bbox_inches='tight',dpi=140);plt.close(ax.figure)
html=(p/'index.html').read_text()
html=html.replace('const scale=d3.scaleLinear().domain([0,33])','const scale=d3.scaleLinear().domain([0,d3.max(rows,r=>r.age_hours)])').replace('100*r.age_hours/33','100*r.age_hours/Math.max(...rows.map(x=>x.age_hours))').replace("'0 0 760 390'","'0 0 760 '+(rows.length*30+30)")
html=html.replace('0–33 hours','relative to the oldest displayed report').replace('Rows follow R-01 through R-12.','Rows follow R-01 through R-24.').replace('the twelve point estimates','the 24 point estimates').replace('location and reviewer, the two fields with missing values','fields with intentionally varied and shared missingness patterns').replace('xbins:{start:18,end:24,size:1}','xbins:{size:1}')
html=re.sub(r"^graph\('chain'.*$","graph('chain',[[rows[0].source_id,rows[0].source],['raw',rows[0].report+' raw record'],['norm','Unit normalization'],['review','Review: '+rows[0].verification],['claim',rows[0].claim_group]],[ [rows[0].source_id,'raw'],['raw','norm'],['norm','review'],['review','claim'] ]);",html,flags=re.M)
html=re.sub(r"^graph\('fan'.*$","{const ns=[...sources.map(s=>['src-'+s,s]),...rows.map(r=>[r.report,r.report+' / '+r.verification]),...['North','East','West'].map(s=>['Claim-'+s,'Claim group '+s])];const es=rows.flatMap(r=>[['src-'+r.source,r.report],[r.report,r.claim_group]]);graph('fan',ns,es)}",html,flags=re.M)
html=re.sub(r"^graph\('shared'.*$","{const relay=rows.filter(r=>r.upstream_report);const ns=[['origin','Fixed station'],...relay.flatMap(r=>[[r.upstream_report,r.upstream_report+' original'],[r.report,r.report+' relay'],['derived-'+r.report,'Derived view '+r.report]])];const es=relay.flatMap(r=>[['origin',r.upstream_report],[r.upstream_report,r.report],[r.report,'derived-'+r.report]]);graph('shared',ns,es)}",html,flags=re.M)
html=html.replace('Sensor A → R-01 observation → unit normalization → displayed estimate. Click nodes for labels.','Follow an actual synthetic record through normalization, recorded review, and a claim group. Click nodes for labels.').replace('Three report nodes connect to an illustrative summary claim.','All 24 records connect their six sources to three geographic claim groups. Grouping is not statistical fusion.').replace('Two derived claims trace back to the same raw observation.','Partner relay records explicitly trace to their upstream Fixed station observations. These are dependent reports.').replace('One labeled cell per report separates reviewed from unreviewed records.','One labeled cell per report shows Reviewed, Pending, or Unreviewed status.').replace('Any trend is created by the synthetic data generator.','Patterns reflect simulated site differences, source characteristics, and age distributions.').replace('All data are fictional.','24 reports from six detailed source profiles. All data are fictional.')
html=html.replace("r.verification==='Reviewed'?'#0f766e':'#b45309'","r.verification==='Reviewed'?'#0f766e':r.verification==='Pending'?'#b45309':'#64748b'")
if 'source-details.js' not in html:html=html.replace('</body>','<script src="source-details.js"></script></body>')
(p/'index.html').write_text(html)
ids={r['report'] for r in rows}
assert len(rows)==24 and len(sources)==6 and len(draws)==14400
assert all(not r['upstream_report'] or r['upstream_report'] in ids for r in rows)
assert all(math.isfinite(r['estimate']) and r['sd']>0 for r in rows)
