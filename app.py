from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import os
import re
import unicodedata
import base64
from google import genai
from google.genai import types as genai_types
from nlp_processor import NLPProcessor

app = FastAPI(title="NutriGPT")

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://nutrigpt.onrender.com").split(",")
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
<title>NutriGPT</title>
<meta name="theme-color" content="#3a9d6e">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="NutriGPT">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/icon-192.png">
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
body{font-family:'Inter',system-ui,sans-serif;color:var(--text);font-size:14px;line-height:1.5;transition:background .25s,color .25s;display:flex;flex-direction:column}
.app{max-width:860px;width:100%;flex:1;margin:0 auto;display:flex;flex-direction:column;background:var(--bg);transition:background .25s;overflow:hidden}

/* ── Header ── */
.header{padding:12px 18px 10px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px;flex-shrink:0}
.icon{width:38px;height:38px;background:linear-gradient(135deg,#22c55e,#15803d);border-radius:11px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 12px rgba(22,163,74,.3)}
.icon svg{width:20px;height:20px;fill:none;stroke:#fff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.header-info{flex:1;min-width:0}
.header h1{font-size:15px;font-weight:700;letter-spacing:-.3px}
.header p{font-size:11px;color:var(--muted);margin-top:1px}
.header-end{display:flex;gap:8px;align-items:center;flex-shrink:0}
.hdr-btn{width:34px;height:34px;background:transparent;border:1px solid var(--border);border-radius:9px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--muted);transition:all .15s}
.hdr-btn:hover{color:var(--text);background:var(--bg)}
.hdr-btn svg{width:16px;height:16px;fill:currentColor}

/* ── Tabs ── */
.tabs{display:flex;gap:4px;padding:10px 14px;background:var(--surface);border-bottom:1px solid var(--border);flex-shrink:0}
.tab{flex:1;padding:8px 10px;font-size:13px;font-weight:600;color:var(--muted);background:transparent;border:none;border-radius:10px;cursor:pointer;transition:all .18s;display:flex;align-items:center;justify-content:center;gap:5px}
.tab:hover{color:var(--text);background:var(--bg)}
.tab.active{background:var(--accent-light);color:var(--accent)}
.tab-icon{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex-shrink:0}

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
</style>
</head>
<body>
<div class="app">
  <div class="header">
    <div class="icon">
      <svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 5-8 5"/></svg>
    </div>
    <div class="header-info">
      <h1>NutriGPT</h1>
      <p>Asistente de nutrici\u00f3n</p>
    </div>
    <div class="header-end">
      <button id="dm" class="hdr-btn" title="Modo oscuro" aria-label="Alternar modo oscuro">
        <svg id="dm-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </div>
  <nav class="tabs">
    <button class="tab active" data-tab="chat"><svg class="tab-icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>Chat</button>
    <button class="tab" data-tab="calc"><svg class="tab-icon" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 10h8M8 14h4"/></svg>Calculadora</button>
    <button class="tab" data-tab="foto"><svg class="tab-icon" viewBox="0 0 24 24"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>Foto</button>
  </nav>
  <div id="panel-chat" class="panel active">
    <div class="msgs" id="msgs">
      <div class="m bot">
        <div class="avatar"><svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 5-8 5"/></svg></div>
        <div class="b">
          Hola, soy <strong>NutriGPT</strong>.<br><br>
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




GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

SYSTEM_PROMPT = (
    "Eres NutriGPT, un asistente de nutrición experto en cocina española e internacional. "
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


def generar_respuesta(mensaje, contexto=None):
    contexto = contexto or {}
    historial = contexto.get("historial", [])

    datos_locales = _buscar_datos_locales(mensaje)
    mensaje_con_datos = mensaje
    if datos_locales:
        datos_str = json.dumps(datos_locales, ensure_ascii=False)
        mensaje_con_datos += f"\n[Base de datos local — usa estos datos: {datos_str}]"

    contents = []
    for turno in historial:
        contents.append(
            genai_types.Content(role=turno["role"], parts=[genai_types.Part(text=turno["text"])])
        )
    contents.append(
        genai_types.Content(role="user", parts=[genai_types.Part(text=mensaje_con_datos)])
    )

    try:
        cliente = genai.Client(api_key=GEMINI_API_KEY)
        response = cliente.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=600,
                temperature=0.7,
            ),
        )
        respuesta = response.text.strip() if response.text else "No pude generar una respuesta."

        historial.append({"role": "user", "text": mensaje})
        historial.append({"role": "model", "text": respuesta})
        contexto["historial"] = historial[-10:]

        return {"respuesta": respuesta, "contexto": contexto}

    except Exception as e:
        return {
            "respuesta": (
                "Hubo un problema al conectar con la IA.<br>"
                f"<small style='color:#6b7280'>{str(e)[:120]}</small>"
            ),
            "contexto": contexto,
        }


JS_CODE = r"""(function(){
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
  try{localStorage.setItem('nutrigpt-dark',on?'1':'0');}catch(e){}
}
var saved=null;try{saved=localStorage.getItem('nutrigpt-dark');}catch(e){}
var prefersDark=!!(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches);
setDark(saved!==null?saved==='1':prefersDark);
dmBtn.addEventListener('click',function(){setDark(!document.documentElement.classList.contains('dark'));});
document.querySelectorAll('.tab').forEach(function(tab){
  tab.addEventListener('click',function(){
    var id=tab.dataset.tab;
    document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('active',t===tab);});
    document.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('active',p.id==='panel-'+id);});
  });
});
	var ctx={last_recipe_ids:[],last_selected_recipe_id:null};
	var AVATAR_IMG='<img src="/icon-192.png" alt="Bot">';
	function addMsg(html,isUser,cls){
  var m=document.createElement('div');
  m.className='m '+(isUser?'u':'bot')+(cls?' '+cls:'');
	  if(!isUser){var av=document.createElement('div');av.className='avatar';av.innerHTML=AVATAR_IMG;m.appendChild(av);}
  var b=document.createElement('div');b.className='b';b.innerHTML=html;
  m.appendChild(b);msgs.appendChild(m);msgs.scrollTop=msgs.scrollHeight;return m;
}
function send(){
  var txt=inp.value.trim();if(!txt)return;
  addMsg(txt,true);inp.value='';
  var t=addMsg('Pensando...',false,'typing');
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensaje:txt,contexto:ctx})})
    .then(function(r){return r.json();})
    .then(function(d){t.remove();if(d.contexto)ctx=d.contexto;addMsg(d.respuesta);})
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
    return generar_respuesta(mensaje, contexto)


@app.post("/api/analyze-foto")
async def analyze_foto(data: dict):
    image_b64 = data.get("image_b64", "")
    mime_type = data.get("mime_type", "image/jpeg")
    if not image_b64:
        return {"error": "No se recibió imagen."}

    client = genai.Client(api_key=GEMINI_API_KEY)
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
        image_data = base64.b64decode(image_b64)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                genai_types.Part.from_bytes(data=image_data, mime_type=mime_type),
                prompt,
            ],
        )
        raw = response.text.strip() if response.text else ""
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
    "name": "NutriGPT",
    "short_name": "NutriGPT",
    "description": "Asistente de nutrición: calorías, macros, calculadora TDEE y estimación por foto",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#e0e5ec",
    "theme_color": "#3a9d6e",
    "orientation": "portrait-primary",
    "icons": [
        {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
        {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
    "categories": ["health", "food"],
}

SW_CODE = r"""
const CACHE='nutrigpt-v1';
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

# Iconos en base64 generados a partir del logo oficial
ICON_192_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAMAAAADACAYAAABS3GwHAAAriElEQVR4nO2deXQc13Wnf/e9quoFK0GCG7ivIkVqoTZLogQttuOxpdiKB3ROFFmKx8dznInNWCPbmUxmmjiZ8dixY0XRTHzi43G0xJNEiC07tqNYliyBpETJJrVy30AIJEgABIm1l6p6784fVdVYSYJEg0ID79OhKHVXd7+uvve9e++7717C5SSVErWAaNxSr0Dg6OHa1INxnkUriWmd8vV6EK8i0GIA1cxcQURJAM5lHathvLjMnCaibgAdDG4G00FpiXeZeDed5kON9U9m81czqHZLSjYCGvX1+nINki7Hh9TV1UnUAQ2bGlT02MbHP7tK+l6tFnQnMa5j5iXCthySBDDAWoM1A8xgZgyoi6EoIICIACKQIJAQAAGsGNrzXSI6xoRdQvNLyrIbt3/hewejl9Y9UyfRADQ0DMjLBA5z4qh7pk421DXoaLar/c6DS+CJ+5j5k8y4yUo4FpihfQXta4C1ZiYGAQQmMFE4wsuiqIaCw2AAxMwgBgNETCAhhCUgLAkQwc+4PhFeJ6IfwtbPNn7+yWPhq6muoU4MnjgLzYQIViqVEvVbtjCIGABuf+wzd4L4c8x8jxV3SlkpqJwPBnwwiIiDqcII+nSBAeZwsmMCLBmzQFLCz7p9RPQzMH136+bvvxRczZTasoXqJ8A0KqzADdPY2//qoY+ywCNCiDuFJaGyHjRrP1wcRcE/31CsMAMaYBYkLBm3A6tA65dI41tb//iJfwVGWhSFoGACWPdMncwL/qMP3AxpbRGW+DBAUFmXGaSJjNAbLggzQxNYyLhDAEP7+nkof8vWLz29Axgqa+OlEMJItala2Vjf6N/wtQdmJkplPYg+Lywp/IyrAWIiyAJ8jmGawQwFMFkJR2hfaTB/J9OnUr/506c7a1O1VmN9o8I4wyPjU4BUSqC+ngHwrd9+6F7LpseEYy/1+3PMgDaCbygEzFAECKskRtr1mnyPN7/y8BM/FVBIpWg8YdNLVoBoGaqtrbX0fUu+IW3rYdYM5fk+EVmX+r4Gw7lgZl/alkWCoDz/2+LZY19tbGz0x2MSXZIChMuPf+PX718QTzpPW3H7Drc/pxDELcWlvKfBMBYYrAFipyQm/az3cjbtPvDrP/nB8UgmL/b9LloBog+65dsPXG9Z1j8Lx1rsp3Nm1jdcVpjZt5IxS7t+s+/7//7Vh5/eeSlKcFEKEH3Axm/df7eMOc+CqEy5xuQxvD8wsy8dywJzr8q5921/5AcvXqwSjFkBoje+7VsP/BbF7B+DOa59rYyja3g/YYYSlpAgynLO+8S2R57+xcUowZjs9bpn6mRjfaN/8zd//64B4VcmymN43yGCDEOkcYrZP775m79/V2N94BiP6fUXuiBySize limit. Use line ranges to read remaining content)
ICON_512_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAB/ZUlEQVR4nO3dd4Bc13Uf/u+5970pW4AFFr0SIAGSAHuTWCCQlG11WbaykG1JpKQ4cmxHUbccx8lyf3HiQskUIydOZEcSRcmFa8mSVaxGiiDBJvYCECwgem/bp7x37/n98d5bLECUxfad/X4kFgxnZ2Znd945995zzxXQaBO0tspa3G8AYH3b+vhU9/vl2z9QV7LhXCt+ifO6SIzMV9W5Apmtos1QzBDINDXaIB71EBQUUhQgGMPvh4gICsQCLUFRVoNe8dKj0C4IjorKYYUeFJH96nWvNbLLqdlRdNH+n372G33Jl7/e2ta1AQCsx40ebW16qvvRyJDxfgE1KA34MDcCvq2tzZ94h+v+9iONQUd0nli5wEFWKOQ8A12minMgaAJQMMYEJjQQY6BeoaqAKtRr+pFQqALJ34iIxoEIRABAkv8bSW8TiBGo9/CRh/c+BlCGokME2zxkq0BftdBX1OnmuCl89eHf/kr3iQ/f2tpq7gfMeoAJwShgAjASFNLS3mIAoH1duxv4n9a23lrADHeeg7lagMuguFSB1SIy04aBMaFNArzzUO8HBHuoAh6AQiEQTT5nmn3SAPDnR0TjT7NBCSQdkqgoBApABDAQSJYUiDEQayBG4CMHF8VeVY+I4AUAzynwjIV/vCgzXvnRx79UGfhELfe0WABob2n36ePTMDCADJWqrL3tRrv+tvVu4C/iqtaWXFNT3SoreoMq3igqb4Rgic0FoQQWGjv4NNhD1SdBXgCoERUZ8BPhz4aIaoVmf1dRBcSnoxkDESPGwFiD7BrpqnEExQ4VfVQEjzqVDR0dfZs2tbVXBzyirL1trV1/2/0OIkwGhoBB5mz0/8IdH/Svvf0Dc0JrboQ1N3nvbxTIiqCQsxDrive/Drive, Docs, Sheets, Slides). Use when performing any operation with the gws CLI.
- skill-creator: Guide for creating or updating skills that extend Manus via specialized knowledge, workflows, or tool integrations. For any modification or improvement request, MUST first read this skill and follow its update workflow instead of editing files directly.
- similarweb-analytics: Analyze websites and domains using SimilarWeb traffic data. Get traffic metrics, engagement stats, global rankings, traffic sources, and geographic distribution for comprehensive website research.
- bgm-prompter: MUST read this skill BEFORE entering generate mode for music tasks. Covers prompt crafting framework, structure syntax, and multi-clip strategy.
- image_processing: Perform deterministic programmatic image operations, such as cropping, resizing, flipping, mirroring, rotating, format conversion, or multi-image stitching.
- media_generation: Generate or modify images, videos, audio, music or speech using AI.
- parallel_processing: Divide task into homogeneous subtasks and execute them in parallel.
- slides_content_writing: Prepare contents before generating slide-based presentations. Must be in a separate phase from `slides_generation` and must occur before the phase with `slides_generation`.
- slides_generation: Generate slide-based presentations, such as slide decks or PowerPoint (PPT/PPTX). Must be in a separate phase from `slides_content_writing` and must occur after the phase with `slides_content_writing`.
- technical_writing: Produce precise, structured writing for technical or academic purposes.
- web_development: Build and deploy interactive websites, web applications, or mobile apps. Must not co-exist with `parallel_processing` in the same phase.
</skills>
<github_integration>
The user has enabled GitHub integration for this task and **explicitly selected** these repositories: mariocm13/Portfolio1
- Always interact with GitHub using the GitHub CLI `gh` via the `shell` tool
- GitHub CLI is already pre-configured and logged in, ready to use directly
- Repositories need to be cloned manually using `$ gh repo clone <repo-name>`
- When creating new repositories, always use `--private` flag by default to protect user privacy (e.g., `gh repo create <name> --private`)
</github_integration>
<user_profile>
Subscription limitations:
- The user does not have access to video generation features due to current subscription plan, MUST supportively ask the user to upgrade subscription when requesting video generation
- The user can only generate presentations with a maximum of 12 slides, MUST supportively ask the user to upgrade subscription when requesting more than 12 slides
- The user does not have access to generate Nano Banana (image mode) presentations, MUST supportively ask the user to upgrade subscription when requesting it
</user_profile>


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
    from fastapi.responses import Response
    import base64
    return Response(content=base64.b64decode(ICON_192_B64), media_type="image/png",
                    headers={"Cache-Control": "public, max-age=604800"})


@app.get("/icon-512.png")
async def get_icon_512():
    from fastapi.responses import Response
    import base64
    return Response(content=base64.b64decode(ICON_512_B64), media_type="image/png",
                    headers={"Cache-Control": "public, max-age=604800"})


if __name__ == "__main__":
    import uvicorn
    raw_port = os.environ.get("PORT", "8000")
    clean_port = "".join(filter(str.isdigit, str(raw_port)))
    port = int(clean_port) if clean_port else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
