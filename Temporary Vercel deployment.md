# SkillFusion multi-file deployment

## Project structure

```text
index.html       # Page markup and JSON-LD
styles.css       # Existing site CSS extracted without redesign
script.js        # Existing site JavaScript, Three.js scene code, GSAP, and particle logic
vercel.json      # Vercel security response headers
DEPLOYMENT.md    # Deployment notes
```

The domain and SEO placeholders remain intentionally unchanged. Do not invent or replace `https://your-domain.com/` until the final domain is known.

## GitHub

Upload all five files to the repository root. The homepage must be named `index.html`.

## Vercel

Import the GitHub repository into Vercel. Use no build command and deploy as a static site. Keep `vercel.json` in the repository root so Vercel applies the security headers.

```bash
vercel
```

## Security compatibility

The Vercel CSP allows same-origin `script.js`, the existing Three.js and GSAP cdnjs scripts, inline styles used by the extracted stylesheet architecture, Google Fonts, HTTPS images, data URLs used by the existing visuals, and same-origin connections. The executable JavaScript is now external, so `script-src 'unsafe-inline'` is not required.

The site retains Subresource Integrity on the pinned CDN scripts and the existing WebGL, particle, GSAP, responsive, WhatsApp, and form behavior.

## Temporary preview checks

After deployment, verify navigation, mobile menu, responsive layout, enquiry validation, WhatsApp handoff to `6361435651`, Three.js, GSAP, and particle rendering. Inspect response headers with:

```bash
curl -I https://YOUR-VERCEL-URL.vercel.app/
```

Use the Vercel URL only for testing. Do not insert it into canonical or social metadata unless it is intended to be the canonical site.

## Final-domain actions

When the real domain is available, update the canonical URL, Open Graph URL, Twitter/OG image URLs, and JSON-LD URL. Then validate `robots.txt`, `sitemap.xml`, HTTPS redirects, certificates, and final security headers.
