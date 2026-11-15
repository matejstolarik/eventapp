import json,re,os
D='/tmp/claude-0/-home-claude/6a6fdeae-1a3b-5ff8-ad92-4c2929c96cc1/scratchpad/eventapp-design/project'
MIC=open('/tmp/claude-0/-home-claude/6a6fdeae-1a3b-5ff8-ad92-4c2929c96cc1/scratchpad/micicon.txt').read()
PINK,PD='#FF4D8D','#1A0710'
T={'concert':('#8B6CFF','#14063A'),'party':('#FF8A3D','#2A1200'),'dj':('#2FD4C0','#002B26'),'culture':('#C6F432','#1B2600')}
ICON={'concert':MIC,'party':'<path d="M5 4h14l-7 8z"></path><path d="M12 12v7"></path><path d="M8 20h8"></path><path d="M15 7l3-4"></path>',
'dj':'<rect x="3" y="4" width="18" height="16" rx="3"></rect><circle cx="11" cy="12" r="5"></circle><circle cx="11" cy="12" r="1"></circle><path d="M18 7v6l-3 2"></path>',
'culture':'<path d="M4 5c3 1.5 7 1.5 10 0v6a5 5 0 0 1-10 0z"></path><path d="M10 13c3 1.5 7 1.5 10 0v6a5 5 0 0 1-10 0z"></path>'}
F="font-family: 'Outfit', sans-serif;"
B="font-family: 'Bricolage Grotesque', sans-serif;"
def svg(paths,size=20,stroke='currentColor',sw=2.2,fill='none'):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
HEART='<path d="M19.5 12.6L12 20l-7.5-7.4A5 5 0 1 1 12 6a5 5 0 1 1 7.5 6.6z"></path>'
FILT='<path d="M4 7h10M18 7h2M4 17h4M12 17h8"></path><circle cx="16" cy="7" r="2"></circle><circle cx="10" cy="17" r="2"></circle>'
CAL='<rect x="3" y="5" width="18" height="16" rx="3"></rect><path d="M3 10h18M8 3v4M16 3v4"></path>'
SEARCH='<circle cx="11" cy="11" r="7"></circle><path d="M20 20l-4-4"></path>'
CHEV='<path d="M9 6l6 6-6 6"></path>'
BACK='<path d="M15 6l-6 6 6 6"></path>'
NAV={'Mapa':'<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"></path><path d="M9 4v14M15 6v14"></path>',
'Akcie':'<path d="M8 6h12M8 12h12M8 18h12"></path><circle cx="4" cy="6" r="1"></circle><circle cx="4" cy="12" r="1"></circle><circle cx="4" cy="18" r="1"></circle>',
'Podniky':'<path d="M4 21V9l8-5 8 5v12"></path><path d="M9 21v-6h6v6"></path>',
'Účet':'<circle cx="12" cy="8" r="4"></circle><path d="M4 21a8 8 0 0 1 16 0"></path>'}
def nav(active):
    out=[]
    for k,p in NAV.items():
        if k==active: out.append(f'<a href="#" style="height: 52px; padding: 0 20px; border-radius: 26px; background: {PINK}; color: {PD}; display: flex; align-items: center; gap: 8px; text-decoration: none; font-size: 15px; font-weight: 600">{svg(p)}{k}</a>')
        else: out.append(f'<a href="#" style="width: 52px; height: 52px; border-radius: 26px; color: #B9B6CC; display: flex; align-items: center; justify-content: center" aria-label="{k}">{svg(p,22,sw=2.1)}</a>')
    return f'<nav style="position: absolute; left: 16px; right: 16px; bottom: 28px; height: 72px; border-radius: 36px; background: #1C1C27; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; box-shadow: 0 -10px 30px rgba(17,17,24,0.9)" aria-label="Hlavná navigácia">{"".join(out)}</nav>'
def art(t,w,h,r=16,seed=0):
    c,d=T[t]; o=['#8B6CFF','#FF8A3D','#2FD4C0','#C6F432','#FF4D8D']
    a,b=o[(seed+1)%5],o[(seed+3)%5]
    return f'<div style="width: {w}px; height: {h}px; border-radius: {r}px; background: {c}; position: relative; overflow: hidden; flex: none"><svg width="{w}" height="{h}" viewBox="0 0 100 100" preserveAspectRatio="none" style="position: absolute; inset: 0" aria-hidden="true"><circle cx="{25+seed*9%40}" cy="35" r="30" fill="{a}" opacity="0.9"></circle><circle cx="78" cy="{60+seed*7%25}" r="34" fill="{b}" opacity="0.8"></circle><path d="M0 100 L100 {10+seed*13%50}" stroke="{d}" stroke-width="7"></path></svg></div>'
def tag(label,kind):
    if kind in T: c,d=T[kind]; st=f'background: {c}; color: {d};'
    elif kind=='genre': st='background: #2A2838; color: #E4DEFF;'
    else: st='background: transparent; color: #F4F2FF; border: 1.5px solid #5D5677;'
    return f'<span style="height: 24px; padding: 0 10px; border-radius: 12px; {st} font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; white-space: nowrap">{label}</span>'
def page(title,body,w=390,h=844):
    return f'''<!doctype html>
<html lang="sk">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&amp;family=Outfit:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#0B0B10}}
a{{color:{PINK}}}
</style>
</helmet>
<div style="width: {w}px; height: {h}px; position: relative; overflow: hidden; background: #111118; {F} color: #F4F2FF">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
# ---- illustrative events (names from real data 2026-11-08, times/genres illustrative)
EV=[
 dict(t='party',name='Chinchilla ☆ Jolina Louise',v='Fuchs2',d='Pi 27. 11.',tm='23:00',tags=[('party','party'),('dj','dj'),('techno','genre')]),
 dict(t='concert',name='Gutafest 2026',v='MeetFactory',d='So 28. 11.',tm='19:00',tags=[('concert','concert'),('party','party'),('punk','genre')]),
 dict(t='dj',name='Amphibian Quadrophonic Soundsystem',v='Archa+',d='Pi 20. 11.',tm='21:00',tags=[('dj','dj'),('party','party'),('experimental','genre')]),
 dict(t='party',name='PSYTRANCE UNITED',v='Čitárna Unijazz',d='Pi 20. 11.',tm='20:00',tags=[('dj','dj'),('party','party'),('trance','genre')]),
 dict(t='concert',name='High on Fire ☆ Cancer Void',v='Fuchs2',d='Ut 1. 12.',tm='19:30',tags=[('concert','concert'),('metal','genre')]),
 dict(t='party',name='TECHNO HOUSE',v='Cross Club',d='St 11. 11.',tm='22:00',tags=[('dj','dj'),('party','party'),('techno','genre'),('house','genre')]),
 dict(t='concert',name='Dudlíkfest 2026',v='Bike Jesus',d='St 11. 11.',tm='18:00',tags=[('concert','concert'),('party','party')]),
 dict(t='party',name='SUNDAY RITUALS – REGGAETON & LATINO',v='EPIC',d='Ne 15. 11.',tm='22:00',tags=[('dj','dj'),('party','party'),('latin','genre')]),
]
def card(e,i,w=148):
    return f'''<a href="#" style="width: {w}px; flex: none; text-decoration: none; color: #F4F2FF; display: flex; flex-direction: column; gap: 6px">
{art(e['t'],w,w,16,i)}
<span style="font-size: 12px; font-weight: 600; color: {T[e['t']][0]}">{e['d']} · {e['tm']}</span>
<span style="{B} font-size: 15px; font-weight: 700; line-height: 1.15; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden">{e['name']}</span>
<span style="font-size: 13px; font-weight: 700; color: #F4F2FF; opacity: 0.85">{e['v']}</span>
</a>'''
def row(title,idx,sub=None):
    cards=''.join(card(EV[i],i) for i in idx)
    s=f'<span style="font-size: 13px; color: #8E8AA6; font-weight: 500">{sub}</span>' if sub else ''
    return f'''<section style="display: flex; flex-direction: column; gap: 12px">
<a href="#" style="display: flex; align-items: baseline; gap: 8px; text-decoration: none; color: #F4F2FF; padding: 0 16px"><span style="{B} font-size: 22px; font-weight: 700">{title}</span>{s}<span style="margin-left: auto; color: #B9B6CC; display: flex">{svg(CHEV,18)}</span></a>
<div style="display: flex; gap: 12px; padding: 0 16px; overflow: hidden">{cards}</div>
</section>'''
def period(active='Tento týždeň'):
    items=['Dnes','Tento týždeň','Víkend','Mesiac']
    out=[]
    for it in items:
        st='background: #F4F2FF; color: #111118; font-weight: 600;' if it==active else 'background: #23232F; color: #B9B6CC; font-weight: 500;'
        out.append(f'<button style="height: 40px; padding: 0 14px; border-radius: 20px; border: 0; {st} {F} font-size: 14px; white-space: nowrap; flex: none">{it}</button>')
    out.append(f'<button style="width: 40px; height: 40px; border-radius: 20px; border: 0; background: #23232F; color: #F4F2FF; display: flex; align-items: center; justify-content: center; flex: none" aria-label="Vybrať dni">{svg(CAL,18)}</button>')
    return f'<div style="display: flex; gap: 8px; overflow: hidden">{"".join(out)}</div>'
def header(title,extra=''):
    return f'''<div style="position: absolute; top: 0; left: 0; right: 0; padding: 52px 16px 12px; background: #111118; z-index: 2; display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; align-items: center; gap: 10px">
<h1 style="margin: 0; {B} font-size: 32px; font-weight: 700; letter-spacing: -0.02em">{title}</h1>
<button style="position: relative; margin-left: auto; width: 44px; height: 44px; border-radius: 22px; border: 0; background: {PINK}; color: {PD}; display: flex; align-items: center; justify-content: center" aria-label="Filter">{svg(FILT,20,sw=2.4)}</button>
</div>
{extra}
</div>'''
# ---- 1 Akcie rows
body=header('Akcie',period())+f'''<div style="position: absolute; top: 172px; left: 0; right: 0; display: flex; flex-direction: column; gap: 26px">
{row('Pre vás',[0,4,5],'tvoje podniky a žánre')}
{row('Novo pridané',[1,2,6],'za posledný týždeň')}
{row('Párty',[3,7,0])}
</div>
{nav('Akcie')}'''
open(f'{D}/AkcieRows.dc.html','w').write(page('Akcie – riadky',body))
# ---- 2 Akcie list (after tapping a row / filter)
def lrow(e,i):
    tags=''.join(tag(a,b) for a,b in e['tags'][:3])
    return f'''<a href="#" style="display: flex; gap: 12px; padding: 10px 16px; text-decoration: none; color: #F4F2FF; align-items: center">
{art(e['t'],72,72,14,i)}
<div style="min-width: 0; display: flex; flex-direction: column; gap: 4px; flex: 1">
<span style="font-size: 12px; font-weight: 600; color: {T[e['t']][0]}">{e['tm']}</span>
<span style="{B} font-size: 16px; font-weight: 700; line-height: 1.15; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{e['name']}</span>
<span style="font-size: 14px; font-weight: 700">{e['v']}</span>
<div style="display: flex; gap: 6px; overflow: hidden">{tags}</div>
</div>
</a>'''
def day(label):
    return f'<p style="margin: 0; padding: 14px 16px 4px; font-size: 13px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #8E8AA6">{label}</p>'
active=f'''<div style="display: flex; gap: 8px; align-items: center"><span style="height: 32px; padding: 0 10px 0 14px; border-radius: 16px; background: {T['party'][0]}; color: {T['party'][1]}; font-size: 14px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px">party {svg('<path d="M6 6l12 12M18 6L6 18"></path>',14,sw=2.6)}</span><span style="font-size: 13px; color: #8E8AA6">7 akcií · tento týždeň</span></div>'''
body=header('Akcie',period()+active)+f'''<div style="position: absolute; top: 218px; left: 0; right: 0">
{day('Streda 11. 11.')}{lrow(EV[5],5)}{lrow(EV[6],6)}
{day('Piatok 13. 11.')}{lrow(EV[3],3)}{lrow(EV[2],2)}
{day('Nedeľa 15. 11.')}{lrow(EV[7],7)}
</div>
{nav('Akcie')}'''
open(f'{D}/AkcieList.dc.html','w').write(page('Akcie – zoznam po ťuknutí na riadok',body))
# ---- 3 Akcie chips variant
cats=[('Všetko',None),('Koncerty','concert'),('Párty','party'),('DJ','dj'),('Kultúra','culture')]
cb=[]
for n,(lab,k) in enumerate(cats):
    on=lab=='Párty'
    ic = svg(ICON[k],22,stroke=(T[k][1] if on else T[k][0]),sw=2) if k else svg('<circle cx="7" cy="7" r="3"></circle><circle cx="17" cy="7" r="3"></circle><circle cx="7" cy="17" r="3"></circle><circle cx="17" cy="17" r="3"></circle>',22,stroke='#F4F2FF' if not on else '#111118',sw=2)
    bg = T[k][0] if (on and k) else '#23232F'
    cb.append(f'<a href="#" style="display: flex; flex-direction: column; align-items: center; gap: 6px; text-decoration: none; color: {"#F4F2FF" if on else "#B9B6CC"}; font-size: 12px; font-weight: {700 if on else 500}; flex: none; width: 62px"><span style="width: 52px; height: 52px; border-radius: 18px; background: {bg}; display: flex; align-items: center; justify-content: center">{ic}</span>{lab}</a>')
chips=f'<div style="display: flex; gap: 8px; overflow: hidden">{"".join(cb)}</div>'
body=header('Akcie',period()+chips)+f'''<div style="position: absolute; top: 262px; left: 0; right: 0">
{day('Streda 11. 11.')}{lrow(EV[5],5)}{lrow(EV[6],6)}
{day('Piatok 13. 11.')}{lrow(EV[3],3)}{lrow(EV[2],2)}
{day('Nedeľa 15. 11.')}{lrow(EV[7],7)}
</div>
{nav('Akcie')}'''
open(f'{D}/AkcieChips.dc.html','w').write(page('Akcie – variant lišta kategórií',body))
# ---- 4 Podniky
V=[('Archa+','concert',['culture-center','alternative'],True),('Bike Jesus','dj',['underground','diy'],True),('Cross Club','dj',['underground','late-night'],False),
   ('Čitárna Unijazz','culture',['cozy','community'],False),('EPIC','party',['commercial','tourist'],False),('Forum Karlín','concert',['concert-hall','large'],True),
   ('Fuchs2','dj',['underground','queer-friendly'],True),('Kasárna Karlín','culture',['hangout','open-air'],False)]
def vrow(n,t,tg,fav,i):
    h=svg(HEART,20,stroke=PINK if fav else '#5D5677',fill=PINK if fav else 'none',sw=2)
    return f'''<a href="#" style="display: flex; gap: 12px; padding: 10px 16px; align-items: center; text-decoration: none; color: #F4F2FF">
{art(t,56,56,28,i)}
<div style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 5px"><span style="{B} font-size: 17px; font-weight: 700">{n}</span><div style="display: flex; gap: 6px">{''.join(tag(x,'char') for x in tg)}</div></div>
{h}
</a>'''
seg=f'''<div style="height: 44px; border-radius: 22px; background: #23232F; display: flex">
<button style="flex: 1; height: 44px; border-radius: 22px; border: 0; background: #F4F2FF; color: #111118; {F} font-size: 14px; font-weight: 600">Všetko</button>
<button style="flex: 1; height: 44px; border-radius: 22px; border: 0; background: transparent; color: #B9B6CC; {F} font-size: 14px; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 5px">{svg(HEART,14)}Obľúbené</button></div>'''
search=f'''<label style="height: 52px; border-radius: 26px; background: #F4F2FF; color: #111118; display: flex; align-items: center; gap: 10px; padding: 0 18px; font-size: 16px">{svg(SEARCH,20,sw=2.4)}<span style="color: #6E6A84">Hľadať podnik</span></label>'''
body=f'''<div style="position: absolute; top: 0; left: 0; right: 0; padding: 52px 16px 8px; display: flex; flex-direction: column; gap: 12px; background: #111118; z-index: 2">
<h1 style="margin: 0; {B} font-size: 32px; font-weight: 700; letter-spacing: -0.02em">Podniky</h1>
{search}{seg}</div>
<div style="position: absolute; top: 236px; left: 0; right: 0">{''.join(vrow(*v,i) for i,v in enumerate(V))}</div>
{nav('Podniky')}'''
open(f'{D}/Podniky.dc.html','w').write(page('Podniky',body))
# ---- 5 Profil podniku
prog=[EV[0],EV[4],EV[0]]
prog=[dict(EV[0],d='Pi 27. 11.'),dict(EV[4],d='Ut 1. 12.'),dict(t='dj',name='Wrong 10 Years: Prison Religion, Wick',v='Fuchs2',d='So 5. 12.',tm='23:00',tags=[('party','party'),('dj','dj'),('ebm','genre')])]
def prow(e,i):
    return f'''<a href="#" style="display: flex; gap: 12px; padding: 10px 16px; text-decoration: none; color: #F4F2FF; align-items: center">
<div style="width: 52px; flex: none; text-align: center"><div style="font-size: 12px; color: #8E8AA6; font-weight: 600">{e['d'].split()[0].upper()}</div><div style="{B} font-size: 22px; font-weight: 700">{e['d'].split()[1].rstrip('.')}</div><div style="font-size: 12px; color: #8E8AA6">{e['d'].split()[2].rstrip('.')}.</div></div>
<div style="min-width: 0; flex: 1; display: flex; flex-direction: column; gap: 4px"><span style="{B} font-size: 16px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{e['name']}</span><span style="font-size: 13px; color: {T[e['t']][0]}; font-weight: 600">{e['tm']}</span><div style="display: flex; gap: 6px">{''.join(tag(a,b) for a,b in e['tags'][:3])}</div></div>
{art(e['t'],56,56,12,i+2)}
</a>'''
body=f'''<div style="position: absolute; top: 0; left: 0; right: 0; height: 200px">{art('dj',390,200,0,4)}<div style="position: absolute; inset: 0; background: linear-gradient(180deg, rgba(17,17,24,0) 30%, #111118 100%)"></div></div>
<button style="position: absolute; top: 52px; left: 16px; width: 44px; height: 44px; border-radius: 22px; border: 0; background: rgba(17,17,24,0.7); color: #F4F2FF; display: flex; align-items: center; justify-content: center" aria-label="Späť">{svg(BACK,22,sw=2.4)}</button>
<button style="position: absolute; top: 52px; right: 16px; width: 44px; height: 44px; border-radius: 22px; border: 0; background: {PINK}; color: {PD}; display: flex; align-items: center; justify-content: center" aria-label="Obľúbený">{svg(HEART,20,fill=PD,stroke=PD)}</button>
<div style="position: absolute; top: 150px; left: 16px; right: 16px; display: flex; flex-direction: column; gap: 8px">
<h1 style="margin: 0; {B} font-size: 34px; font-weight: 700; letter-spacing: -0.02em">Fuchs2</h1>
<span style="font-size: 14px; color: #B9B6CC">Štvanice, Praha 7 · 1,2 km</span>
<div style="display: flex; flex-wrap: wrap; gap: 6px">{tag('dance-club','char')}{tag('underground','char')}{tag('queer-friendly','char')}{tag('late-night','char')}</div>
</div>
<div style="position: absolute; top: 282px; left: 0; right: 0">
<p style="margin: 0; padding: 4px 16px 4px; {B} font-size: 22px; font-weight: 700">Program</p>
{''.join(prow(e,i) for i,e in enumerate(prog))}
<a href="#" style="margin: 6px 16px 0; height: 52px; border-radius: 16px; background: #1C1C27; display: flex; align-items: center; padding: 0 16px; color: #F4F2FF; text-decoration: none; font-size: 15px; font-weight: 600">O podniku<span style="margin-left: auto; color: #B9B6CC; display: flex; transform: rotate(90deg)">{svg(CHEV,18)}</span></a>
<div style="margin: 10px 16px 0; display: flex; gap: 8px">
<a href="#" style="flex: 1; height: 44px; border-radius: 22px; background: #23232F; color: #F4F2FF; display: flex; align-items: center; justify-content: center; gap: 6px; text-decoration: none; font-size: 14px; font-weight: 600">Web</a>
<a href="#" style="flex: 1; height: 44px; border-radius: 22px; background: #23232F; color: #F4F2FF; display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 14px; font-weight: 600">Instagram</a>
<a href="#" style="flex: 1; height: 44px; border-radius: 22px; background: #23232F; color: #F4F2FF; display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 14px; font-weight: 600">Na mape</a>
</div>
</div>
{nav('Podniky')}'''
open(f'{D}/Podnik.dc.html','w').write(page('Profil podniku',body))
# ---- 6 Stránka akcie
e=prog[2]
small=lambda ic,lab: f'<a href="#" style="flex: 1; height: 64px; border-radius: 18px; background: #1C1C27; color: #F4F2FF; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; text-decoration: none; font-size: 12px; font-weight: 600">{ic}{lab}</a>'
CHECK='<path d="M5 12l5 5 9-10"></path>'
SHARE='<path d="M12 3v13M7 8l5-5 5 5"></path><path d="M5 14v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5"></path>'
EXP='<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"></path>'
body=f'''<div style="position: absolute; top: 0; left: 0; right: 0; height: 390px">{art('dj',390,390,0,2)}<div style="position: absolute; inset: 0; background: linear-gradient(180deg, rgba(17,17,24,0) 55%, #111118 100%)"></div></div>
<button style="position: absolute; top: 52px; left: 16px; width: 44px; height: 44px; border-radius: 22px; border: 0; background: rgba(17,17,24,0.7); color: #F4F2FF; display: flex; align-items: center; justify-content: center" aria-label="Späť">{svg(BACK,22,sw=2.4)}</button>
<button style="position: absolute; top: 300px; right: 16px; height: 36px; padding: 0 12px; border-radius: 18px; border: 0; background: rgba(17,17,24,0.7); color: #F4F2FF; display: flex; align-items: center; gap: 6px; {F} font-size: 13px; font-weight: 600" aria-label="Zobraziť plagát">{svg(EXP,16)}Plagát</button>
<div style="position: absolute; top: 350px; left: 16px; right: 16px; display: flex; flex-direction: column; gap: 10px">
<h1 style="margin: 0; {B} font-size: 28px; font-weight: 700; line-height: 1.08; letter-spacing: -0.02em">{e['name']}</h1>
<a href="#" style="font-size: 17px; font-weight: 700; color: #F4F2FF; text-decoration: none; display: flex; align-items: center; gap: 4px">Fuchs2 <span style="color: #B9B6CC; display: flex">{svg(CHEV,16)}</span></a>
<span style="font-size: 15px; color: #B9B6CC">Sobota 5. 12. · 23:00 · 350 Kč</span>
<div style="display: flex; flex-wrap: wrap; gap: 6px">{tag('party','party')}{tag('dj','dj')}{tag('ebm','genre')}{tag('post-punk','genre')}{tag('underground','char')}</div>
<a href="#" style="margin-top: 4px; height: 54px; border-radius: 27px; background: {PINK}; color: {PD}; display: flex; align-items: center; justify-content: center; text-decoration: none; font-size: 17px; font-weight: 700">Lístky</a>
<div style="display: flex; gap: 8px">{small(svg(CHECK,20),'Idem')}{small(svg(CAL,20),'Kalendár')}{small(svg(SHARE,20),'Zdieľať')}{small(svg('<rect x="3" y="3" width="18" height="18" rx="5"></rect><circle cx="12" cy="12" r="4"></circle><circle cx="17.5" cy="6.5" r="1"></circle>',20),'IG podniku')}</div>
<p style="margin: 4px 0 0; font-size: 14px; line-height: 1.5; color: #B9B6CC">Popis akcie zo zdroja. Ak chýba, sem pôjde popis dohľadaný AI s označením zdroja…</p>
</div>'''
open(f'{D}/Akcia.dc.html','w').write(page('Stránka akcie',body))
# canvas
c=json.load(open(f'{D}/canvas.json'))
new=[('AkcieRows.dc.html','Akcie – riadky (predvolené)'),('AkcieList.dc.html','Akcie – po ťuknutí na riadok / filter'),('AkcieChips.dc.html','Akcie – variant lišta kategórií'),('Podniky.dc.html','Podniky'),('Podnik.dc.html','Profil podniku'),('Akcia.dc.html','Stránka akcie')]
for i,(f,t) in enumerate(new):
    c['boards'][f]={"h":844,"radius":40,"title":t,"w":390,"x":i*470,"y":2700}
    if f not in c['order']: c['order'].append(f)
json.dump(c,open(f'{D}/canvas.json','w'),ensure_ascii=False,indent=2)
print('ok')
