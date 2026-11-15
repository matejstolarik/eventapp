const {chromium}=require('playwright');const fs=require('fs');
const src=process.argv[2], out=process.argv[3];
const boards=[['FilterSheet','09-filter']];
(async()=>{const b=await chromium.launch();
for(const [f,n] of boards){let s=fs.readFileSync(src+'/'+f+'.dc.html','utf8');
const p=await b.newPage({viewport:{width:390,height:844},deviceScaleFactor:2});
const helm=s.match(/<helmet>([\s\S]*?)<\/helmet>/)[1];const body=s.match(/<\/helmet>([\s\S]*?)<\/x-dc>/)[1];
const page='<!doctype html><html lang="sk"><head><meta charset="utf-8"><title>'+n+'</title>'+helm+'</head><body>'+body+'</body></html>';
fs.writeFileSync(out+'/html/'+n+'.html',page);
await p.setContent(page);await p.waitForTimeout(900);await p.screenshot({path:out+'/screens/'+n+'.png'});await p.close();}
await b.close()})();
