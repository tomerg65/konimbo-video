import sys, soundfile as sf, re
import tokenizers, phonikud_onnx.model as _m
_orig=tokenizers.Tokenizer
class _T:
    @staticmethod
    def from_pretrained(*a,**k): return _orig.from_file('/home/claude/tts/dicta_tokenizer.json')
_m.Tokenizer=_T
from phonikud_onnx import Phonikud
from phonikud import phonemize
from piper_onnx import Piper
D='/mnt/user-data/uploads/Downloads/'
_pk=None; _pp={}
def tts(text, voice='shaul', out='out.wav', length=1.0):
    global _pk
    if _pk is None: _pk=Phonikud(D+'phonikud-1.0.int8.onnx')
    if voice not in _pp: _pp[voice]=Piper(D+voice+'.onnx','model.config.json')
    dia=_pk.add_diacritics(text)
    ph=phonemize(dia)
    try: s,sr=_pp[voice].create(ph,is_phonemes=True,length_scale=length)
    except TypeError: s,sr=_pp[voice].create(ph,is_phonemes=True)
    sf.write(out,s,sr); return dia,ph,len(s)/sr
if __name__=='__main__':
    t="ה־ERP שלכם מצוין. אבל המכירות, השיווק והשירות שלכם, לא סובלים אותו. יוליפ מאחדת את כל ערוצי המכירה למקום אחד."
    for v in ('shaul','michael'):
        print(v, tts(t,v,f'test_{v}.wav'))
