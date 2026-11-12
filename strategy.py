"""v17n-5 exp6. FAMILY livestock-late-pressure-reversion.
Mechanism: livestock liquidity thins into the close; hedger imbalance moves price temporarily and
should revert next cash morning. Fade PREVIOUS session's 12:00-12:29 CT move (same contract) at
next-session 10:00 CT; exit 12:50. Hypothesis: reversal survives stressed costs in HE/LE.
Falsifier: negative stressed era or <70% positive years.
"""
import numpy as np
FAMILY = 'livestock-late-pressure-reversion'
PARAMS = {'entry_sec': 36000, 'exit_sec': 46500, 'min_move_usd': 150., 'stop_usd': 250.}
def entry_risk(panel): return {s: np.full(len(d), 290.) for s, d in panel.items()}
def signals(panel):
    res = {}
    for s, d in panel.items():
        out = np.zeros(len(d), dtype=np.int64)
        if s not in ('HE', 'LE'): res[s] = out; continue
        sec = d.ct_sec.to_numpy(); c = d.close.to_numpy(float); ss = d.session.astype(str).to_numpy()
        ctr = d.contract.to_numpy(); prev_move, prev_ctr = 0., None; i = 0
        while i < len(d):
            j = i
            while j < len(d) and ss[j] == ss[i]: j += 1
            pos = 0
            if prev_ctr == ctr[i] and abs(prev_move) * 400 >= PARAMS['min_move_usd']:
                pos = -int(np.sign(prev_move)); stop = None
            for k in range(i, j):
                if pos and stop is None and sec[k] >= PARAMS['entry_sec']: stop = c[k] - pos * (PARAMS['stop_usd'] / 400.)
                if sec[k] < PARAMS['entry_sec'] or sec[k] >= PARAMS['exit_sec'] - 60 and sec[k] < 61200: 
                    if pos and sec[k] >= PARAMS['exit_sec'] - 60: pos = 0
                    continue
                if pos and pos * (c[k] - stop) <= 0: pos = 0
                out[k] = pos
            w = np.flatnonzero((sec[i:j] >= 43200) & (sec[i:j] < 45000)) + i
            prev_move = c[w[-1]] - c[w[0]] if len(w) >= 2 else 0.
            prev_ctr = ctr[j - 1]; i = j
        res[s] = out
    return res
