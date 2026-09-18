from pathlib import Path
import re

src = Path('/home/ubuntu/skillfusion-github-package/index.html').read_text(encoding='utf-8')
out = Path('/home/ubuntu/upload')

style = re.search(r'<style>(.*?)</style>', src, re.S | re.I)
if not style:
    raise SystemExit('style block not found')
css = style.group(1).strip() + '\n'
html = src[:style.start()] + '<link rel="stylesheet" href="styles.css">' + src[style.end():]

# Mask HTML comments so script examples in documentation comments cannot match.
def mask_comment(m):
    return ''.join('\n' if c == '\n' else ' ' for c in m.group(0))
masked = re.sub(r'<!--.*?-->', mask_comment, html, flags=re.S)
pattern = re.compile(r'<script(?P<attrs>(?:\s+[^>]*)?)>(?P<body>.*?)</script>', re.S | re.I)
replacements = []
blocks = []
for m in pattern.finditer(masked):
    original = html[m.start():m.end()]
    attrs = m.group('attrs') or ''
    body = m.group('body')
    if re.search(r'\bsrc\s*=', attrs, re.I) or re.search(r'\btype\s*=\s*["\']application/ld\+json["\']', attrs, re.I):
        continue
    if body.strip():
        blocks.append(body.strip())
        replacements.append((m.start(), m.end(), ''))

if len(blocks) != 3:
    raise SystemExit(f'expected 3 live inline executable blocks, found {len(blocks)}')
for start, end, replacement in reversed(replacements):
    html = html[:start] + replacement + html[end:]
html = html.replace('</body>', '<script src="script.js" defer></script>\n</body>')
(out / 'index(7).html').write_text(html, encoding='utf-8')
(out / 'styles.css').write_text(css, encoding='utf-8')
(out / 'script.js').write_text('\n\n'.join(blocks) + '\n', encoding='utf-8')
print('safe split complete:', len(blocks), 'inline blocks; css/js written')
