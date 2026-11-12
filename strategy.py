"""v17n-5 exp4. FAMILY bitcoin-weekend-gap-continuation.
Mechanism: CME bitcoin futures are closed over weekend while spot reprices; Monday reopening gap
reflects accumulated spot information and persists through US morning liquidity.
Hypothesis: follow Monday 09:30 gap from Friday settlement through 12:50 is cost-positive.
Falsifier: any negative stressed era or <70% positive years.
"""
import numpy as np
FAMILY = 'bitcoin-weekend-gap-continuation'
PARAMS = {'signal_sec': 34140, 'exit_sec': 46500, 'min_gap_points': 100., 'stop_usd': 250.}
RISK = 290.
def entry_risk(panel): return {s: np.full(len(d), RISK) for s,d in panel.items()}
def signals(panel):
    result = {}
    for s,df in panel.items():
        out=np.zeros(len(df),dtype=np.int64)
        if s != 'MBT': result[s]=out; continue
        sec=df.ct_sec.to_numpy(); close=df.close.to_numpy(float); sess=df.session.astype(str).to_numpy()
        prev_close=None; i=0
        while i<len(df):
            j=i
            while j<len(df) and sess[j]==sess[i]: j+=1
            date=np.datetime64(sess[i][:10], 'D')
            # 1970-01-05 was Monday; session labels are CT trading dates.
            monday=(int(date.astype(int))+3)%7 == 0
            pos=0; entered=False
            for k in range(i,j):
                if not entered and monday and prev_close is not None and sec[k]>=PARAMS['signal_sec'] and sec[k]<PARAMS['exit_sec']-60:
                    gap=close[k]-prev_close
                    if abs(gap)>=PARAMS['min_gap_points']:
                        pos=int(np.sign(gap)); entered=True; stop=close[k]-pos*(PARAMS['stop_usd']/.1)
                elif pos and (pos*(close[k]-stop)<=0 or PARAMS['exit_sec']-60<=sec[k]<61200): pos=0
                out[k]=pos
            prev_close=close[j-1]; i=j
        result[s]=out
    return result
