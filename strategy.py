"""v17n-5 exp1. FAMILY grain-open-gap-fade.

Mechanism: thin overnight Globex grain book overshoots on Asia/FX/weather headlines; when the
day-session (08:30 CT) participants arrive, part of the overshoot is retraced. Signal evaluated
after the 09:29 bar (outside the 08:30-09:30 entry-diversity window, fill 09:30 open).
Hypothesis: fading |gap| >= Z_THR trailing-mean-abs daily gap, vs prior session last close
(same contract only), earns positive stressed PnL on ZC/ZS/ZW in >=70% of years.
Falsifier: negative stressed PnL in any of 3 eras or <70% positive years.
"""
import numpy as np

FAMILY = "grain-open-gap-fade"
PARAMS = {'z_thr': 1.0, 'lookback_sessions': 20, 'exit_sec': 46500, 'stop_usd': 250.}
SYMS = ('ZC', 'ZS', 'ZW')
SIG_SEC = 34140   # 09:29 bar; close known at 09:30
DECLARED_RISK = PARAMS['stop_usd'] + 40.   # stop plus one-minute overshoot allowance

def entry_risk(panel):
    return {s: np.full(len(df), DECLARED_RISK) for s, df in panel.items()}

def signals(panel):
    # Per-symbol point values; grain floor all 3 roots in this family.
    pv = {'ZC': 50., 'ZS': 50., 'ZW': 50., 'ZL': 600., 'HE': 400., 'LE': 400., 'MBT': .1}
    result = {}
    for s, df in panel.items():
        n = len(df)
        out = np.zeros(n, dtype=np.int64)
        if s not in pv:
            result[s] = out
            continue
        close = df.close.to_numpy(float)
        sec = df.ct_sec.to_numpy()
        sess = df.session.astype(str).to_numpy()
        cvar = df.contract.to_numpy()
        stop_ticks = PARAMS['stop_usd'] / pv[s]
        # Trailing mean-abs daily gap (prior sessions only, same contract).
        last_close, last_contract, gap_hist = None, None, []
        i = 0
        while i < n:
            j = i
            while j < n and sess[j] == sess[i]:
                j += 1
            k = i
            pos = 0
            side = 0
            entered = False
            while k < j:
                if pos == 0 and not entered:
                    if (SIG_SEC <= sec[k] < PARAMS['exit_sec'] - 60 and last_close is not None and last_contract == cvar[k]
                            and len(gap_hist) >= PARAMS['lookback_sessions']):
                        gap = close[k] - last_close
                        mad = float(np.mean(gap_hist[-PARAMS['lookback_sessions']:]))
                        if mad > 0 and abs(gap) >= PARAMS['z_thr'] * mad:
                            side = -int(np.sign(gap))
                            pos = side
                            entered = True
                            stop = close[k] - side * stop_ticks
                else:
                    if side * (close[k] - stop) >= 0:   # crossed stop
                        pos = 0
                    elif PARAMS['exit_sec'] - 60 <= sec[k] < 61200:  # flat from 12:49 close
                        pos = 0
                out[k] = pos
                k += 1
            gap_hist.append(abs(close[j - 1] - last_close) if (last_close is not None and last_contract == cvar[j - 1]) else 0.)
            last_close, last_contract = close[j - 1], cvar[j - 1]
            i = j
        result[s] = out
    return result
