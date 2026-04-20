# Logo & Splash Animation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the app icon/logo with `Logo.png` everywhere it appears (header, PWA icons, apple-touch-icon) and show a fullscreen startup animation video on page load (9:16 for mobile portrait, 4:3 for desktop/landscape).

**Architecture:** All changes are inside `app.py` — the single-file FastAPI app that renders HTML, CSS, JS, and serves static endpoints. Add new GET endpoints to serve Logo.png and the three animation videos. Add a splash overlay `<div>` that plays the correct video and dismisses after playback (or on tap/click). Swap the header SVG icon for an `<img>` pointing to `/logo.png`. Update PWA icon endpoints to redirect to `/logo.png`.

**Tech Stack:** FastAPI, Python 3, vanilla JS, HTML5 `<video>`, CSS animations, PWA manifest.

---

## File Map

| File | Change |
|------|--------|
| `app.py:49` | Update apple-touch-icon href to `/logo.png` |
| `app.py:82` | Update `.icon` CSS — remove gradient bg, add overflow:hidden |
| `app.py:84` | Replace `.icon svg` rule with `.icon img` rule |
| `app.py:303-305` | Replace SVG leaf inside `.icon` with `<img src="/logo.png">` |
| `app.py:~116` | Add `#splash` CSS after existing keyframes |
| `app.py:300` | Add splash overlay HTML before `<div class="app">` |
| `app.py:~1133` | Add splash JS (video selection, dismiss logic) |
| `app.py:1946-1949` | Update manifest icons to use `/logo.png` |
| `app.py:1980-1984` | Remove unused `ICON_SVG` constant |
| `app.py:2003-2016` | Replace icon-192/512 endpoints to redirect to `/logo.png` |
| `app.py:~2017` | Add `/logo.png`, `/anim-9-16.mp4`, `/anim-4-3.mp4`, `/anim-1-1.mp4` endpoints |

---

### Task 1: Serve Logo.png and animation videos as static endpoints

**Files:**
- Modify: `app.py` (after `get_icon_512` function, around line 2017)

- [ ] **Step 1: Replace icon-192 and icon-512 endpoints to redirect to /logo.png**

Replace the existing functions (lines 2003–2016):

```python
@app.get("/icon-192.png")
async def get_icon_192():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/logo.png", status_code=302)


@app.get("/icon-512.png")
async def get_icon_512():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/logo.png", status_code=302)
```

- [ ] **Step 2: Remove unused ICON_SVG constant**

Delete lines 1980–1984 (the `ICON_SVG` string and its comment — `# SVG icon rendered as PNG placeholder...` through the closing `"""`).

- [ ] **Step 3: Add four new GET endpoints before `if __name__ == "__main__":`**

```python
@app.get("/logo.png")
async def get_logo():
    from fastapi.responses import FileResponse
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo.png")
    return FileResponse(path, media_type="image/png",
                        headers={"Cache-Control": "public, max-age=604800"})


@app.get("/anim-9-16.mp4")
async def get_anim_9_16():
    from fastapi.responses import FileResponse
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Animación_9_16.mp4")
    return FileResponse(path, media_type="video/mp4",
                        headers={"Cache-Control": "public, max-age=604800"})


@app.get("/anim-4-3.mp4")
async def get_anim_4_3():
    from fastapi.responses import FileResponse
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Animación_4_3.mp4")
    return FileResponse(path, media_type="video/mp4",
                        headers={"Cache-Control": "public, max-age=604800"})


@app.get("/anim-1-1.mp4")
async def get_anim_1_1():
    from fastapi.responses import FileResponse
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Animación_1_1.mp4")
    return FileResponse(path, media_type="video/mp4",
                        headers={"Cache-Control": "public, max-age=604800"})
```

- [ ] **Step 4: Start the server and verify endpoints return 200**

```bash
cd C:/Users/mario/OneDrive/Escritorio/nutrition-gpt
uvicorn app:app --reload --port 8000
```

Open in browser:
- `http://localhost:8000/logo.png` → should display Logo.png image
- `http://localhost:8000/icon-192.png` → should redirect and show Logo.png
- `http://localhost:8000/anim-9-16.mp4` → should stream/download video

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: serve Logo.png and animation videos as static endpoints"
```

---

### Task 2: Replace header icon with Logo.png image

**Files:**
- Modify: `app.py` lines 82–84 (CSS) and lines 303–305 (HTML)

- [ ] **Step 1: Update `.icon` CSS (line 82)**

Current:
```css
.icon{width:46px;height:46px;background:linear-gradient(135deg,#42b87a 0%,#1f8c4e 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:5px 5px 12px rgba(31,140,78,.45),-3px -3px 8px rgba(255,255,255,.65)}
```

Replace with:
```css
.icon{width:46px;height:46px;border-radius:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:5px 5px 12px rgba(31,140,78,.45),-3px -3px 8px rgba(255,255,255,.65);overflow:hidden;background:transparent}
```

- [ ] **Step 2: Replace `.icon svg` rule with `.icon img` rule (line 84)**

Current:
```css
.icon svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
```

Replace with:
```css
.icon img{width:100%;height:100%;object-fit:cover;border-radius:14px}
```

- [ ] **Step 3: Replace SVG leaf with img tag in HTML (lines 303–305)**

Current:
```html
    <div class="icon">
      <svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 5-8 5"/></svg>
    </div>
```

Replace with:
```html
    <div class="icon">
      <img src="/logo.png" alt="NutriGPT logo">
    </div>
```

- [ ] **Step 4: Verify header shows logo**

Reload `http://localhost:8000` — top-left icon should show Logo.png instead of the green leaf SVG.

- [ ] **Step 5: Commit**

```bash
git add app.py
git commit -m "feat: replace header SVG icon with Logo.png image"
```

---

### Task 3: Update PWA manifest and apple-touch-icon to use Logo.png

**Files:**
- Modify: `app.py` line 49 (HTML head) and lines 1946–1949 (MANIFEST dict)

- [ ] **Step 1: Update apple-touch-icon link in HTML head (line 49)**

Current:
```html
<link rel="apple-touch-icon" href="/icon-192.png">
```

Replace with:
```html
<link rel="apple-touch-icon" href="/logo.png">
```

- [ ] **Step 2: Update MANIFEST icons array (lines 1946–1949)**

Current:
```python
    "icons": [
        {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
        {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
```

Replace with:
```python
    "icons": [
        {"src": "/logo.png", "sizes": "192x192 512x512 1024x1024", "type": "image/png", "purpose": "any maskable"},
    ],
```

- [ ] **Step 3: Verify manifest**

Open `http://localhost:8000/manifest.json` — should show `"src": "/logo.png"` in the icons array.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: update PWA manifest and apple-touch-icon to use Logo.png"
```

---

### Task 4: Add splash screen CSS and HTML

**Files:**
- Modify: `app.py` CSS block (~line 116) and HTML body (~line 300)

- [ ] **Step 1: Add splash CSS after the `@keyframes slideUp` line (~line 116)**

After the line containing `@keyframes slideUp{from{transform:translateY(70px);opacity:0}to{transform:translateY(0);opacity:1}}`, insert:

```css
#splash{position:fixed;inset:0;z-index:9999;background:#000;display:flex;align-items:center;justify-content:center;transition:opacity .6s ease}
#splash.hidden{opacity:0;pointer-events:none}
#splash video{width:100%;height:100%;object-fit:cover}
```

- [ ] **Step 2: Insert splash overlay HTML before `<div class="app">`**

Current (line 300–301):
```html
<body>
<div class="app">
```

Replace with:
```html
<body>
<div id="splash">
  <video id="splash-video" playsinline muted autoplay></video>
</div>
<div class="app">
```

- [ ] **Step 3: Verify a black fullscreen overlay appears on load**

Reload `http://localhost:8000` — should see a black fullscreen screen (video src not set yet, that's Task 5).

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add splash screen CSS and HTML overlay"
```

---

### Task 5: Add splash screen JavaScript

**Files:**
- Modify: `app.py` JS block (find the opening `<script>` tag, insert JS right after it)

- [ ] **Step 1: Add splash JS immediately after the opening `<script>` tag**

Find the line that reads `<script>` (opening of the main script block) and insert the following JS right after it:

```javascript
(function(){
  var splash=document.getElementById('splash');
  var video=document.getElementById('splash-video');
  var dismissed=false;

  function dismissSplash(){
    if(dismissed)return;
    dismissed=true;
    clearTimeout(fallback);
    splash.classList.add('hidden');
    splash.addEventListener('transitionend',function(){splash.remove();},{once:true});
  }

  // Select video: mobile portrait (max-width 767px, taller than wide) → 9:16, else → 4:3
  var isMobilePortrait=(window.innerWidth<=767&&window.innerHeight>window.innerWidth)
    ||window.matchMedia('(max-width:767px) and (orientation:portrait)').matches;
  video.src=isMobilePortrait?'/anim-9-16.mp4':'/anim-4-3.mp4';

  video.addEventListener('ended',dismissSplash);
  splash.addEventListener('click',dismissSplash);
  video.addEventListener('error',dismissSplash);

  // Safety fallback: dismiss after 8 seconds if video stalls
  var fallback=setTimeout(dismissSplash,8000);

  video.play().catch(dismissSplash);
})();
```

- [ ] **Step 2: Verify splash animation on desktop**

Reload `http://localhost:8000` — 4:3 animation plays fullscreen, then app appears. Clicking dismisses early.

Check the browser Network tab: confirm `/anim-4-3.mp4` is requested.

- [ ] **Step 3: Verify splash animation on simulated mobile (Chrome DevTools)**

Open DevTools → toggle device toolbar → select iPhone 12 (390×844, portrait). Hard-reload (`Ctrl+Shift+R`).

Check Network tab: confirm `/anim-9-16.mp4` is requested instead.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add responsive splash animation JS (9:16 mobile portrait, 4:3 desktop)"
```

---

## Self-Review

### Spec coverage

| Requirement | Task |
|-------------|------|
| Change logo in header | Task 2 |
| Change logo for PWA / mobile home screen icon | Tasks 1, 3 |
| Change apple-touch-icon (iOS) | Task 3 |
| Startup animation plays on web load | Tasks 4, 5 |
| Mobile portrait uses 9:16 animation | Task 5 (JS detection) |
| Desktop uses 4:3 animation | Task 5 (JS fallback) |
| Serve animation video files | Task 1 |

All requirements covered. No gaps.

### Placeholder scan

No TBD, TODO, "implement later", or "similar to Task N" patterns found.

### Consistency check

All endpoint paths defined in Task 1 (`/logo.png`, `/anim-9-16.mp4`, `/anim-4-3.mp4`) match exactly the paths referenced in Task 5 JS and Tasks 2–3 HTML/manifest.
