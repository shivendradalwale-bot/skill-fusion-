from pathlib import Path
import re

root = Path('/home/ubuntu/upload')
html_path = root / 'index(7).html'
html = html_path.read_text(encoding='utf-8')

style_match = re.search(r'<style>(.*?)</style>', html, flags=re.S | re.I)
if not style_match:
    raise SystemExit('Expected embedded style block was not found')
css = style_match.group(1).strip() + '\n'
(root / 'styles.css').write_text(css, encoding='utf-8')
html = html[:style_match.start()] + '<link rel="stylesheet" href="styles.css">' + html[style_match.end():]

# Extract executable inline scripts only. Keep JSON-LD in the document and retain external CDN scripts.
script_pattern = re.compile(r'<script(?!\s+type=["\']application/ld\+json["\'])((?:\s+[^>]*)?)>(.*?)</script>', flags=re.S | re.I)
blocks = []

def replace_script(match):
    attrs = match.group(1) or ''
    body = match.group(2)
    if re.search(r'\bsrc\s*=', attrs, flags=re.I):
        return match.group(0)
    if not body.strip():
        return match.group(0)
    blocks.append(body.strip())
    return ''

html = script_pattern.sub(replace_script, html)
if len(blocks) != 5:
    raise SystemExit(f'Expected 5 inline executable script blocks, found {len(blocks)}')

js = '\n\n'.join(blocks) + '\n'
(root / 'script.js').write_text(js, encoding='utf-8')
html = html.replace('</body>', '<script src="script.js" defer></script>\n</body>')
html_path.write_text(html, encoding='utf-8')
print(f'Extracted {len(css)} CSS characters to styles.css')
print(f'Extracted {len(js)} JavaScript characters to script.js')
print('Updated index(7).html with external stylesheet and deferred script references')
