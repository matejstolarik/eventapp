const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844}});
for(const f of process.argv.slice(3)){let s=fs.readFileSync(process.argv[2]+'/'+f+'.dc.html','utf8');
const helm=s.match(/<helmet>([\s\S]*?)<\/helmet>/)[1];const body=s.match(/<\/helmet>([\s\S]*?)<\/x-dc>/)[1];
await p.setContent('<html><head>'+helm+'</head><body>'+body+'</body></html>');await p.waitForTimeout(700);
await p.screenshot({path:'s_'+f+'.png'});}
await b.close()})();
