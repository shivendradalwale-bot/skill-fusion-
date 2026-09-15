# Temporary Vercel deployment

## Files

Keep these files together in the deployment root:

- `index.html` — rename the supplied `index(7).html` to this filename.
- `vercel.json` — Vercel response-security headers for the static site.

The existing domain and SEO placeholders are intentionally unchanged. Do not replace `https://your-domain.com/` until the final domain is known.

## Deploy with Vercel CLI

```bash
mv 'index(7).html' index.html
npm i -g vercel
vercel
```

For a temporary preview, use the generated Vercel preview URL. Do not change the canonical, Open Graph, Twitter, or JSON-LD domain placeholders yet.

## Deploy through the Vercel dashboard

1. Create or import a project.
2. Upload the folder containing `index.html` and `vercel.json`.
3. Use the default framework preset or `Other` for a static site.
4. Deploy without adding a build command.
5. Confirm that `vercel.json` is at the project root.

## Headers configured by `vercel.json`

- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()`
- `X-Frame-Options: DENY`
- HTTP-header `Content-Security-Policy` with allowances for the existing inline CSS/JavaScript, cdnjs Three.js/GSAP resources, Google Fonts, HTTPS images, WebGL, and same-origin connections.

## Post-deployment checks

Open the Vercel URL and verify navigation, the mobile menu, responsive layout, Three.js and particle canvases, the enquiry form, and the WhatsApp handoff. Inspect the response headers in browser developer tools or with:

```bash
curl -I https://YOUR-VERCEL-URL.vercel.app/
```

Replace `YOUR-VERCEL-URL` only in the command when testing. Do not place that temporary URL into the website SEO metadata unless it is intended to be the canonical site.

## Final-domain checklist

When the real domain is available, update the canonical URL, Open Graph URL, Twitter/OG image URLs, and JSON-LD URL. Then validate the final `robots.txt`, `sitemap.xml`, HTTPS redirect, certificate, and production metadata.
