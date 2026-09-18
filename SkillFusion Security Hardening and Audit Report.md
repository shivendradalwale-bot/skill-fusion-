# SkillFusion Security Hardening and Audit Report

**Audit target:** `/home/ubuntu/upload/index(7).html`  
**Audit date:** 2026-09-15  
**Scope:** Static frontend security, third-party resources, forms, external links, browser runtime, responsive functionality, Three.js/WebGL, GSAP, and particle rendering.

## Executive conclusion

The website is a mostly static frontend with no exposed API keys, passwords, tokens, authentication flow, database integration, or unsafe HTML injection path. The existing form is client-side only and displays a fixed confirmation message; it does not send user-controlled content to a server. The existing Three.js, GSAP, and particle systems were preserved.

The HTML was hardened with a browser-compatible Content Security Policy, a strict referrer policy, Subresource Integrity for the three pinned CDN scripts, and safe opener isolation for WhatsApp links opened in new tabs. Accessibility-related security hygiene was retained from the previous QA pass. The final security/functionality regression found no JavaScript page errors, no failed requests, no CSP violations, no horizontal overflow, no broken anchors, and no unsafe new-tab links.

Some protections cannot be safely enforced from HTML. HTTPS, HSTS, frame protection, server-side CSP delivery, permissions policy, and production form abuse controls must be configured at the hosting, CDN, or web-server layer.

## A. Protections that already existed

The source already used HTTPS URLs for Google Fonts, cdnjs, Schema.org, and WhatsApp. No HTTP mixed-content URL was found. The site did not contain inline event-handler attributes such as `onclick`, and the audit found no `innerHTML`, `document.write`, `eval`, `new Function`, or `insertAdjacentHTML` usage. These are favorable indicators because user-controlled values are not inserted into HTML markup.

The form used native required-field validation and the submit handler called `preventDefault()`. It reset the form after displaying a fixed, non-user-derived acknowledgement. The site also already included a skip link, semantic navigation structure, `aria-hidden` decoration for SVGs and canvases, and reduced-motion handling for the animation layers.

The 3D enhancement had useful defensive behavior. It checked reduced-motion preferences, tested WebGL availability, wrapped renderer construction in `try/catch`, and used `IntersectionObserver` to start section-level render loops only while their containing sections were visible. The particle system also reduced particle counts on smaller and lower-power devices and handled WebGL context loss.

## B. Protections added

### Browser policy metadata

The document now contains a meta-delivered Content Security Policy with the following controls:

- `default-src 'self'` limits unspecified resource types to the site origin.
- `base-uri 'self'` prevents untrusted base URL changes.
- `object-src 'none'` disables legacy plugin content.
- `form-action 'self'` limits native form submission destinations.
- `script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com` preserves the existing inline scripts and allows only the required cdnjs library origin.
- `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com` preserves the existing inline style architecture and Google Fonts stylesheet.
- `font-src 'self' https://fonts.gstatic.com` allows only local fonts and Google’s font host.
- `img-src 'self' data: https:` preserves the existing inline SVG/data use and HTTPS image compatibility.
- `connect-src 'self'` prevents unexpected browser-side API connections.
- `upgrade-insecure-requests` upgrades accidental HTTP subresources to HTTPS.

The policy deliberately retains `'unsafe-inline'` because the current website is a single self-contained HTML file with large inline CSS and JavaScript blocks. Removing it would require a structural refactor into external files or nonce/hash-based policies and would violate the request to preserve the existing implementation.

### Subresource Integrity

SHA-384 integrity hashes and `crossorigin="anonymous"` were added to the pinned cdnjs resources:

- Three.js `r128`
- GSAP `3.12.2`
- GSAP ScrollTrigger `3.12.2`

This prevents a modified response from being executed if the CDN content no longer matches the reviewed versions. If any of these libraries are upgraded, the integrity hash must be regenerated at the same time.

### External-tab isolation

Both WhatsApp links using `target="_blank"` now include `rel="noopener noreferrer"`. This prevents the opened page from accessing `window.opener` and reduces referrer leakage.

### Existing accessibility hardening retained

The mobile menu uses synchronized `aria-expanded` and `aria-label` values. The form labels are explicitly associated with their controls, and the main fields have stable `name`, `id`, and autocomplete attributes. These changes reduce ambiguity for assistive technology and make future server-side form integration safer.

## C. Deployment configuration still required

### HTTPS and HSTS

Serve the production site exclusively over HTTPS and redirect HTTP to HTTPS at the edge. After confirming that every required subresource and domain is HTTPS-compatible, send this header from the hosting layer:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Do not add `preload` until the domain, subdomains, and operational ownership meet the preload requirements.

### Server-delivered security headers

The following headers must be configured by the web server or CDN because they are not reliably enforceable through a meta tag:

```http
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=()
Content-Security-Policy: [use the reviewed policy, delivered as an HTTP response header]
Content-Security-Policy: frame-ancestors 'none';
```

`frame-ancestors` was intentionally removed from the meta policy after Chromium correctly reported that the directive is ignored when delivered through HTML. It belongs in the HTTP response header. `X-Frame-Options: DENY` may also be added as a legacy fallback, although `frame-ancestors` is the stronger modern control.

A practical production CSP header should begin with the same allowlist used in the HTML, but the deployment team should consider migrating inline CSS and JavaScript to external files or nonce/hash-based authorization over time. That would allow removal of `'unsafe-inline'`.

### Domain and social metadata

Replace every `https://your-domain.com/` placeholder in the canonical URL, Open Graph URL, Open Graph image, Twitter image, and JSON-LD URL. Upload a real 1200×630 social preview image and ensure it is served over HTTPS. Add and validate `robots.txt` and `sitemap.xml` at the final domain.

### Form abuse protection

The current enquiry form is frontend-only and does not transmit data. If a backend or form service is connected later, add server-side validation, output encoding, rate limiting, CSRF protection where applicable, spam controls, logging with data minimization, and a clear retention policy. Never trust the browser’s `required`, `type="email"`, or client-side checks as server validation.

## D. Remaining risks

The largest current policy limitation is `'unsafe-inline'`, which is required by the existing single-file architecture. It increases the impact of any future HTML injection vulnerability, although the current audit found no unsafe DOM sink and no user-controlled HTML insertion.

The CDN libraries remain a supply-chain dependency. SRI reduces tampering risk, but production should monitor library versions and pin intentional upgrades. A future hardening step could self-host the reviewed library files or move them to a controlled asset pipeline.

The particle field runs continuously when WebGL is available, while section-level scenes pause off-screen. This is a performance consideration rather than a direct security flaw. Production should test on real mobile hardware and retain the existing low-power tiering.

The HTML meta policy cannot set all response-level protections. A production security scanner may still report missing HSTS, `frame-ancestors`, `X-Content-Type-Options`, and `Permissions-Policy` until the deployment headers are configured.

## Verification results

The hardened build was tested at 1440×1000 and 390×844 using Chromium with WebGL enabled through the automated Playwright runner.

| Check | Result |
|---|---|
| JavaScript page errors | Passed; none detected |
| Failed network requests | Passed; none detected |
| CSP violations | Passed after moving `frame-ancestors` out of the meta policy |
| Horizontal overflow | Passed at desktop and mobile sizes |
| Internal anchors | Passed; no missing targets |
| Mobile menu | Passed; open/close state and ARIA state synchronized |
| Form presence and native validation | Passed |
| Form label associations | Passed |
| New-tab opener protection | Passed; zero unprotected `_blank` links |
| Three.js canvases | Passed; six canvases initialized and visible in the test environment |
| Particle/WebGL runtime | Passed; no page errors |
| Mixed-content URLs | Passed; no `http://` resource found |
| Exposed secrets | Passed; no API keys, passwords, tokens, or bearer credentials found |

## References

[1]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP "MDN Content Security Policy"
[2]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security "MDN Strict-Transport-Security"
[3]: https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity "MDN Subresource Integrity"
[4]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/frame-ancestors "MDN CSP frame-ancestors directive"
[5]: https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/noopener "MDN rel=noopener"
