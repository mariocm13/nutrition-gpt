from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import os
import re
import unicodedata
import base64
from groq import Groq
from nlp_processor import NLPProcessor

app = FastAPI(title="NutrIA")

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "https://nutrition-gpt-eta.vercel.app",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

nlp = NLPProcessor()

CALORIES_DATA_PATH = "data/calories.json"


HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NutrIA</title>
<meta name="theme-color" content="#10b981" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#06120c" media="(prefers-color-scheme: dark)">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="NutrIA">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap">
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
button,input,select,textarea{-webkit-appearance:none;appearance:none;touch-action:manipulation;user-select:none;-webkit-user-select:none;font-family:inherit;font-feature-settings:'tnum' 1}

:root{
  /* Brand — layered emerald w/ teal halo */
  --brand-50:#ecfdf5; --brand-100:#d1fae5; --brand-200:#a7f3d0;
  --brand-400:#34d399; --brand-500:#10b981; --brand-600:#059669;
  --brand-700:#047857; --brand-800:#065f46; --brand-900:#053a2a;
  /* Cool secondary for data viz / charts */
  --cool-300:#7dd3fc; --cool-500:#0ea5e9; --cool-700:#0369a1;
  /* Warm accent for energy/kcal */
  --warm-300:#fcd34d; --warm-400:#fbbf24; --warm-500:#f59e0b; --warm-600:#d97706;
  /* Background — soft cream + green wash */
  --bg:#f1f7f3;
  --bg-mesh-1:#dff2e7; --bg-mesh-2:#eaf4fa; --bg-mesh-3:#fef7e6;
  --surface:#ffffff;
  --surface-2:#f6faf7;
  --surface-3:#edf4ef;
  --surface-glass:rgba(255,255,255,.62);
  --surface-glass-strong:rgba(255,255,255,.82);
  --border:#dfe9e3; --border-strong:#c2d2c8;
  --text:#062014; --text-soft:#2f4a3d; --muted:#647568;
  /* Tokens */
  --accent:var(--brand-600); --accent-h:var(--brand-700);
  --accent-soft:var(--brand-50); --accent-light:var(--brand-100); --accent-muted:var(--brand-200);
  /* Shadows with green tint */
  --sh-xs:0 1px 2px rgba(15,60,40,.05),0 0 0 1px rgba(15,60,40,.02);
  --sh-sm:0 2px 8px rgba(15,60,40,.08),0 1px 2px rgba(15,60,40,.04);
  --sh:0 12px 32px -10px rgba(15,60,40,.16),0 6px 12px -6px rgba(15,60,40,.08);
  --sh-lg:0 32px 60px -18px rgba(15,60,40,.24),0 10px 22px -8px rgba(15,60,40,.12);
  --sh-glow:0 12px 32px -8px rgba(16,185,129,.45);
  --sh-glow-warm:0 12px 32px -8px rgba(245,158,11,.4);
  /* Radii */
  --r-xs:8px; --r-sm:12px; --r-md:16px; --r-lg:20px; --r-xl:24px; --r-2xl:28px; --r-3xl:36px; --r-pill:999px;
  /* Motion */
  --t-fast:.15s; --t:.22s; --t-slow:.35s;
  --ease-out:cubic-bezier(.16,1,.3,1);
  --ease-spring:cubic-bezier(.34,1.56,.64,1);
  --ease-soft:cubic-bezier(.4,0,.2,1);
  /* Layout */
  --sidebar-w:260px;
  --topbar-h:68px;
  --bottom-nav-h:74px;
}
html.dark{
  --bg:#04130c;
  --bg-mesh-1:#0a2017; --bg-mesh-2:#091a25; --bg-mesh-3:#1a1407;
  --surface:#0f2018; --surface-2:#0a1810; --surface-3:#08140d;
  --surface-glass:rgba(12,28,20,.62);
  --surface-glass-strong:rgba(12,28,20,.85);
  --border:#1d2f25; --border-strong:#2a4034;
  --text:#e9f5ee; --text-soft:#b3c9bd; --muted:#7f9489;
  --accent:#34d399; --accent-h:#10b981;
  --accent-soft:#0b1f15; --accent-light:#0f2e1f; --accent-muted:#1a3a27;
  --sh-xs:0 1px 2px rgba(0,0,0,.5),0 0 0 1px rgba(255,255,255,.03);
  --sh-sm:0 2px 8px rgba(0,0,0,.5),0 1px 2px rgba(0,0,0,.35);
  --sh:0 12px 32px -10px rgba(0,0,0,.6),0 6px 12px -6px rgba(0,0,0,.4);
  --sh-lg:0 32px 60px -18px rgba(0,0,0,.75);
  --sh-glow:0 12px 32px -8px rgba(52,211,153,.35);
  --sh-glow-warm:0 12px 32px -8px rgba(252,211,77,.3);
}

html,body{height:100%;overflow:hidden;overscroll-behavior:none}
body{
  font-family:'Inter',system-ui,-apple-system,sans-serif;
  color:var(--text);
  font-size:14px;
  line-height:1.55;
  background:var(--bg);
  transition:background var(--t-slow) var(--ease-soft),color var(--t-slow);
  position:relative;
  overflow:hidden;
}
/* ── Animated mesh background ── */
body::before{
  content:"";
  position:fixed;inset:-15%;
  background:
    radial-gradient(48% 38% at 12% 10%,var(--bg-mesh-1) 0%,transparent 60%),
    radial-gradient(40% 38% at 92% 18%,var(--bg-mesh-2) 0%,transparent 65%),
    radial-gradient(46% 40% at 75% 92%,var(--bg-mesh-3) 0%,transparent 60%),
    radial-gradient(30% 26% at 5% 88%,var(--accent-soft) 0%,transparent 70%);
  pointer-events:none;z-index:0;opacity:.95;
  animation:meshDrift 30s ease-in-out infinite alternate;
}
body::after{
  content:"";position:fixed;inset:0;
  background:radial-gradient(circle at 50% 0%,rgba(255,255,255,.04) 0%,transparent 60%);
  pointer-events:none;z-index:0;
}
html.dark body::before{opacity:.7}
@keyframes meshDrift{
  0%{transform:translate(0,0) scale(1) rotate(0deg)}
  50%{transform:translate(-2%,1%) scale(1.03) rotate(.4deg)}
  100%{transform:translate(2%,-1.5%) scale(1.05) rotate(-.3deg)}
}

/* ── App shell (sidebar + main) ── */
.app{
  position:relative;z-index:1;
  display:grid;
  grid-template-columns:var(--sidebar-w) 1fr;
  height:100vh;height:100dvh;
  width:100%;
}
@media(max-width:1023px){
  .app{grid-template-columns:1fr;padding-bottom:calc(var(--bottom-nav-h) + env(safe-area-inset-bottom,0px))}
}

/* ── Sidebar (desktop primary nav) ── */
.sidebar{
  display:flex;flex-direction:column;
  padding:22px 18px 16px;
  background:var(--surface-glass-strong);
  backdrop-filter:saturate(180%) blur(22px);
  -webkit-backdrop-filter:saturate(180%) blur(22px);
  border-right:1px solid var(--border);
  position:relative;z-index:6;
  gap:6px;
  animation:slideRight .4s var(--ease-out) both;
}
@keyframes slideRight{from{transform:translateX(-12px);opacity:0}to{transform:translateX(0);opacity:1}}
@media(max-width:1023px){.sidebar{display:none}}

.brand{
  display:flex;align-items:center;gap:12px;
  padding:6px 8px 18px;
  border-bottom:1px dashed var(--border);
  margin-bottom:14px;
}
.brand-logo{
  width:46px;height:46px;border-radius:14px;
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;overflow:hidden;
  background:linear-gradient(135deg,var(--brand-400),var(--brand-700));
  box-shadow:0 10px 24px -6px rgba(16,185,129,.5),inset 0 1px 0 rgba(255,255,255,.3);
  position:relative;
}
.brand-logo::after{content:"";position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.35),transparent 55%);pointer-events:none}
.brand-logo img{width:100%;height:100%;object-fit:cover;border-radius:14px;position:relative;z-index:1}
.brand-name{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-size:18px;font-weight:800;letter-spacing:-.4px;background:linear-gradient(135deg,var(--text) 0%,var(--brand-700) 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
html.dark .brand-name{background:linear-gradient(135deg,var(--text) 0%,var(--brand-400) 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.brand-tag{font-size:11px;color:var(--muted);font-weight:600;margin-top:1px}

.side-section{font-size:10px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.14em;padding:10px 12px 6px}

.side-foot{
  margin-top:auto;
  padding:14px 12px;
  border-top:1px dashed var(--border);
  font-size:11px;color:var(--muted);
  display:flex;align-items:center;gap:8px;
}
.side-foot-dot{width:8px;height:8px;border-radius:50%;background:var(--brand-500);box-shadow:0 0 0 4px rgba(16,185,129,.18);animation:pulseDot 2s ease-in-out infinite}
@keyframes pulseDot{0%,100%{box-shadow:0 0 0 4px rgba(16,185,129,.18)}50%{box-shadow:0 0 0 8px rgba(16,185,129,0)}}

/* ── Main column ── */
.main{
  display:flex;flex-direction:column;
  min-width:0;min-height:0;
  position:relative;
  overflow:hidden;
}

/* ── Topbar ── */
.topbar{
  height:var(--topbar-h);
  padding:0 22px;
  display:flex;align-items:center;gap:14px;
  background:var(--surface-glass);
  backdrop-filter:saturate(180%) blur(18px);
  -webkit-backdrop-filter:saturate(180%) blur(18px);
  border-bottom:1px solid var(--border);
  flex-shrink:0;position:relative;z-index:5;
}
@media(max-width:1023px){.topbar{padding:0 14px;height:60px}}
.topbar-mobile-brand{display:none;align-items:center;gap:10px}
.topbar-mobile-brand .brand-logo{width:36px;height:36px;border-radius:11px;box-shadow:0 6px 16px -4px rgba(16,185,129,.45),inset 0 1px 0 rgba(255,255,255,.25)}
.topbar-mobile-brand .brand-logo img{border-radius:11px}
.topbar-mobile-brand .brand-name{font-size:16px}
@media(max-width:1023px){.topbar-mobile-brand{display:flex}}

.topbar-title{
  flex:1;min-width:0;
  display:flex;flex-direction:column;justify-content:center;
}
@media(max-width:1023px){.topbar-title{display:none}}
.topbar-title h1{
  font-family:'Plus Jakarta Sans','Inter',sans-serif;
  font-size:22px;font-weight:800;letter-spacing:-.5px;
  color:var(--text);
  display:flex;align-items:center;gap:10px;
}
.topbar-title .tt-tag{
  font-size:10.5px;font-weight:700;
  padding:3px 9px;border-radius:var(--r-pill);
  background:var(--accent-light);color:var(--accent);
  border:1px solid var(--accent-muted);
  letter-spacing:.06em;text-transform:uppercase;
}
.topbar-title p{font-size:12.5px;color:var(--muted);margin-top:2px;font-weight:500}

.topbar-end{display:flex;gap:8px;align-items:center;flex-shrink:0;margin-left:auto}
.hdr-btn{
  width:40px;height:40px;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:13px;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;color:var(--text-soft);
  transition:all var(--t) var(--ease-out);
  box-shadow:var(--sh-xs);
}
.hdr-btn:hover{color:var(--accent);background:var(--accent-soft);border-color:var(--accent-muted);transform:translateY(-1px);box-shadow:var(--sh-sm)}
.hdr-btn:active{transform:translateY(0) scale(.94)}
.hdr-btn:focus-visible{outline:none;box-shadow:0 0 0 3px var(--accent-muted)}
.hdr-btn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

/* ── Unified responsive nav ── */
.nav-tab{
  cursor:pointer;border:none;background:transparent;
  color:var(--text-soft);
  display:flex;align-items:center;
  transition:color var(--t) var(--ease-out),background var(--t) var(--ease-out),transform var(--t) var(--ease-spring);
  position:relative;
}
.nav-tab svg{
  fill:none;stroke:currentColor;
  stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;
  pointer-events:none;
  transition:transform var(--t) var(--ease-spring);
}
.nav-tab .nav-lbl{pointer-events:none}

/* Sidebar nav style (desktop ≥1024px) */
@media(min-width:1024px){
  .sidebar .nav-tab{
    gap:12px;width:100%;
    padding:11px 14px;
    border-radius:14px;
    font-size:14px;font-weight:600;
    margin-bottom:2px;
  }
  .sidebar .nav-tab svg{width:20px;height:20px;flex-shrink:0}
  .sidebar .nav-tab:hover{background:var(--surface-3);color:var(--text)}
  .sidebar .nav-tab.active{
    color:#fff;
    background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
    box-shadow:0 10px 24px -8px rgba(16,185,129,.55),inset 0 1px 0 rgba(255,255,255,.18);
    font-weight:700;
  }
  .sidebar .nav-tab.active svg{transform:scale(1.08)}
  .sidebar .nav-tab:focus-visible{outline:none;box-shadow:0 0 0 3px var(--accent-muted)}
  .bottom-nav{display:none}
}

/* Bottom nav style (mobile <1024px) */
@media(max-width:1023px){
  .bottom-nav{
    position:fixed;bottom:0;left:0;right:0;z-index:100;
    background:var(--surface-glass-strong);
    backdrop-filter:saturate(180%) blur(22px);
    -webkit-backdrop-filter:saturate(180%) blur(22px);
    border-top:1px solid var(--border);
    display:flex;align-items:stretch;justify-content:space-around;
    height:var(--bottom-nav-h);
    padding-bottom:env(safe-area-inset-bottom,0);
  }
  .bottom-nav .nav-tab{
    flex:1;min-width:44px;
    flex-direction:column;align-items:center;justify-content:center;
    gap:3px;padding:8px 4px 10px;
    color:var(--muted);
  }
  .bottom-nav .nav-tab svg{width:23px;height:23px}
  .bottom-nav .nav-lbl{font-size:10.5px;font-weight:600;letter-spacing:.01em;transition:font-weight var(--t)}
  .bottom-nav .nav-tab:hover{color:var(--text-soft)}
  .bottom-nav .nav-tab.active{color:var(--accent)}
  .bottom-nav .nav-tab.active svg{transform:translateY(-2px) scale(1.08)}
  .bottom-nav .nav-tab.active .nav-lbl{font-weight:700}
  .bottom-nav .nav-tab::before{
    content:"";position:absolute;top:6px;left:50%;
    transform:translateX(-50%) scaleX(0);
    width:30px;height:3px;
    background:linear-gradient(90deg,var(--brand-400),var(--brand-600));
    border-radius:0 0 4px 4px;
    transition:transform var(--t) var(--ease-spring);
    transform-origin:center;
  }
  .bottom-nav .nav-tab.active::before{transform:translateX(-50%) scaleX(1)}
  .sidebar{display:none}
}

/* ── Panel stack ── */
.panel-stack{
  flex:1;min-height:0;
  position:relative;
  display:flex;flex-direction:column;
  overflow:hidden;
}
.panel{display:none;flex:1;flex-direction:column;min-height:0;overflow:hidden;position:relative}
.panel.active{display:flex;animation:panelIn .4s var(--ease-out)}
@keyframes panelIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* Display helper */
.dispnum{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-feature-settings:'tnum' 1;letter-spacing:-.02em}

/* ── Chat panel ── */
.chat-layout{
  flex:1;min-height:0;
  display:grid;
  grid-template-columns:1fr;
  position:relative;
}
@media(min-width:1280px){
  .chat-layout{grid-template-columns:1fr 320px;gap:0}
}
.chat-main{display:flex;flex-direction:column;min-height:0;min-width:0;position:relative}
.chat-suggest{
  display:flex;gap:8px;flex-wrap:wrap;
  padding:14px 22px 0;
  flex-shrink:0;
}
@media(max-width:1023px){.chat-suggest{padding:12px 14px 0}}
.chip{
  font-size:12.5px;font-weight:600;
  padding:7px 13px;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-pill);
  color:var(--text-soft);
  cursor:pointer;
  display:inline-flex;align-items:center;gap:6px;
  box-shadow:var(--sh-xs);
  transition:all var(--t) var(--ease-out);
}
.chip:hover{color:var(--accent);background:var(--accent-soft);border-color:var(--accent-muted);transform:translateY(-1px)}
.chip:active{transform:scale(.97)}
.chip svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

.msgs{
  flex:1;overflow-y:auto;
  padding:18px 22px 14px;
  display:flex;flex-direction:column;gap:14px;
  scrollbar-width:thin;scrollbar-color:var(--border) transparent;
  -webkit-overflow-scrolling:touch;overscroll-behavior:contain;
}
@media(max-width:1023px){.msgs{padding:16px 14px 14px}}
.msgs::-webkit-scrollbar{width:6px}
.msgs::-webkit-scrollbar-thumb{background:var(--border);border-radius:6px}
.msgs::-webkit-scrollbar-thumb:hover{background:var(--border-strong)}
.m{display:flex;gap:10px;animation:fadeUp .35s var(--ease-out) both;max-width:880px;width:100%}
.m.u{justify-content:flex-end;margin-left:auto}
.m.bot{align-items:flex-start}
.avatar{
  width:34px;height:34px;min-width:34px;
  border-radius:12px;
  background:linear-gradient(135deg,var(--brand-400),var(--brand-700));
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;margin-top:2px;
  box-shadow:0 6px 16px -3px rgba(16,185,129,.45),inset 0 1px 0 rgba(255,255,255,.25);
  position:relative;
}
.avatar::after{content:"";position:absolute;inset:0;border-radius:12px;background:linear-gradient(135deg,rgba(255,255,255,.28),transparent 60%);pointer-events:none}
.avatar svg{width:17px;height:17px;fill:none;stroke:#fff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;position:relative;z-index:1}
.b{max-width:78%;padding:14px 18px;line-height:1.65;font-size:14.5px;word-wrap:break-word}
.m.bot .b{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:6px 20px 20px 20px;
  box-shadow:var(--sh-sm);
  color:var(--text);
}
.m.u .b{
  background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
  color:#fff;
  border-radius:20px 6px 20px 20px;
  box-shadow:0 10px 26px -8px rgba(16,185,129,.5),inset 0 1px 0 rgba(255,255,255,.2);
}
.typing .b{
  color:var(--muted);
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:6px 20px 20px 20px;
  animation:typingPulse 1.5s ease-in-out infinite;
}
@keyframes typingPulse{0%,100%{opacity:1}50%{opacity:.55}}

.composer{
  padding:12px 22px 18px;
  background:var(--surface-glass);
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
  border-top:1px solid var(--border);
  display:flex;gap:10px;align-items:center;
  flex-shrink:0;
}
@media(max-width:1023px){.composer{padding:10px 14px 14px}}
#inp{
  flex:1;padding:14px 22px;
  border:1.5px solid var(--border);
  border-radius:var(--r-pill);
  font-size:15px;
  background:var(--surface);
  color:var(--text);
  outline:none;
  transition:border-color var(--t),box-shadow var(--t);
  user-select:auto;-webkit-user-select:auto;
  box-shadow:var(--sh-xs);
}
#inp:focus{border-color:var(--accent);box-shadow:0 0 0 4px var(--accent-muted)}
#inp::placeholder{color:var(--muted)}
#btn{
  width:48px;height:48px;flex-shrink:0;
  background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
  color:#fff;border:none;border-radius:50%;
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  box-shadow:var(--sh-glow);
  transition:transform var(--t) var(--ease-spring),box-shadow var(--t),filter var(--t);
  position:relative;overflow:hidden;
}
#btn::before{content:"";position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.25),transparent 60%);pointer-events:none}
#btn:hover{transform:translateY(-1px) scale(1.03);filter:brightness(1.05)}
#btn:active{transform:scale(.92);box-shadow:0 4px 10px rgba(16,185,129,.25)}
#btn:focus-visible{outline:none;box-shadow:0 0 0 4px var(--accent-muted),var(--sh-glow)}
#btn svg{width:20px;height:20px;fill:none;stroke:#fff;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round;position:relative;z-index:1}

/* Right rail (desktop chat) */
.chat-rail{
  display:none;
  flex-direction:column;gap:14px;
  padding:18px 22px;
  border-left:1px solid var(--border);
  background:var(--surface-glass);
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
  overflow-y:auto;
}
@media(min-width:1280px){.chat-rail{display:flex}}
.rail-card{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-lg);
  padding:16px;
  box-shadow:var(--sh-xs);
  animation:fadeUp .4s var(--ease-out) both;
}
.rail-card-title{font-size:11px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.12em;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.rail-card-title::before{content:"";width:4px;height:14px;border-radius:2px;background:linear-gradient(180deg,var(--brand-400),var(--brand-600))}
.rail-stat{display:flex;justify-content:space-between;align-items:baseline;padding:7px 0;border-bottom:1px dashed var(--border);font-size:13px;color:var(--text-soft)}
.rail-stat:last-child{border-bottom:none}
.rail-stat-val{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-weight:700;color:var(--text);font-feature-settings:'tnum' 1}
.rail-tip{font-size:13px;color:var(--text-soft);line-height:1.6}
.rail-tip strong{color:var(--accent);font-weight:700}

/* ── Splash ── */
#splash{
  position:fixed;inset:0;z-index:9999;
  background:radial-gradient(circle at center,#0a1f15 0%,#000 80%);
  display:flex;align-items:center;justify-content:center;
  transition:opacity .7s var(--ease-out);
}
#splash.hidden{opacity:0;pointer-events:none}
#splash video{width:100%;height:100%;object-fit:cover}
small{font-size:12px}

/* ── Generic content wrapper ── */
.content-scroll{
  flex:1;overflow-y:auto;
  padding:22px 26px 28px;
  -webkit-overflow-scrolling:touch;
  scrollbar-width:thin;scrollbar-color:var(--border) transparent;
}
.content-scroll::-webkit-scrollbar{width:8px}
.content-scroll::-webkit-scrollbar-thumb{background:var(--border);border-radius:8px}
@media(max-width:1023px){.content-scroll{padding:16px 14px 24px}}
.content-wide{max-width:1280px;margin:0 auto;width:100%}

/* ── Calculator panel ── */
.calc-grid{display:grid;grid-template-columns:1fr;gap:20px}
@media(min-width:980px){.calc-grid{grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:24px;align-items:start}}

.card{
  background:var(--surface);
  border-radius:var(--r-xl);
  padding:24px;
  box-shadow:var(--sh);
  border:1px solid var(--border);
  animation:fadeUp .4s var(--ease-out) both;
  position:relative;overflow:hidden;
}
.card::before{
  content:"";position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--brand-400),var(--brand-600),var(--brand-400));
  background-size:200% 100%;
  animation:shimmer 6s linear infinite;
  opacity:.7;
}
.card-title{
  font-family:'Plus Jakarta Sans','Inter',sans-serif;
  font-size:19px;font-weight:800;letter-spacing:-.4px;
  margin-bottom:6px;color:var(--text);
  display:flex;align-items:center;gap:12px;
}
.card-title-icon{
  width:36px;height:36px;border-radius:11px;
  background:linear-gradient(135deg,var(--brand-100),var(--brand-200));
  color:var(--brand-700);
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.5);
}
.card-title-icon svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
html.dark .card-title-icon{background:linear-gradient(135deg,var(--accent-light),var(--accent-muted));color:var(--brand-400)}
.card-sub{font-size:13px;color:var(--muted);margin-bottom:18px;line-height:1.5}

.calc-row.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.calc-group{margin-bottom:14px}
.calc-label{
  display:block;font-size:11px;font-weight:800;
  color:var(--muted);text-transform:uppercase;
  letter-spacing:.1em;margin-bottom:8px;
}
.calc-inp{
  width:100%;padding:13px 15px;
  border:1.5px solid var(--border);
  border-radius:var(--r-sm);
  font-size:16px;
  background:var(--surface-2);
  color:var(--text);outline:none;
  transition:border-color var(--t),box-shadow var(--t),background var(--t);
  -webkit-appearance:none;
  user-select:auto;-webkit-user-select:auto;
}
.calc-inp:focus{border-color:var(--accent);box-shadow:0 0 0 4px var(--accent-muted);background:var(--surface)}
.calc-sel{
  width:100%;padding:13px 15px;
  border:1.5px solid var(--border);
  border-radius:var(--r-sm);
  font-size:14px;
  background:var(--surface-2);
  color:var(--text);outline:none;cursor:pointer;
  transition:border-color var(--t),box-shadow var(--t);
}
.calc-sel:focus{border-color:var(--accent);box-shadow:0 0 0 4px var(--accent-muted)}
.seg{display:flex;gap:4px;flex-wrap:wrap;background:var(--surface-2);padding:4px;border-radius:var(--r-sm);border:1px solid var(--border)}
.seg-btn{
  flex:1;padding:10px 8px;border:none;border-radius:10px;
  font-size:13px;font-weight:700;
  background:transparent;color:var(--muted);
  cursor:pointer;
  transition:all var(--t) var(--ease-out);
  white-space:nowrap;touch-action:manipulation;position:relative;
}
.seg-btn:hover{color:var(--text-soft)}
.seg-btn.active{
  background:var(--surface);color:var(--accent);
  box-shadow:0 2px 8px -2px rgba(16,185,129,.25),var(--sh-xs);
  font-weight:800;
}
html.dark .seg-btn.active{background:var(--accent-light)}
.calc-btn{
  width:100%;padding:15px;
  background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
  color:#fff;border:none;
  border-radius:var(--r-md);
  font-size:15px;font-weight:800;letter-spacing:.01em;
  cursor:pointer;
  box-shadow:var(--sh-glow);
  transition:transform var(--t) var(--ease-spring),box-shadow var(--t),filter var(--t);
  touch-action:manipulation;margin-top:10px;
  position:relative;overflow:hidden;
}
.calc-btn::before{
  content:"";position:absolute;inset:0;
  background:linear-gradient(120deg,transparent 30%,rgba(255,255,255,.2) 50%,transparent 70%);
  background-size:200% 100%;background-position:-200% 0;
  transition:background-position .7s var(--ease-soft);
  pointer-events:none;
}
.calc-btn:hover{transform:translateY(-1px);filter:brightness(1.05)}
.calc-btn:hover::before{background-position:200% 0}
.calc-btn:active{transform:scale(.98);box-shadow:0 4px 12px -2px rgba(16,185,129,.3)}
.calc-btn:focus-visible{outline:none;box-shadow:0 0 0 4px var(--accent-muted),var(--sh-glow)}

#calc-result{display:flex;flex-direction:column;gap:16px}
.calc-result{padding:0 !important;background:transparent !important;box-shadow:none !important;border:none !important;animation:none !important}
.res-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.res-box{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-md);
  padding:16px 10px;text-align:center;
  transition:transform var(--t) var(--ease-out);
  box-shadow:var(--sh-xs);
}
.res-box:hover{transform:translateY(-2px);box-shadow:var(--sh-sm)}
.res-box.accent{
  background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
  border-color:transparent;
  box-shadow:0 12px 32px -10px rgba(16,185,129,.5),inset 0 1px 0 rgba(255,255,255,.22);
  position:relative;overflow:hidden;
}
.res-box.accent::after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 20% 0%,rgba(255,255,255,.25),transparent 50%);pointer-events:none}
.res-box.accent .res-val,.res-box.accent .res-lbl,.res-box.accent .res-sub{color:#fff;position:relative}
.res-val{
  font-family:'Plus Jakarta Sans','Inter',sans-serif;
  font-size:26px;font-weight:800;color:var(--accent);
  line-height:1;letter-spacing:-.02em;
  font-feature-settings:'tnum' 1;
}
.res-lbl{font-size:10.5px;font-weight:800;color:var(--muted);margin-top:7px;text-transform:uppercase;letter-spacing:.1em}
.res-sub{font-size:10px;color:var(--muted);margin-top:3px}

.macro-title{font-size:11.5px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.macro-title::before{content:"";flex:0 0 4px;height:14px;border-radius:2px;background:linear-gradient(180deg,var(--brand-400),var(--brand-600))}
.macro-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px}
.macro-box{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-md);
  padding:14px 8px;text-align:center;
  transition:transform var(--t) var(--ease-out),border-color var(--t);
  box-shadow:var(--sh-xs);
}
.macro-box:hover{transform:translateY(-2px);border-color:var(--accent-muted)}
.macro-val{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-size:21px;font-weight:800;color:var(--text);letter-spacing:-.01em;font-feature-settings:'tnum' 1}
.macro-lbl{font-size:11px;color:var(--muted);margin-top:4px;font-weight:600}
.macro-g{font-size:10.5px;color:var(--accent);font-weight:800;margin-top:3px}
.res-note{
  font-size:13px;color:var(--text-soft);
  line-height:1.65;padding:14px 16px;
  background:var(--accent-soft);
  border-radius:var(--r-md);
  border:1px solid var(--accent-muted);
}
html.dark .res-note{background:var(--accent-light);border-color:var(--accent-muted);color:var(--text-soft)}

/* Empty state for results */
.empty-results{
  border:2px dashed var(--border-strong);
  border-radius:var(--r-xl);
  padding:38px 24px;
  text-align:center;
  background:var(--surface-2);
  display:flex;flex-direction:column;align-items:center;gap:10px;
  animation:fadeUp .4s var(--ease-out) both;
}
.empty-results svg{width:54px;height:54px;color:var(--accent);fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round;opacity:.8}
.empty-results-title{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-size:16px;font-weight:700;color:var(--text)}
.empty-results-text{font-size:13px;color:var(--muted);max-width:240px;line-height:1.55}

/* ── Foto panel ── */
.foto-grid{display:grid;grid-template-columns:1fr;gap:20px;align-items:start}
@media(min-width:980px){.foto-grid{grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:24px}}

.foto-drop{
  border:2px dashed var(--border-strong);
  border-radius:var(--r-xl);
  padding:36px 22px;min-height:240px;
  display:flex;align-items:center;justify-content:center;flex-direction:column;gap:14px;
  cursor:pointer;
  transition:all var(--t) var(--ease-out);
  background:var(--surface-2);
  position:relative;
  overflow:hidden;
}
.foto-drop:hover,.foto-drop.drag{
  border-color:var(--accent);
  background:var(--accent-soft);
  transform:translateY(-2px);
  box-shadow:0 12px 32px -10px rgba(16,185,129,.3);
}
.foto-drop:hover .foto-icon-svg{transform:scale(1.1) rotate(-3deg)}
#foto-preview{width:100%;border-radius:var(--r-lg);max-height:360px;object-fit:contain;display:block}
#foto-placeholder{display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center}
.foto-icon-svg{
  width:54px;height:54px;
  color:var(--accent);
  transition:transform var(--t) var(--ease-spring);
  fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;
}
.foto-hint{font-size:14.5px;color:var(--text-soft);font-weight:600;line-height:1.4}
.foto-hint small{display:block;color:var(--muted);font-size:12px;font-weight:500;margin-top:4px}
.foto-pick-btn{
  padding:10px 24px;
  background:var(--accent-light);
  border:1px solid var(--accent-muted);
  border-radius:var(--r-pill);
  font-size:13px;font-weight:800;color:var(--accent);
  cursor:pointer;margin-top:4px;
  transition:all var(--t) var(--ease-out);
}
.foto-pick-btn:hover{background:var(--accent-muted);transform:translateY(-1px)}
.foto-pick-btn:active{transform:scale(.98)}
.foto-status{font-size:13.5px;color:var(--muted);text-align:center;margin:14px 0 4px;min-height:20px;font-weight:500}
.foto-result{animation:fadeUp .4s var(--ease-out) both}
.foto-food-name{font-size:15px;font-weight:700;text-align:center;margin-bottom:6px;color:var(--text);text-transform:capitalize;letter-spacing:-.1px}
.foto-kcal-big{
  font-family:'Plus Jakarta Sans','Inter',sans-serif;
  font-size:68px;font-weight:800;
  background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
  -webkit-background-clip:text;background-clip:text;
  -webkit-text-fill-color:transparent;
  text-align:center;line-height:1;
  margin-bottom:18px;letter-spacing:-3px;
  font-feature-settings:'tnum' 1;
  animation:pop .5s var(--ease-spring) both;
}
.foto-kcal-unit{font-size:20px;font-weight:700;opacity:.65;-webkit-text-fill-color:initial;background:none;color:var(--muted);margin-left:6px}
.foto-portion-row{
  display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;
  padding:14px 16px;
  background:var(--surface-2);
  border-radius:var(--r-md);
  border:1px solid var(--border);
}
.foto-portion-row .calc-label{margin-bottom:0;flex-shrink:0}
.foto-slider{flex:1;min-width:80px;accent-color:var(--accent);height:4px}
.foto-slider-val{font-size:14px;font-weight:800;color:var(--accent);min-width:60px;text-align:right;font-feature-settings:'tnum' 1}
.foto-macros{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px}
.foto-macro-box{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-md);
  padding:13px 8px;text-align:center;
  transition:transform var(--t) var(--ease-out);
  box-shadow:var(--sh-xs);
}
.foto-macro-box:hover{transform:translateY(-2px)}
.foto-macro-val{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-size:19px;font-weight:800;color:var(--text);font-feature-settings:'tnum' 1}
.foto-macro-lbl{font-size:10px;color:var(--muted);margin-top:4px;font-weight:800;text-transform:uppercase;letter-spacing:.08em}
.foto-tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;justify-content:center}
.tag{
  font-size:11px;padding:5px 12px;
  border-radius:var(--r-pill);
  background:var(--accent-light);color:var(--accent);
  font-weight:800;
  border:1px solid var(--accent-muted);
}
.foto-disclaimer{font-size:11.5px;color:var(--muted);text-align:center;line-height:1.55;padding:0 4px}

/* ── Diary panel ── */
.diary-layout{display:grid;grid-template-columns:1fr;gap:18px}
.diary-toolbar{
  display:flex;align-items:center;justify-content:space-between;gap:14px;
  padding:14px 16px;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-lg);
  box-shadow:var(--sh-xs);
  flex-wrap:wrap;
}
.diary-nav{display:flex;align-items:center;gap:10px}
.diary-nav-btn{
  background:var(--surface-2);border:1px solid var(--border);
  border-radius:11px;
  width:38px;height:38px;cursor:pointer;
  color:var(--text-soft);font-size:18px;
  display:flex;align-items:center;justify-content:center;
  transition:all var(--t) var(--ease-out);
}
.diary-nav-btn:hover{color:var(--accent);background:var(--accent-soft);border-color:var(--accent-muted)}
.diary-nav-btn:active{transform:scale(.92)}
.diary-date-lbl{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-size:16px;font-weight:700;color:var(--text);letter-spacing:-.2px}
.diary-today-tag{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;padding:5px 11px;border-radius:var(--r-pill);background:var(--accent-light);color:var(--accent);border:1px solid var(--accent-muted)}

.summary-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
@media(min-width:720px){.summary-grid{grid-template-columns:repeat(4,1fr)}}
.summary-card{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-lg);
  padding:16px 16px 18px;
  box-shadow:var(--sh-xs);
  transition:transform var(--t) var(--ease-out),box-shadow var(--t);
  animation:fadeUp .35s var(--ease-out) both;
  position:relative;overflow:hidden;
}
.summary-card::before{
  content:"";position:absolute;top:0;left:0;width:100%;height:3px;
  background:linear-gradient(90deg,var(--brand-400),var(--brand-600));
  opacity:0;transition:opacity var(--t);
}
.summary-card:hover{transform:translateY(-3px);box-shadow:var(--sh-sm)}
.summary-card:hover::before{opacity:1}
.summary-card:nth-child(2)::before{background:linear-gradient(90deg,#a78bfa,#7c3aed)}
.summary-card:nth-child(3)::before{background:linear-gradient(90deg,var(--warm-400),var(--warm-600))}
.summary-card:nth-child(4)::before{background:linear-gradient(90deg,var(--cool-300),var(--cool-500))}
.summary-card:nth-child(1){animation-delay:0s}
.summary-card:nth-child(2){animation-delay:.05s}
.summary-card:nth-child(3){animation-delay:.1s}
.summary-card:nth-child(4){animation-delay:.15s}
.summary-card-lbl{font-size:10.5px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px}
.summary-card-val{font-family:'Plus Jakarta Sans','Inter',sans-serif;font-size:22px;font-weight:800;color:var(--text);font-feature-settings:'tnum' 1;letter-spacing:-.02em}
.summary-card-goal{font-size:11.5px;color:var(--muted);margin-top:2px;font-feature-settings:'tnum' 1}
.progress-bar{height:7px;border-radius:4px;background:var(--surface-2);margin-top:11px;overflow:hidden;border:1px solid var(--border)}
.progress-fill{height:100%;border-radius:4px;transition:width .6s var(--ease-out);position:relative;overflow:hidden}
.progress-fill::after{
  content:"";position:absolute;inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);
  background-size:200% 100%;
  animation:shimmer 2.5s linear infinite;
}
.progress-fill.ok{background:linear-gradient(90deg,var(--brand-400),var(--brand-600))}
.progress-fill.warn{background:linear-gradient(90deg,#fbbf24,#f59e0b)}
.progress-fill.over{background:linear-gradient(90deg,#f87171,#ef4444)}

.diary-body{display:grid;grid-template-columns:1fr;gap:18px}
@media(min-width:1100px){.diary-body{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px;align-items:start}}

.diary-section-title{font-size:11.5px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin:0 0 12px;display:flex;align-items:center;gap:8px}
.diary-section-title::before{content:"";flex:0 0 4px;height:14px;border-radius:2px;background:linear-gradient(180deg,var(--brand-400),var(--brand-600))}
.diary-section{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-xl);
  padding:18px;
  box-shadow:var(--sh-xs);
}
.diary-entry{
  display:flex;align-items:center;gap:12px;
  padding:13px 14px;
  background:var(--surface-2);
  border:1px solid var(--border);
  border-radius:var(--r-sm);
  margin-bottom:8px;
  transition:all var(--t) var(--ease-out);
  animation:slideIn .25s var(--ease-out) both;
}
.diary-entry:hover{border-color:var(--accent-muted);transform:translateX(2px);background:var(--surface)}
.diary-entry-name{flex:1;font-size:14.5px;font-weight:600;color:var(--text)}
.diary-entry-meta{font-size:12.5px;color:var(--muted);font-feature-settings:'tnum' 1}
.diary-del{background:transparent;border:none;cursor:pointer;color:var(--muted);font-size:16px;line-height:1;padding:6px 8px;border-radius:8px;transition:all var(--t) var(--ease-out)}
.diary-del:hover{color:#ef4444;background:rgba(239,68,68,.1)}
.diary-empty{
  font-size:13.5px;color:var(--muted);
  text-align:center;padding:28px 18px;
  background:var(--surface-2);
  border:1.5px dashed var(--border);
  border-radius:var(--r-md);
}
.diary-add-form{
  display:flex;gap:8px;flex-wrap:wrap;align-items:stretch;
  margin-top:12px;
  padding:12px;
  background:var(--surface-2);
  border:1px solid var(--border);
  border-radius:var(--r-md);
}
.diary-add-form input{
  flex:1;min-width:120px;padding:11px 14px;
  border:1.5px solid var(--border);
  border-radius:var(--r-sm);
  font-size:14px;
  background:var(--surface);color:var(--text);
  outline:none;
  transition:all var(--t);
}
.diary-add-form input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-muted)}
.diary-g-inp{max-width:90px;min-width:70px;flex:none}
.diary-add-btn{
  padding:11px 22px;
  background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
  color:#fff;border:none;
  border-radius:var(--r-sm);
  font-size:13.5px;font-weight:800;cursor:pointer;
  white-space:nowrap;
  box-shadow:var(--sh-glow);
  transition:transform var(--t) var(--ease-spring),filter var(--t);
}
.diary-add-btn:hover{transform:translateY(-1px);filter:brightness(1.05)}
.diary-add-btn:active{transform:scale(.97)}
.diary-add-err{font-size:12.5px;color:#ef4444;margin-top:8px;min-height:16px;font-weight:600}

.chart-wrap{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--r-xl);
  padding:18px;
  box-shadow:var(--sh-xs);
  position:relative;overflow:hidden;
}
.chart-wrap-title{font-size:11.5px;font-weight:800;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.chart-wrap-title::before{content:"";flex:0 0 4px;height:14px;border-radius:2px;background:linear-gradient(180deg,var(--brand-400),var(--brand-600))}
.chart-fallback{font-size:13px;color:var(--muted);text-align:center;padding:20px 0;display:none}

.add-to-diary-btn{
  margin-top:10px;padding:8px 16px;
  background:var(--accent-light);
  border:1px solid var(--accent-muted);
  border-radius:var(--r-pill);
  font-size:12px;font-weight:800;color:var(--accent);
  cursor:pointer;
  transition:all var(--t) var(--ease-out);
  display:inline-flex;align-items:center;gap:6px;
}
.add-to-diary-btn:hover{background:var(--accent-muted);transform:translateY(-1px)}
.add-to-diary-btn:active{transform:scale(.98)}
.alert-card{
  margin-top:10px;padding:12px 15px;
  border-radius:var(--r-sm);
  border-left:3px solid;
  font-size:12.5px;line-height:1.55;
  animation:slideIn .3s var(--ease-out) both;
}
.alert-card.green{border-color:var(--accent);background:var(--accent-soft);color:var(--brand-800)}
.alert-card.yellow{border-color:#f59e0b;background:#fefce8;color:#92400e}
.alert-card.red{border-color:#ef4444;background:#fef2f2;color:#991b1b}
html.dark .alert-card.green{background:var(--accent-light);color:var(--brand-200)}
html.dark .alert-card.yellow{background:#2a1f00;color:#fbbf24}
html.dark .alert-card.red{background:#240a0a;color:#f87171}

/* ── Modal ── */
.modal-overlay{
  position:fixed;inset:0;z-index:200;
  background:rgba(8,20,14,.6);
  backdrop-filter:blur(8px);
  -webkit-backdrop-filter:blur(8px);
  display:none;align-items:flex-end;justify-content:center;
}
@media(min-width:768px){.modal-overlay{align-items:center}}
.modal-overlay.open{display:flex;animation:overlayIn .25s var(--ease-out)}
@keyframes overlayIn{from{opacity:0}to{opacity:1}}
.modal-sheet{
  background:var(--surface);
  border-radius:var(--r-2xl) var(--r-2xl) 0 0;
  padding:26px 22px 32px;
  width:100%;max-width:520px;
  box-shadow:var(--sh-lg);
  animation:sheetUp .4s var(--ease-spring) both;
  overflow-y:auto;max-height:90vh;
  position:relative;
  border:1px solid var(--border);border-bottom:none;
}
@media(min-width:768px){.modal-sheet{border-radius:var(--r-2xl);border-bottom:1px solid var(--border);margin:0 18px}}
.modal-sheet::before{
  content:"";display:block;
  width:40px;height:4px;
  background:var(--border-strong);
  border-radius:2px;
  margin:-12px auto 16px;
}
@media(min-width:768px){.modal-sheet::before{display:none}}
@keyframes sheetUp{from{transform:translateY(100%)}to{transform:translateY(0)}}
.modal-title{
  font-family:'Plus Jakarta Sans','Inter',sans-serif;
  font-size:20px;font-weight:800;letter-spacing:-.4px;
  margin-bottom:22px;color:var(--text);
}
.modal-actions{display:flex;gap:10px;margin-top:24px}
.modal-btn{
  flex:1;padding:14px;
  border-radius:var(--r-md);
  font-size:14px;font-weight:800;cursor:pointer;
  border:none;
  transition:all var(--t) var(--ease-out);
}
.modal-btn.primary{
  background:linear-gradient(135deg,var(--brand-500),var(--brand-700));
  color:#fff;
  box-shadow:var(--sh-glow);
}
.modal-btn.primary:hover{transform:translateY(-1px);filter:brightness(1.05)}
.modal-btn.primary:active{transform:scale(.98)}
.modal-btn.secondary{background:var(--surface-2);border:1.5px solid var(--border);color:var(--text)}
.modal-btn.secondary:hover{border-color:var(--accent-muted);color:var(--accent)}

/* ── Keyframes ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideIn{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
@keyframes pop{0%{transform:scale(.85);opacity:0}60%{transform:scale(1.03);opacity:1}100%{transform:scale(1)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}

/* ── Responsive tweaks ── */
@media(max-width:560px){
  .res-row{grid-template-columns:1fr 1fr;gap:8px}
  .res-row .res-box.accent{grid-column:span 2}
  .res-val{font-size:22px}
  .macro-val{font-size:19px}
  .foto-macros{grid-template-columns:repeat(3,1fr)}
  .foto-kcal-big{font-size:56px;letter-spacing:-2.4px}
  .diary-toolbar{padding:12px 14px}
  .diary-date-lbl{font-size:14.5px}
}

/* ── Reduced motion ── */
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{
    animation-duration:.01ms !important;
    animation-iteration-count:1 !important;
    transition-duration:.01ms !important;
  }
  body::before{animation:none}
  .card::before,.progress-fill::after{animation:none}
}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js" onerror="window._chartJSFailed=true"></script>
</head>
<body>
<script>
  window.si = window.si || function () { (window.siq = window.siq || []).push(arguments); };
</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
<div id="splash">
  <video id="splash-video" playsinline muted autoplay></video>
</div>
<div class="app">
  <!-- Sidebar (desktop) -->
  <aside class="sidebar" aria-label="Navegaci\u00f3n lateral">
    <div class="brand">
      <div class="brand-logo">
        <img src="/logo.png" alt="NutrIA logo">
      </div>
      <div>
        <div class="brand-name">NutrIA</div>
        <div class="brand-tag">Asistente de nutrici\u00f3n</div>
      </div>
    </div>
    <div class="side-section">Navegaci\u00f3n</div>
    <button class="nav-tab active" data-tab="chat" aria-label="Chat">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
      <span class="nav-lbl">Chat IA</span>
    </button>
    <button class="nav-tab" data-tab="diario" aria-label="Diario">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
      <span class="nav-lbl">Diario</span>
    </button>
    <button class="nav-tab" data-tab="calc" aria-label="Calculadora">
      <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M8 10h8M8 14h4"/></svg>
      <span class="nav-lbl">Macros</span>
    </button>
    <button class="nav-tab" data-tab="foto" aria-label="An\u00e1lisis por foto">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
      <span class="nav-lbl">Foto IA</span>
    </button>
  </aside>

  <!-- Main column -->
  <div class="main">
    <!-- Topbar -->
    <header class="topbar">
      <div class="topbar-mobile-brand">
        <div class="brand-logo">
          <img src="/logo.png" alt="NutrIA logo">
        </div>
        <div class="brand-name">NutrIA</div>
      </div>
      <div class="topbar-title">
        <h1 id="topbar-title-text">NutrIA</h1>
        <p id="topbar-title-sub">Pregunta lo que quieras sobre nutrici\u00f3n</p>
      </div>
      <div class="topbar-end">
        <button id="prof-btn" class="hdr-btn" title="Perfil" aria-label="Perfil de usuario">
          <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </button>
        <button id="dm" class="hdr-btn" title="Modo oscuro" aria-label="Alternar modo oscuro">
          <svg id="dm-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
        </button>
      </div>
    </header>

    <!-- Panel stack -->
    <div class="panel-stack">

      <!-- CHAT panel -->
      <div id="panel-chat" class="panel active">
        <div class="chat-layout">
          <div class="chat-main">
            <div class="chat-suggest" id="chat-suggest" aria-label="Sugerencias">
              <button class="chip" data-prompt="\u00bfQu\u00e9 puedo cocinar con pollo y arroz?"><svg viewBox="0 0 24 24"><path d="M12 3v18M3 12h18"/></svg>Receta con pollo y arroz</button>
              <button class="chip" data-prompt="\u00bfCu\u00e1ntas calor\u00edas tiene el salm\u00f3n?"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>Calor\u00edas del salm\u00f3n</button>
              <button class="chip" data-prompt="\u00bfLa avena es buena para desayunar?"><svg viewBox="0 0 24 24"><path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z"/></svg>\u00bfAvena al desayuno?</button>
              <button class="chip" data-prompt="Dame un men\u00fa alto en prote\u00edna para hoy"><svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="3"/><path d="M9 9h6M9 13h6M9 17h4"/></svg>Men\u00fa alto en prote\u00edna</button>
            </div>
            <div class="msgs" id="msgs">
              <div class="m bot">
                <div class="avatar"><svg viewBox="0 0 24 24"><path d="M12 2a3 3 0 013 3v0a3 3 0 01-3 3 3 3 0 01-3-3v0a3 3 0 013-3z"/><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/></svg></div>
                <div class="b">
                  Hola, soy <strong>NutrIA</strong>.<br><br>
                  Preg\u00fantame sobre recetas, calor\u00edas o nutrici\u00f3n. Por ejemplo:<br>
                  \u2014 <em>Qu\u00e9 puedo cocinar con pollo y arroz</em><br>
                  \u2014 <em>Cu\u00e1ntas calor\u00edas tiene el salm\u00f3n</em><br>
                  \u2014 <em>La avena es buena para desayunar?</em>
                </div>
              </div>
            </div>
            <div class="composer">
              <input type="text" id="inp" placeholder="Escribe tu pregunta..." autocomplete="off" enterkeyhint="send" inputmode="text">
              <button id="btn" aria-label="Enviar"><svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>
            </div>
          </div>
          <aside class="chat-rail" aria-label="Resumen lateral">
            <div class="rail-card">
              <div class="rail-card-title">Hoy</div>
              <div class="rail-stat"><span>Calor\u00edas</span><span class="rail-stat-val" id="rail-kcal">\u2014</span></div>
              <div class="rail-stat"><span>Prote\u00edna</span><span class="rail-stat-val" id="rail-prot">\u2014</span></div>
              <div class="rail-stat"><span>Carbohidratos</span><span class="rail-stat-val" id="rail-carb">\u2014</span></div>
              <div class="rail-stat"><span>Grasas</span><span class="rail-stat-val" id="rail-fat">\u2014</span></div>
            </div>
            <div class="rail-card">
              <div class="rail-card-title">Atajos</div>
              <div class="rail-tip">Cambia a <strong>Diario</strong> para registrar comidas o a <strong>Foto IA</strong> para estimar calor\u00edas de un plato.</div>
            </div>
            <div class="rail-card">
              <div class="rail-card-title">Consejo</div>
              <div class="rail-tip">Bebe agua antes y durante las comidas para mejorar la <strong>saciedad</strong> y la digesti\u00f3n.</div>
            </div>
          </aside>
        </div>
      </div>

      <!-- DIARIO panel -->
      <div id="panel-diario" class="panel">
        <div class="content-scroll">
          <div class="content-wide diary-layout">
            <div class="diary-toolbar">
              <div class="diary-nav">
                <button class="diary-nav-btn" id="diary-prev" aria-label="D\u00eda anterior">&#8592;</button>
                <span class="diary-date-lbl" id="diary-date-lbl"></span>
                <button class="diary-nav-btn" id="diary-next" aria-label="D\u00eda siguiente">&#8594;</button>
              </div>
              <span class="diary-today-tag" id="diary-today-tag" style="display:none">Hoy</span>
            </div>
            <div class="summary-grid">
              <div class="summary-card">
                <div class="summary-card-lbl">Calor\u00edas</div>
                <div class="summary-card-val" id="sc-kcal-val">0</div>
                <div class="summary-card-goal" id="sc-kcal-goal">/ \u2014 kcal</div>
                <div class="progress-bar"><div class="progress-fill ok" id="sc-kcal-bar" style="width:0%"></div></div>
              </div>
              <div class="summary-card">
                <div class="summary-card-lbl">Prote\u00edna</div>
                <div class="summary-card-val" id="sc-prot-val">0g</div>
                <div class="summary-card-goal" id="sc-prot-goal">/ \u2014 g</div>
                <div class="progress-bar"><div class="progress-fill ok" id="sc-prot-bar" style="width:0%"></div></div>
              </div>
              <div class="summary-card">
                <div class="summary-card-lbl">Carbos</div>
                <div class="summary-card-val" id="sc-carbs-val">0g</div>
                <div class="summary-card-goal" id="sc-carbs-goal">/ \u2014 g</div>
                <div class="progress-bar"><div class="progress-fill ok" id="sc-carbs-bar" style="width:0%"></div></div>
              </div>
              <div class="summary-card">
                <div class="summary-card-lbl">Grasa</div>
                <div class="summary-card-val" id="sc-fat-val">0g</div>
                <div class="summary-card-goal" id="sc-fat-goal">/ \u2014 g</div>
                <div class="progress-bar"><div class="progress-fill ok" id="sc-fat-bar" style="width:0%"></div></div>
              </div>
            </div>
            <div class="diary-body">
              <div class="diary-section">
                <div class="diary-section-title">Entradas del d\u00eda</div>
                <div id="diary-list"></div>
                <div class="diary-add-form">
                  <input type="text" id="diary-food-inp" placeholder="Nombre del alimento">
                  <input type="number" id="diary-g-inp" class="diary-g-inp" placeholder="g" value="100" min="1">
                  <button class="diary-add-btn" id="diary-add-btn">A\u00f1adir</button>
                </div>
                <div class="diary-add-err" id="diary-add-err"></div>
              </div>
              <div class="chart-wrap">
                <div class="chart-wrap-title">\u00daltimos 7 d\u00edas \u2014 Calor\u00edas</div>
                <div style="position:relative;height:220px">
                  <canvas id="diary-chart"></canvas>
                </div>
                <div class="chart-fallback" id="chart-fallback">Gr\u00e1fica no disponible</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- CALC panel -->
      <div id="panel-calc" class="panel">
        <div class="content-scroll">
          <div class="content-wide">
            <div class="calc-grid">
              <div class="card">
                <div class="card-title">
                  <span class="card-title-icon"><svg viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M8 10h8M8 14h4"/></svg></span>
                  Calculadora de macros
                </div>
                <div class="card-sub">Calcula tu BMR, TDEE y reparto de macronutrientes seg\u00fan tu objetivo.</div>
                <div class="calc-row">
                  <div class="calc-group">
                    <label class="calc-label">Sexo</label>
                    <div class="seg" id="sexo-seg">
                      <button class="seg-btn active" data-val="h">Hombre</button>
                      <button class="seg-btn" data-val="m">Mujer</button>
                    </div>
                  </div>
                </div>
                <div class="calc-row two">
                  <div class="calc-group">
                    <label class="calc-label">Edad (a\u00f1os)</label>
                    <input class="calc-inp" type="number" id="c-edad" min="10" max="100" placeholder="25">
                  </div>
                  <div class="calc-group">
                    <label class="calc-label">Peso (kg)</label>
                    <input class="calc-inp" type="number" id="c-peso" min="30" max="300" placeholder="70">
                  </div>
                </div>
                <div class="calc-row">
                  <div class="calc-group">
                    <label class="calc-label">Altura (cm)</label>
                    <input class="calc-inp" type="number" id="c-altura" min="100" max="250" placeholder="170">
                  </div>
                </div>
                <div class="calc-group">
                  <label class="calc-label">Actividad f\u00edsica</label>
                  <select class="calc-sel" id="c-act">
                    <option value="1.2">Sedentario (sin ejercicio)</option>
                    <option value="1.375">Poco activo (1\u20133 d\u00edas/semana)</option>
                    <option value="1.55" selected>Moderado (3\u20135 d\u00edas/semana)</option>
                    <option value="1.725">Activo (6\u20137 d\u00edas/semana)</option>
                    <option value="1.9">Muy activo (2 sesiones/d\u00eda)</option>
                  </select>
                </div>
                <div class="calc-group">
                  <label class="calc-label">Objetivo</label>
                  <div class="seg" id="goal-seg">
                    <button class="seg-btn active" data-val="cut">Perder grasa</button>
                    <button class="seg-btn" data-val="mant">Mantener</button>
                    <button class="seg-btn" data-val="bulk">Ganar m\u00fasculo</button>
                  </div>
                </div>
                <button class="calc-btn" id="calc-go">Calcular</button>
              </div>

              <div>
                <div class="empty-results" id="calc-empty">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
                  <div class="empty-results-title">Tus resultados</div>
                  <div class="empty-results-text">Rellena el formulario y pulsa <strong>Calcular</strong> para ver BMR, TDEE y tus macros recomendados.</div>
                </div>
                <div class="calc-result" id="calc-result" style="display:none">
                  <div class="res-row">
                    <div class="res-box">
                      <div class="res-val" id="r-bmr"></div>
                      <div class="res-lbl">BMR</div>
                      <div class="res-sub">metabolismo basal</div>
                    </div>
                    <div class="res-box accent">
                      <div class="res-val" id="r-tdee"></div>
                      <div class="res-lbl">TDEE</div>
                      <div class="res-sub">gasto total diario</div>
                    </div>
                    <div class="res-box">
                      <div class="res-val" id="r-obj"></div>
                      <div class="res-lbl">Objetivo</div>
                      <div class="res-sub" id="r-obj-lbl"></div>
                    </div>
                  </div>
                  <div>
                    <div class="macro-title">Macros diarios recomendados</div>
                    <div class="macro-row">
                      <div class="macro-box">
                        <div class="macro-val" id="r-prot"></div>
                        <div class="macro-lbl">Prote\u00edna</div>
                        <div class="macro-g" id="r-prot-g"></div>
                      </div>
                      <div class="macro-box">
                        <div class="macro-val" id="r-carb"></div>
                        <div class="macro-lbl">Carbohidratos</div>
                        <div class="macro-g" id="r-carb-g"></div>
                      </div>
                      <div class="macro-box">
                        <div class="macro-val" id="r-fat"></div>
                        <div class="macro-lbl">Grasas</div>
                        <div class="macro-g" id="r-fat-g"></div>
                      </div>
                    </div>
                  </div>
                  <div class="res-note" id="r-note"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FOTO panel -->
      <div id="panel-foto" class="panel">
        <div class="content-scroll">
          <div class="content-wide">
            <div class="foto-grid">
              <div class="card">
                <div class="card-title">
                  <span class="card-title-icon"><svg viewBox="0 0 24 24"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg></span>
                  Estimar calor\u00edas por foto
                </div>
                <div class="card-sub">Sube una imagen de tu comida y la IA estima calor\u00edas y macros al instante.</div>
                <div class="foto-drop" id="foto-drop">
                  <input type="file" id="foto-inp" accept="image/*" capture="environment" style="display:none">
                  <div id="foto-preview-wrap" style="display:none;width:100%">
                    <img id="foto-preview" alt="preview">
                  </div>
                  <div id="foto-placeholder">
                    <svg class="foto-icon-svg" viewBox="0 0 24 24" aria-hidden="true"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
                    <div class="foto-hint">Arrastra una foto o haz click<small>JPG, PNG \u00b7 hasta ~10 MB</small></div>
                    <button class="foto-pick-btn" id="foto-pick">Elegir imagen</button>
                  </div>
                </div>
                <button class="calc-btn" id="foto-go" style="display:none;margin-top:14px">Analizar calor\u00edas</button>
                <div id="foto-status" class="foto-status"></div>
              </div>

              <div>
                <div class="empty-results" id="foto-empty">
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
                  <div class="empty-results-title">Resultado del an\u00e1lisis</div>
                  <div class="empty-results-text">Sube una foto y pulsa <strong>Analizar</strong>. Aqu\u00ed ver\u00e1s las calor\u00edas, macros y etiquetas detectadas.</div>
                </div>
                <div id="foto-result" class="foto-result card" style="display:none;animation:fadeUp .4s var(--ease-out) both">
                  <div class="foto-food-name" id="foto-food-name"></div>
                  <div class="foto-kcal-big" id="foto-kcal-big"></div>
                  <div class="foto-portion-row">
                    <label class="calc-label">Porci\u00f3n (g)</label>
                    <input type="range" id="foto-slider" min="50" max="500" value="100" step="10" class="foto-slider">
                    <span class="foto-slider-val" id="foto-slider-val">100 g</span>
                  </div>
                  <div class="foto-macros" id="foto-macros"></div>
                  <div class="foto-tags" id="foto-tags"></div>
                  <div class="foto-disclaimer">Estimaci\u00f3n orientativa basada en IA. No sustituye asesoramiento nutricional profesional.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Bottom nav (mobile only) -->
    <nav class="bottom-nav" aria-label="Navegaci\u00f3n principal m\u00f3vil">
      <button class="nav-tab active" data-tab="chat" aria-label="Chat">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        <span class="nav-lbl">Chat</span>
      </button>
      <button class="nav-tab" data-tab="diario" aria-label="Diario">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
        <span class="nav-lbl">Diario</span>
      </button>
      <button class="nav-tab" data-tab="calc" aria-label="Calculadora">
        <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M8 10h8M8 14h4"/></svg>
        <span class="nav-lbl">Macros</span>
      </button>
      <button class="nav-tab" data-tab="foto" aria-label="An\u00e1lisis por foto">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
        <span class="nav-lbl">Foto</span>
      </button>
    </nav>
  </div>

  <!-- Profile modal -->
  <div id="modal-perfil" class="modal-overlay">
    <div class="modal-sheet">
      <div class="modal-title">Mi perfil</div>
      <div class="calc-group">
        <label class="calc-label">Nombre (opcional)</label>
        <input type="text" id="p-nombre" class="calc-inp" placeholder="Tu nombre">
      </div>
      <div class="calc-row two">
        <div class="calc-group">
          <label class="calc-label">Edad (a\u00f1os)</label>
          <input type="number" id="p-edad" class="calc-inp" placeholder="25" min="10" max="99">
        </div>
        <div class="calc-group">
          <label class="calc-label">Peso (kg)</label>
          <input type="number" id="p-peso" class="calc-inp" placeholder="70" min="30" max="300">
        </div>
      </div>
      <div class="calc-group">
        <label class="calc-label">Altura (cm)</label>
        <input type="number" id="p-altura" class="calc-inp" placeholder="170" min="100" max="250">
      </div>
      <div class="calc-group">
        <label class="calc-label">Sexo</label>
        <div class="seg" id="p-sexo-seg">
          <button class="seg-btn active" data-val="hombre">Hombre</button>
          <button class="seg-btn" data-val="mujer">Mujer</button>
        </div>
      </div>
      <div class="calc-group">
        <label class="calc-label">Objetivo</label>
        <div class="seg" id="p-goal-seg">
          <button class="seg-btn active" data-val="cut">Perder grasa</button>
          <button class="seg-btn" data-val="mant">Mantener</button>
          <button class="seg-btn" data-val="bulk">Ganar m\u00fasculo</button>
        </div>
      </div>
      <div class="modal-actions">
        <button id="perfil-cerrar" class="modal-btn secondary">Cerrar</button>
        <button id="perfil-guardar" class="modal-btn primary">Guardar</button>
      </div>
    </div>
  </div>
</div>
<script src="/app.js"></script>

</body>
</html>"""

# (script moved to /app.js endpoint below)


def normalizar_texto(texto):
    texto = texto.lower()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokens_relevantes(texto):
    stopwords = {
        "de", "del", "la", "el", "los", "las", "con", "sin", "para",
        "por", "un", "una", "y", "o", "que", "en", "esa", "ese", "esta", "este",
    }
    return [t for t in normalizar_texto(texto).split() if len(t) > 2 and t not in stopwords]



def load_json_file(path, empty_value):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return empty_value


recipes_db = load_json_file("data/recipes_large.json", {"recetas": []})
calories_db = load_json_file(CALORIES_DATA_PATH, {"alimentos": []})



def buscar_alimentos_similares(termino):
    termino_normalizado = normalizar_texto(termino)
    resultados = []
    for alimento in calories_db.get("alimentos", []):
        nombre_normalizado = normalizar_texto(alimento["nombre"])
        score = 0
        if termino_normalizado == nombre_normalizado:
            score = 100
        elif termino_normalizado and termino_normalizado in nombre_normalizado:
            score = 80
        else:
            interseccion = set(tokens_relevantes(termino)) & set(tokens_relevantes(alimento["nombre"]))
            if interseccion:
                score = len(interseccion) * 20
        if score > 0:
            resultados.append((score, alimento))
    resultados.sort(key=lambda item: (-item[0], item[1]["nombre"]))
    return [alimento for _, alimento in resultados[:5]]


def buscar_alimento(termino):
    resultados = buscar_alimentos_similares(termino)
    return resultados[0] if resultados else None




GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = (
    "Eres NutrIA, un asistente de nutrición experto en cocina española e internacional. "
    "Respondes siempre en español, de forma clara, amigable y concisa. "
    "Usa formato HTML simple: <strong> para énfasis, <br> para saltos de línea, <em> para cursiva. "
    "No uses markdown (no uses **, ##, *, etc). "
    "Cuando el sistema te proporcione datos nutricionales exactos de la base de datos, úsalos — son precisos. "
    "Para estimaciones propias, indícalo brevemente. "
    "Mantén las respuestas útiles y al punto, sin ser demasiado largas."
)


def _buscar_datos_locales(mensaje):
    texto = normalizar_texto(mensaje)
    encontrados = []
    for alimento in calories_db.get("alimentos", []):
        nombre_norm = normalizar_texto(alimento.get("nombre", ""))
        if nombre_norm and len(nombre_norm) > 2 and nombre_norm in texto:
            encontrados.append(alimento)
    if not encontrados:
        try:
            analisis = nlp.procesar(mensaje)
            if analisis.get("alimento"):
                candidatos = buscar_alimentos_similares(analisis["alimento"])
                encontrados = candidatos[:3]
        except Exception:
            pass
    return encontrados[:4]


def generar_respuesta(mensaje, contexto=None, perfil=None):
    contexto = contexto or {}
    historial = contexto.get("historial", [])

    perfil_info = ""
    if perfil:
        perfil_info = (
            f"\nPerfil del usuario: {perfil.get('nombre','Anónimo')}, "
            f"{perfil.get('edad',0)} años, {perfil.get('peso',0)} kg, "
            f"{perfil.get('altura',0)} cm, sexo={perfil.get('sexo','')}, "
            f"objetivo={perfil.get('objetivo','')}."
        )

    datos_locales = _buscar_datos_locales(mensaje)
    mensaje_con_datos = mensaje
    if datos_locales:
        datos_str = json.dumps(datos_locales, ensure_ascii=False)
        mensaje_con_datos += f"\n[Base de datos local — usa estos datos: {datos_str}]"

    messages = [{"role": "system", "content": SYSTEM_PROMPT + perfil_info}]
    for turno in historial:
        role = "assistant" if turno["role"] == "model" else "user"
        messages.append({"role": role, "content": turno["text"]})
    messages.append({"role": "user", "content": mensaje_con_datos})

    if not GROQ_API_KEY:
        return {"respuesta": "El servicio de IA no está configurado. Contacta al administrador.", "contexto": contexto}

    try:
        cliente = Groq(api_key=GROQ_API_KEY)
        response = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=600,
            temperature=0.7,
        )
        respuesta = response.choices[0].message.content.strip()

        historial.append({"role": "user", "text": mensaje})
        historial.append({"role": "model", "text": respuesta})
        contexto["historial"] = historial[-10:]

        result = {"respuesta": respuesta, "contexto": contexto}
        if datos_locales:
            first = datos_locales[0]
            result["alimento_detectado"] = {
                "nombre": first.get("nombre", ""),
                "kcal": first.get("calorias", 0),
                "proteina": first.get("proteina", 0),
                "carbos": first.get("carbohidratos", 0),
                "grasa": first.get("grasas", 0),
            }
        return result

    except Exception as e:
        return {
            "respuesta": (
                "Hubo un problema al conectar con la IA.<br>"
                f"<small style='color:#6b7280'>{str(e)[:120]}</small>"
            ),
            "contexto": contexto,
        }


JS_CODE = r"""(function(){
var _splash=document.getElementById('splash');
var _splashVideo=document.getElementById('splash-video');
var _splashDismissed=false;
function _dismissSplash(){
  if(_splashDismissed)return;
  _splashDismissed=true;
  clearTimeout(_splashFallback);
  _splash.classList.add('hidden');
  _splash.addEventListener('transitionend',function(){_splash.remove();},{once:true});
}
var _isMobilePortrait=(window.innerWidth<=767&&window.innerHeight>window.innerWidth)
  ||window.matchMedia('(max-width:767px) and (orientation:portrait)').matches;
_splashVideo.src=_isMobilePortrait?'/anim-9-16.mp4':'/anim-4-3.mp4';
_splashVideo.addEventListener('timeupdate',function(){
  if(_splashVideo.duration&&_splashVideo.currentTime>=_splashVideo.duration-1.5)_dismissSplash();
});
_splashVideo.addEventListener('ended',_dismissSplash);
_splash.addEventListener('click',_dismissSplash);
_splashVideo.addEventListener('error',_dismissSplash);
var _splashFallback=setTimeout(_dismissSplash,8000);
_splashVideo.play().catch(_dismissSplash);
var dmBtn=document.getElementById('dm');
var dmIcon=document.getElementById('dm-icon');
var msgs=document.getElementById('msgs');
var inp=document.getElementById('inp');
var btn=document.getElementById('btn');
var SUN='<path d="M12 4.5a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0112 4.5zm0 13.5a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0v-.75A.75.75 0 0112 18zm7.5-6.75a.75.75 0 010 1.5h-.75a.75.75 0 010-1.5h.75zm-15 0a.75.75 0 010 1.5H3.75a.75.75 0 010-1.5H4.5zm12.86-5.61a.75.75 0 010 1.06l-.53.53a.75.75 0 01-1.06-1.06l.53-.53a.75.75 0 011.06 0zm-10.6 10.6a.75.75 0 010 1.06l-.53.53a.75.75 0 01-1.06-1.06l.53-.53a.75.75 0 011.06 0zm10.6 0a.75.75 0 011.06 1.06l-.53.53a.75.75 0 01-1.06-1.06l.53-.53a.75.75 0 010-1.06zM5.86 6.14a.75.75 0 011.06 0l.53.53A.75.75 0 016.39 7.73l-.53-.53a.75.75 0 010-1.06zM12 8.25a3.75 3.75 0 100 7.5 3.75 3.75 0 000-7.5z"/>';
var MOON='<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>';
function setDark(on){
  document.documentElement.classList.toggle('dark',on);
  dmIcon.innerHTML=on?SUN:MOON;
  try{localStorage.setItem('nutria-dark',on?'1':'0');}catch(e){}
}
var saved=null;try{saved=localStorage.getItem('nutria-dark');}catch(e){}
var prefersDark=!!(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches);
setDark(saved!==null?saved==='1':prefersDark);
dmBtn.addEventListener('click',function(){setDark(!document.documentElement.classList.contains('dark'));});
function _setActiveTab(id){
  document.querySelectorAll('.nav-tab').forEach(function(t){t.classList.toggle('active',t.dataset.tab===id);});
  document.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('active',p.id==='panel-'+id);});
}
window._setActiveTab=_setActiveTab;
document.querySelectorAll('.nav-tab').forEach(function(tab){
  tab.addEventListener('click',function(){_setActiveTab(tab.dataset.tab);});
});
// Chat suggestion chips
document.querySelectorAll('.chip[data-prompt]').forEach(function(c){
  c.addEventListener('click',function(){
    var p=c.getAttribute('data-prompt')||'';
    var inp=document.getElementById('inp');
    if(inp){inp.value=p;inp.focus();}
    var btn=document.getElementById('btn');
    if(btn)btn.click();
  });
});
// ── Profile ──
var _perfil={nombre:'',edad:0,peso:0,altura:0,sexo:'hombre',objetivo:'cut'};
(function(){
  try{var s=localStorage.getItem('nutria-profile');if(s)_perfil=JSON.parse(s);}catch(e){}
  var modal=document.getElementById('modal-perfil');
  var sexoSeg2=document.getElementById('p-sexo-seg');
  var goalSeg2=document.getElementById('p-goal-seg');
  function syncUI(){
    document.getElementById('p-nombre').value=_perfil.nombre||'';
    document.getElementById('p-edad').value=_perfil.edad||'';
    document.getElementById('p-peso').value=_perfil.peso||'';
    document.getElementById('p-altura').value=_perfil.altura||'';
    sexoSeg2.querySelectorAll('.seg-btn').forEach(function(b){b.classList.toggle('active',b.dataset.val===_perfil.sexo);});
    goalSeg2.querySelectorAll('.seg-btn').forEach(function(b){b.classList.toggle('active',b.dataset.val===_perfil.objetivo);});
  }
  syncUI();
  sexoSeg2.querySelectorAll('.seg-btn').forEach(function(b){
    b.addEventListener('click',function(){
      sexoSeg2.querySelectorAll('.seg-btn').forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');_perfil.sexo=b.dataset.val;
    });
  });
  goalSeg2.querySelectorAll('.seg-btn').forEach(function(b){
    b.addEventListener('click',function(){
      goalSeg2.querySelectorAll('.seg-btn').forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');_perfil.objetivo=b.dataset.val;
    });
  });
  document.getElementById('prof-btn').addEventListener('click',function(){
    syncUI();modal.classList.add('open');
  });
  document.getElementById('perfil-cerrar').addEventListener('click',function(){modal.classList.remove('open');});
  modal.addEventListener('click',function(e){if(e.target===modal)modal.classList.remove('open');});
  document.getElementById('perfil-guardar').addEventListener('click',function(){
    _perfil.nombre=document.getElementById('p-nombre').value.trim();
    _perfil.edad=parseFloat(document.getElementById('p-edad').value)||0;
    _perfil.peso=parseFloat(document.getElementById('p-peso').value)||0;
    _perfil.altura=parseFloat(document.getElementById('p-altura').value)||0;
    try{localStorage.setItem('nutria-profile',JSON.stringify(_perfil));}catch(e){}
    modal.classList.remove('open');
    if(typeof _renderDiary==='function')_renderDiary();
  });
})();
function _computeGoals(){
  var p=_perfil;
  if(!p.peso||!p.altura||!p.edad)return null;
  var bmr=p.sexo==='hombre'
    ?(10*p.peso+6.25*p.altura-5*p.edad+5)
    :(10*p.peso+6.25*p.altura-5*p.edad-161);
  var tdee=Math.round(bmr*1.55);
  var objCal,protFactor,fatFactor;
  if(p.objetivo==='cut'){objCal=Math.max(tdee-500,1200);protFactor=2.2;fatFactor=0.9;}
  else if(p.objetivo==='bulk'){objCal=tdee+300;protFactor=2.0;fatFactor=1.0;}
  else{objCal=tdee;protFactor=1.8;fatFactor=0.9;}
  var protG=Math.round(protFactor*p.peso);
  var fatG=Math.round(fatFactor*p.peso);
  var carbG=Math.round(Math.max(objCal-protG*4-fatG*9,0)/4);
  return{kcal:Math.round(objCal),prot:protG,carbs:carbG,fat:fatG};
}
	var ctx={last_recipe_ids:[],last_selected_recipe_id:null};
	function addMsg(html,isUser,cls){
  var m=document.createElement('div');
  m.className='m '+(isUser?'u':'bot')+(cls?' '+cls:'');
  var b=document.createElement('div');b.className='b';b.innerHTML=html;
  m.appendChild(b);msgs.appendChild(m);msgs.scrollTop=msgs.scrollHeight;return m;
}
function send(){
  var txt=inp.value.trim();if(!txt)return;
  addMsg(txt,true);inp.value='';
  var t=addMsg('Pensando...',false,'typing');
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensaje:txt,contexto:ctx,perfil:_perfil})})
    .then(function(r){return r.json();})
    .then(function(d){
      t.remove();
      if(d.contexto)ctx=d.contexto;
      var msgEl=addMsg(d.respuesta);
      if(d.alimento_detectado){
        var ad=d.alimento_detectado;
        var atdBtn=document.createElement('button');
        atdBtn.className='add-to-diary-btn';
        atdBtn.textContent='\u2295 A\u00f1adir al diario';
        atdBtn.addEventListener('click',function(){
          window._diaryAddFromChat(ad.nombre,ad.kcal,ad.proteina,ad.carbos,ad.grasa);
        });
        msgEl.querySelector('.b').appendChild(atdBtn);
      }
      _runAlerts(msgEl);
    })
    .catch(function(){t.remove();addMsg('Error de conexion. Intenta de nuevo.');});
}
inp.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
btn.addEventListener('click',send);

var sexoSeg=document.getElementById('sexo-seg');
var goalSeg=document.getElementById('goal-seg');
var calcGo=document.getElementById('calc-go');
var calcResult=document.getElementById('calc-result');
var sexoVal='h';
var goalVal='cut';
function setupSeg(seg,cb){
  seg.querySelectorAll('.seg-btn').forEach(function(b){
    b.addEventListener('click',function(){
      seg.querySelectorAll('.seg-btn').forEach(function(x){x.classList.remove('active');});
      b.classList.add('active');cb(b.dataset.val);
    });
  });
}
setupSeg(sexoSeg,function(v){sexoVal=v;});
setupSeg(goalSeg,function(v){goalVal=v;});
calcGo.addEventListener('click',function(){
  var edad=parseFloat(document.getElementById('c-edad').value);
  var peso=parseFloat(document.getElementById('c-peso').value);
  var altura=parseFloat(document.getElementById('c-altura').value);
  var act=parseFloat(document.getElementById('c-act').value);
  if(!edad||!peso||!altura||isNaN(edad)||isNaN(peso)||isNaN(altura)){
    calcGo.textContent='Rellena todos los campos';
    setTimeout(function(){calcGo.textContent='Calcular';},2000);return;
  }
  var bmr=sexoVal==='h'
    ?(10*peso+6.25*altura-5*edad+5)
    :(10*peso+6.25*altura-5*edad-161);
  bmr=Math.round(bmr);
  var tdee=Math.round(bmr*act);
  var objCal,objLabel,protFactor,fatFactor;
  if(goalVal==='cut'){objCal=Math.max(tdee-500,1200);objLabel='D\u00e9ficit \u2212500 kcal';protFactor=2.2;fatFactor=0.9;}
  else if(goalVal==='bulk'){objCal=tdee+300;objLabel='Super\u00e1vit +300 kcal';protFactor=2.0;fatFactor=1.0;}
  else{objCal=tdee;objLabel='Mantenimiento';protFactor=1.8;fatFactor=0.9;}
  var protG=Math.round(protFactor*peso);
  var fatG=Math.round(fatFactor*peso);
  var carbG=Math.round(Math.max(objCal-protG*4-fatG*9,0)/4);
  var pct=function(g,cal){return Math.round(g*cal/objCal*100);};
  document.getElementById('r-bmr').textContent=bmr+' kcal';
  document.getElementById('r-tdee').textContent=tdee+' kcal';
  document.getElementById('r-obj').textContent=objCal+' kcal';
  document.getElementById('r-obj-lbl').textContent=objLabel;
  document.getElementById('r-prot').textContent=pct(protG,4)+'%';
  document.getElementById('r-prot-g').textContent=protG+'g / d\u00eda';
  document.getElementById('r-carb').textContent=pct(carbG,4)+'%';
  document.getElementById('r-carb-g').textContent=carbG+'g / d\u00eda';
  document.getElementById('r-fat').textContent=pct(fatG,9)+'%';
  document.getElementById('r-fat-g').textContent=fatG+'g / d\u00eda';
  var notes={
    cut:'Con d\u00e9ficit de 500 kcal perder\u00e1s ~0,5 kg/semana. Prioriza prote\u00edna alta y entreno de fuerza para preservar m\u00fasculo.',
    bulk:'Super\u00e1vit controlado de 300 kcal para ganar m\u00fasculo con m\u00ednima grasa. Combina con progresivo entreno de fuerza.',
    mant:'Revisa tu peso cada 2 semanas y ajusta \u00b1100 kcal seg\u00fan evoluci\u00f3n real.'
  };
  document.getElementById('r-note').textContent=notes[goalVal];
  calcResult.style.display='flex';
  var ce=document.getElementById('calc-empty');if(ce)ce.style.display='none';
  calcResult.scrollIntoView({behavior:'smooth',block:'nearest'});
});

if('serviceWorker' in navigator){
  navigator.serviceWorker.register('/sw.js').catch(function(){});
}
// ── Diary ──
var _renderDiary;
(function(){
  var _diary={};
  var _today=new Date();
  var _curDate=new Date(_today.getFullYear(),_today.getMonth(),_today.getDate());
  function _dateKey(d){return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
  function _loadDiary(){try{var s=localStorage.getItem('nutria-diary');if(s)_diary=JSON.parse(s);}catch(e){}}
  function _saveDiary(){try{localStorage.setItem('nutria-diary',JSON.stringify(_diary));}catch(e){}}
  _loadDiary();
  function _dayEntries(key){return _diary[key]||[];}
  function _totals(entries){
    return entries.reduce(function(a,e){
      a.kcal+=(e.kcal||0);a.prot+=(e.proteina||0);a.carbs+=(e.carbos||0);a.fat+=(e.grasa||0);return a;
    },{kcal:0,prot:0,carbs:0,fat:0});
  }
  function _progressClass(pct){return pct>110?'over':pct>90?'warn':'ok';}
  function _updateBar(id,pct){
    var el=document.getElementById(id);
    if(!el)return;
    el.style.width=Math.min(pct,100)+'%';
    el.className='progress-fill '+_progressClass(pct);
  }
  function _renderSummary(){
    var key=_dateKey(_curDate);
    var t=_totals(_dayEntries(key));
    var goals=_computeGoals();
    document.getElementById('sc-kcal-val').textContent=Math.round(t.kcal);
    document.getElementById('sc-prot-val').textContent=Math.round(t.prot)+'g';
    document.getElementById('sc-carbs-val').textContent=Math.round(t.carbs)+'g';
    document.getElementById('sc-fat-val').textContent=Math.round(t.fat)+'g';
    if(goals){
      document.getElementById('sc-kcal-goal').textContent='/ '+goals.kcal+' kcal';
      document.getElementById('sc-prot-goal').textContent='/ '+goals.prot+'g';
      document.getElementById('sc-carbs-goal').textContent='/ '+goals.carbs+'g';
      document.getElementById('sc-fat-goal').textContent='/ '+goals.fat+'g';
      _updateBar('sc-kcal-bar',goals.kcal>0?Math.round(t.kcal/goals.kcal*100):0);
      _updateBar('sc-prot-bar',goals.prot>0?Math.round(t.prot/goals.prot*100):0);
      _updateBar('sc-carbs-bar',goals.carbs>0?Math.round(t.carbs/goals.carbs*100):0);
      _updateBar('sc-fat-bar',goals.fat>0?Math.round(t.fat/goals.fat*100):0);
    } else {
      ['sc-kcal-goal','sc-prot-goal','sc-carbs-goal','sc-fat-goal'].forEach(function(id){
        var el=document.getElementById(id);if(el)el.textContent='/ \u2014';
      });
    }
    // Rail card mirror
    var rk=document.getElementById('rail-kcal');if(rk)rk.textContent=Math.round(t.kcal)+(goals?(' / '+goals.kcal):'');
    var rp=document.getElementById('rail-prot');if(rp)rp.textContent=Math.round(t.prot)+'g'+(goals?(' / '+goals.prot+'g'):'');
    var rc=document.getElementById('rail-carb');if(rc)rc.textContent=Math.round(t.carbs)+'g'+(goals?(' / '+goals.carbs+'g'):'');
    var rf=document.getElementById('rail-fat');if(rf)rf.textContent=Math.round(t.fat)+'g'+(goals?(' / '+goals.fat+'g'):'');
    // Today tag
    var tag=document.getElementById('diary-today-tag');
    if(tag){
      var today=new Date();
      var isToday=today.toDateString()===_curDate.toDateString();
      tag.style.display=isToday?'inline-block':'none';
    }
  }
  function _renderList(){
    var key=_dateKey(_curDate);
    var entries=_dayEntries(key);
    var list=document.getElementById('diary-list');
    if(!entries.length){list.innerHTML='<div class="diary-empty">No hay entradas para este d\u00eda</div>';return;}
    list.innerHTML=entries.map(function(e,i){
      return '<div class="diary-entry">'+
        '<span class="diary-entry-name">'+e.nombre+'</span>'+
        '<span class="diary-entry-meta">'+e.gramos+'g \u00b7 '+Math.round(e.kcal)+' kcal</span>'+
        '<button class="diary-del" data-idx="'+i+'">\u00d7</button>'+
        '</div>';
    }).join('');
    list.querySelectorAll('.diary-del').forEach(function(btn){
      btn.addEventListener('click',function(){
        var idx=parseInt(btn.dataset.idx);
        _diary[key].splice(idx,1);
        if(!_diary[key].length)delete _diary[key];
        _saveDiary();_render();
      });
    });
  }
  function _updateDateLabel(){
    var opts={day:'numeric',month:'short',year:'numeric'};
    var lbl=document.getElementById('diary-date-lbl');
    if(lbl)lbl.textContent=_curDate.toLocaleDateString('es-ES',opts);
    var nextBtn=document.getElementById('diary-next');
    var todayKey=_dateKey(new Date());
    if(nextBtn)nextBtn.disabled=_dateKey(_curDate)===todayKey;
  }
  var _chart=null;
  function _renderChart(){
    var canvas=document.getElementById('diary-chart');
    var fallback=document.getElementById('chart-fallback');
    if(!canvas)return;
    if(typeof Chart==='undefined'){
      canvas.style.display='none';
      if(fallback)fallback.style.display='block';
      return;
    }
    var labels=[],data=[];
    for(var i=6;i>=0;i--){
      var d=new Date(_today.getFullYear(),_today.getMonth(),_today.getDate()-i);
      var key=_dateKey(d);
      labels.push(d.toLocaleDateString('es-ES',{day:'numeric',month:'short'}));
      data.push(Math.round(_totals(_dayEntries(key)).kcal));
    }
    var goals=_computeGoals();
    var goalKcal=goals?goals.kcal:null;
    var accent=getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()||'#16a34a';
    if(_chart){_chart.destroy();_chart=null;}
    var datasets=[{
      data:data,
      backgroundColor:accent+'99',
      borderColor:accent,
      borderWidth:1,
      borderRadius:6,
    }];
    if(goalKcal){
      datasets.push({
        type:'line',
        data:Array(7).fill(goalKcal),
        borderColor:'#ef4444',
        borderWidth:1.5,
        borderDash:[4,4],
        pointRadius:0,
        fill:false,
      });
    }
    _chart=new Chart(canvas,{
      type:'bar',
      data:{labels:labels,datasets:datasets},
      options:{
        responsive:true,maintainAspectRatio:false,
        plugins:{legend:{display:false}},
        scales:{
          x:{grid:{display:false}},
          y:{beginAtZero:true,grid:{color:'rgba(128,128,128,.1)'}}
        }
      }
    });
  }
  function _render(){_renderSummary();_renderList();_updateDateLabel();_renderChart();}
  _renderDiary=_render;
  document.getElementById('diary-prev').addEventListener('click',function(){
    _curDate.setDate(_curDate.getDate()-1);_render();
  });
  document.getElementById('diary-next').addEventListener('click',function(){
    var todayDate=new Date(_today.getFullYear(),_today.getMonth(),_today.getDate());
    if(_curDate<todayDate){_curDate.setDate(_curDate.getDate()+1);_render();}
  });
  function _addEntry(nombre,gramos,data){
    var key=_dateKey(_curDate);
    var factor=gramos/100;
    var entry={
      nombre:nombre,gramos:gramos,
      kcal:(data.kcal||0)*factor,
      proteina:(data.proteina||0)*factor,
      carbos:(data.carbos||0)*factor,
      grasa:(data.grasa||0)*factor,
    };
    if(!_diary[key])_diary[key]=[];
    _diary[key].push(entry);
    _saveDiary();_render();
  }
  window._diaryAddFromChat=function(nombre,kcal100,prot100,carbs100,fat100){
    document.getElementById('diary-food-inp').value=nombre;
    document.getElementById('diary-g-inp').value=100;
    if(window._setActiveTab){window._setActiveTab('diario');}else{
      document.querySelectorAll('.nav-tab').forEach(function(t){t.classList.toggle('active',t.dataset.tab==='diario');});
      document.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('active',p.id==='panel-diario');});
    }
    _render();
    document.getElementById('diary-food-inp').focus();
  };
  document.getElementById('diary-add-btn').addEventListener('click',function(){
    var nombre=document.getElementById('diary-food-inp').value.trim();
    var gramos=parseFloat(document.getElementById('diary-g-inp').value)||100;
    var err=document.getElementById('diary-add-err');
    if(!nombre){err.textContent='Introduce el nombre del alimento.';return;}
    err.textContent='';
    fetch('/api/calories?food='+encodeURIComponent(nombre))
      .then(function(r){return r.json();})
      .then(function(d){
        if(!d||!d.calorias){err.textContent='Alimento no encontrado.';return;}
        _addEntry(nombre,gramos,{kcal:d.calorias,proteina:d.proteina||0,carbos:d.carbohidratos||0,grasa:d.grasas||0});
        document.getElementById('diary-food-inp').value='';
        document.getElementById('diary-g-inp').value=100;
      })
      .catch(function(){err.textContent='Error al buscar el alimento.';});
  });
  document.getElementById('diary-food-inp').addEventListener('keydown',function(e){
    if(e.key==='Enter'){e.preventDefault();document.getElementById('diary-add-btn').click();}
  });
  document.querySelectorAll('.nav-tab').forEach(function(tab){
    tab.addEventListener('click',function(){
      if(tab.dataset.tab==='diario')_render();
    });
  });
  window._getDiaryTotals=function(){
    return _totals(_dayEntries(_dateKey(new Date(_today.getFullYear(),_today.getMonth(),_today.getDate()))));
  };
})();
// ── Alerts ──
function _runAlerts(msgEl){
  if(!_perfil||!_perfil.peso||!_perfil.altura||!_perfil.edad)return;
  var t=typeof window._getDiaryTotals==='function'?window._getDiaryTotals():null;
  if(!t||t.kcal===0)return;
  var goals=_computeGoals();
  if(!goals)return;
  var checks=[
    {key:'kcal', label:'Calor\u00edas', consumed:t.kcal,  goal:goals.kcal,  unit:'kcal'},
    {key:'prot', label:'Prote\u00edna', consumed:t.prot,  goal:goals.prot,  unit:'g'},
    {key:'carbs',label:'Carbos',        consumed:t.carbs, goal:goals.carbs, unit:'g'},
    {key:'fat',  label:'Grasa',         consumed:t.fat,   goal:goals.fat,   unit:'g'},
  ];
  var worst=null;
  checks.forEach(function(c){
    if(!c.goal)return;
    var pct=c.consumed/c.goal*100;
    var score=0,level='',text='';
    if(pct>110){
      score=100;level='red';
      text=c.label+': has superado el objetivo en ~'+Math.round(c.consumed-c.goal)+' '+c.unit;
    } else if(pct>=90){
      score=50;level='green';
      text='\u00a1'+c.label+' del d\u00eda completada! ('+Math.round(pct)+'%)';
    } else if(pct>=50){
      score=10;level='yellow';
      text=c.label+': te faltan ~'+Math.round(c.goal-c.consumed)+' '+c.unit;
    } else {
      score=20;level='red';
      text=c.label+': solo llevas el '+Math.round(pct)+'% del objetivo';
    }
    if(!worst||score>worst.score)worst={score:score,level:level,text:text};
  });
  if(!worst)return;
  var card=document.createElement('div');
  card.className='alert-card '+worst.level;
  card.textContent=worst.text;
  msgEl.querySelector('.b').appendChild(card);
}

// ─── FOTO PANEL ───────────────────────────────────────────────
(function(){
  // MobileNet label → nombre alimento para buscar en /api/calories
  var FOOD_MAP = {
    'banana':['platano'],'apple':['manzana'],'orange':['naranja'],
    'strawberry':['fresa'],'lemon':['limon'],'pineapple':['pina'],
    'mango':['mango'],'watermelon':['sandia'],'grape':['uva'],
    'peach':['melocoton'],'cherry':['cereza'],'blueberry':['arandanos'],
    'raspberry':['frambuesas'],'blackberry':['moras'],'plum':['ciruelas'],
    'kiwi':['kiwi'],'papaya':['papaya'],'pomegranate':['granada'],
    'fig':['higo fresco'],'date':['datiles'],'coconut':['coco rallado'],
    'lychee':['lichi'],'passion fruit':['maracuya'],'apricot':['albaricoque'],
    'pear':['pera'],'melon':['melon'],
    'broccoli':['brocoli'],'carrot':['zanahoria'],'corn':['maiz cocido'],
    'mushroom':['champiñon'],'cucumber':['pepino'],'tomato':['tomate'],
    'lettuce':['lechuga'],'avocado':['aguacate'],'onion':['cebolla'],
    'garlic':['ajo'],'pepper':['pimiento rojo'],'zucchini':['calabacin'],
    'eggplant':['berenjena'],'spinach':['espinacas'],'kale':['kale'],
    'asparagus':['esparragos'],'artichoke':['alcachofas'],'celery':['apio'],
    'leek':['puerro'],'cauliflower':['coliflor'],'pumpkin':['calabaza'],
    'sweet potato':['boniato cocido'],'potato':['patata cocida'],
    'beet':['remolachas'],'green beans':['judias verdes'],
    'brussels sprouts':['coles de bruselas'],'arugula':['rucula'],
    'ginger':['jengibre fresco'],
    'egg':['huevo'],'omelette':['huevo'],'scrambled eggs':['huevo'],
    'fried egg':['huevo'],'boiled egg':['huevo'],
    'chicken':['pechuga de pollo'],'roast chicken':['pollo entero asado'],
    'chicken breast':['pechuga de pollo'],'chicken thigh':['muslo de pollo'],
    'beef':['ternera lomo'],'steak':['ternera lomo'],
    'hamburger':['hamburguesa con pan'],'cheeseburger':['hamburguesa con pan'],
    'burger':['hamburguesa con pan'],'ground beef':['ternera picada'],
    'pork':['cerdo lomo'],'bacon':['bacon'],'ham':['jamon serrano'],
    'chorizo':['chorizo'],'hot dog':['salchichas de pollo'],
    'sausage':['salchichas de pollo'],'turkey':['pavo pechuga'],
    'lamb':['cordero pierna'],'duck':['pato pechuga'],
    'salmon':['salmon'],'tuna':['atun fresco'],
    'canned tuna':['atun en agua'],'shrimp':['gambas'],
    'lobster':['langostinos'],'crab':['cangrejo'],
    'cod':['bacalao'],'hake':['merluza'],'sea bass':['lubina'],
    'sea bream':['dorada'],'trout':['trucha'],
    'sardine':['sardinas en aceite'],'anchovy':['anchoas en aceite'],
    'squid':['calamar'],'octopus':['pulpo cocido'],
    'mussel':['mejillones cocidos'],'tofu':['tofu'],'tempeh':['tempeh'],
    'cheese':['queso cheddar'],'cheddar':['queso cheddar'],
    'mozzarella':['mozzarella'],'parmesan':['parmesano'],'brie':['queso brie'],
    'feta':['queso fresco'],'cottage cheese':['requesson'],
    'butter':['mantequilla'],'milk':['leche entera'],
    'skim milk':['leche desnatada'],'almond milk':['leche de almendras'],
    'oat milk':['leche de avena'],'soy milk':['leche de soja'],
    'yogurt':['yogur griego'],'greek yogurt':['yogur griego'],
    'kefir':['kefir'],'cream':['nata para cocinar'],
    'bread':['pan blanco'],'white bread':['pan blanco'],
    'whole wheat bread':['pan integral'],'pita':['pan de pita'],
    'rice':['arroz blanco'],'brown rice':['arroz integral'],
    'pasta':['pasta cocida'],'whole wheat pasta':['pasta integral cocida'],
    'couscous':['cuscus cocido'],'quinoa':['quinoa cocida'],
    'oatmeal':['avena'],'granola':['granola'],
    'polenta':['polenta cocida'],'millet':['mijo cocido'],
    'buckwheat':['trigo sarraceno cocido'],'rice cake':['galletas de arroz'],
    'pretzel':['pan blanco'],'bagel':['pan blanco'],'baguette':['pan blanco'],
    'croissant':['croissant'],'waffle':['gofre'],'pancake':['crepe'],
    'lentil':['lentejas cocidas'],'chickpea':['garbanzos cocidos'],
    'black bean':['alubias negras cocidas'],
    'white bean':['alubias blancas cocidas'],
    'pinto bean':['alubias pintas cocidas'],'soybean':['soja cocida'],
    'edamame':['edamame'],'fava bean':['habas cocidas'],
    'pea':['guisantes cocidos'],
    'almond':['almendras'],'walnut':['nueces'],'peanut':['cacahuetes'],
    'pistachio':['pistachos'],'hazelnut':['avellanas'],'cashew':['anacardos'],
    'macadamia':['nueces de macadamia'],
    'sunflower seed':['pipas de girasol'],
    'pumpkin seed':['pipas de calabaza'],'sesame':['sesamo'],
    'chia seed':['semillas de chia'],'flaxseed':['semillas de lino'],
    'peanut butter':['mantequilla de cacahuete'],
    'almond butter':['mantequilla de almendras'],
    'olive oil':['aceite de oliva'],'coconut oil':['aceite de coco'],
    'sunflower oil':['aceite de girasol'],'honey':['miel'],
    'ketchup':['ketchup'],'mayonnaise':['mayonesa'],
    'soy sauce':['salsa de soja'],'olive':['aceituna'],
    'hummus':['garbanzos cocidos'],'guacamole':['aguacate'],
    'french fries':['patatas fritas'],'chips':['patatas fritas'],
    'popcorn':['palomitas de maiz'],'granola bar':['barrita de cereales'],
    'chocolate':['chocolate negro 70%'],'dark chocolate':['chocolate negro 70%'],
    'pizza':['pizza de queso'],'ice cream':['helado'],
    'cake':['pastel'],'cheesecake':['tarta de queso'],
    'brownie':['brownie'],'donut':['donut'],'muffin':['magdalena'],
    'cookie':['galleta'],'nachos':['nachos'],'churro':['churro'],
    'sushi':['sushi'],'ramen':['ramen'],'pad thai':['pad thai'],
    'fried rice':['arroz frito'],'spring roll':['rollitos primavera'],
    'dumpling':['dumpling'],'noodles':['fideos cocidos'],
    'curry':['curry'],'tikka masala':['curry'],
    'kebab':['kebab'],'shawarma':['shawarma'],'falafel':['falafel'],
    'burrito':['burrito'],'taco':['tacos'],'quesadilla':['quesadilla'],
    'sandwich':['sandwich'],'wrap':['wrap'],
    'soup':['sopa'],'salad':['ensalada'],'caesar salad':['ensalada'],
    'paella':['paella'],'risotto':['risotto'],
    'tiramisu':['tiramisu'],'french toast':['torrija'],'crepe':['crepe'],
    'coffee':['cafe solo'],'espresso':['cafe solo'],
    'cappuccino':['cafe con leche'],'latte':['cafe con leche'],
    'tea':['te verde'],'orange juice':['zumo de naranja'],
    'coconut water':['agua de coco'],'beer':['cerveza'],'wine':['vino'],
    'smoothie':['batido'],'milkshake':['batido con leche'],
    'protein shake':['proteina whey'],'protein powder':['proteina whey']
  };

  var fotoDrop=document.getElementById('foto-drop');
  var fotoInp=document.getElementById('foto-inp');
  var fotoPick=document.getElementById('foto-pick');
  var fotoPreview=document.getElementById('foto-preview');
  var fotoPreviewWrap=document.getElementById('foto-preview-wrap');
  var fotoPlaceholder=document.getElementById('foto-placeholder');
  var fotoGo=document.getElementById('foto-go');
  var fotoStatus=document.getElementById('foto-status');
  var fotoResult=document.getElementById('foto-result');
  var fotoFoodName=document.getElementById('foto-food-name');
  var fotoKcalBig=document.getElementById('foto-kcal-big');
  var fotoSlider=document.getElementById('foto-slider');
  var fotoSliderVal=document.getElementById('foto-slider-val');
  var fotoMacros=document.getElementById('foto-macros');
  var fotoTags=document.getElementById('foto-tags');

  var currentAlimento=null;
  var currentImageB64=null;
  var currentImageMime='image/jpeg';

  function setStatus(msg){fotoStatus.textContent=msg;}

  function showPreview(file){
    currentImageMime=file.type||'image/jpeg';
    var reader=new FileReader();
    reader.onload=function(e){
      var dataUrl=e.target.result;
      fotoPreview.src=dataUrl;
      currentImageB64=dataUrl.split(',')[1];
      fotoPreviewWrap.style.display='block';
      fotoPlaceholder.style.display='none';
      fotoGo.style.display='block';
      fotoResult.style.display='none';
      setStatus('');
    };
    reader.readAsDataURL(file);
  }

  fotoDrop.addEventListener('click',function(e){
    if(e.target===fotoPick||e.target.closest('#foto-pick'))return;
    if(fotoPreviewWrap.style.display!=='none')fotoInp.click();
  });
  fotoPick.addEventListener('click',function(e){e.stopPropagation();fotoInp.click();});
  fotoInp.addEventListener('change',function(){if(this.files[0])showPreview(this.files[0]);});
  fotoDrop.addEventListener('dragover',function(e){e.preventDefault();fotoDrop.classList.add('drag');});
  fotoDrop.addEventListener('dragleave',function(){fotoDrop.classList.remove('drag');});
  fotoDrop.addEventListener('drop',function(e){
    e.preventDefault();fotoDrop.classList.remove('drag');
    var f=e.dataTransfer.files[0];if(f&&f.type.startsWith('image/'))showPreview(f);
  });

  function renderResult(alimento,gramos){
    var factor=gramos/100;
    var kcal=Math.round((alimento.calorias||0)*factor);
    fotoKcalBig.textContent=kcal+' kcal';
    var macros=[
      {v:Math.round((alimento.proteina||0)*factor),l:'Prote\u00edna'},
      {v:Math.round((alimento.carbohidratos||0)*factor),l:'Carbos'},
      {v:Math.round((alimento.grasa||0)*factor),l:'Grasas'},
    ];
    fotoMacros.innerHTML=macros.map(function(m){
      return '<div class="foto-macro-box"><div class="foto-macro-val">'+m.v+'g</div><div class="foto-macro-lbl">'+m.l+'</div></div>';
    }).join('');
    var tags=[];
    if(alimento.fibra)tags.push('Fibra '+alimento.fibra+'g');
    if(alimento.categoria)tags.push(alimento.categoria);
    fotoTags.innerHTML=tags.map(function(t){return '<span class="tag">'+t+'</span>';}).join('');
  }

  fotoSlider.addEventListener('input',function(){
    fotoSliderVal.textContent=this.value+' g';
    if(currentAlimento)renderResult(currentAlimento,parseInt(this.value));
  });

  fotoGo.addEventListener('click',function(){
    if(!currentImageB64)return;
    fotoResult.style.display='none';
    setStatus('Analizando imagen con IA\u2026');
    fotoGo.disabled=true;

    fetch('/api/analyze-foto',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({image_b64:currentImageB64,mime_type:currentImageMime})
    })
    .then(function(r){return r.json();})
    .then(function(d){
      fotoGo.disabled=false;
      if(d.error){setStatus(d.error);return;}
      currentAlimento=d;
      var gramos=parseInt(fotoSlider.value);
      fotoFoodName.textContent=d.nombre;
      renderResult(d,gramos);
      fotoResult.style.display='block';
      var fe=document.getElementById('foto-empty');if(fe)fe.style.display='none';
      setStatus('');
    })
    .catch(function(){
      fotoGo.disabled=false;
      setStatus('Error al analizar la imagen. Intenta de nuevo.');
    });
  });
})();
})();"""


@app.get("/", response_class=HTMLResponse)
async def get_home():
    return HTML_PAGE


@app.get("/app.js")
async def get_js():
    from fastapi.responses import Response
    return Response(content=JS_CODE, media_type="text/javascript; charset=utf-8")


@app.post("/api/chat")
async def chat(data: dict):
    mensaje = data.get("mensaje", "")
    contexto = data.get("contexto", {}) or {}
    perfil = data.get("perfil")
    return generar_respuesta(mensaje, contexto, perfil=perfil)


@app.post("/api/analyze-foto")
async def analyze_foto(data: dict):
    image_b64 = data.get("image_b64", "")
    mime_type = data.get("mime_type", "image/jpeg")
    if not image_b64:
        return {"error": "No se recibió imagen."}

    prompt = (
        "Eres un nutricionista experto en cocina española e internacional. "
        "Analiza esta foto de comida y responde SOLO con un JSON válido (sin texto adicional, sin markdown) "
        "con estos campos exactos:\n"
        '{"nombre": "nombre del plato en español", '
        '"calorias": kcal_por_100g_como_numero, '
        '"proteina": gramos_por_100g, '
        '"carbohidratos": gramos_por_100g, '
        '"grasa": gramos_por_100g, '
        '"fibra": gramos_por_100g_o_null, '
        '"categoria": "categoria breve como Carne, Verdura, Cereal, Legumbre, etc."}\n'
        "Si no puedes identificar comida en la imagen, devuelve: "
        '{"error": "No se detecta comida en la imagen."}'
    )
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
                ],
            }],
            max_tokens=300,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        result = json.loads(raw)
        return result
    except (json.JSONDecodeError, ValueError):
        return {"error": "No pude interpretar la respuesta de la IA."}
    except Exception as e:
        return {"error": f"Error al analizar: {str(e)}"}


@app.get("/api/calories")
async def get_calories(food: str):
    alimento = buscar_alimento(food)
    if alimento:
        return {"found": True, **alimento}
    return {"found": False}


@app.get("/api/stats")
async def get_stats():
    return {
        "total_recetas": len(recipes_db.get("recetas", [])),
        "total_alimentos": len(calories_db.get("alimentos", [])),
    }


MANIFEST = {
    "name": "NutrIA",
    "short_name": "NutrIA",
    "description": "Asistente de nutrición: calorías, macros, calculadora TDEE y estimación por foto",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#e0e5ec",
    "theme_color": "#3a9d6e",
    "orientation": "portrait-primary",
    "icons": [
        {"src": "/logo.png", "sizes": "192x192 512x512 1024x1024", "type": "image/png", "purpose": "any maskable"},
    ],
    "categories": ["health", "food"],
}

SW_CODE = r"""
const CACHE='nutria-v1';
const PRECACHE=['/','/app.js'];
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/','/app.js'])).then(()=>self.skipWaiting()));
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',e=>{
  const url=new URL(e.request.url);
  if(e.request.method!=='GET')return;
  if(url.pathname.startsWith('/api/')){
    e.respondWith(fetch(e.request).catch(()=>new Response('{"error":"offline"}',{headers:{'Content-Type':'application/json'}})));
    return;
  }
  e.respondWith(caches.match(e.request).then(cached=>{
    const net=fetch(e.request).then(res=>{
      const clone=res.clone();
      caches.open(CACHE).then(c=>c.put(e.request,clone));
      return res;
    });
    return cached||net;
  }));
});
"""
@app.get("/manifest.json")
async def get_manifest():
    from fastapi.responses import JSONResponse
    return JSONResponse(content=MANIFEST, headers={"Cache-Control": "public, max-age=86400"})


@app.get("/sw.js")
async def get_sw():
    from fastapi.responses import Response
    return Response(
        content=SW_CODE,
        media_type="text/javascript; charset=utf-8",
        headers={"Cache-Control": "no-cache, no-store"},
    )


@app.get("/icon-192.png")
async def get_icon_192():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/logo.png", status_code=302)


@app.get("/icon-512.png")
async def get_icon_512():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/logo.png", status_code=302)


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


if __name__ == "__main__":
    import uvicorn
    raw_port = os.environ.get("PORT", "8000")
    clean_port = "".join(filter(str.isdigit, str(raw_port)))
    port = int(clean_port) if clean_port else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
