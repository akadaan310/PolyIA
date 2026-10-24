import fontkit from '@pdf-lib/fontkit';
import { readFileSync } from 'node:fs';
const chars = process.argv[2];
for (const f of ['DejaVuSansMono', 'DejaVuSans', 'DejaVuSerif']) {
  const font = fontkit.create(readFileSync(`public/fonts/pdf/${f}.ttf`));
  const missing = [...new Set(chars)].filter((c) => !font.hasGlyphForCodePoint(c.codePointAt(0)));
  console.log(f, 'missing:', JSON.stringify(missing.join('')));
}
