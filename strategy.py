"""v17n-5 exp3. FAMILY livestock-cash-open-breakout.

Mechanism: cattle and hog futures have thin pre-cash liquidity; price discovery accelerates once
US cash-market participants establish opening range. Break range after 09:30 CT, exit 12:50.
Hypothesis: direction of completed 08:30-09:30 opening-range break has positive stressed PnL.
Falsifier: any negative era PnL or fewer than 70% positive years.
"""
import numpy as np

FAMILY = "livestock-cash-open-breakout"
PARAMS = {'range_start_sec': 30600, 'range_end_sec': 34200, 'exit_sec': 46500,
          'stop_usd': 250.}
SYMS = ('HE', 'LE')
RISK = PARAMS['stop_usd'] + 40.

def entry_risk(panel):
    return {s: np.full(len(d), RISK) for s, d in panel.items()}

def signals(panel):
    result = {}
    for s, df in panel.items():
        out = np.zeros(len(df), dtype=np.int64)
        if s not in SYMS:
            result[s] = out
            continue
        sec, high, low, close = (df[x].to_numpy() for x in ('ct_sec', 'high', 'low', 'close'))
        sessions = df.session.astype(str).to_numpy()
        i = 0
        while i < len(df):
            j = i
            while j < len(df) and sessions[j] == sessions[i]:
                j += 1
            window = np.flatnonzero((sec[i:j] >= PARAMS['range_start_sec']) &
                                    (sec[i:j] < PARAMS['range_end_sec'])) + i
            pos, entered = 0, False
            if len(window):
                top, bottom = high[window].max(), low[window].min()
                stop_dist = PARAMS['stop_usd'] / 400.
                for k in range(window[-1] + 1, j):
                    if not entered and sec[k] < PARAMS['exit_sec'] - 60:
                        if close[k] > top:
                            pos, entered, stop = 1, True, close[k] - stop_dist
                        elif close[k] < bottom:
                            pos, entered, stop = -1, True, close[k] + stop_dist
                    elif pos:
                        if pos * (close[k] - stop) <= 0 or PARAMS['exit_sec'] - 60 <= sec[k] < 61200:
                            pos = 0
                    out[k] = pos
            i = j
        result[s] = out
    return result
