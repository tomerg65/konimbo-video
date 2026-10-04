import numpy as np, json, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
ev = json.load(open(sys.argv[1])); out = sys.argv[2]
DUR = ev['duration']; N = int(SR * (DUR + 0.5))
BPM = 100; beat = 60 / BPM; bar = 4 * beat
rng = np.random.default_rng(7)

def note(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def env(n, a, d, s=0.0, r=0.0):
    e = np.ones(n); na = max(1, int(a * SR)); nd = int(d * SR)
    e[:na] = np.linspace(0, 1, na)
    if nd: e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    e[na + nd:] = s
    return e
def add(buf, x, t):
    i = int(t * SR); j = min(len(buf), i + len(x))
    if i < len(buf) and j > i: buf[i:j] += x[:j - i]

# A minor: Am F C G
prog = [[57, 60, 64], [53, 57, 60], [48, 55, 60], [55, 59, 62]]
roots = [45, 41, 48, 43]
pad = np.zeros(N); arp = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N); sfx = np.zeros(N)

# intensity curve 0..1 from events
def intensity(t):
    for a, b, v in ev['sections']:
        if a <= t < b: return v
    return 0.6

nbars = int(DUR / bar) + 2
for bi in range(nbars):
    t0 = bi * bar; ch = prog[bi % 4]; n = int(bar * SR * 1.05); tt = np.arange(n) / SR
    # pad: detuned saw-ish via few harmonics
    x = np.zeros(n)
    for m in ch:
        for det in (-0.08, 0.08):
            f = note(m + 12) * (1 + det / 100)
            for h in range(1, 6): x += np.sin(2 * np.pi * f * h * tt + h) / (h * 1.6)
    x = lp(x, 1600) * env(n, 0.35, 0.6, 0.8, 0) * np.linspace(1, 0.85, n)
    x[-int(0.12 * SR):] *= np.linspace(1, 0, int(0.12 * SR))
    add(pad, x * 0.022, t0)
    # bass
    I = intensity(t0 + 0.1)
    if I > 0.3:
        for k in range(4):
            nb = int(beat * SR * 0.9); tb = np.arange(nb) / SR; f = note(roots[bi % 4])
            y = np.sin(2 * np.pi * f * tb) + 0.3 * np.sin(2 * np.pi * 2 * f * tb)
            add(bass, y * env(nb, 0.01, 0.4, 0.5) * 0.10 * min(1, I * 1.2), t0 + k * beat)
    # arp 8ths
    seq = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[0] + 24, ch[1] + 12, ch[2] + 12]
    for k, m in enumerate(seq):
        na = int(0.5 * SR); ta = np.arange(na) / SR; f = note(m)
        y = np.sin(2 * np.pi * f * ta) * 0.7 + np.sin(2 * np.pi * 2 * f * ta) * 0.18 + np.sin(2 * np.pi * 3 * f * ta) * 0.06
        y *= np.exp(-ta * 9)
        add(arp, y * 0.05 * (0.6 + 0.4 * I), t0 + k * beat / 2)
    # drums
    if I >= 0.5:
        for k in range(4):
            tk = t0 + k * beat
            if k in (0, 2):
                nk = int(0.35 * SR); tkk = np.arange(nk) / SR
                f = 110 * np.exp(-tkk * 18) + 45
                kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tkk * 9)
                add(drums, kick * 0.30 * I, tk)
            if I >= 0.75 and k in (1, 3):
                nc = int(0.2 * SR); cl = hp(rng.standard_normal(nc), 1200) * np.exp(-np.arange(nc) / SR * 22)
                add(drums, cl * 0.035, tk)
            for hh in (0, 0.5):
                nh = int(0.06 * SR); h = hp(rng.standard_normal(nh), 7000) * np.exp(-np.arange(nh) / SR * 70)
                add(drums, h * (0.018 if hh else 0.011) * I, tk + hh * beat)

# SFX: whoosh at boundaries (soft), in the same space
for tb in ev['boundaries']:
    nw = int(0.7 * SR); tw = np.arange(nw) / SR
    w = rng.standard_normal(nw)
    # sweep via changing lowpass: mix of two bands
    w = lp(w, 2500) * np.sin(np.pi * tw / 0.7) ** 2
    add(sfx, w * 0.022, tb - 0.45)
# clicks: soft pitched ticks (E6)
for tc in ev['clicks']:
    nc = int(0.09 * SR); tcc = np.arange(nc) / SR
    c = (np.sin(2 * np.pi * note(88) * tcc) * 0.6 + np.sin(2 * np.pi * note(76) * tcc) * 0.4) * np.exp(-tcc * 55)
    add(sfx, c * 0.06, tc)
# success chimes (A major-ish in key: A5 E6)
for ts in ev.get('success', []):
    for k, m in enumerate([81, 88]):
        nc = int(0.6 * SR); tcc = np.arange(nc) / SR
        c = np.sin(2 * np.pi * note(m) * tcc) * np.exp(-tcc * 6)
        add(sfx, c * 0.035, ts + k * 0.09)

mix = pad + arp + bass + drums + sfx
# simple room: short feedback delay
d = int(0.19 * SR); wet = np.zeros_like(mix); wet[d:] += mix[:-d] * 0.18; wet[2 * d:] += mix[:-2 * d] * 0.08
mix = mix + lp(wet, 3000)
# fades
fi = int(0.4 * SR); mix[:fi] *= np.linspace(0, 1, fi)
end = int(DUR * SR); fo = int(2.5 * SR)
mix[end - fo:end] *= np.linspace(1, 0, fo); mix[end:] = 0
mix = mix[:end]
# gentle compression + normalize
mix = np.tanh(mix * 2.2) / 2.2
mix = mix / np.max(np.abs(mix)) * 0.8
st = np.stack([mix, np.roll(mix, int(0.004 * SR)) * 0.97], 1)
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print('ok', DUR)
