// Task 065 part 4: fail when web/src contains mojibake.  61aa01c re-wrote
// EventPanel.tsx with its UTF-8 text decoded as Windows-1252 and saved again
// as UTF-8 ('·' -> 'Â·', 'á' -> 'Ã¡', 'ť' -> 'Å¥').  The broken sequences are
// UTF-8 lead bytes shown as Latin-1 / Windows-1252 characters.
// Run by `npm test` (before vitest).  `node scripts/check-encoding.mjs --self-test`
// checks the pattern only.
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const SRC = join(dirname(fileURLToPath(import.meta.url)), '..', 'src')
const EXT = /\.(ts|tsx|css|json|html|svg)$/
const BROKEN = /Â[ -¿]|Ã[\u0080-¿Œ-™]|â€|Å[ -¿Œ-™]|Ä[\u008c-\u009b -¿Œ-™]/

function selfTest() {
  const bad = [' Â· ', 'VybranÃ¡', 'OtvoriÅ¥', 'Å tÃ­tky', 'â€ž', 'ÄŤ']
  const good = ['Vybraná · Otvoriť · Štítky · Čtení · Zdarma 350 Kč – „x“ ’ …', 'Å', 'Ãx']
  const wrong = [...bad.filter(s => !BROKEN.test(s)), ...good.filter(s => BROKEN.test(s))]
  if (wrong.length) {
    console.error('check-encoding: pattern self-test failed for', wrong)
    process.exit(1)
  }
}

function files(dir) {
  return readdirSync(dir).flatMap(name => {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) return files(p)
    return EXT.test(name) ? [p] : []
  })
}

selfTest()
if (!process.argv.includes('--self-test')) {
  const hits = []
  for (const f of files(SRC)) {
    readFileSync(f, 'utf8').split('\n').forEach((line, i) => {
      if (BROKEN.test(line)) hits.push(`${relative(SRC, f)}:${i + 1}: ${line.trim().slice(0, 80)}`)
    })
  }
  if (hits.length) {
    console.error('check-encoding: mojibake (UTF-8 read as Windows-1252) in web/src:\n' + hits.join('\n'))
    process.exit(1)
  }
  console.log('check-encoding: web/src ok')
}
