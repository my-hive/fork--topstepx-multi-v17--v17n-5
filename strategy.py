"""v17n-5 exp5. FAMILY grain-report-shock-drift.
Mechanism: USDA scheduled releases (WASDE/stocks ~11:00 CT) are information shocks; grains underreact
and drift in shock direction because inventory holders reprice slowly. Detect shock causally from
11:00-11:04 volume > VOL_MULT x trailing-20-session median of same window (no calendar needed).
Enter at 11:05 close direction of 11:00 open->11:04 close move, exit 13:00, stop $250.
Falsifier: negative stressed era or <70% positive years on ZC/ZS/ZW.
"""
import numpy as np
FAMILY = 'grain-report-shock-drift'
PARAMS = {'vol_mult': 3., 'lookback': 20, 'exit_sec': 46800, 'stop_usd': 250.}
START, SIG = 39600, 39840   # 11:00 .. 11:04 bar-start inclusive; signal bar 11:04
def entry_risk(panel): return {s: np.full(len(d), 290.) for s, d in panel.items()}
def signals(panel):
    res = {}
    for s, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if s not in ('ZC', 'ZS', 'ZW'): res[s] = out; continue
        sec = df.ct_sec.to_numpy(); o = df.open.to_numpy(float); c = df.close.to_numpy(float); v = df.volume.to_numpy(float)
        hist = []; stopd = PARAMS['stop_usd'] / 50.
        for idx in df.groupby('session', sort=False).indices.values():
            w = idx[(sec[idx] >= START) & (sec[idx] <= SIG)]
            if len(w) == 5 and sec[w[-1]] == SIG:
                vol = v[w].sum()
                if len(hist) >= PARAMS['lookback'] and vol > PARAMS['vol_mult'] * np.median(hist[-PARAMS['lookback']:]) and c[w[-1]] != o[w[0]]:
                    pos = int(np.sign(c[w[-1]] - o[w[0]])); stop = c[w[-1]] - pos * stopd
                    for k in idx[idx > w[-1]]:
                        if sec[k] >= PARAMS['exit_sec'] - 60 or pos * (c[k] - stop) <= 0: break
                        out[k] = pos
                hist.append(vol)
            elif len(w): hist.append(v[w].sum())
        res[s] = out
    return res
