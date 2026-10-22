from pathlib import Path
import json
import numpy as np
import soundfile as sf

FS = 22050
MODES = ['original', 'prediction', 'previous']

def run(x, mode):
    a = np.zeros(4)
    P = 1000 * np.eye(4)
    z = x.copy()
    errors = np.zeros(len(x))
    mask = np.zeros(len(x), dtype=bool)
    stable = True
    for k in range(4, len(x)):
        phi = z[k-4:k][::-1]
        pred = a @ phi
        errors[k] = x[k] - pred
        # Stop divergent experiments before overflow; no clipping or recovery.
        if not np.isfinite(pred) or abs(pred) > 1e6 or not np.isfinite(P).all():
            stable = False
            break
        if k >= 225:
            mask[k] = abs(errors[k]) > 3 * np.std(errors[k-221:k])
        if mask[k]:
            if mode == 'prediction':
                z[k] = pred
            elif mode == 'previous':
                z[k] = z[k-1]
            P /= .999
        else:
            q = P @ phi
            gain = q / (.999 + phi @ q)
            a += gain * errors[k]
            P = (P - np.outer(gain, phi @ P)) / .999
    y = x.copy()
    fixed = np.zeros(len(x), dtype=bool)
    changes = np.diff(np.r_[False, mask, False].astype(int))
    for left, right in zip(np.flatnonzero(changes == 1), np.flatnonzero(changes == -1)):
        if left > 0 and right < len(x) and right-left <= 4:
            y[left:right] = np.linspace(x[left-1], x[right], right-left+2)[1:-1]
            fixed[left:right] = True
    info = dict(stable=stable, processed=k+1, detected=int(mask.sum()), repaired=int(fixed.sum()), max_history=float(np.max(np.abs(z[:k+1]))))
    return y, mask, fixed, info

out = Path('porownanie_wariantow')
out.mkdir(exist_ok=True)
results = []
rng = np.random.default_rng(193582)
t = np.arange(3*FS)/FS
signals = {
    'harmonic': .12*np.sin(2*np.pi*220*t)+.06*np.sin(2*np.pi*440*t)+.025*np.sin(2*np.pi*880*t),
    'changing': (.07+.05*np.sin(2*np.pi*1.7*t))*np.sin(2*np.pi*(150*t+100*t*t)) + .04*np.sin(2*np.pi*650*t),
}
for name, clean in signals.items():
    noisy=clean.copy(); truth=np.zeros(len(clean),dtype=bool)
    for i,pos in enumerate(np.arange(int(.3*FS),len(clean)-int(.15*FS),int(.2*FS))):
        width=i%4+1
        noisy[pos:pos+width]+=rng.choice([-1,1],width)*rng.uniform(.4,.7,width)
        truth[pos:pos+width]=True
    for mode in MODES:
        y,mask,fixed,info=run(noisy,mode)
        noise_mse=float(np.mean((noisy-clean)**2))
        mse=float(np.mean((y-clean)**2))
        info.update(test=name,kind='synthetic',mode=mode,truth=int(truth.sum()),tp=int((mask&truth).sum()),fp=int((mask&~truth).sum()),repaired_truth=int((fixed&truth).sum()),changed_clean=int((fixed&~truth).sum()),mse=mse,input_mse=noise_mse,gain_db=float(10*np.log10(noise_mse/mse)))
        # Control: same signal with no added impulses.
        yc,mc,fc,ic=run(clean,mode)
        info.update(clean_control_detected=int(mc.sum()),clean_control_mse=float(np.mean((yc-clean)**2)))
        results.append(info); print(json.dumps(info),flush=True)
for name in ['01','02','03','04','17','22','23']:
    x,fs=sf.read(f'nagrania/{name}.wav',always_2d=True); x=x[:,0]
    if name!='02': x=x[:3*fs]
    for mode in MODES:
        y,mask,fixed,info=run(x,mode)
        info.update(test=name+'.wav',kind='recording',mode=mode,n=len(x),duration=len(x)/fs,changed_rms=float(np.sqrt(np.mean((y-x)**2))))
        results.append(info); print(json.dumps(info),flush=True)
        if name=='02' and info['stable']:
            sf.write(out/f'02_{mode}.wav',y,fs,subtype='PCM_16')
    (out/'wyniki.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
(out/'wyniki.json').write_text(json.dumps(results,indent=2),encoding='utf-8')

