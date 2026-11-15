import sys, asyncio
from playwright.async_api import async_playwright
F='/tmp/fonts/node_modules/@fontsource'
css=''
for fam,d,ws in [('Outfit','outfit',[400,500,600,700]),('Bricolage Grotesque','bricolage-grotesque',[500,700])]:
    for w in ws:
        for sub in ['latin','latin-ext']:
            css+=f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(file://{F}/{d}/files/{d}-{sub}-{w}-normal.woff2)}}\n"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--allow-file-access-from-files'])
        pg=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=2)
        for n in sys.argv[1:]:
            await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort())
            await pg.goto(f'file:///home/claude/eventapp/docs/design/html/{n}.html')
            await pg.add_style_tag(content=css)
            await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'/home/claude/eventapp/docs/design/screens/{n}.png')
        await b.close()
asyncio.run(main())
