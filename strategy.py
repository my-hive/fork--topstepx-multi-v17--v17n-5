"""v17n-5 exp8. FAMILY corn-soy-open-hour-relative-value.
Mechanism: corn/soy are acreage and feed substitutes; thin 08:30-09:29 CT liquidity can exaggerate
their separation and US commercial flow converges it. Long 09:30 underperformer, short outperformer
when normalized return spread >=1 trailing 20-day SD; flat 12:50. Falsifier: negative era or
<70% positive years.
"""
import numpy as np
FAMILY='corn-soy-open-hour-relative-value'
PARAMS={'signal_sec':34140,'exit_sec':46500,'lookback':20,'z_threshold':1.}
def entry_risk(panel): return {s:np.full(len(d),290.) for s,d in panel.items()}
def signals(panel):
 r={s:np.zeros(len(d),dtype=np.int64) for s,d in panel.items()}
 if not {'ZC','ZS'}<=set(panel):return r
 a,b=panel['ZC'],panel['ZS']
 # session -> first row index, prefix-complete
 ia={str(day):ix for day, ix in a.groupby('session', sort=False).indices.items()}
 ib={str(day):ix for day, ix in b.groupby('session', sort=False).indices.items()}
 ca=a.close.to_numpy(float); cb=b.close.to_numpy(float); sa=a.ct_sec.to_numpy(); sb=b.ct_sec.to_numpy(); hist=[]
 for day in sorted(set(ia)&set(ib)):
  xa,xb=ia[day],ib[day]
  wa=xa[(sa[xa]>=30600)&(sa[xa]<=PARAMS['signal_sec'])];wb=xb[(sb[xb]>=30600)&(sb[xb]<=PARAMS['signal_sec'])]
  if len(wa)>=2 and len(wb)>=2:
   spread=(ca[wa[-1]]/ca[wa[0]]-1)-(cb[wb[-1]]/cb[wb[0]]-1)
   if len(hist)>=PARAMS['lookback']:
    sd=np.std(hist[-PARAMS['lookback']:])
    if sd and abs(spread)>=PARAMS['z_threshold']*sd:
     side=-int(np.sign(spread))
     ha=xa[(xa>wa[-1])&(sa[xa]<PARAMS['exit_sec']-60)];hb=xb[(xb>wb[-1])&(sb[xb]<PARAMS['exit_sec']-60)]
     r['ZC'][ha]=side;r['ZS'][hb]=-side
   hist.append(spread)
 return r
