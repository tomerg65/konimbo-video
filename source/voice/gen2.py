import json, re, os, soundfile as sf, sys
sys.path.insert(0,'/home/claude/tts')
import say
from lines_v2 import SEG
voice='shaul'; ls=0.95; os.makedirs('out_v2',exist_ok=True)
say._pk=say.Phonikud(say.D+'phonikud-1.0.int8.onnx'); say._pp[voice]=say.Piper(say.D+voice+'.onnx','model.config.json')
res=[]
for sc,cue,text,mn in SEG:
    dia=say._pk.add_diacritics(text); ph=say.phonemize(dia)
    import re
    ph=re.sub(r'(be|ve|le|ha)?jˈ?[ou]ˈ?lˈ?ip', lambda m:(m.group(1) or '')+'julˈip', ph)
    for a,b in [('mutsˈaʁ','motsˈaʁ'),('liemakˈoʁ','limkˈoʁ'),('limakˈoʁ','limkˈoʁ'),('ˈumlaj','umlˈaj'),('ʃemokaʁˈim','ʃemoχʁˈim'),('paʁjˈoʁˈiti','pʁajˈoʁiti'),
      ('ʔˈaj ʔˈaj','ʔej ʔˈaj'),('hamedˈa','hamejdˈa'),('safˈek','sapˈak'),('modˈulˈaʁit','modulˈaʁit'),('haʔˈi ʔˈaʁ pˈi','haʔi ʔaʁ pˈi'),('ʔˈi ʔˈaʁ pˈi','ʔi ʔaʁ pˈi'),
      ('ʔaχˈat mˈa','ʔaχˈat, mˈa'),('ʃiʃˈim kˈol','ʃiʃˈim, kˈol'),('halakˈoaχ meχˈiʁ','halakˈoaχ, meχˈiʁ'),('lehatsˈia','lehatsˈiʔa'),('umχabˈeʁet','umeχabˈeʁet')]: ph=ph.replace(a,b)
    ph=re.sub(r'ʔˈo saʔ\S*','ʔˈo sˈap.',ph)
    ph=ph.replace('ʔˈaj ʔˈaj','ʔej ʔˈaj')
    for a,b in [('peʁjˈoʁiti','pʁajˈoʁiti'),('saʔˈap','sˈap'),('χaʃvʃevˈet','χeʃbeʃˈevet'),('hatavlˈet','hatablˈet'),('lemakˈoʁ','limkˈoʁ'),
                ('umχinˈa','umeχinˈa'),('ʔˈo sˈi ʔˈeʁ','ʔˈo sˈi ʔˈaʁ'),('hamʔuχˈad','hameʔuχˈad'),('ˈulmi','ulemˈi'),('tablˈet','tˈablet'),('tavlˈet','tˈablet'),('ʔˈo sˈi ʔˈaʁ','ʔo si ʔˈaʁ'),('ʔˈo sˈi ʔˈeʁ','ʔo si ʔˈaʁ')]: ph=ph.replace(a,b)
    import re as _re
    ph=_re.sub(r'lakˈoaχ ʃ\S* ʃiʃˈim','lakˈoaχ, ʃalˈoʃ ʃiʃˈim',ph)
    s,sr=say._pp[voice].create(ph,is_phonemes=True,length_scale=ls)
    fn=f'out_v2/{sc}_{cue}.wav'; sf.write(fn,s,sr); res.append([sc,cue,round(len(s)/sr,3),mn]); print(sc,cue,round(len(s)/sr,2),ph)
json.dump(res,open('out_v2/segs.json','w'))
