import json,sys
sys.path.insert(0,'/tmp/claude-0/-home-claude/6a6fdeae-1a3b-5ff8-ad92-4c2929c96cc1/scratchpad/gen')
D='/tmp/claude-0/-home-claude/6a6fdeae-1a3b-5ff8-ad92-4c2929c96cc1/scratchpad/eventapp-design/project'
MIC=open('/tmp/claude-0/-home-claude/6a6fdeae-1a3b-5ff8-ad92-4c2929c96cc1/scratchpad/micicon.txt').read()
PINK,PD='#FF4D8D','#1A0710'
T={'concert':('#8B6CFF','#14063A','#A890FF'),'party':('#FF8A3D','#2A1200','#FFAA70'),'dj':('#2FD4C0','#002B26','#6BE6D6'),'culture':('#C6F432','#1B2600','#DBFF73')}
ICON={'concert':MIC,'party':'<path d="M5 4h14l-7 8z"></path><path d="M12 12v7"></path><path d="M8 20h8"></path><path d="M15 7l3-4"></path>',
'dj':'<rect x="3" y="4" width="18" height="16" rx="3"></rect><circle cx="11" cy="12" r="5"></circle><circle cx="11" cy="12" r="1"></circle><path d="M18 7v6l-3 2"></path>',
'culture':'<path d="M4 5c3 1.5 7 1.5 10 0v6a5 5 0 0 1-10 0z"></path><path d="M10 13c3 1.5 7 1.5 10 0v6a5 5 0 0 1-10 0z"></path>'}
F="font-family: 'Outfit', sans-serif;"; B="font-family: 'Bricolage Grotesque', sans-serif;"
def svg(p,s=20,st='currentColor',sw=2.2,fill='none'): return f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="{fill}" stroke="{st}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'
BLD='<path d="M4 21h16M6 21V10M18 21V10M10 21V10M14 21V10M3 10l9-6 9 6z"></path>'
RIGHT='<path d="M9 6l6 6-6 6"></path>'
LEFT='<path d="M15 6l-6 6 6 6"></path>'
LOCP='<circle cx="12" cy="12" r="4"></circle><path d="M12 2v3M12 19v3M2 12h3M19 12h3"></path>'
HEART='<path d="M19.5 12.6L12 20l-7.5-7.4A5 5 0 1 1 12 6a5 5 0 1 1 7.5 6.6z"></path>'
# map background (variant A palette, richer)
MAP='''<svg width="390" height="844" viewBox="0 0 390 844" style="position: absolute; inset: 0" aria-hidden="true">
<rect width="390" height="844" fill="#1E1E2A"></rect>
<rect x="250" y="100" width="120" height="90" rx="20" fill="#1C2E24"></rect><rect x="20" y="470" width="100" height="80" rx="18" fill="#1C2E24"></rect><rect x="280" y="560" width="90" height="70" rx="16" fill="#1C2E24"></rect>
<g stroke="#34344A" stroke-width="3" fill="none">
<path d="M0 120 L390 100"></path><path d="M0 200 L390 185"></path><path d="M0 410 L390 380"></path><path d="M0 520 L390 500"></path><path d="M0 700 L390 660"></path>
<path d="M40 0 L60 844"></path><path d="M210 0 L230 844"></path><path d="M340 0 L320 844"></path><path d="M90 300 L330 270"></path><path d="M0 600 L200 560"></path>
</g>
<path d="M-20 160 C 80 130, 140 220, 210 260 S 300 340, 260 430 S 160 530, 220 610 S 360 710, 420 770" stroke="#1D3352" stroke-width="34" fill="none" stroke-linecap="round"></path>
<g stroke="#4A4A66" stroke-width="6" fill="none"><path d="M0 330 L390 290"></path><path d="M0 640 L390 580"></path><path d="M120 0 L170 844"></path></g>
<path d="M300 0 L250 844" stroke="#5E5E7E" stroke-width="8"></path>
<g font-family="Outfit, sans-serif" font-size="11" font-weight="600" fill="#B4B0CC" stroke="#111118" stroke-width="3" paint-order="stroke" letter-spacing="1.5">
<text x="250" y="240">HOLEŠOVICE</text><text x="20" y="250">LETNÁ</text><text x="270" y="460">KARLÍN</text><text x="60" y="440">STARÉ MĚSTO</text><text x="250" y="720">ŽIŽKOV</text><text x="40" y="760">NOVÉ MĚSTO</text></g>
<text x="195" y="345" font-family="Outfit, sans-serif" font-size="11" font-style="italic" fill="#6F8BB5" stroke="#111118" stroke-width="3" paint-order="stroke">Vltava</text>
<text x="173" y="292" font-family="Outfit, sans-serif" font-size="10" fill="#8E8AA6" stroke="#111118" stroke-width="3" paint-order="stroke">Štvanice</text>
</svg>'''
def metro(x,y,name):
    return f'<div style="position: absolute; left: {x}px; top: {y}px; display: flex; align-items: center; gap: 4px; font-size: 10px; color: #8E8AA6; font-weight: 500; text-shadow: 0 0 3px #111118"><span style="width: 16px; height: 16px; border-radius: 8px; background: #3A3A50; color: #E4E2EE; font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center">M</span>{name}</div>'
def landmark(x,y,name):
    return f'<div style="position: absolute; left: {x}px; top: {y}px; display: flex; align-items: center; gap: 4px; font-size: 10px; color: #8E8AA6; text-shadow: 0 0 3px #111118"><span style="width: 16px; height: 16px; border-radius: 4px; background: #3A3A50; display: flex; align-items: center; justify-content: center">{svg(BLD,11,"#E4E2EE",2)}</span>{name}</div>'
PINPATH="M25 61 Q23.2 57.6 20.5 54.5 C10 43 3 36 3 25 A22 22 0 1 1 47 25 C47 36 40 43 29.5 54.5 Q26.8 57.6 25 61 Z"
def pin(x,y,t,fav=False,extra=0,live=False,label=None,sel=False,selstyle='outline'):
    c,d,hi=T[t]
    badges=''
    if fav: badges+=f'<span style="position: absolute; top: -2px; right: -4px; width: 20px; height: 20px; border-radius: 10px; background: #F4F2FF; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.4)">{svg(HEART,12,"#111118",2,"#111118")}</span>'
    if extra: badges+=f'<span style="position: absolute; top: -2px; left: -6px; height: 20px; min-width: 20px; padding: 0 5px; box-sizing: border-box; border-radius: 10px; background: #111118; color: #F4F2FF; border: 1.5px solid #F4F2FF; font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center">+{extra}</span>'
    ring=f'<span class="pinlive" style="position: absolute; left: 3px; top: 3px; width: 44px; height: 44px; border-radius: 22px; --c: {c}"></span>' if live else ''
    lab=f'<span style="position: absolute; left: 50%; top: {74 if sel and selstyle=="dot" else 66}px; transform: translateX(-50%); white-space: nowrap; font-size: {13 if sel else 12}px; font-weight: {800 if sel else 600}; color: {"#FFFFFF" if sel else "#E4E2EE"}; text-shadow: 0 0 3px #111118, 0 0 3px #111118, 0 1px 2px #111118; letter-spacing: 0.01em">{label}</span>' if label else ''
    sc='transform: scale(1.22); transform-origin: 50% 100%; z-index: 4;' if sel else ''
    outline=''
    if sel and selstyle=='outline': outline=f'<svg width="50" height="64" viewBox="0 0 50 64" style="position: absolute; inset: 0; overflow: visible" aria-hidden="true"><path d="{PINPATH}" fill="none" stroke="#FFFFFF" stroke-width="5"></path></svg>'
    if sel and selstyle=='glow': outline=f'<span style="position: absolute; left: -8px; top: -8px; width: 66px; height: 66px; border-radius: 33px; background: radial-gradient(circle, {c}88 0%, {c}33 45%, transparent 70%)"></span>'
    if sel and selstyle=='dot': outline=''
    dot=f'<span style="position: absolute; left: 50%; top: 61px; width: 10px; height: 10px; margin-left: -5px; border-radius: 5px; background: {c}; box-shadow: 0 0 0 3px #111118, 0 0 10px {c}"></span>' if (sel and selstyle=='dot') else ''
    return f'''<div style="position: absolute; left: {x-25}px; top: {y-61}px; width: 50px; height: 64px; {sc}"><div style="position: absolute; inset: 0; filter: drop-shadow(0 8px 6px rgba(0,0,0,0.55)) drop-shadow(0 2px 2px rgba(0,0,0,0.35))">{outline}
{ring}
<svg width="50" height="64" viewBox="0 0 50 64" style="position: absolute; inset: 0" aria-hidden="true"><path d="{PINPATH}" fill="{c}"></path></svg>
<span style="position: absolute; left: 7px; top: 7px; width: 36px; height: 36px; border-radius: 18px; background: {d}; display: flex; align-items: center; justify-content: center">{svg(ICON[t],22,c,2)}</span>
{badges}
</div>{dot}{lab}
</div>'''
def selpin(x,y,t,name,fav=False):
    c,d,hi=T[t]
    h=f'{svg(HEART,14,d,2,d)}' if fav else ''
    return f'''<div style="position: absolute; left: {x}px; top: {y-66}px; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; filter: drop-shadow(0 8px 6px rgba(0,0,0,0.55)) drop-shadow(0 2px 2px rgba(0,0,0,0.35)); z-index: 4">
<div style="display: flex; align-items: center; gap: 8px; height: 48px; padding: 0 16px 0 6px; border-radius: 24px; background: {c}; color: {d}; font-size: 16px; font-weight: 700; white-space: nowrap">
<span style="width: 36px; height: 36px; border-radius: 18px; background: {d}; display: flex; align-items: center; justify-content: center">{svg(ICON[t],22,c,2)}</span>{name}{h}</div>
<svg width="22" height="18" viewBox="0 0 22 18" style="margin-top: -1px" aria-hidden="true"><path d="M0 0 H22 L11 18 Z" fill="{c}"></path></svg>
</div>'''
CSS='''@keyframes pinpulse{0%{box-shadow:0 0 0 0 var(--c);opacity:.9}100%{box-shadow:0 0 0 16px transparent;opacity:0}}
.pinlive{animation:pinpulse 1.6s ease-out infinite}
@media (prefers-reduced-motion: reduce){.pinlive{animation:none;box-shadow:0 0 0 6px var(--c);opacity:.5}}'''
def topbar():
    return f'''<div style="position: absolute; top: 56px; left: 16px; right: 16px; display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 8px; z-index: 5">
<button style="height: 44px; padding: 0 14px; border-radius: 22px; border: 0; background: #F4F2FF; color: #111118; {F} font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 6px">Dnes{svg('<path d="M6 9l6 6 6-6"></path>',16,sw=2.4)}</button>
<div style="height: 44px; border-radius: 22px; background: #23232F; display: flex"><button style="flex: 1; height: 44px; border-radius: 22px; border: 0; background: #F4F2FF; color: #111118; {F} font-size: 14px; font-weight: 600">Všetko</button><button style="flex: 1; height: 44px; border-radius: 22px; border: 0; background: transparent; color: #B9B6CC; {F} font-size: 14px; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 5px">{svg(HEART,14)}Obľúbené</button></div>
<button style="width: 44px; height: 44px; border-radius: 22px; border: 0; background: {PINK}; color: {PD}; display: flex; align-items: center; justify-content: center" aria-label="Filter">{svg('<path d="M4 7h10M18 7h2M4 17h4M12 17h8"></path><circle cx="16" cy="7" r="2"></circle><circle cx="10" cy="17" r="2"></circle>',20,sw=2.4)}</button></div>'''
NAV=f'''<nav style="position: absolute; left: 16px; right: 16px; bottom: 28px; height: 72px; border-radius: 36px; background: #1C1C27; display: flex; align-items: center; justify-content: space-between; padding: 0 10px; z-index: 5">
<a href="#" style="height: 52px; padding: 0 20px; border-radius: 26px; background: {PINK}; color: {PD}; display: flex; align-items: center; gap: 8px; text-decoration: none; font-size: 15px; font-weight: 600">{svg('<path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z"></path><path d="M9 4v14M15 6v14"></path>')}Mapa</a>
''' + ''.join(f'<a href="#" style="width: 52px; height: 52px; border-radius: 26px; color: #B9B6CC; display: flex; align-items: center; justify-content: center">{svg(p,22,sw=2.1)}</a>' for p in ['<path d="M8 6h12M8 12h12M8 18h12"></path><circle cx="4" cy="6" r="1"></circle><circle cx="4" cy="12" r="1"></circle><circle cx="4" cy="18" r="1"></circle>','<path d="M4 21V9l8-5 8 5v12"></path><path d="M9 21v-6h6v6"></path>','<circle cx="12" cy="8" r="4"></circle><path d="M4 21a8 8 0 0 1 16 0"></path>'])+'</nav>'
LOC=f'<button style="position: absolute; right: 16px; bottom: 132px; width: 52px; height: 52px; border-radius: 26px; border: 0; background: #F4F2FF; color: #111118; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.4)">{svg(LOCP,22)}</button>'
INFO='<span style="position: absolute; left: 16px; bottom: 112px; width: 22px; height: 22px; border-radius: 11px; background: rgba(35,35,47,0.85); color: #B9B6CC; font-size: 12px; font-weight: 700; display: flex; align-items: center; justify-content: center">i</span>'
def page(title,body):
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
{CSS}
</style>
</helmet>
<div style="width: 390px; height: 844px; position: relative; overflow: hidden; background: #111118; {F} color: #F4F2FF">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":390,"height":844}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
POIS=metro(150,214,'Vltavská')+metro(300,520,'Křižíkova')+metro(70,560,'Můstek')+landmark(95,640,'Národní divadlo')
# 1: pins overview
body=MAP+POIS+pin(110,190,'party',fav=True)+pin(190,300,'party',live=True)+pin(214,318,'concert')+pin(70,480,'culture',extra=1)+pin(225,590,'concert',fav=True)+pin(330,420,'dj')+topbar()+INFO+LOC+NAV
PINSMAP_OLD=None
open(f'{D}/PinsMap.dc.html','w').write(page('Mapa – piny',body))
# 2: selected + card
def tag(label,k):
    st=f'background: {T[k][0]}; color: {T[k][1]};' if k in T else 'background: #2A2838; color: #E4DEFF;'
    return f'<span style="height: 32px; padding: 0 14px; border-radius: 16px; {st} font-size: 14px; font-weight: 600; display: inline-flex; align-items: center; white-space: nowrap; flex: none">{label}</span>'
arrow=lambda d,pos: f'<button style="position: absolute; {pos}; bottom: 330px; width: 36px; height: 36px; border-radius: 18px; border: 0; background: #F4F2FF; color: #111118; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.45); z-index: 6" aria-label="{"Ďalšie miesto" if d=="r" else "Predošlé miesto"}">{svg(RIGHT if d=="r" else LEFT,18,sw=2.8)}</button>'
card=f'''<section style="position: absolute; left: 12px; right: 12px; bottom: 112px; border-radius: 28px; background: #1C1C27; padding: 16px; box-sizing: border-box; border: 1px solid #2E2D3C; z-index: 6">
<a href="#" style="display: flex; gap: 14px; text-decoration: none; color: #F4F2FF">
<div style="width: 88px; height: 88px; border-radius: 18px; background: #FF8A3D; flex: none; position: relative; overflow: hidden"><svg width="88" height="88" viewBox="0 0 88 88" style="position: absolute; inset: 0"><circle cx="30" cy="34" r="22" fill="#8B6CFF"></circle><circle cx="58" cy="56" r="26" fill="#C6F432" opacity="0.85"></circle><path d="M12 76 L76 12" stroke="#2A1200" stroke-width="6"></path></svg></div>
<div style="min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: 6px"><p style="margin: 0; {B} font-size: 21px; font-weight: 700; line-height: 1.1">Wrong 10 Years: Prison Religion, Wick</p><p style="margin: 0; font-size: 14px; color: #B9B6CC">Fuchs2 · 23:00 · 1,2 km</p></div></a>
<div style="position: relative; margin-top: 14px; overflow: hidden; -webkit-mask-image: linear-gradient(90deg, #000 80%, transparent); mask-image: linear-gradient(90deg, #000 80%, transparent)"><div style="display: flex; gap: 8px">{tag('party','party')}{tag('dj','dj')}{tag('ebm','g')}{tag('post-punk','g')}{tag('industrial','g')}{tag('techno','g')}</div></div>
<div style="display: flex; justify-content: center; gap: 6px; margin-top: 12px"><span style="width: 6px; height: 6px; border-radius: 3px; background: #F4F2FF"></span><span style="width: 6px; height: 6px; border-radius: 3px; background: #5D5677"></span></div>
</section>'''
body=MAP+POIS+pin(110,190,'party',fav=True)+pin(214,318,'concert')+pin(70,480,'culture',extra=1)+pin(225,590,'concert',fav=True)+pin(330,420,'dj')+selpin(190,300,'party','Fuchs2')+topbar()+arrow('l','left: 16px')+arrow('r','right: 16px')+card+NAV
open(f'{D}/PinsSelected.dc.html','w').write(page('Mapa – vybraný pin a karta',body))
c=json.load(open(f'{D}/canvas.json'))
for i,(f,t) in enumerate([('PinsMap.dc.html','Mapa – piny (návrh 2)'),('PinsSelected.dc.html','Mapa – vybraný pin, karta so šípkami (návrh 2)')]):
    c['boards'][f]={"h":844,"radius":40,"title":t,"w":390,"x":i*470,"y":3700}
    if f not in c['order']: c['order'].append(f)
json.dump(c,open(f'{D}/canvas.json','w'),ensure_ascii=False,indent=2)

FITP='<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"></path><circle cx="12" cy="12" r="2"></circle>'
FIT=f'<button style="position: absolute; right: 20px; bottom: 196px; width: 44px; height: 44px; border-radius: 22px; border: 0; background: #F4F2FF; color: #111118; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.4)" aria-label="Celá mapa">{svg(FITP,20)}</button>'
body=MAP+POIS+pin(110,190,'party',fav=True,label='Cross Club')+pin(190,300,'party',live=True,label='Fuchs2')+pin(214,318,'concert',label='Bike Jesus')+pin(70,480,'culture',extra=1,label='Archa+')+pin(225,590,'concert',fav=True,label='Palác Akropolis')+pin(330,420,'dj',label='Roxy')+topbar()+INFO+FIT+LOC+NAV
open(f'{D}/PinsLabels.dc.html','w').write(page('Mapa – piny s menami',body))
body=MAP+POIS+pin(110,190,'party',fav=True,label='Cross Club')+pin(214,318,'concert',label='Bike Jesus')+pin(70,480,'culture',extra=1,label='Archa+')+pin(225,590,'concert',fav=True,label='Palác Akropolis')+pin(330,420,'dj',label='Roxy')+pin(190,300,'party',label='Fuchs2',sel=True,selstyle='glow')+topbar()+arrow('l','left: 16px')+arrow('r','right: 16px')+card+NAV
open(f'{D}/PinsLabelsSelected.dc.html','w').write(page('Mapa – piny s menami, vybraný',body))
c=json.load(open(f'{D}/canvas.json'))
for i,(f,t) in enumerate([('PinsLabels.dc.html','Mapa – piny s menami (návrh 3)'),('PinsLabelsSelected.dc.html','Mapa – vybraný pin bez pilulky (návrh 3)')]):
    c['boards'][f]={"h":844,"radius":40,"title":t,"w":390,"x":(i+2)*470,"y":3700}
    if f not in c['order']: c['order'].append(f)
json.dump(c,open(f'{D}/canvas.json','w'),ensure_ascii=False,indent=2)

def mini(selstyle,title):
    inner=MAP+pin(110,190,'party',fav=True,label='Cross Club')+pin(214,318,'concert',label='Bike Jesus')+pin(70,480,'culture',extra=1,label='Archa+')+pin(330,420,'dj',label='Roxy')+pin(190,300,'party',label='Fuchs2',sel=True,selstyle=selstyle)
    return f'<div style="display: flex; flex-direction: column; gap: 12px"><p style="margin: 0; {B} font-size: 22px; font-weight: 700">{title}</p><div style="position: relative; width: 390px; height: 560px; overflow: hidden; border-radius: 28px; background: #111118">{inner}</div></div>'
COMPASS=f'<button style="position: absolute; right: 16px; top: 116px; width: 44px; height: 44px; border-radius: 22px; border: 0; background: #F4F2FF; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.4)" aria-label="Otočiť na sever"><svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true" style="transform: rotate(-24deg)"><path d="M12 2l4 10h-8z" fill="#FF4D8D"></path><path d="M12 22l-4-10h8z" fill="#5D5677"></path><circle cx="12" cy="12" r="1.6" fill="#111118"></circle></svg></button>'
board=f'''<div style="width: 1340px; height: 680px; box-sizing: border-box; padding: 40px; background: #0F0F15; {F} color: #F4F2FF; display: grid; grid-template-columns: repeat(3, 390px); gap: 35px">{mini('glow','A · žiara vo farbe typu + bodka')}{mini('dot','B · len zväčšenie + bodka na mieste')}{mini('outline','C · biely obrys (predošlý)')}</div>'''
html=page('Vybraný pin – varianty',board).replace('<div style="width: 390px; height: 844px; position: relative; overflow: hidden; background: #111118; font-family: \'Outfit\', sans-serif; color: #F4F2FF">','<div>').replace('"$preview":{"width":390,"height":844}','"$preview":{"width":1340,"height":680}')
open(f'{D}/PinSelVariants.dc.html','w').write(html)
body=MAP+POIS+pin(110,190,'party',fav=True,label='Cross Club')+pin(214,318,'concert',label='Bike Jesus')+pin(70,480,'culture',extra=1,label='Archa+')+pin(225,590,'concert',fav=True,label='Palác Akropolis')+pin(330,420,'dj',label='Roxy')+pin(190,300,'party',live=True,label='Fuchs2')+topbar()+COMPASS+INFO+LOC+NAV
open(f'{D}/PinsLabels.dc.html','w').write(page('Mapa – piny s menami',body))
c=json.load(open(f'{D}/canvas.json'))
c['boards']['PinSelVariants.dc.html']={"h":680,"title":"Vybraný pin – varianty","w":1340,"x":1880,"y":3700}
if 'PinSelVariants.dc.html' not in c['order']: c['order'].append('PinSelVariants.dc.html')
json.dump(c,open(f'{D}/canvas.json','w'),ensure_ascii=False,indent=2)

# ---- edge indicators
def peek(x,y,t,side,rot=0):
    # pin partially outside screen: place pin so that ~45% visible
    c,d,hi=T[t]
    return f'<div style="position: absolute; left: {x-25}px; top: {y-32}px; width: 50px; height: 64px; transform: rotate({rot}deg); opacity: 0.92">{"" }<svg width="50" height="64" viewBox="0 0 50 64" style="position: absolute; inset: 0" aria-hidden="true"><path d="{PINPATH}" fill="{c}"></path></svg><span style="position: absolute; left: 7px; top: 7px; width: 36px; height: 36px; border-radius: 18px; background: {d}; display: flex; align-items: center; justify-content: center">{svg(ICON[t],22,c,2)}</span></div>'
def chip(x,y,arrow,n,pos=''):
    return f'<button style="position: absolute; {pos} height: 29px; padding: 0 9px; border-radius: 15px; border: 1px solid #3A3A50; background: rgba(28,28,39,0.92); color: #F4F2FF; {F} font-size: 12px; font-weight: 700; display: flex; align-items: center; gap: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.45)">{arrow}{n}</button>'
CH=lambda p: svg(p,14,sw=2.8)
L_='<path d="M15 6l-6 6 6 6"></path>'; R_='<path d="M9 6l6 6-6 6"></path>'; U_='<path d="M6 15l6-6 6 6"></path>'; D_='<path d="M6 9l6 6 6-6"></path>'
base=MAP+POIS+pin(170,330,'party',label='Fuchs2')+pin(214,348,'concert',label='Bike Jesus')+pin(110,460,'culture',label='Archa+')
# A: peeking pins along edges (clip by container overflow)
bodyA=base+peek(-6,250,'dj','left',90)+peek(-6,560,'concert','left',90)+peek(396,300,'party','right',-90)+peek(396,380,'concert','right',-90)+peek(396,620,'culture','right',-90)+peek(300,686,'party','bottom',180)+topbar()+INFO+LOC+NAV
open(f'{D}/EdgePeek.dc.html','w').write(page('Mapa – vykukujúce piny na okraji',bodyA))
bodyB=base+chip(0,0,CH(L_),'2','left: 8px; top: 250px;')+chip(0,0,CH(R_),'3','right: 8px; top: 470px;')+chip(0,0,CH(U_),'1','left: 250px; top: 112px;')+chip(0,0,CH(D_),'1','left: 120px; bottom: 116px;')+topbar()+INFO+LOC+NAV
open(f'{D}/EdgeChips.dc.html','w').write(page('Mapa – odznaky s počtom na okraji',bodyB))
c=json.load(open(f'{D}/canvas.json'))
for i,(f,t) in enumerate([('EdgePeek.dc.html','Akcie mimo obrazovky – A vykukujúce piny'),('EdgeChips.dc.html','Akcie mimo obrazovky – B odznaky s počtom')]):
    c['boards'][f]={"h":844,"radius":40,"title":t,"w":390,"x":i*470,"y":4700}
    if f not in c['order']: c['order'].append(f)
json.dump(c,open(f'{D}/canvas.json','w'),ensure_ascii=False,indent=2)
