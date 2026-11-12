"""v17n-5 exp8. FAMILY corn-soy-overnight-relative-value.
Mechanism: corn and soy compete for acreage/feed demand; their correlated overnight returns can
separate on thin liquidity and converge once US commercial flow begins. At 09:30 CT long overnight
underperformer and short outperformer when normalized return spread exceeds 1 trailing standard
deviation; exit 12:50. Hypothesis: spread convergence covers stressed paired costs.
Falsifier: negative era PnL or fewer than 70% positive years.
"""
import numpy as np
FAMILY='corn-soy-overnight-relative-value'
PARAMS={'signal_sec':34140,'exit_sec':46500,'lookback':20,'z_threshold':1.,'stop_usd':250.}
def entry_risk(panel): return {s:np.full(len(d),290.) for s,d in panel.items()}
def signals(panel):
 r={s:np.zeros(len(d),dtype=np.int64) for s,d in panel.items()}
 if not {'ZC','ZS'}<=set(panel):return r
 a,b=panel['ZC'],panel['ZS']; ia={str(x):i for i,x in enumerate(a.session)}; ib={str(x):i for i,x in enumerate(b.session)}
 hist=[]
 for day in sorted(set(ia)&set(ib)):
  xa,xb=ia[day],ib[day]; sa=a.ct_sec.to_numpy()[xa];sb=b.ct_sec.to_numpy()[xb];ca=a.close.to_numpy(float);cb=b.close.to_numpy(float)
  wa=xa[(sa>=30600)&(sa<=PARAMS['signal_sec'])];wb=xb[(sb>=30600)&(sb<=PARAMS['signal_sec'])]
  if len(wa)>=2 and len(wb)>=2:
   spread=(ca[wa[-1]]/ca[wa[0]]-1)-(cb[wb[-1]]/cb[wb[0]]-1)
   if len(hist)>=PARAMS['lookback']:
    sd=np.std(hist[-PARAMS['lookback']:])
    if sd and abs(spread)>=PARAMS['z_threshold']*sd:
     side=-int(np.sign(spread)); r['ZC'][xa[(sa>PARAMS['signal_sec'])&(sa<PARAMS['exit_sec']-60)]]=side; r['ZS'][xb[(sb>PARAMS['signal_sec'])&(sb<PARAMS['exit_sec']-60)]]=-side
   hist.append(spread)
 return r
