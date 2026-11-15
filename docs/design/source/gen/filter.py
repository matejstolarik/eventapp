import json,sys
exec(open('pins.py').read().split("# ---- edge indicators")[0].split("PINSMAP_OLD=None")[0])
def badge(n,on,dark=None):
    if n is None: return ''
    st=f'background: {dark}; color: #F4F2FF;' if on and dark else ('background: #111118; color: #F4F2FF;' if on else 'background: #3A3A50; color: #E4E2EE;')
    return f'<span style="min-width: 18px; height: 18px; padding: 0 5px; box-sizing: border-box; border-radius: 9px; {st} font-size: 11px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; margin-left: 2px">{n}</span>'
def tchip(t,label,on,n=None):
    c,d,hi=T[t]
    if on: st=f'background: {c}; color: {d}; border: 1.5px solid {c};'; ic=svg(ICON[t],18,d,2)
    else: st=f'background: transparent; color: #F4F2FF; border: 1.5px solid {c};'; ic=svg(ICON[t],18,c,2)
    op='opacity: 0.45;' if n==0 else ''
    return f'<button style="height: 40px; padding: 0 10px 0 10px; border-radius: 20px; {st} {op} {F} font-size: 14px; font-weight: 600; display: inline-flex; align-items: center; gap: 7px">{ic}{label}{badge(n,on,d)}</button>'
def nchip(label,on,n=None):
    st='background: #F4F2FF; color: #111118; border: 1.5px solid #F4F2FF; font-weight: 700;' if on else 'background: #2A2838; color: #E4DEFF; border: 1.5px solid #2A2838; font-weight: 500;'
    op='opacity: 0.45;' if n==0 else ''
    return f'<button style="height: 34px; padding: 0 9px 0 13px; border-radius: 17px; {st} {op} {F} font-size: 13px; display: inline-flex; align-items: center; gap: 6px">{label}{badge(n,on)}</button>'
def sec(title,inner,more=''):
    m=f'<span style="margin-left: auto; font-size: 13px; color: #B9B6CC; font-weight: 500">{more}</span>' if more else ''
    return f'<div style="display: flex; flex-direction: column; gap: 10px"><div style="display: flex; align-items: baseline"><p style="margin: 0; font-size: 13px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #8E8AA6">{title}</p>{m}</div><div style="display: flex; flex-wrap: wrap; gap: 8px">{inner}</div></div>'
size=f'''<div style="height: 40px; border-radius: 20px; background: #23232F; display: flex; width: 100%">{''.join(f'<button style="flex: 1; height: 40px; border-radius: 20px; border: 0; {"background: #F4F2FF; color: #111118; font-weight: 700;" if on else "background: transparent; color: #B9B6CC; font-weight: 500;"} {F} font-size: 14px">{l}</button>' for l,on in [('Malé',True),('Stredné',False),('Veľké',False)])}</div>'''
genres=['techno','house','drum-and-bass','post-punk','indie','rock','metal','jazz','hip-hop','experimental','ebm','latin']
sheet=f'''<div style="position: absolute; inset: 0; background: rgba(8,8,12,0.6)"></div>
<section style="position: absolute; left: 0; right: 0; bottom: 0; height: 730px; border-radius: 28px 28px 0 0; background: #1C1C27; border-top: 1px solid #2E2D3C; box-sizing: border-box; padding: 10px 16px 0; display: flex; flex-direction: column; z-index: 10">
<span style="align-self: center; width: 40px; height: 5px; border-radius: 3px; background: #3A3A50"></span>
<div style="display: flex; align-items: center; margin: 14px 0 18px"><h2 style="margin: 0; {B} font-size: 26px; font-weight: 700">Filter</h2><button style="margin-left: auto; border: 0; background: transparent; color: #B9B6CC; {F} font-size: 14px; font-weight: 600; text-decoration: underline; text-underline-offset: 3px">Zrušiť všetko</button></div>
<div style="display: flex; flex-direction: column; gap: 22px; overflow: hidden; flex: 1">
{sec('Typ akcie',tchip('concert','Koncert',False,5)+tchip('party','Párty',True,3)+tchip('dj','DJ',True,4)+tchip('culture','Kultúra',False,0))}
{sec('Žáner',''.join(nchip(g,g in ('techno','ebm','post-punk'),n) for g,n in zip(genres,[3,2,1,1,0,0,0,0,0,1,1,0])),'Všetky (30) ›')}
{sec('Charakter miesta',''.join(nchip(g,g=='underground',n) for g,n in zip(['underground','alternative','commercial','queer-friendly','late-night','cozy','community','english-friendly'],[3,4,1,2,3,0,1,0])))}
{sec('Veľkosť miesta',size)}
</div>
<div style="padding: 14px 0 34px; background: #1C1C27"><button style="width: 100%; height: 54px; border-radius: 27px; border: 0; background: {PINK}; color: {PD}; {F} font-size: 17px; font-weight: 700">Zobraziť 12 akcií</button></div>
</section>'''
body=MAP+pin(110,190,'party',label='Cross Club')+pin(190,300,'party',label='Fuchs2')+topbar()+sheet
open(f'{D}/FilterSheet.dc.html','w').write(page('Filter – panel',body))
c=json.load(open(f'{D}/canvas.json'))
c['boards']['FilterSheet.dc.html']={"h":844,"radius":40,"title":"Filter – panel (návrh)","w":390,"x":940,"y":4700}
if 'FilterSheet.dc.html' not in c['order']: c['order'].append('FilterSheet.dc.html')
json.dump(c,open(f'{D}/canvas.json','w'),ensure_ascii=False,indent=2)
