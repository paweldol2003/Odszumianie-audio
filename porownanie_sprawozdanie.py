import ast,json
from pathlib import Path
import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
nb=json.loads(Path('odszumianie.ipynb').read_text(encoding='utf-8'))
for id in ['etap2-rls','etap4-interpolacja']:
 s=''.join(next(c for c in nb['cells'] if c['id']==id)['source'])
 tree=ast.parse(s)
 tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) or isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['r','lam','okno']]
 exec(compile(tree,id,'exec'))
rows=[]
for name in ['03','04','17','22','23']:
 data,fs=sf.read(f'nagrania/{name}.wav',always_2d=True); x=data[:,0]; t=np.arange(len(x))/fs
 fig,ax=plt.subplots(4,2,figsize=(11,10),sharex=True,sharey='row',constrained_layout=True)
 for col,(variant,swap) in enumerate([('A',False),('B',True)]):
  e,prog,mask,coeffs=detekcja(x,swap); y,fixed=interpolacja(x,mask)
  assert np.isfinite(y).all() and np.isfinite(coeffs[r:]).all()
  omitted=mask & ~fixed
  stats=dict(file=name+'.wav',variant=variant,n=len(x),duration=len(x)/fs,detected=int(mask.sum()),repaired=int(fixed.sum()),omitted=int(omitted.sum()),omitted_runs=int(np.count_nonzero(np.diff(np.r_[False,omitted].astype(int))==1)),percent=100*fixed.mean(),change_rmse=float(np.sqrt(np.mean((y-x)**2))))
  rows.append(stats); print(json.dumps(stats),flush=True)
  ax[0,col].plot(t,x,color='.75',lw=.4,label='Wejście'); ax[0,col].plot(t,y,lw=.4,label='Wynik')
  ax[0,col].set(title=f'{variant}: sygnał po rekonstrukcji',ylabel='Amplituda'); ax[0,col].legend(fontsize=8)
  ax[1,col].plot(t,x-y,lw=.4); ax[1,col].set(title=f'{variant}: wejście − wynik',ylabel='Różnica')
  ax[2,col].plot(t[::10],coeffs[::10],lw=.5); ax[2,col].set(title=f'{variant}: parametry AR(4)',ylabel='Parametr'); ax[2,col].legend(['a1','a2','a3','a4'],ncol=4,fontsize=7)
  ax[3,col].plot(t,np.abs(e),lw=.4,label='|e|'); ax[3,col].plot(t,prog,lw=.5,label='3σ'); ax[3,col].legend(fontsize=8)
  ax[3,col].set(title=f'{variant}: detekcja',ylabel='Amplituda',xlabel='Czas [s]')
  sf.write(f'sprawozdanie/{name}_{variant}_odszumiony.wav',y,fs,subtype='PCM_16')
 for axis in ax.flat: axis.grid(alpha=.25)
 fig.savefig(f'sprawozdanie/images/{name}_AB.png',dpi=150); plt.close(fig)
 Path('sprawozdanie/wyniki_AB.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
