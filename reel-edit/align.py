from faster_whisper import WhisperModel
import json,wave,numpy as np
w=wave.open('audio2.wav');A=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
m=WhisperModel('whisper-small',device='cpu',compute_type='int8')
# (src_in, src_out, expected text)
P=[("A",0.15,4.66,"gautam bhai, aap karwa chauth ke liye itna achha achha collection leke aaye, is baar karwa chauth pe kya laaye ho?"),
("B",4.80,6.22,"aapke liye leke aaye hain,"),
("C1",7.50,8.35,"karwa chauth par"),
("C2",8.50,10.92,"alag alag prakar ki thaali, lota aur chhalni."),
("D1",17.28,19.25,"jiske liye aapko aana hoga krishna shringar,"),
("D2",19.43,19.97,"jo hai"),
("D3",20.10,21.28,"bhati chauraha, ratanada, jodhpur."),
("E1",21.80,23.27,"uske saath saath aapko"),
("E2",23.41,25.10,"alag alag prakar ke karwe bhi milenge."),
("F1",25.30,25.78,"aapko"),
("F2",25.91,28.72,"thaali pe rakhne ke liye alag alag prakar ke thaalposh bhi milenge."),
("G1",29.00,30.10,"saath hi saath"),
("G2",30.29,31.38,"alag alag prakar ki chunri"),
("G3",31.59,33.30,"bhi milegi. iske saath aapko"),
("G4",33.44,34.52,"solah shringar bhi milega."),
("H1",34.75,37.25,"isko lene ke liye aapko aana hoga"),
("H2",37.42,38.32,"krishna shringar,"),
("I1",38.52,39.12,"jo hai"),
("I2",39.28,42.20,"lotus restaurant ke saamne, bhati chauraha, ratanada, jodhpur."),
]
out=[]
for name,a,b,txt in P:
    pad=0.05
    seg=A[int((a-pad)*16000):int((b+pad)*16000)]
    segs,_=m.transcribe(seg,language='en',initial_prompt=txt,word_timestamps=True,beam_size=5,condition_on_previous_text=False,without_timestamps=False)
    ws=[{'w':x.word.strip(),'s':round(x.start+a-pad,2),'e':round(x.end+a-pad,2)} for s in segs for x in s.words]
    print(name,a,b,'|',txt,'\n   ->',' '.join(f"{x['w']}@{x['s']}" for x in ws))
    out.append({'name':name,'in':a,'out':b,'text':txt,'asr':ws})
json.dump(out,open('work/align.json','w'),ensure_ascii=False,indent=1)
