import json,sys,collections
d=json.load(open(sys.argv[1]+'/events.json',encoding='utf-8')); st=json.load(open(sys.argv[1]+'/state.json',encoding='utf-8'))
print('generated',d['generated_at'],'events',len(d['events']))
NEW=['lucerna-music-bar','o2-arena','o2-universum','jazz-republic']
for vid in NEW:
    es=[e for e in d['events'] if e['venue_id']==vid]
    f=lambda k: sum(1 for e in es if e.get(k))
    print(vid,len(es),'start',f('start_time'),'doors',f('doors_time'),'any_time',sum(1 for e in es if e.get('start_time') or e.get('doors_time')),
          'price',sum(1 for e in es if e.get('price')),'price_src',sum(1 for e in es if e.get('price_text') and 'price_text' not in (e.get('enrichment') or {})),
          'image_url',f('image_url'),'thumb',f('image_thumb'),'sold_out',sum(1 for e in es if e.get('sold_out')),
          'ai',sum(1 for e in es if (e.get('enrichment') or {}).get('run')))
for v in d['venues']:
    if v['id'] in NEW: print(v['id'],'image_card',v.get('image_card'))
enr_today=[e for e in d['events'] if ((e.get('enrichment') or {}).get('run') or {}).get('checked_at')=='2026-11-21']
print('AI enriched in this run (checked_at 2026-11-21):',len(enr_today),'rechecked',sum(1 for e in enr_today if e['enrichment']['run'].get('rechecked_from')))
print('events in window w/o AI run:',sum(1 for e in d['events'] if not (e.get('enrichment') or {}).get('run') and e.get('status')!='cancelled'))
print('ai_cost',st.get('ai_cost'))
print('adapter_detail', {k:len(v) for k,v in (st.get('adapter_detail') or {}).items()})
