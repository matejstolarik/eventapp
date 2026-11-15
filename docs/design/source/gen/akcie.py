import sys
NAV=open('/tmp/nav.html').read()
OUT=sys.argv[1]
HEAD='''<!doctype html><html lang="sk"><head><meta charset="utf-8"><title>{t}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&amp;family=Outfit:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<style>body{{margin:0;background:#0B0B10}}
.tg{{-webkit-mask-image:linear-gradient(90deg,#000 78%,transparent);mask-image:linear-gradient(90deg,#000 78%,transparent)}}</style>
</head><body>
<div style="width:390px;height:844px;position:relative;overflow:hidden;background:#111118;font-family:'Outfit',sans-serif;color:#F4F2FF">'''
def svg(p,s=20,w=2.4): return f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'
I=dict(search='<circle cx="11" cy="11" r="7"></circle><path d="M20 20l-3.5-3.5"></path>',
 chev='<path d="M6 9l6 6 6-6"></path>', x='<path d="M6 6l12 12M18 6L6 18"></path>',
 spark='<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"></path><path d="M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z"></path>',
 filt='<path d="M4 7h10M18 7h2M4 17h4M12 17h8"></path><circle cx="16" cy="7" r="2"></circle><circle cx="10" cy="17" r="2"></circle>',
 inf='<path d="M7 9a3 3 0 1 0 0 6c2 0 3-1.5 5-3s3-3 5-3a3 3 0 1 1 0 6c-2 0-3-1.5-5-3s-3-3-5-3z"></path>',
 cal='<rect x="3" y="5" width="18" height="16" rx="3"></rect><path d="M3 10h18M8 3v4M16 3v4"></path>',
 check='<path d="M5 12l5 5 9-10"></path>')
TYPE={'c':('#8B6CFF','#14063A'),'p':('#FF8A3D','#2A1200'),'d':('#2FD4C0','#002B26'),'k':('#C6F432','#1B2600')}
SH=['<span style="position:absolute;width:74px;height:74px;border-radius:50%;background:{a};right:-18px;top:6px"></span>',
 '<span style="position:absolute;width:140px;height:18px;border-radius:4px;background:{d};left:-14px;top:26px;transform:rotate(-24deg)"></span>',
 '<span style="position:absolute;width:62px;height:62px;border-radius:50%;border:7px solid {d};left:24px;top:6px;box-sizing:border-box"></span>',
 '<span style="position:absolute;width:86px;height:86px;border-radius:50%;background:{a};left:-24px;top:-24px"></span>',
 '<span style="position:absolute;width:130px;height:12px;background:{d};left:-8px;top:30px"></span><span style="position:absolute;width:130px;height:12px;background:{d};left:-8px;top:52px"></span>']
ACC=['#C6F432','#FF4D8D','#F4F2FF','#FF8A3D','#2FD4C0']
def card(i,t,date,time,poster,name,venue,tags,me=False,new=False):
    bg,dk=TYPE[t]; sh=SH[i%5].format(a=ACC[(i+1)%5] if ACC[(i+1)%5]!=bg else ACC[(i+2)%5],d=dk)
    badges=''
    if me: badges+=f'<span style="position:absolute;top:6px;left:6px;z-index:2;height:18px;padding:0 6px;border-radius:9px;background:#111118;color:#F4F2FF;font-size:10px;font-weight:600;display:flex;align-items:center;gap:3px">{svg(I["spark"],11,2.4)}pre teba</span>'
    if new: badges+='<span style="position:absolute;top:6px;right:6px;z-index:2;height:18px;padding:0 6px;border-radius:9px;background:#F4F2FF;color:#111118;font-size:10px;font-weight:600;display:flex;align-items:center">nové</span>'
    tg=''.join(f'<span style="flex:none;height:18px;padding:0 6px;border-radius:9px;font-size:10px;font-weight:500;display:flex;align-items:center;'+('border:1.5px solid #5D5677;color:#F4F2FF;box-sizing:border-box' if x.startswith('*') else 'background:#2A2838;color:#E4DEFF')+f'">{x.lstrip("*")}</span>' for x in tags)
    return f'''<div style="min-width:0">
<div style="width:100%;aspect-ratio:1/1;border-radius:12px;background:{bg};color:{dk};position:relative;overflow:hidden;display:flex;align-items:flex-end;padding:7px;box-sizing:border-box">{sh}{badges}<span style="position:relative;z-index:1;font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:15px;line-height:.95;text-transform:uppercase">{poster}</span></div>
<div style="margin-top:6px;font-size:12px;font-weight:600;white-space:nowrap;overflow:hidden"><span style="color:#8E8AA6;font-weight:500">{date} · </span><span style="color:{bg}">{time}</span></div>
<div style="font-size:13px;font-weight:500;line-height:1.25;max-height:2.5em;overflow:hidden;margin-top:1px">{name}</div>
<div style="font-size:12px;font-weight:700;color:#B9B6CC;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px">{venue}</div>
<div class="tg" style="display:flex;gap:4px;margin-top:5px;overflow:hidden">{tg}</div></div>'''
def grid(cards): return '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px 8px;align-items:start">'+''.join(cards)+'</div>'
def day(t): return ''
def header(period,search=None,me=False,new=False,count='',sort='dátum'):
    if search is None:
        top=f'''<div style="display:flex;align-items:center;height:44px"><h1 style="margin:0;font-family:'Bricolage Grotesque',sans-serif;font-size:32px;font-weight:700;letter-spacing:-0.02em">Akcie</h1>
<button style="margin-left:auto;width:44px;height:44px;border-radius:22px;border:0;background:#23232F;color:#F4F2FF;display:flex;align-items:center;justify-content:center" aria-label="Hľadať">{svg(I["search"],20)}</button></div>'''
    else:
        top=f'''<div style="display:flex;align-items:center;height:44px;gap:8px"><div style="flex:1;height:44px;border-radius:22px;background:#F4F2FF;color:#111118;display:flex;align-items:center;gap:8px;padding:0 14px;font-size:15px;font-weight:500">{svg(I["search"],18)}{search}<span style="width:2px;height:20px;background:#FF4D8D;margin-left:-6px"></span></div>
<button style="width:44px;height:44px;border-radius:22px;border:0;background:#23232F;color:#F4F2FF;display:flex;align-items:center;justify-content:center" aria-label="Zavrieť hľadanie">{svg(I["x"],20)}</button></div>'''
    chip=lambda lab,on,ic='': f'<button style="height:40px;padding:0 14px;border-radius:20px;border:0;background:{"#FF4D8D" if on else "#23232F"};color:{"#1A0710" if on else "#B9B6CC"};font-family:Outfit,sans-serif;font-size:14px;font-weight:{600 if on else 500};display:flex;align-items:center;gap:6px;white-space:nowrap;flex:none">{ic}{lab}</button>'
    bar=f'''<div style="display:flex;gap:8px;align-items:center">
<button style="height:44px;padding:0 14px;border-radius:22px;border:0;background:#F4F2FF;color:#111118;font-family:Outfit,sans-serif;font-size:15px;font-weight:600;display:flex;align-items:center;gap:6px;white-space:nowrap;flex:none">{period}{svg(I["chev"],16)}</button>
<div class="tg" style="flex:1;min-width:0;display:flex;gap:8px;overflow:hidden">{chip("Pre teba",me,svg(I["spark"],16,2.2))}{chip("Nové",new)}</div>
<button style="width:44px;height:44px;border-radius:22px;border:0;background:#FF4D8D;color:#1A0710;display:flex;align-items:center;justify-content:center;flex:none" aria-label="Filter">{svg(I["filt"],20)}</button></div>
<div style="display:flex;justify-content:space-between;align-items:center;font-size:13px;color:#8E8AA6;margin-top:2px"><span>{count}</span><span style="display:flex;align-items:center;gap:4px">Zoradiť: <b style="color:#F4F2FF;font-weight:600">{sort}</b>{svg(I["chev"],14)}</span></div>'''
    return f'<div style="padding:52px 16px 0;display:flex;flex-direction:column;gap:14px">{top}{bar}</div>'
EV=[('c','Nová<br>Vlna','Nová Vlna – krst albumu','Palác Akropolis',['concert','indie','post-punk','*alternative'],True,False,'20:00'),
 ('k','Hamlet<br>remix','Hamlet remix','Archa+',['theatre','*english-friendly','*experimental'],False,False,'20:00'),
 ('c','Kovy','Kovy','Forum Karlín',['concert','rock','*commercial'],False,False,'19:30'),
 ('d','Lumen','Lumen all night long','Bike Jesus',['dj','house','techno','*diy'],True,False,'22:00'),
 ('p','2000s','Párty 2000s','EPIC',['party','pop','disco'],False,False,'22:00'),
 ('p','Nocturne<br>XL','Nocturne XL: techno noc s hosťami z Berlína','Fuchs2',['party','techno','ebm','*late-night'],True,True,'23:00'),
 ('d','Bass<br>shift','Bass Shift','Cross Club',['dj','drum-and-bass','dubstep'],False,False,'23:00'),
 ('c','Trio<br>Kvet','Trio Kvet','Čitárna Unijazz',['concert','jazz','*cozy'],False,False,'20:00'),
 ('k','Mesto<br>a my','Mesto a my: diskusia','MeetFactory',['talk','*art-space'],False,True,'19:00'),
 ('c','Echo<br>Park','Echo Park','Palác Akropolis',['concert','indie'],False,False,'20:30'),
 ('p','Club<br>Mix','Club Mix','Roxy',['party','house','techno'],False,False,'23:00'),
 ('d','Low<br>end','Low End','Cross Club',['dj','dub'],False,False,'21:00')]
def cards(idx,dates):
    return [card(n,EV[i][0],dates[k] if isinstance(dates,list) else dates,EV[i][7],EV[i][1],EV[i][2],EV[i][3],EV[i][4],EV[i][5],EV[i][6]) for n,(k,i) in enumerate(enumerate(idx))]
END='</div></body></html>'
def page(name,body,overlay=''):
    open(f'{OUT}/{name}.html','w').write(HEAD.format(t=name)+body+NAV+overlay+END)
# 10 default Dnes
b=header('Dnes',count='12 akcií · 3 pre teba')+'<div style="padding:14px 16px 0">'+day('DNES · NEDEĽA 15. 11.')+grid(cards(range(12),'Dnes'))+'</div>'
page('10-akcie-mriezka',b)
# 11 period sheet
b=header('7 dní',count='31 akcií · 9 pre teba')+'<div style="padding:14px 16px 0">'+day('DNES · NEDEĽA 15. 11.')+grid(cards([0,3,5],'Dnes')+cards([7,8,1],'Zajtra'))+'</div>'
row=lambda lab,on=False,ic='',sub='': f'<div style="height:48px;border-radius:24px;padding:0 16px;display:flex;align-items:center;gap:10px;font-size:16px;font-weight:{600 if on else 500};background:{"#F4F2FF" if on else "transparent"};color:{"#111118" if on else "#F4F2FF"}">{ic}<span>{lab}</span><span style="margin-left:auto;font-size:13px;color:{"#4A4760" if on else "#8E8AA6"};font-weight:500">{sub}</span></div>'
sheet=f'''<div style="position:absolute;inset:0;background:rgba(11,11,16,.6);z-index:5"></div>
<div style="position:absolute;left:0;right:0;bottom:0;z-index:6;background:#1C1C27;border-radius:28px 28px 0 0;padding:10px 12px 124px">
<div style="width:40px;height:4px;border-radius:2px;background:#3A3848;margin:0 auto 12px"></div>
<div style="font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-weight:700;padding:0 16px 8px">Obdobie</div>
{row("Kedykoľvek",False,svg(I["inf"],20,2.2),"všetky akcie")}
<div style="height:1px;background:#2E2D3C;margin:6px 16px"></div>
{row("Dnes",False,'','Ne 15. 11.')}{row("Zajtra",False,'','Po 16. 11.')}{row("Tento víkend",False,'','Pi 20.–Ne 22. 11.')}{row("Najbližších 7 dní",True,'','15.–21. 11.')}{row("Najbližších 30 dní",False,'','15. 11.–14. 12.')}
{row("Iný dátum",False,svg(I["cal"],20,2.2),'')}
</div>'''
page('11-akcie-obdobie',b,sheet)
# 12 search
b=header('Kedykoľvek',search='techno',count='3 akcie')+'<div style="padding:14px 16px 0">'+day('DNES · NEDEĽA 15. 11.')+grid(cards([3],'Dnes')+cards([5,10],'Pi 20. 11.'))+'</div>'
page('12-akcie-hladanie',b)
