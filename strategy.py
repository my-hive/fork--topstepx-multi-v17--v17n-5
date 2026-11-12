"""v17n-5 exp7. FAMILY bitcoin-us-cash-open-reversion.
Mechanism: CME bitcoin's 24h venue absorbs overnight crypto flow; US equity-cash-open liquidity
rebalances exaggerated 08:30-09:29 CT movement. Fade its move at 09:30, exit 12:50.
Hypothesis: cash-flow reversal is positive after stressed MBT costs. Falsifier: any negative era
or fewer than 70% profitable years.
"""
import numpy as np
FAMILY='bitcoin-us-cash-open-reversion'
PARAMS={'start_sec':30600,'signal_sec':34140,'exit_sec':46500,'min_move_usd':150.,'stop_usd':250.}
def entry_risk(panel): return {s:np.full(len(d),290.) for s,d in panel.items()}
def signals(panel):
 r={}
 for s,d in panel.items():
  out=np.zeros(len(d),dtype=np.int64)
  if s!='MBT':r[s]=out;continue
  sec=d.ct_sec.to_numpy(); c=d.close.to_numpy(float)
  for ix in d.groupby('session',sort=False).indices.values():
   w=ix[(sec[ix]>=PARAMS['start_sec'])&(sec[ix]<=PARAMS['signal_sec'])]
   pos=0;stop=0.
   if len(w)>=2:
    move=c[w[-1]]-c[w[0]]
    if abs(move)*.1>=PARAMS['min_move_usd']:
     pos=-int(np.sign(move));stop=c[w[-1]]-pos*(PARAMS['stop_usd']/.1)
   for k in ix[ix>w[-1]] if len(w) else []:
    if sec[k]>=PARAMS['exit_sec']-60:break
    if pos*(c[k]-stop)<=0:pos=0
    out[k]=pos
  r[s]=out
 return r
