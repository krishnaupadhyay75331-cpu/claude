import json; from edl import keep, s2e
tr=json.load(open('../tr_hi.json'))
ROMAN=[
 "pushpa ji, agar kisi ke mann mein koi sawaal aata toh uske liye poori kundli dikhana zaroori hai??",
 "zaroori nahi hai, har sawaal ke liye alag tarika ho sakta hai.",
 "toh phir prashna kundli kya hoti hai??",
 "prashna kundli mein dekhte ki kisi khaas sawaal ko paramparik jyotish paddhati ke anusaar samajhne ki koshish ki jaati hai",
 "is mein sawaal aur usse judi paristhiti ko dhyaan se samajhna zaroori hota hai",
 "matlab kisi ko specific sawaal poochna ho toh uske baare mein jaan sakta hai??",
 "bilkul, sab se pehle apna sawaal _ spasht rakhiye",
 "phir samjhe ki aapke liye kaunsa consultation sahi rahega",
 "aapko bhi prashna kundli ke baare mein jaanna hai?",
 "toh maa _ jyotish ko follow karein aur consultation ke liye DM karein jai mata di",
]
W=[]
for si,(seg,rom) in enumerate(zip(tr,ROMAN)):
    r=rom.split(); assert len(r)==len(seg['words']),(si,len(r),len(seg['words']))
    for j,(rw,w) in enumerate(zip(r,seg['words'])):
        W.append(dict(seg=si,i=j,text=rw,s=s2e(w['s']),e=s2e(w['e'])))
def ws(si,a,b): return [w for w in W if w['seg']==si and a<=w['i']<=b and w['text']!='_']
# stacks: (seg, lead range, hero idx, trail range, style)
ST=[(0,(0,7),8,(9,10),'n'),(0,(11,13),14,(15,17),'red'),
    (1,(0,0),1,(2,2),'n'),(1,(3,6),7,(8,11),'n'),
    (2,(0,1),2,(3,6),'depth'),
    (3,(0,5),6,(7,8),'n'),(3,(9,9),10,(11,13),'n'),(3,(14,15),16,(17,19),'n'),
    (4,(0,5),6,(7,7),'n'),(4,(1,0),8,(9,13),'n'),
    (5,(0,2),3,(4,7),'n'),(5,(8,10),11,(12,13),'n'),
    (6,(1,0),0,(1,0),'depth'),(6,(1,5),7,(8,8),'n'),
    (7,(0,5),6,(7,8),'n'),
    (8,(0,2),3,(4,8),'n'),
    (9,(0,0),5,(6,6),'n'),
    (9,(7,10),11,(12,12),'cta'),
    (9,(13,15),None,(1,0),'script')]
stacks=[]
for si,(la,lb),h,(ta,tb),style in ST:
    lead=ws(si,la,lb); trail=ws(si,ta,tb); hero=ws(si,h,h) if h is not None else []
    allw=lead+hero+trail
    stacks.append(dict(style=style,lead=lead,hero=hero[0] if hero else None,trail=trail,
                       start=min(w['s'] for w in allw),last=max(w['e'] for w in allw)))
for a,b in zip(stacks,stacks[1:]): a['end']=min(b['start']-0.03,a['last']+0.6)
stacks[-1]['end']=None
E=lambda t: round(s2e(t),3)
# shots: (src_in, src_out, angle, zoom spec)  zoom: [scale_start, scale_end, focus 'face'|'hands'|'center']
SH=[(0.18,2.44,'A',[1.0,1.05,'face']),(2.44,4.29,'A',[1.45,1.5,'face']),
    (4.52,6.0,'B',[1.0,1.05,'face']),(6.0,7.24,'B',[1.4,1.45,'face']),
    (7.55,9.23,'A',[1.0,1.06,'face']),
    (9.23,11.45,'B',[1.0,1.05,'face'],'whip'),(11.45,13.2,'CW_idols',[1.0,1.08,'center']),
    (13.2,15.0,'B',[1.45,1.5,'hands']),(15.32,17.46,'B',[1.0,1.05,'face']),
    (17.46,18.6,'CW_shiva',[1.0,1.08,'center']),(18.6,19.59,'B',[1.4,1.45,'face']),
    (19.73,21.6,'A',[1.0,1.05,'face']),(21.6,23.83,'A',[1.5,1.55,'face']),
    (23.83,24.9,'B',[1.0,1.04,'face']),(24.9,26.19,'B',[1.45,1.5,'face']),(26.44,29.28,'B',[1.08,1.15,'face']),
    (29.8,31.84,'A',[1.0,1.05,'face']),(31.84,36.2,'A',[1.3,1.38,'face'])]
shots=[]; acc=0
for s in SH:
    a,b=s[0],s[1]; ea,eb=E(a),E(b)
    shots.append(dict(src_in=a,src_out=b,e_in=ea,e_out=eb,angle=s[2],zoom=s[3],tin=(s[4] if len(s)>4 else None)))
tl=dict(total=E(36.2),words=W,stacks=stacks,shots=shots,
  trans=[dict(t=E(4.52),k='tint'),dict(t=E(9.23),k='whip'),dict(t=E(11.45),k='white'),dict(t=E(13.2),k='cream'),
         dict(t=E(15.32),k='white'),dict(t=E(17.46),k='bokeh'),dict(t=E(18.6),k='cream'),dict(t=E(19.73),k='tint'),
         dict(t=E(23.83),k='flare'),dict(t=E(29.8),k='bokeh'),dict(t=E(29.8),k='burn')],
  ov=dict(q=[E(1.94),E(4.95)],name=[E(4.6),E(7.1)],halo=[E(26.6),E(29.28)],
          tags=[dict(t=E(27.0),text='Spasht Sawaal'),dict(t=E(27.2),text='Prashna Kundli'),dict(t=E(27.4),text='Sahi Consultation')]))
json.dump(tl,open('../reel/src/timeline.json','w'),indent=1,ensure_ascii=False)
print('total',tl['total']); [print(round(s['start'],2),s['style'],s['hero']['text'] if s['hero'] else '-',' '.join(w['text'] for w in s['lead']),'|',' '.join(w['text'] for w in s['trail'])) for s in stacks]
print([ (s['angle'],s['e_in'],s['e_out']) for s in shots])
