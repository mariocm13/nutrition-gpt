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

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://nutria.onrender.com").split(",")
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
<meta name="theme-color" content="#3a9d6e">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="NutrIA">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
button,input,select{-webkit-appearance:none;appearance:none;touch-action:manipulation;user-select:none;-webkit-user-select:none;font-family:inherit}
:root{
  --bg:#f0f4f8;
  --surface:#ffffff;
  --surface2:#f8fafc;
  --border:#dde3ea;
  --text:#0d1b2a;
  --muted:#64748b;
  --accent:#16a34a;
  --accent-h:#15803d;
  --accent-light:#dcfce7;
  --accent-muted:#bbf7d0;
  --sh-xs:0 1px 3px rgba(0,0,0,.06);
  --sh:0 4px 20px rgba(0,0,0,.07),0 2px 8px rgba(0,0,0,.04);
  --sh-lg:0 12px 40px rgba(0,0,0,.1),0 4px 16px rgba(0,0,0,.06);
}
html.dark{
  --bg:#0d1117;
  --surface:#161b22;
  --surface2:#0d1117;
  --border:#30363d;
  --text:#e6edf3;
  --muted:#8b949e;
  --accent:#3fb950;
  --accent-h:#2ea043;
  --accent-light:#0d1f0d;
  --accent-muted:#1a3a1a;
}
html,body{height:100%;overflow:hidden;background:var(--bg);overscroll-behavior:none}
body{font-family:'Inter',system-ui,sans-serif;color:var(--text);font-size:14px;line-height:1.5;transition:background .25s,color .25s;display:flex;flex-direction:column;padding-bottom:60px}
.app{max-width:860px;width:100%;flex:1;margin:0 auto;display:flex;flex-direction:column;background:var(--bg);transition:background .25s;overflow:hidden}

/* ── Header ── */
.header{padding:12px 18px 10px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;flex-shrink:0}
.icon{width:38px;height:38px;border-radius:11px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 12px rgba(22,163,74,.3);overflow:hidden;background:transparent}
.icon img{width:100%;height:100%;object-fit:cover;border-radius:11px}
.header-info{flex:1;min-width:0}
.header h1{font-size:15px;font-weight:700;letter-spacing:-.3px}
.header p{font-size:11px;color:var(--muted);margin-top:1px}
.header-end{display:flex;gap:8px;align-items:center;flex-shrink:0}
.hdr-btn{width:34px;height:34px;background:transparent;border:1px solid var(--border);border-radius:9px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--muted);transition:all .15s}
.hdr-btn:hover{color:var(--text);background:var(--bg)}
.hdr-btn svg{width:16px;height:16px;fill:currentColor}

/* ── Bottom Nav ── */
.bottom-nav{position:fixed;bottom:0;left:0;right:0;z-index:100;background:var(--surface);border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-around;height:60px;max-width:860px;margin:0 auto}
.nav-tab{flex:1;height:60px;min-width:44px;background:transparent;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;color:var(--muted);transition:color .18s}
.nav-tab.active{color:var(--accent)}
.nav-tab svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;pointer-events:none}

/* ── Panels ── */
.panel{display:none;flex:1;flex-direction:column;min-height:0;overflow:hidden}
.panel.active{display:flex}

/* ── Chat ── */
.msgs{flex:1;overflow-y:auto;padding:18px 16px 10px;display:flex;flex-direction:column;gap:14px;scrollbar-width:thin;scrollbar-color:var(--border) transparent;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
.msgs::-webkit-scrollbar{width:4px}
.msgs::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.m{display:flex;gap:9px;animation:fadeUp .2s ease both}
.m.u{justify-content:flex-end}
.m.bot{align-items:flex-start}
.avatar{width:30px;height:30px;min-width:30px;border-radius:9px;background:linear-gradient(135deg,#22c55e,#15803d);display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px;box-shadow:0 2px 8px rgba(22,163,74,.2)}
.avatar svg{width:15px;height:15px;fill:none;stroke:#fff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.b{max-width:80%;padding:12px 16px;line-height:1.75;font-size:14px}
.m.bot .b{background:var(--surface);border:1px solid var(--border);border-radius:4px 18px 18px 18px;box-shadow:var(--sh-xs)}
.m.u .b{background:linear-gradient(135deg,var(--accent),var(--accent-h));color:#fff;border-radius:18px 4px 18px 18px;box-shadow:0 4px 14px rgba(22,163,74,.25)}
.typing .b{color:var(--muted);font-style:italic;background:var(--surface);border:1px solid var(--border);border-radius:4px 18px 18px 18px}

/* ── Composer ── */
.composer{padding:8px 14px 14px;background:var(--surface);border-top:1px solid var(--border);display:flex;gap:10px;align-items:center;flex-shrink:0}
#inp{flex:1;padding:12px 18px;border:1.5px solid var(--border);border-radius:24px;font-size:15px;background:var(--bg);color:var(--text);outline:none;transition:border-color .2s;user-select:auto;-webkit-user-select:auto}
#inp:focus{border-color:var(--accent)}
#inp::placeholder{color:var(--muted)}
#btn{width:44px;height:44px;flex-shrink:0;background:linear-gradient(135deg,var(--accent),var(--accent-h));color:#fff;border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 12px rgba(22,163,74,.3);transition:transform .15s,box-shadow .15s}
#btn:active{transform:scale(.92);box-shadow:0 2px 6px rgba(22,163,74,.2)}
#btn svg{width:20px;height:20px;fill:none;stroke:#fff;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}

/* ── Animations ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
#splash{position:fixed;inset:0;z-index:9999;background:#000;display:flex;align-items:center;justify-content:center;transition:opacity .6s ease}
#splash.hidden{opacity:0;pointer-events:none}
#splash video{width:100%;height:100%;object-fit:cover}
small{font-size:12px}

/* ── Calculator ── */
.calc-wrap{flex:1;overflow-y:auto;padding:18px;background:var(--bg);-webkit-overflow-scrolling:touch}
.calc-card{background:var(--surface);border-radius:20px;padding:22px;box-shadow:var(--sh);margin-bottom:14px;border:1px solid var(--border)}
.calc-title{font-size:17px;font-weight:700;margin-bottom:20px;color:var(--text);display:flex;align-items:center;gap:10px}
.calc-title-icon{width:32px;height:32px;border-radius:9px;background:var(--accent-light);display:flex;align-items:center;justify-content:center;font-size:17px}
.calc-row.two{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.calc-group{margin-bottom:14px}
.calc-label{display:block;font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.09em;margin-bottom:7px}
.calc-inp{width:100%;padding:11px 14px;border:1.5px solid var(--border);border-radius:12px;font-size:16px;background:var(--bg);color:var(--text);outline:none;transition:border-color .2s;-webkit-appearance:none;user-select:auto;-webkit-user-select:auto}
.calc-inp:focus{border-color:var(--accent)}
.calc-sel{width:100%;padding:11px 14px;border:1.5px solid var(--border);border-radius:12px;font-size:14px;background:var(--bg);color:var(--text);outline:none;cursor:pointer;transition:border-color .2s}
.calc-sel:focus{border-color:var(--accent)}
.seg{display:flex;gap:6px;flex-wrap:wrap}
.seg-btn{flex:1;padding:9px 8px;border:1.5px solid var(--border);border-radius:10px;font-size:13px;font-weight:600;background:var(--bg);color:var(--muted);cursor:pointer;transition:all .18s;white-space:nowrap;touch-action:manipulation}
.seg-btn.active{background:var(--accent-light);border-color:var(--accent);color:var(--accent)}
.calc-btn{width:100%;padding:13px;background:linear-gradient(135deg,var(--accent),var(--accent-h));color:#fff;border:none;border-radius:14px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 4px 16px rgba(22,163,74,.28);transition:transform .15s,box-shadow .15s;touch-action:manipulation;margin-top:4px}
.calc-btn:active{transform:scale(.98);box-shadow:0 2px 8px rgba(22,163,74,.15)}
.calc-result{background:var(--surface);border-radius:20px;padding:22px;box-shadow:var(--sh);border:1px solid var(--border)}
.res-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px}
.res-box{background:var(--bg);border:1px solid var(--border);border-radius:14px;padding:14px 8px;text-align:center}
.res-box.accent{background:linear-gradient(135deg,var(--accent),var(--accent-h));border-color:transparent;box-shadow:0 6px 20px rgba(22,163,74,.22)}
.res-box.accent .res-val,.res-box.accent .res-lbl,.res-box.accent .res-sub{color:#fff}
.res-val{font-size:19px;font-weight:700;color:var(--accent);line-height:1}
.res-lbl{font-size:10px;font-weight:700;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.06em}
.res-sub{font-size:10px;color:var(--muted);margin-top:2px}
.macro-title{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}
.macro-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px}
.macro-box{background:var(--bg);border:1px solid var(--border);border-radius:14px;padding:12px 8px;text-align:center}
.macro-val{font-size:17px;font-weight:700;color:var(--text)}
.macro-lbl{font-size:11px;color:var(--muted);margin-top:3px}
.macro-g{font-size:10px;color:var(--accent);font-weight:700;margin-top:2px}
.res-note{font-size:12px;color:var(--muted);line-height:1.65;padding:12px 14px;background:var(--bg);border-radius:12px;border:1px solid var(--border)}

/* ── Foto ── */
@media(max-width:600px){
  .header{padding:10px 12px 8px}
  .tabs{padding:8px 10px}
  .msgs{padding:12px 12px 8px;gap:10px}
  .composer{padding:6px 10px 12px}
  .calc-wrap{padding:12px}
  .foto-wrap{padding:12px}
  .foto-macros{grid-template-columns:repeat(2,1fr)}
  .res-val{font-size:16px}
  .macro-val{font-size:15px}
}
.foto-wrap{flex:1;overflow-y:auto;padding:20px;display:flex;justify-content:center;align-items:flex-start;background:var(--bg)}
.foto-card{background:var(--surface);border-radius:22px;box-shadow:var(--sh);border:1px solid var(--border);padding:26px 22px;width:100%;max-width:440px}
.foto-title{font-size:18px;font-weight:700;margin-bottom:4px;text-align:center;color:var(--text)}
.foto-subtitle{font-size:13px;color:var(--muted);text-align:center;margin-bottom:20px;line-height:1.5}
.foto-drop{border:2px dashed var(--border);border-radius:18px;padding:28px 20px;min-height:165px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:10px;cursor:pointer;transition:border-color .2s,background .2s;background:var(--bg)}
.foto-drop:hover,.foto-drop.drag{border-color:var(--accent);background:var(--accent-light)}
#foto-preview{width:100%;border-radius:14px;max-height:230px;object-fit:contain;display:block}
#foto-placeholder{display:flex;flex-direction:column;align-items:center;gap:8px}
.foto-icon{font-size:38px;line-height:1}
.foto-hint{font-size:13px;color:var(--muted);text-align:center}
.foto-pick-btn{padding:8px 20px;background:var(--accent-light);border:none;border-radius:11px;font-size:13px;font-weight:600;color:var(--accent);cursor:pointer;margin-top:2px;transition:background .2s}
.foto-pick-btn:hover{background:var(--accent-muted)}
.foto-status{font-size:13px;color:var(--muted);text-align:center;margin:12px 0;min-height:20px}
.foto-result{margin-top:8px}
.foto-food-name{font-size:14px;font-weight:600;text-align:center;margin-bottom:4px;color:var(--muted)}
.foto-kcal-big{font-size:52px;font-weight:800;color:var(--accent);text-align:center;line-height:1;margin-bottom:14px;letter-spacing:-2px}
.foto-kcal-unit{font-size:18px;font-weight:600;opacity:.7}
.foto-portion-row{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.foto-slider{flex:1;min-width:80px;accent-color:var(--accent)}
.foto-slider-val{font-size:13px;font-weight:700;color:var(--accent);min-width:44px;text-align:right}
.foto-macros{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px}
.foto-macro-box{background:var(--bg);border:1px solid var(--border);border-radius:14px;padding:11px 6px;text-align:center}
.foto-macro-val{font-size:17px;font-weight:700;color:var(--text)}
.foto-macro-lbl{font-size:9px;color:var(--muted);margin-top:3px;font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.foto-tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.tag{font-size:11px;padding:4px 10px;border-radius:20px;background:var(--accent-light);color:var(--accent);font-weight:600}
.foto-disclaimer{font-size:10px;color:var(--muted);text-align:center;line-height:1.5}
/* ── Profile Modal ── */
.modal-overlay{position:fixed;inset:0;z-index:200;background:rgba(0,0,0,.45);display:none;align-items:flex-end;justify-content:center}
.modal-overlay.open{display:flex}
.modal-sheet{background:var(--surface);border-radius:22px 22px 0 0;padding:24px 20px 32px;width:100%;max-width:860px;box-shadow:var(--sh-lg);animation:fadeUp .25s ease both;overflow-y:auto;max-height:90vh}
.modal-title{font-size:16px;font-weight:700;margin-bottom:18px;color:var(--text)}
.modal-actions{display:flex;gap:10px;margin-top:20px}
.modal-btn{flex:1;padding:12px;border-radius:13px;font-size:14px;font-weight:700;cursor:pointer;border:none;transition:all .15s}
.modal-btn.primary{background:linear-gradient(135deg,var(--accent),var(--accent-h));color:#fff;box-shadow:0 4px 14px rgba(22,163,74,.25)}
.modal-btn.secondary{background:var(--bg);border:1.5px solid var(--border);color:var(--text)}
/* ── Diary ── */
.diary-wrap{flex:1;overflow-y:auto;padding:16px;background:var(--bg);-webkit-overflow-scrolling:touch}
.diary-nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.diary-nav-btn{background:transparent;border:1px solid var(--border);border-radius:9px;width:34px;height:34px;cursor:pointer;color:var(--muted);font-size:18px;display:flex;align-items:center;justify-content:center;transition:all .15s}
.diary-nav-btn:hover{color:var(--text);background:var(--bg)}
.diary-date-lbl{font-size:15px;font-weight:700;color:var(--text)}
.summary-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
.summary-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:14px 12px}
.summary-card-lbl{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.summary-card-val{font-size:16px;font-weight:700;color:var(--text)}
.summary-card-goal{font-size:11px;color:var(--muted);margin-top:1px}
.progress-bar{height:5px;border-radius:3px;background:var(--border);margin-top:8px;overflow:hidden}
.progress-fill{height:100%;border-radius:3px;transition:width .3s}
.progress-fill.ok{background:var(--accent)}
.progress-fill.warn{background:#f59e0b}
.progress-fill.over{background:#ef4444}
.diary-section-title{font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin:16px 0 8px}
.diary-entry{display:flex;align-items:center;gap:8px;padding:10px 12px;background:var(--surface);border:1px solid var(--border);border-radius:12px;margin-bottom:6px}
.diary-entry-name{flex:1;font-size:14px;font-weight:600;color:var(--text)}
.diary-entry-meta{font-size:12px;color:var(--muted)}
.diary-del{background:transparent;border:none;cursor:pointer;color:var(--muted);font-size:16px;line-height:1;padding:0 4px;transition:color .15s}
.diary-del:hover{color:#ef4444}
.diary-empty{font-size:13px;color:var(--muted);text-align:center;padding:20px 0;font-style:italic}
.diary-add-form{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;margin-bottom:8px}
.diary-add-form input{flex:1;min-width:120px;padding:10px 12px;border:1.5px solid var(--border);border-radius:12px;font-size:14px;background:var(--bg);color:var(--text);outline:none;transition:border-color .2s}
.diary-add-form input:focus{border-color:var(--accent)}
.diary-g-inp{max-width:80px;min-width:60px;flex:none}
.diary-add-btn{padding:10px 16px;background:linear-gradient(135deg,var(--accent),var(--accent-h));color:#fff;border:none;border-radius:12px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;box-shadow:0 3px 10px rgba(22,163,74,.2);transition:transform .15s}
.diary-add-btn:active{transform:scale(.97)}
.diary-add-err{font-size:12px;color:#ef4444;margin-top:4px;min-height:16px}
.chart-wrap{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:16px;margin-top:8px}
.chart-wrap-title{font-size:12px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}
.chart-fallback{font-size:13px;color:var(--muted);text-align:center;padding:20px 0;display:none}
.add-to-diary-btn{margin-top:8px;padding:7px 14px;background:var(--accent-light);border:1px solid var(--accent-muted);border-radius:10px;font-size:12px;font-weight:700;color:var(--accent);cursor:pointer;transition:background .15s;display:inline-block}
.add-to-diary-btn:hover{background:var(--accent-muted)}
.alert-card{margin-top:8px;padding:10px 12px;border-radius:10px;border-left:3px solid;font-size:12px;line-height:1.5}
.alert-card.green{border-color:var(--accent);background:var(--accent-light);color:var(--accent)}
.alert-card.yellow{border-color:#f59e0b;background:#fefce8;color:#92400e}
.alert-card.red{border-color:#ef4444;background:#fef2f2;color:#991b1b}
html.dark .alert-card.yellow{background:#292100;color:#fbbf24}
html.dark .alert-card.red{background:#200a0a;color:#f87171}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js" onerror="window._chartJSFailed=true"></script>
</head>
<body>
<div id="splash">
  <video id="splash-video" playsinline muted autoplay></video>
</div>
<div class="app">
  <div class="header">
    <div class="icon">
      <img src="/logo.png" alt="NutrIA logo">
    </div>
    <div class="header-info">
      <h1>NutrIA</h1>
      <p>Asistente de nutrici\u00f3n</p>
    </div>
    <div class="header-end">
      <button id="prof-btn" class="hdr-btn" title="Perfil" aria-label="Perfil de usuario">
        <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </button>
      <button id="dm" class="hdr-btn" title="Modo oscuro" aria-label="Alternar modo oscuro">
        <svg id="dm-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </div>
  <nav class="bottom-nav">
    <button class="nav-tab active" data-tab="chat">
      <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
    </button>
    <button class="nav-tab" data-tab="diario">
      <svg viewBox="0 0 24 24"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
    </button>
    <button class="nav-tab" data-tab="calc">
      <svg viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M8 10h8M8 14h4"/></svg>
    </button>
    <button class="nav-tab" data-tab="foto">
      <svg viewBox="0 0 24 24"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>
    </button>
  </nav>
  <div id="panel-chat" class="panel active">
    <div class="msgs" id="msgs">
      <div class="m bot">
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
  <div id="panel-diario" class="panel">
    <div class="diary-wrap">
      <div class="diary-nav">
        <button class="diary-nav-btn" id="diary-prev">&#8592;</button>
        <span class="diary-date-lbl" id="diary-date-lbl"></span>
        <button class="diary-nav-btn" id="diary-next">&#8594;</button>
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
      <div class="diary-section-title">Entradas del d\u00eda</div>
      <div id="diary-list"></div>
      <div class="diary-section-title">A\u00f1adir alimento</div>
      <div class="diary-add-form">
        <input type="text" id="diary-food-inp" placeholder="Nombre del alimento">
        <input type="number" id="diary-g-inp" class="diary-g-inp" placeholder="g" value="100" min="1">
        <button class="diary-add-btn" id="diary-add-btn">A\u00f1adir</button>
      </div>
      <div class="diary-add-err" id="diary-add-err"></div>
      <div class="chart-wrap">
        <div class="chart-wrap-title">\u00daltimos 7 d\u00edas \u2014 Calor\u00edas</div>
        <div style="position:relative;height:160px">
          <canvas id="diary-chart"></canvas>
        </div>
        <div class="chart-fallback" id="chart-fallback">Gr\u00e1fica no disponible</div>
      </div>
    </div>
  </div>
  <div id="panel-calc" class="panel">
    <div class="calc-wrap">
      <div class="calc-card">
        <div class="calc-title">Calculadora de macros</div>
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
        <div class="res-note" id="r-note"></div>
      </div>
    </div>
  </div>
  <div id="panel-foto" class="panel">
    <div class="foto-wrap">
      <div class="foto-card">
        <div class="foto-title">Estimar calorías por foto</div>
        <div class="foto-subtitle">Sube una imagen y la IA estima las calorías al instante</div>
        <div class="foto-drop" id="foto-drop">
          <input type="file" id="foto-inp" accept="image/*" capture="environment" style="display:none">
          <div id="foto-preview-wrap" style="display:none">
            <img id="foto-preview" alt="preview">
          </div>
          <div id="foto-placeholder">
            <div class="foto-icon">📷</div>
            <div class="foto-hint">Sube o haz una foto de tu comida</div>
            <button class="foto-pick-btn" id="foto-pick">Elegir imagen</button>
          </div>
        </div>
        <button class="calc-btn" id="foto-go" style="display:none">Analizar calorías</button>
        <div id="foto-status" class="foto-status"></div>
        <div id="foto-result" class="foto-result" style="display:none">
          <div class="foto-food-name" id="foto-food-name"></div>
          <div class="foto-kcal-big" id="foto-kcal-big"></div>
          <div class="foto-portion-row">
            <label class="calc-label">Porción (g)</label>
            <input type="range" id="foto-slider" min="50" max="500" value="100" step="10" class="foto-slider">
            <span class="foto-slider-val" id="foto-slider-val">100 g</span>
          </div>
          <div class="foto-macros" id="foto-macros"></div>
          <div class="foto-tags" id="foto-tags"></div>
          <div class="foto-disclaimer">Estimación orientativa basada en IA. No sustituye asesoramiento nutricional profesional.</div>
        </div>
      </div>
    </div>
  </div>
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
document.querySelectorAll('.nav-tab').forEach(function(tab){
  tab.addEventListener('click',function(){
    var id=tab.dataset.tab;
    document.querySelectorAll('.nav-tab').forEach(function(t){t.classList.toggle('active',t===tab);});
    document.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('active',p.id==='panel-'+id);});
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
  calcResult.style.display='block';
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
    document.querySelectorAll('.nav-tab').forEach(function(t){t.classList.toggle('active',t.dataset.tab==='diario');});
    document.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('active',p.id==='panel-diario');});
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
