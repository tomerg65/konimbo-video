import sys, json, importlib
sys.argv_=sys.argv
from say import *
import say
mod=importlib.import_module(sys.argv[1]); voice=sys.argv[2]; ls=float(sys.argv[3]) if len(sys.argv)>3 else 1.0
FIX=[('jolˈip','julˈip'),('bejolˈip','bejulˈip'),('jolip','julip')]
import os; os.makedirs(f'out_{voice}',exist_ok=True)
res={}
for key,text in mod.LINES:
    if say._pk is None: say._pk=say.Phonikud(say.D+'phonikud-1.0.int8.onnx')
    if voice not in say._pp: say._pp[voice]=say.Piper(say.D+voice+'.onnx','model.config.json')
    dia=say._pk.add_diacritics(text); ph=say.phonemize(dia)
    import re
    ph=re.sub(r'(be|ve|le|ha)?jˈ?[ou]ˈ?lˈ?ip', lambda m:(m.group(1) or '')+'julˈip', ph)
    for a,b in [('mutsˈaʁ','motsˈaʁ'),('liemakˈoʁ','limkˈoʁ'),('limakˈoʁ','limkˈoʁ'),('ˈumlaj','umlˈaj'),('ʃemokaʁˈim','ʃemoχʁˈim'),('paʁjˈoʁˈiti','pʁajˈoʁiti'),
      ('ʔˈaj ʔˈaj','ʔej ʔˈaj'),('hamedˈa','hamejdˈa'),('safˈek','sapˈak'),('modˈulˈaʁit','modulˈaʁit'),('haʔˈi ʔˈaʁ pˈi','haʔi ʔaʁ pˈi'),('ʔˈi ʔˈaʁ pˈi','ʔi ʔaʁ pˈi'),
      ('ʔaχˈat mˈa','ʔaχˈat, mˈa'),('ʃiʃˈim kˈol','ʃiʃˈim, kˈol'),('halakˈoaχ meχˈiʁ','halakˈoaχ, meχˈiʁ'),('lehatsˈia','lehatsˈiʔa'),('umχabˈeʁet','umeχabˈeʁet')]: ph=ph.replace(a,b)
    ph=re.sub(r'ʔˈo saʔ\S*','ʔˈo sˈap.',ph)
    try: s,sr=say._pp[voice].create(ph,is_phonemes=True,length_scale=ls)
    except TypeError: s,sr=say._pp[voice].create(ph,is_phonemes=True)
    sf.write(f'out_{voice}/{key}.wav',s,sr); res[key]=round(len(s)/sr,2); print(key,res[key],ph)
json.dump(res,open(f'out_{voice}/dur.json','w'))
