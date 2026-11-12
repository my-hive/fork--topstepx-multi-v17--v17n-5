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
 ia={str(x):int(np.searchsorted(a.session.astype(str).to_numpy(),x)) for x in a.session.unique()}
 ib={str(x):int(np.searchsorted(b.session.astype(str).to_numpy(),x)) for x in b.session.unique()}
 ca=a.close.to_numpy(float); cb=b.close.to_numpy(float); sa=a.ct_sec.to_numpy(); sb=b.ct_sec.to_numpy(); hist=[]
 for day in sorted(set(ia)&set(ib)):
  xa,xb=ia[day],ib[day]
  n1=np.searchsorted(sa,30600,'left',sorter=None) if False else None
  da=xa+np.searchsorted(sa[xa:xa+200],30600); db=xb+np.searchsorted(sb[xb:xb+200],30600)
  ea=xa+np.searchsorted(sa[xa:xa+200],PARAMS['signal_sec'],'right');eb=xb+np.searchsorted(sb[xb:xb+200],PARAMS['signal_sec'],'right')
  if ea-da>=2 and eb-db>=2:
   spread=(ca[ea-1]/ca[da]-1)-(cb[eb-1]/cb[db]-1)
   if len(hist)>=PARAMS['lookback']:
    sd=np.std(hist[-PARAMS['lookback']:])
    if sd and abs(spread)>=PARAMS['z_threshold']*sd:
     side=-int(np.sign(spread))
     ta=xa+np.searchsorted(sa[xa:xa+500],PARAMS['exit_sec']-60);tb=xb+np.searchsorted(sb[xb:xb+500],PARAMS['exit_sec']-60)
     r['ZC'][ea:ta]=side;r['ZS'][eb:tb]=-side
   hist.append(spread)
 return r
