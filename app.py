from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import os
import re
import unicodedata
import requests
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

DRIVE_FILE_ID = "1pMn-MyxfEaag0rzZbwYSzSciYnRDOodw"
CALORIES_DATA_PATH = "data/calories.json"
RECIPES_DATA_PATH = "data/recipes_large.json"
NUTRITION_KNOWLEDGE_PATH = "data/nutrition_knowledge.json"

ORDINALES = {
    "primera": 1, "primero": 1, "segunda": 2, "segundo": 2,
    "tercera": 3, "tercero": 3, "cuarta": 4, "cuarto": 4,
    "quinta": 5, "quinto": 5, "ultima": -1, "ultimo": -1,
}

MEDICAL_RISK_KEYWORDS = {
    "diabetes", "embarazo", "embarazada", "renal", "rinon",
    "hipertension", "alergia", "medicacion", "trigliceridos",
    "colesterol", "trastorno alimentario", "anemia",
}

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
button,input{-webkit-appearance:none;appearance:none;touch-action:manipulation;user-select:none;-webkit-user-select:none}
:root{
  --bg:#e0e5ec;
  --nm-d:#a3b1c6;
  --nm-l:#ffffff;
  --text:#31456a;
  --muted:#7b8fa6;
  --accent:#3a9d6e;
  --accent-light:#cce8da;
  --r:16px;
  --sh:6px 6px 14px var(--nm-d),-6px -6px 14px var(--nm-l);
  --sh-sm:3px 3px 8px var(--nm-d),-3px -3px 8px var(--nm-l);
  --sh-in:inset 4px 4px 9px var(--nm-d),inset -4px -4px 9px var(--nm-l);
  --sh-press:inset 2px 2px 5px var(--nm-d),inset -2px -2px 5px var(--nm-l);
}
html.dark{
  --bg:#1e2130;
  --nm-d:#13151e;
  --nm-l:#2a2f42;
  --text:#c8d0e7;
  --muted:#6e7a9a;
  --accent:#4ade80;
  --accent-light:#0d2318;
}
html,body{height:100%;overflow:hidden;background:var(--bg);overscroll-behavior:none}
body{font-family:'Inter',system-ui,sans-serif;color:var(--text);font-size:14px;line-height:1.5;transition:background .3s,color .3s;display:flex;flex-direction:column}
.app{max-width:960px;width:100%;flex:1;margin:0 auto;display:flex;flex-direction:column;background:var(--bg);transition:background .3s;overflow:hidden}
.header{padding:18px 22px 14px;display:flex;align-items:center;gap:14px;flex-shrink:0}
.icon{width:44px;height:44px;background:var(--accent);border-radius:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:4px 4px 10px rgba(58,157,110,.4),-2px -2px 6px rgba(255,255,255,.5)}
html.dark .icon{box-shadow:4px 4px 10px rgba(0,0,0,.5),-2px -2px 6px rgba(74,222,128,.15)}
.icon svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.header h1{font-size:17px;font-weight:700;letter-spacing:-.4px}
.header p{font-size:11px;color:var(--muted);margin-top:2px}
.header-end{margin-left:auto}
#dm{width:40px;height:40px;background:var(--bg);border:none;border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--muted);box-shadow:var(--sh-sm);transition:box-shadow .2s,color .2s}
#dm:active{box-shadow:var(--sh-press);color:var(--accent)}
#dm svg{width:17px;height:17px;fill:currentColor}
.tabs{display:flex;gap:12px;padding:0 22px 16px;flex-shrink:0}
.tab{flex:1;padding:11px;font-size:13px;font-weight:600;color:var(--muted);background:var(--bg);border:none;border-radius:14px;cursor:pointer;font-family:inherit;box-shadow:var(--sh-sm);transition:box-shadow .2s,color .2s,background .3s}
.tab.active{box-shadow:var(--sh-press);color:var(--accent)}
.panel{display:none;flex:1;flex-direction:column;min-height:0;overflow:hidden}
.panel.active{display:flex}
.msgs{flex:1;overflow-y:auto;padding:8px 22px 14px;display:flex;flex-direction:column;gap:14px;scrollbar-width:thin;scrollbar-color:var(--nm-d) transparent;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
.msgs::-webkit-scrollbar{width:4px}
.msgs::-webkit-scrollbar-thumb{background:var(--nm-d);border-radius:4px}
.m{display:flex;animation:fadeUp .22s ease both}
.m.u{justify-content:flex-end}
.b{max-width:78%;padding:12px 16px;border-radius:18px;line-height:1.7;font-size:14px}
.m.bot .b{background:var(--bg);box-shadow:var(--sh-sm);border-radius:6px 18px 18px 18px}
.m.u .b{background:var(--accent);color:#fff;box-shadow:4px 4px 10px rgba(58,157,110,.35),-2px -2px 6px rgba(255,255,255,.4);border-radius:18px 6px 18px 18px}
html.dark .m.u .b{box-shadow:4px 4px 10px rgba(74,222,128,.25),-2px -2px 5px rgba(42,47,66,.8)}
.typing .b{color:var(--muted);font-style:italic}
.composer{padding:14px 22px 22px;display:flex;gap:10px;flex-shrink:0;background:var(--bg)}
#inp{flex:1;padding:13px 16px;border:none;border-radius:14px;font-size:16px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);transition:box-shadow .2s,background .3s,color .3s;user-select:auto;-webkit-user-select:auto}
#inp:focus{box-shadow:var(--sh-in),0 0 0 2px var(--accent)}
#inp::placeholder{color:var(--muted)}
#btn{padding:13px 22px;background:var(--accent);color:#fff;border:none;border-radius:14px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:4px 4px 10px rgba(58,157,110,.4),-2px -2px 6px rgba(255,255,255,.35);transition:box-shadow .15s,transform .1s;flex-shrink:0}
#btn:active{transform:scale(.97);box-shadow:inset 2px 2px 5px rgba(0,0,0,.18),inset -1px -1px 3px rgba(255,255,255,.1)}
html.dark #btn{box-shadow:4px 4px 10px rgba(0,0,0,.4),-2px -2px 6px rgba(74,222,128,.15)}
.gallery-top{padding:6px 22px 0;flex-shrink:0}
#gsearch{width:100%;padding:13px 16px;border:none;border-radius:14px;font-size:16px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);transition:box-shadow .2s,background .3s,color .3s;display:block;user-select:auto;-webkit-user-select:auto}
#gsearch:focus{box-shadow:var(--sh-in),0 0 0 2px var(--accent)}
#gsearch::placeholder{color:var(--muted)}
.filters{display:flex;gap:8px;padding:14px 22px;overflow-x:auto;flex-shrink:0;scrollbar-width:none}
.filters::-webkit-scrollbar{display:none}
.filter-btn{padding:8px 15px;border-radius:22px;font-size:12px;font-weight:600;border:none;background:var(--bg);color:var(--muted);cursor:pointer;white-space:nowrap;font-family:inherit;flex-shrink:0;box-shadow:var(--sh-sm);transition:box-shadow .2s,color .2s,background .3s}
.filter-btn.active{box-shadow:var(--sh-press);color:var(--accent)}
.gallery-grid{flex:1;min-height:0;overflow-y:auto;padding:2px 22px 22px;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:18px;align-content:start;scrollbar-width:thin;scrollbar-color:var(--nm-d) transparent;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
.gallery-grid::-webkit-scrollbar{width:4px}
.gallery-grid::-webkit-scrollbar-thumb{background:var(--nm-d);border-radius:4px}
.card{border-radius:20px;overflow:hidden;cursor:pointer;box-shadow:var(--sh);transition:box-shadow .2s,transform .2s,background .3s;animation:fadeUp .25s ease both;background:var(--bg)}
.card:hover{transform:translateY(-3px);box-shadow:8px 8px 18px var(--nm-d),-8px -8px 18px var(--nm-l)}
.card:active{transform:scale(.98);box-shadow:var(--sh-press)}
.card-img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}
.card-ph{width:100%;aspect-ratio:4/3;display:none;align-items:center;justify-content:center;font-size:42px;background:linear-gradient(135deg,var(--accent-light),var(--bg))}
.card-body{padding:11px 13px 13px}
.card-name{font-size:13px;font-weight:700;line-height:1.35;margin-bottom:5px;color:var(--text)}
.card-cal{font-size:11px;color:var(--accent);font-weight:700;margin-bottom:7px}
.card-tags{display:flex;gap:5px;flex-wrap:wrap}
.tag{font-size:10px;padding:3px 9px;border-radius:10px;background:var(--bg);box-shadow:var(--sh-press);color:var(--accent);font-weight:600}
.empty{grid-column:1/-1;text-align:center;padding:50px 20px;color:var(--muted);font-size:13px}
.modal-wrap{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:100;display:flex;align-items:flex-end;justify-content:center;animation:fadeIn .2s ease}
.modal{background:var(--bg);border-radius:28px 28px 0 0;max-width:960px;width:100%;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;animation:slideUp .28s ease;box-shadow:0 -8px 40px rgba(0,0,0,.18)}
.modal-img{width:100%;height:190px;object-fit:cover;flex-shrink:0;display:block}
.modal-ph{width:100%;height:190px;display:none;align-items:center;justify-content:center;font-size:64px;flex-shrink:0;background:linear-gradient(135deg,var(--accent-light),var(--bg))}
.modal-body{padding:22px 24px 34px;overflow-y:auto;flex:1}
.modal-head{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:18px}
.modal-name{font-size:19px;font-weight:700;line-height:1.3}
.modal-kcal{font-size:13px;color:var(--accent);font-weight:700;margin-top:4px}
.x-btn{width:36px;height:36px;border-radius:50%;border:none;background:var(--bg);cursor:pointer;color:var(--muted);font-size:19px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:var(--sh-sm);transition:box-shadow .15s,color .15s;font-family:inherit}
.x-btn:active{box-shadow:var(--sh-press);color:var(--accent)}
.modal-sec{margin-top:20px}
.modal-sec h3{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px}
.modal-ing{font-size:13px;line-height:2.2}
.modal-step{display:flex;gap:12px;margin-bottom:11px;font-size:13px;line-height:1.65}
.sn{width:24px;height:24px;min-width:24px;border-radius:50%;background:var(--bg);box-shadow:var(--sh-sm);color:var(--accent);font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes slideUp{from{transform:translateY(70px);opacity:0}to{transform:translateY(0);opacity:1}}
small{font-size:12px}
.calc-wrap{flex:1;overflow-y:auto;padding:18px 22px 30px;-webkit-overflow-scrolling:touch}
.calc-card{background:var(--bg);border-radius:22px;padding:22px;box-shadow:var(--sh);margin-bottom:18px}
.calc-title{font-size:16px;font-weight:700;margin-bottom:20px;color:var(--text)}
.calc-row{margin-bottom:16px}
.calc-row.two{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:0}
.calc-row.two .calc-group{margin-bottom:16px}
.calc-group{margin-bottom:16px}
.calc-label{display:block;font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
.calc-inp{width:100%;padding:12px 14px;border:none;border-radius:12px;font-size:16px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);-webkit-appearance:none;user-select:auto;-webkit-user-select:auto}
.calc-inp:focus{box-shadow:var(--sh-in),0 0 0 2px var(--accent)}
.calc-sel{width:100%;padding:12px 14px;border:none;border-radius:12px;font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);-webkit-appearance:none;cursor:pointer}
.seg{display:flex;gap:8px;flex-wrap:wrap}
.seg-btn{flex:1;padding:10px 8px;border:none;border-radius:12px;font-size:13px;font-weight:600;font-family:inherit;background:var(--bg);color:var(--muted);cursor:pointer;box-shadow:var(--sh-sm);transition:box-shadow .2s,color .2s;white-space:nowrap;touch-action:manipulation}
.seg-btn.active{box-shadow:var(--sh-press);color:var(--accent)}
.calc-btn{width:100%;padding:14px;background:var(--accent);color:#fff;border:none;border-radius:14px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:4px 4px 10px rgba(58,157,110,.4),-2px -2px 6px rgba(255,255,255,.35);transition:box-shadow .15s,transform .1s;touch-action:manipulation;margin-top:4px}
.calc-btn:active{transform:scale(.98);box-shadow:inset 2px 2px 5px rgba(0,0,0,.18)}
.calc-result{background:var(--bg);border-radius:22px;padding:22px;box-shadow:var(--sh)}
.res-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:22px}
.res-box{background:var(--bg);border-radius:16px;padding:14px 10px;text-align:center;box-shadow:var(--sh-sm)}
.res-box.accent{box-shadow:4px 4px 12px rgba(58,157,110,.35),-4px -4px 12px rgba(255,255,255,.5)}
.res-val{font-size:22px;font-weight:700;color:var(--accent);line-height:1}
.res-lbl{font-size:11px;font-weight:700;color:var(--text);margin-top:4px;text-transform:uppercase;letter-spacing:.06em}
.res-sub{font-size:10px;color:var(--muted);margin-top:2px}
.macro-title{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px}
.macro-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px}
.macro-box{background:var(--bg);border-radius:16px;padding:14px 10px;text-align:center;box-shadow:var(--sh-sm)}
.macro-val{font-size:18px;font-weight:700;color:var(--text)}
.macro-lbl{font-size:11px;color:var(--muted);margin-top:4px}
.macro-g{font-size:10px;color:var(--accent);font-weight:700;margin-top:2px}
.res-note{font-size:12px;color:var(--muted);line-height:1.6;padding:12px 14px;background:var(--bg);border-radius:12px;box-shadow:var(--sh-in)}
@media(max-width:600px){
  .header{padding:14px 16px 10px}
  .tabs{padding:0 16px 12px;gap:8px}
  .msgs{padding:8px 14px 12px}
  .composer{padding:10px 14px 18px;gap:8px}
  #btn{padding:13px 16px;font-size:12px}
  .gallery-top{padding:6px 14px 0}
  .filters{padding:12px 14px}
  .gallery-grid{padding:2px 14px 18px;gap:12px;grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
  .card-name{font-size:12px}
  .modal-body{padding:18px 18px 28px}
  .foto-wrap{padding:14px}
  .foto-macros{grid-template-columns:repeat(2,1fr)}
}
.foto-wrap{flex:1;overflow-y:auto;padding:22px;display:flex;justify-content:center;align-items:flex-start}
.foto-card{background:var(--bg);border-radius:24px;box-shadow:var(--sh);padding:28px 24px;width:100%;max-width:480px}
.foto-title{font-size:17px;font-weight:700;margin-bottom:20px;text-align:center}
.foto-drop{border-radius:18px;box-shadow:var(--sh-in);padding:20px;min-height:180px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;cursor:pointer;transition:box-shadow .2s}
.foto-drop.drag{box-shadow:inset 0 0 0 2px var(--accent),var(--sh-in)}
#foto-preview{width:100%;border-radius:12px;max-height:260px;object-fit:contain;display:block}
#foto-placeholder{display:flex;flex-direction:column;align-items:center;gap:10px}
.foto-icon{font-size:44px}
.foto-hint{font-size:13px;color:var(--muted);text-align:center}
.foto-pick-btn{padding:10px 24px;background:var(--bg);border:none;border-radius:14px;font-size:13px;font-weight:600;color:var(--accent);cursor:pointer;font-family:inherit;box-shadow:var(--sh-sm);margin-top:4px}
.foto-status{font-size:13px;color:var(--muted);text-align:center;margin:14px 0;min-height:20px}
.foto-result{margin-top:10px}
.foto-food-name{font-size:16px;font-weight:700;text-align:center;margin-bottom:4px}
.foto-kcal-big{font-size:42px;font-weight:800;color:var(--accent);text-align:center;line-height:1.1;margin-bottom:14px}
.foto-portion-row{display:flex;align-items:center;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.foto-slider{flex:1;min-width:80px;accent-color:var(--accent)}
.foto-slider-val{font-size:13px;font-weight:600;color:var(--accent);min-width:44px;text-align:right}
.foto-macros{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.foto-macro-box{background:var(--bg);border-radius:14px;box-shadow:var(--sh-sm);padding:10px;text-align:center}
.foto-macro-val{font-size:17px;font-weight:700;color:var(--text)}
.foto-macro-lbl{font-size:10px;color:var(--muted);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
.foto-tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.foto-disclaimer{font-size:10px;color:var(--muted);text-align:center;line-height:1.5}
</style>
</head>
<body>
<div class="app">
  <div class="header">
    <div class="icon">
      <svg viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 008 20C19 20 22 3 22 3c-1 2-8 5-8 5"/></svg>
    </div>
    <div>
      <h1>NutriGPT</h1>
      <p>Asistente de nutrici\u00f3n y recetas</p>
    </div>
    <div class="header-end">
      <button id="dm" title="Modo oscuro" aria-label="Alternar modo oscuro">
        <svg id="dm-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </div>
  <nav class="tabs">
    <button class="tab active" data-tab="chat">Chat</button>
    <button class="tab" data-tab="recetas">Recetas</button>
    <button class="tab" data-tab="calc">Calculadora</button>
    <button class="tab" data-tab="foto">📷 Foto</button>
  </nav>
  <div id="panel-chat" class="panel active">
    <div class="msgs" id="msgs">
      <div class="m bot">
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
      <button id="btn">Enviar</button>
    </div>
  </div>
  <div id="panel-recetas" class="panel">
    <div class="gallery-top">
      <input type="text" id="gsearch" placeholder="Buscar recetas\u2026" autocomplete="off">
    </div>
    <div class="filters">
      <button class="filter-btn active" data-cat="all">Todas</button>
      <button class="filter-btn" data-cat="pollo">Pollo</button>
      <button class="filter-btn" data-cat="pescado">Pescado</button>
      <button class="filter-btn" data-cat="carne">Carne</button>
      <button class="filter-btn" data-cat="vegetariano">Vegetariano</button>
      <button class="filter-btn" data-cat="arroz">Arroz</button>
      <button class="filter-btn" data-cat="legumbres">Legumbres</button>
      <button class="filter-btn" data-cat="pasta">Pasta</button>
      <button class="filter-btn" data-cat="desayuno">Desayuno</button>
      <button class="filter-btn" data-cat="sopa">Sopas</button>
      <button class="filter-btn" data-cat="ensalada">Ensaladas</button>
      <button class="filter-btn" data-cat="postre">Postres</button>
    </div>
    <div class="gallery-grid" id="gg">
      <div class="empty">Cargando recetas\u2026</div>
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
</div>
  <div id="panel-foto" class="panel">
    <div class="foto-wrap">
      <div class="foto-card">
        <div class="foto-title">Estimar calorías por foto</div>
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
<div id="modal" style="display:none"></div>
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.20.0/dist/tf.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.1/dist/mobilenet.min.js"></script>
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


def construir_lista_html(items, limit=3):
    return "".join(f"\u2014 {item}<br>" for item in items[:limit])


def load_recipes_from_drive():
    url = f"https://docs.google.com/uc?export=download&id={DRIVE_FILE_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as exc:
        print(f"Error cargando recetas desde Drive: {exc}")
    if os.path.exists(RECIPES_DATA_PATH):
        with open(RECIPES_DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"recetas": []}


def load_json_file(path, empty_value):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return empty_value


recipes_db = load_recipes_from_drive()
calories_db = load_json_file(CALORIES_DATA_PATH, {"alimentos": []})
nutrition_knowledge = load_json_file(NUTRITION_KNOWLEDGE_PATH, {"topics": [], "food_profiles": []})
recipes_by_id = {receta["id"]: receta for receta in recipes_db.get("recetas", [])}


def buscar_recetas(terminos, strict=False):
    if isinstance(terminos, str):
        terminos = tokens_relevantes(terminos)
    resultados = []
    for receta in recipes_db.get("recetas", []):
        contenido = normalizar_texto(" ".join([receta["nombre"]] + receta["ingredientes"]))
        score = 0
        tiene_match_directo = False
        for termino in terminos:
            termino_normalizado = normalizar_texto(termino)
            if not termino_normalizado:
                continue
            if termino_normalizado in contenido:
                score += 3
                tiene_match_directo = True
            else:
                for token in termino_normalizado.split():
                    if len(token) > 3 and token in contenido:
                        score += 1
        if score > 0 and (not strict or tiene_match_directo):
            resultados.append((score, receta))
    resultados.sort(key=lambda item: (-item[0], item[1].get("calorias_aprox", 0)))
    return [receta for _, receta in resultados[:10]]


USOS_INGREDIENTE = {
    "melon": ["Ensalada de frutas con menta", "Batido de melón y yogur", "Gazpacho de melón", "Macedonias frescas"],
    "sandia": ["Zumo de sandía con limón", "Granizado de sandía", "Ensalada de verano con feta y sandía", "Batido rosa refrescante"],
    "fresa": ["Batido de fresas con leche", "Yogur con fresas y granola", "Ensalada con fresas y espinacas"],
    "platano": ["Batido proteico de plátano", "Tostadas con plátano y mantequilla de cacahuete", "Porridge con plátano"],
    "manzana": ["Zumo natural de manzana", "Ensalada de frutas", "Manzana al horno con canela"],
    "naranja": ["Zumo de naranja natural", "Smoothie cítrico", "Ensalada de naranja con hinojo"],
    "limon": ["Agua con limón", "Vinagreta de limón para ensaladas", "Limonada casera"],
    "aguacate": ["Guacamole casero", "Tostada de aguacate con huevo", "Ensalada verde con aguacate"],
    "tomate": ["Gazpacho andaluz", "Ensalada de tomate y mozzarella", "Salsa casera de tomate"],
    "pepino": ["Ensalada fresca de pepino", "Gazpacho", "Agua detox con pepino y limón"],
    "espinaca": ["Batido verde con espinacas", "Salteado de espinacas con ajo", "Ensalada de espinacas"],
    "zanahoria": ["Zumo de zanahoria y naranja", "Crudités con hummus", "Crema de zanahoria"],
    "brocoli": ["Brócoli al vapor con limón", "Crema de brócoli", "Salteado de brócoli con ajo"],
    "pollo": ["Pollo a la plancha con verduras", "Pechuga al horno con especias", "Caldo de pollo casero"],
    "salmon": ["Salmón a la plancha con limón", "Salmón al horno con miel", "Tartar de salmón"],
    "atun": ["Ensalada de atún con huevo", "Pasta con atún y tomate", "Tataki de atún"],
    "huevo": ["Tortilla española", "Huevos revueltos con verduras", "Huevos al plato"],
    "arroz": ["Arroz con verduras salteadas", "Arroz caldoso", "Risotto de setas"],
    "pasta": ["Pasta con tomate casero", "Pasta con atún", "Pasta salteada con verduras"],
    "avena": ["Porridge con fruta", "Overnight oats", "Tortitas de avena y plátano"],
    "yogur": ["Smoothie bowl", "Yogur con frutas y semillas", "Tzatziki"],
    "queso": ["Tostada con queso y tomate", "Ensalada caprese", "Quesadillas de verduras"],
    "lentejas": ["Lentejas estofadas", "Ensalada de lentejas", "Sopa de lentejas"],
    "garbanzos": ["Hummus casero", "Ensalada de garbanzos", "Potaje de garbanzos"],
}


def crear_sugerencia_ingredientes(ingredientes):
    sugerencias = []
    for ing in ingredientes:
        ing_norm = normalizar_texto(ing)
        for key, ideas in USOS_INGREDIENTE.items():
            if key in ing_norm or ing_norm in key:
                sugerencias.extend(ideas)
                break
    sugerencias_unicas = list(dict.fromkeys(sugerencias))[:6]
    ingredientes_str = " y ".join(f"<strong>{i}</strong>" for i in ingredientes[:3])
    if sugerencias_unicas:
        lista = "".join(f"\u2014 {s}<br>" for s in sugerencias_unicas)
        return (
            f"No tengo recetas guardadas con {ingredientes_str}, "
            f"pero con esos ingredientes puedes preparar:<br><br>{lista}<br>"
            "\u00bfQuieres detalles de alguna de estas ideas? "
            "Tambi\u00e9n puedes explorar la pesta\u00f1a de <em>Recetas</em>."
        )
    return (
        f"No encontr\u00e9 recetas con {ingredientes_str}.<br><br>"
        "Los ingredientes con m\u00e1s recetas en mi base de datos son: "
        "<em>pollo, arroz, salm\u00f3n, avena, huevo y legumbres</em>. "
        "Prueba combinando alguno de ellos."
    )


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


def calcular_calorias_estimadas(alimento_info, cantidad):
    valor = cantidad.get("valor")
    unidad = cantidad.get("unidad")
    if not valor or not unidad:
        return None, None
    calorias_base = alimento_info["calorias"]
    unidad_base = normalizar_texto(alimento_info["unidad"])
    unidad_norm = normalizar_texto(unidad)
    factor = None
    if "100" in unidad_base:
        if unidad_norm in {"g", "gramo", "gramos"}:
            factor = valor / 100
        elif unidad_norm == "kg":
            factor = valor * 10
    if factor is None:
        return None, None
    calorias = round(calorias_base * factor, 1)
    macros = None
    if all(k in alimento_info for k in ("proteina", "carbohidratos", "grasas")):
        macros = {
            "proteina": round(alimento_info["proteina"] * factor, 1),
            "carbohidratos": round(alimento_info["carbohidratos"] * factor, 1),
            "grasas": round(alimento_info["grasas"] * factor, 1),
        }
        if "fibra" in alimento_info:
            macros["fibra"] = round(alimento_info["fibra"] * factor, 1)
    return calorias, macros


def formatear_macros(alimento_info, factor=1.0):
    if not all(k in alimento_info for k in ("proteina", "carbohidratos", "grasas")):
        return ""
    p = round(alimento_info["proteina"] * factor, 1)
    c = round(alimento_info["carbohidratos"] * factor, 1)
    g = round(alimento_info["grasas"] * factor, 1)
    f = round(alimento_info.get("fibra", 0) * factor, 1)
    linea = f"Prote\u00edna {p}g \u00b7 Carbohidratos {c}g \u00b7 Grasas {g}g"
    if f:
        linea += f" \u00b7 Fibra {f}g"
    return f"<br><small style='color:#6b7280'>{linea}</small>"


def formatear_detalle_receta(receta):
    ingredientes = "".join(f"\u2014 {ing}<br>" for ing in receta["ingredientes"][:8])
    pasos = "".join(f"{i}. {paso}<br>" for i, paso in enumerate(receta["instrucciones"][:5], 1))
    return (
        f"<strong>{receta['nombre']}</strong><br><br>"
        f"Aproximadamente <strong>{receta['calorias_aprox']} kcal</strong>.<br><br>"
        f"<strong>Ingredientes:</strong><br>{ingredientes}<br>"
        f"<strong>Preparaci\u00f3n:</strong><br>{pasos}"
    )


def formatear_ingredientes_receta(receta):
    ingredientes = "".join(f"\u2014 {ing}<br>" for ing in receta["ingredientes"][:10])
    return f"<strong>Ingredientes de {receta['nombre']}:</strong><br><br>{ingredientes}"


def formatear_preparacion_receta(receta):
    pasos = "".join(f"{i}. {paso}<br>" for i, paso in enumerate(receta["instrucciones"][:8], 1))
    return f"<strong>C\u00f3mo se prepara {receta['nombre']}:</strong><br><br>{pasos}"


def explicar_capacidades():
    return (
        "Hola, soy <strong>NutriGPT</strong>.<br><br>"
        "Puedo ayudarte con:<br><br>"
        "<strong>Recetas</strong><br>"
        "\u2014 \u201cQu\u00e9 puedo cocinar con pollo y espinacas\u201d<br>"
        "\u2014 \u201cDame una cena alta en prote\u00edna\u201d<br><br>"
        "<strong>Calor\u00edas y macros</strong><br>"
        "\u2014 \u201cCu\u00e1ntas calor\u00edas tiene el arroz\u201d<br>"
        "\u2014 \u201cCu\u00e1ntas calor\u00edas tienen 250 g de salm\u00f3n\u201d<br><br>"
        "<strong>Nutrici\u00f3n pr\u00e1ctica</strong><br>"
        "\u2014 \u201cLa avena es buena para desayunar?\u201d<br>"
        "\u2014 \u201cQu\u00e9 me conviene para perder grasa sin pasar hambre?\u201d<br><br>"
        "Despu\u00e9s de darte recetas puedes seguir con <em>la 2</em>, "
        "<em>dame ingredientes</em> o <em>c\u00f3mo se hace</em>."
    )


def es_pregunta_sobre_receta(texto_normalizado):
    pistas = [
        "la receta", "esa receta", "ese plato", "esa opcion", "la opcion",
        "ingredientes", "como se hace", "preparacion", "pasos",
        "primera", "segunda", "tercera", "cuarta", "quinta",
    ]
    if re.search(r"\b[1-5]\b", texto_normalizado):
        return True
    return any(pista in texto_normalizado for pista in pistas)


def extraer_indice_receta(texto_normalizado, total):
    match = re.search(r"\b([1-9])\b", texto_normalizado)
    if match:
        valor = int(match.group(1))
        if 1 <= valor <= total:
            return valor - 1
    for palabra, indice in ORDINALES.items():
        if palabra in texto_normalizado:
            if indice == -1:
                return total - 1
            if 1 <= indice <= total:
                return indice - 1
    return None


def buscar_receta_por_nombre(texto, recetas_contexto):
    texto_normalizado = normalizar_texto(texto)
    for receta in recetas_contexto:
        nombre = normalizar_texto(receta["nombre"])
        if nombre and (nombre in texto_normalizado or texto_normalizado in nombre):
            return receta
        tokens_nombre = set(tokens_relevantes(receta["nombre"]))
        tokens_texto = set(tokens_relevantes(texto))
        if tokens_nombre and len(tokens_nombre & tokens_texto) >= max(1, min(2, len(tokens_nombre))):
            return receta
    return None


def obtener_recetas_contexto(contexto):
    recipe_ids = contexto.get("last_recipe_ids", []) if contexto else []
    return [recipes_by_id[rid] for rid in recipe_ids if rid in recipes_by_id]


def resolver_receta_referenciada(mensaje, contexto):
    recetas_contexto = obtener_recetas_contexto(contexto)
    if not recetas_contexto:
        return None
    texto_normalizado = normalizar_texto(mensaje)
    receta_por_nombre = buscar_receta_por_nombre(mensaje, recetas_contexto)
    if receta_por_nombre:
        return receta_por_nombre
    indice = extraer_indice_receta(texto_normalizado, len(recetas_contexto))
    if indice is not None:
        return recetas_contexto[indice]
    recipe_id = contexto.get("last_selected_recipe_id") if contexto else None
    if recipe_id in recipes_by_id and (
        re.search(r"\b(esa|ese|receta|ingredientes|pasos|preparacion)\b", texto_normalizado)
        or "como se hace" in texto_normalizado
    ):
        return recipes_by_id[recipe_id]
    return None


def responder_detalle_receta(receta, mensaje):
    texto_normalizado = normalizar_texto(mensaje)
    if "ingredientes" in texto_normalizado:
        return formatear_ingredientes_receta(receta)
    if "como se hace" in texto_normalizado or "preparacion" in texto_normalizado or "pasos" in texto_normalizado:
        return formatear_preparacion_receta(receta)
    if "calorias" in texto_normalizado or "kcal" in texto_normalizado:
        return (
            f"<strong>{receta['nombre']}</strong><br><br>"
            f"Esta receta ronda las <strong>{receta['calorias_aprox']} kcal</strong>."
        )
    return formatear_detalle_receta(receta)


def buscar_temas_nutricion(texto):
    texto_normalizado = normalizar_texto(texto)
    resultados = []
    for topic in nutrition_knowledge.get("topics", []):
        score = 0
        for keyword in topic.get("keywords", []):
            if normalizar_texto(keyword) in texto_normalizado:
                score += 2
        if score > 0:
            resultados.append((score, topic))
    resultados.sort(key=lambda item: -item[0])
    return [topic for _, topic in resultados[:3]]


def buscar_perfil_alimento(texto, alimento=""):
    candidatos_normalizados = [normalizar_texto(c) for c in [texto, alimento] if c]
    for profile in nutrition_knowledge.get("food_profiles", []):
        aliases = [normalizar_texto(profile["name"])] + [
            normalizar_texto(a) for a in profile.get("aliases", [])
        ]
        for candidato in candidatos_normalizados:
            for alias in aliases:
                if alias and (alias in candidato or candidato in alias):
                    return profile
    return None


def detectar_riesgo_medico(texto):
    texto_normalizado = normalizar_texto(texto)
    return any(normalizar_texto(kw) in texto_normalizado for kw in MEDICAL_RISK_KEYWORDS)


def responder_nutricion(mensaje, analisis):
    texto_normalizado = normalizar_texto(mensaje)
    perfil = buscar_perfil_alimento(mensaje, analisis.get("alimento", ""))
    temas = buscar_temas_nutricion(mensaje)
    partes = []

    if perfil:
        partes.append(f"<strong>{perfil['name']}</strong> \u2014 {perfil['summary']}")
        alimento_info = buscar_alimento(perfil["name"])
        if alimento_info:
            macro_str = formatear_macros(alimento_info)
            partes.append(
                f"<br><br>Aporta unas <strong>{alimento_info['calorias']} kcal</strong> "
                f"por {alimento_info['unidad']}.{macro_str}"
            )
        if perfil.get("highlights"):
            partes.append(
                "<br><br><strong>Lo m\u00e1s \u00fatil en la pr\u00e1ctica:</strong><br>"
                + construir_lista_html(perfil["highlights"], limit=3)
            )
        if perfil.get("watchouts"):
            partes.append(f"<br><strong>Ten en cuenta:</strong> {perfil['watchouts']}")

    if temas:
        tema_principal = temas[0]
        if not perfil:
            partes.append(tema_principal["summary"])
        partes.append(
            "<br><br><strong>En la pr\u00e1ctica:</strong><br>"
            + construir_lista_html(tema_principal["tips"], limit=3)
        )

    if not perfil and not temas:
        partes.append(
            "Si quieres comer mejor sin complicarte, la base es bastante simple: "
            "prote\u00edna en cada comida, fruta o verdura a diario y alimentos poco procesados "
            "en cantidades que puedas mantener."
        )
        partes.append(
            "<br><br>Montando cada comida con tres piezas \u2014 prote\u00edna, vegetal y "
            "carbohidrato ajustado a tu actividad \u2014 casi siempre es suficiente para mejorar."
        )

    if detectar_riesgo_medico(texto_normalizado):
        partes.append(
            "<br><br>Si hay una condici\u00f3n m\u00e9dica, embarazo o medicaci\u00f3n, "
            "lo ideal es personalizarlo con un profesional."
        )

    partes.append(
        "<br><br><em>\u00bfQuieres que lo adapte a un objetivo concreto? "
        "Perder grasa, ganar m\u00fasculo, desayuno, cena o pre/post entreno.</em>"
    )
    return "".join(partes)


def generar_respuesta(mensaje, contexto=None):
    contexto = contexto or {}
    analisis = nlp.procesar(mensaje)
    intencion = analisis["intencion"]
    palabras_clave = analisis["palabras_clave"]
    ingredientes = analisis["ingredientes"]
    alimento = analisis["alimento"]
    cantidad = analisis["cantidad"]
    texto_normalizado = normalizar_texto(mensaje)

    receta_referenciada = None
    if intencion in {"general", "recetas"} or es_pregunta_sobre_receta(texto_normalizado):
        receta_referenciada = resolver_receta_referenciada(mensaje, contexto)
        if receta_referenciada and (es_pregunta_sobre_receta(texto_normalizado) or intencion == "general"):
            contexto["last_selected_recipe_id"] = receta_referenciada["id"]
            return {
                "respuesta": responder_detalle_receta(receta_referenciada, mensaje),
                "contexto": contexto,
            }

    if intencion == "ayuda":
        return {"respuesta": explicar_capacidades(), "contexto": contexto}

    if intencion == "recetas":
        terminos = ingredientes if ingredientes else palabras_clave
        strict = bool(ingredientes)
        recetas = buscar_recetas(terminos, strict=strict)

        if recetas:
            recetas_top = recetas[:5]
            contexto["last_recipe_ids"] = [r["id"] for r in recetas_top]
            contexto["last_selected_recipe_id"] = recetas_top[0]["id"]

            if len(recetas_top) == 1 or "detalle" in texto_normalizado or "ingredientes" in texto_normalizado:
                return {"respuesta": formatear_detalle_receta(recetas_top[0]), "contexto": contexto}

            partes = ["Aqu\u00ed tienes opciones que encajan con lo que buscas:<br><br>"]
            for i, receta in enumerate(recetas_top, 1):
                contenido = normalizar_texto(" ".join([receta["nombre"]] + receta["ingredientes"]))
                coincidencias = [t for t in terminos if normalizar_texto(t) in contenido]
                motivo = (
                    f" <span style='color:#6b7280;font-size:12px'>{', '.join(coincidencias[:3])}</span>"
                    if coincidencias else ""
                )
                partes.append(
                    f"<strong>{i}. {receta['nombre']}</strong> \u2014 {receta['calorias_aprox']} kcal{motivo}<br>"
                )
            partes.append(
                "<br><em>Pide detalles con: la 2, dame ingredientes de la 3, "
                "c\u00f3mo se hace la primera\u2026</em>"
            )
            return {"respuesta": "".join(partes), "contexto": contexto}

        if ingredientes:
            return {"respuesta": crear_sugerencia_ingredientes(ingredientes), "contexto": contexto}
        termino_busqueda = ", ".join(terminos) if terminos else "tu consulta"
        return {
            "respuesta": (
                f"No encontr\u00e9 recetas para <strong>{termino_busqueda}</strong>.<br><br>"
                "Prueba con uno o dos ingredientes principales, como:<br>"
                "<em>cena ligera con pollo</em> o <em>desayuno con avena</em>."
            ),
            "contexto": contexto,
        }

    if intencion == "calorias":
        candidatos = []
        if alimento:
            candidatos.extend(buscar_alimentos_similares(alimento))
        for palabra in palabras_clave:
            for candidato in buscar_alimentos_similares(palabra):
                if candidato not in candidatos:
                    candidatos.append(candidato)

        if candidatos:
            principal = candidatos[0]
            partes = [f"<strong>{principal['nombre']}</strong><br><br>"]
            partes.append(f"<strong>{principal['calorias']} kcal</strong> por {principal['unidad']}.")

            calorias_estimadas, macros_estimados = calcular_calorias_estimadas(principal, cantidad)
            if calorias_estimadas is not None:
                partes.append(
                    f"<br>Para {cantidad['valor']} {cantidad['unidad']}: "
                    f"<strong>{calorias_estimadas} kcal</strong>."
                )
                if macros_estimados:
                    linea = (
                        f"Prote\u00edna {macros_estimados['proteina']}g \u00b7 "
                        f"Carbohidratos {macros_estimados['carbohidratos']}g \u00b7 "
                        f"Grasas {macros_estimados['grasas']}g"
                    )
                    if "fibra" in macros_estimados:
                        linea += f" \u00b7 Fibra {macros_estimados['fibra']}g"
                    partes.append(f"<br><small style='color:#6b7280'>{linea}</small>")
            else:
                partes.append(formatear_macros(principal))

            if len(candidatos) > 1:
                partes.append(
                    "<br><br>Tambi\u00e9n podr\u00eda ser: "
                    + ", ".join(item["nombre"] for item in candidatos[1:4]) + "."
                )

            partes.append(
                "<br><br><em>\u00bfQuieres saber si encaja en tu objetivo? "
                "Perder grasa, ganar m\u00fasculo o rendimiento deportivo.</em>"
            )
            return {"respuesta": "".join(partes), "contexto": contexto}

        return {
            "respuesta": (
                "No encuentro ese alimento.<br><br>"
                "Prueba con un nombre m\u00e1s concreto, como: "
                "<em>pechuga de pollo</em>, <em>arroz blanco</em>, "
                "<em>salm\u00f3n</em> o <em>manzana</em>."
            ),
            "contexto": contexto,
        }

    if intencion == "nutricion" or buscar_temas_nutricion(mensaje) or buscar_perfil_alimento(mensaje, alimento):
        return {"respuesta": responder_nutricion(mensaje, analisis), "contexto": contexto}

    return {
        "respuesta": (
            "No termin\u00e9 de entender lo que buscas.<br><br>"
            "Puedo ayudarte con recetas, calor\u00edas o nutrici\u00f3n pr\u00e1ctica:<br>"
            "\u2014 <em>Qu\u00e9 puedo cocinar con pollo y espinacas</em><br>"
            "\u2014 <em>Cu\u00e1ntas calor\u00edas tiene el arroz</em><br>"
            "\u2014 <em>La avena es buena para desayunar?</em>"
        ),
        "contexto": contexto,
    }


JS_CODE = r"""(function(){
var dmBtn=document.getElementById('dm');
var dmIcon=document.getElementById('dm-icon');
var msgs=document.getElementById('msgs');
var inp=document.getElementById('inp');
var btn=document.getElementById('btn');
var gg=document.getElementById('gg');
var gsearch=document.getElementById('gsearch');
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
    if(id==='recetas'&&!galleryLoaded)loadGallery();
  });
});
var ctx={last_recipe_ids:[],last_selected_recipe_id:null};
var galleryLoaded=false,allRecipes=[],recipesMap={},activeFilter='all',searchTerm='';
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
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensaje:txt,contexto:ctx})})
    .then(function(r){return r.json();})
    .then(function(d){t.remove();if(d.contexto)ctx=d.contexto;addMsg(d.respuesta);})
    .catch(function(){t.remove();addMsg('Error de conexion. Intenta de nuevo.');});
}
inp.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
btn.addEventListener('click',send);
var Q='?w=800&h=600&fit=crop&auto=format';
var PHOTOS={
  salmon:'https://images.unsplash.com/photo-1467003909585-2f8a72700288'+Q,
  avena:'https://images.unsplash.com/photo-1517673132405-a56a62b18caf'+Q,
  batido:'https://images.unsplash.com/photo-1553530666-ba11a7da3888'+Q,
  tostada:'https://images.unsplash.com/photo-1484723091739-30990d4d5b21'+Q,
  ensalada:'https://images.unsplash.com/photo-1512621776951-a57141f2eefd'+Q,
  pasta:'https://images.unsplash.com/photo-1551183053-bf91798d454e'+Q,
  sopa:'https://images.unsplash.com/photo-1547592166-23ac45744acd'+Q,
  pollo:'https://images.unsplash.com/photo-1598103442097-8b74394b95c1'+Q,
  pescado:'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2'+Q,
  huevo:'https://images.unsplash.com/photo-1482049016688-2d3e1b311543'+Q,
  carne:'https://images.unsplash.com/photo-1544025162-d76694265947'+Q,
  arroz:'https://images.unsplash.com/photo-1516684732162-798a0062be99'+Q,
  verdura:'https://images.unsplash.com/photo-1540420773420-3366772f4999'+Q,
  fruta:'https://images.unsplash.com/photo-1619566636858-adf3ef46400b'+Q,
  legumbre:'https://images.unsplash.com/photo-1546069901-ba9599a7e63c'+Q,
  yogur:'https://images.unsplash.com/photo-1488477181946-6428a0291777'+Q,
  queso:'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d'+Q,
  seta:'https://images.unsplash.com/photo-1504674900247-0877df9cc836'+Q,
  curry:'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38'+Q,
  wok:'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd'+Q,
  sandwich:'https://images.unsplash.com/photo-1528735602780-2552fd46c7af'+Q,
  tortilla:'https://images.unsplash.com/photo-1565958011703-44f9829ba187'+Q,
  quinoa:'https://images.unsplash.com/photo-1512058564366-18510be2db19'+Q,
  gazpacho:'https://images.unsplash.com/photo-1476124369491-e7addf5db371'+Q
};
var DEFAULT_POOL=[
  'https://images.unsplash.com/photo-1498837167922-ddd27525d352'+Q,
  'https://images.unsplash.com/photo-1490645935967-10de6ba17061'+Q,
  'https://images.unsplash.com/photo-1473093295043-cdd812d0e601'+Q,
  'https://images.unsplash.com/photo-1414235077428-338989a2e8c0'+Q,
  'https://images.unsplash.com/photo-1504674900247-0877df9cc836'+Q,
  'https://images.unsplash.com/photo-1529042410759-befb1204b468'+Q,
  'https://images.unsplash.com/photo-1476224203421-9ac39bcb3327'+Q,
  'https://images.unsplash.com/photo-1540189549336-e6e99d7aa571'+Q,
  'https://images.unsplash.com/photo-1565299585323-38d6b0865b47'+Q,
  'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445'+Q,
  'https://images.unsplash.com/photo-1546069901-ba9599a7e63c'+Q,
  'https://images.unsplash.com/photo-1512621776951-a57141f2eefd'+Q,
  'https://images.unsplash.com/photo-1547592180-85f173990554'+Q,
  'https://images.unsplash.com/photo-1476224203421-9ac39bcb3327'+Q,
  'https://images.unsplash.com/photo-1506354666786-959d6d497f1a'+Q,
  'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd'+Q
];
var EMOJIS={salmon:'&#x1F41F;',avena:'&#x1F33E;',batido:'&#x1F964;',tostada:'&#x1F35E;',ensalada:'&#x1F957;',pasta:'&#x1F35D;',sopa:'&#x1F35C;',pollo:'&#x1F357;',pescado:'&#x1F420;',huevo:'&#x1F373;',carne:'&#x1F969;',arroz:'&#x1F35A;',verdura:'&#x1F966;',fruta:'&#x1F34E;',legumbre:'&#x1FAD8;',yogur:'&#x1F962;',queso:'&#x1F9C0;',seta:'&#x1F344;',curry:'&#x1F35B;',wok:'&#x1FAD5;',sandwich:'&#x1F96A;',tortilla:'&#x1F373;',quinoa:'&#x1F33E;',gazpacho:'&#x1F35C;'};
function photoKey(r){
  var t=((r.nombre||'')+' '+(r.ingredientes||[]).join(' ')).toLowerCase();
  var checks=[
    ['salmon'],['avena','porridge','overnight'],['batido','smoothie','shake'],
    ['tostada','pan tostado'],['ensalada'],['pasta','espagueti','macarron','fideo'],
    ['sopa','crema de','caldo','pure'],['pollo','pechuga','contramuslo'],
    ['atun','merluza','dorada','bacalao','salmon','pescado'],
    ['huevo','tortilla de huevo','revuelto'],
    ['carne','ternera','cerdo','cordero','buey','jamon','bacon','pavo'],
    ['arroz','risotto'],['brocoli','coliflor','espinaca','zanahoria','pimiento','calabacin','verdura'],
    ['fruta','fresa','arandano','melon','sandia','pera','manzana','platano','mango','kiwi','piña'],
    ['lenteja','garbanzo','alubia','judias','legumbre'],
    ['yogur','kefir'],['queso'],['seta','champiñon','boletus'],
    ['curry','tikka','masala'],['wok','salteado','oriental','chino'],
    ['sandwich','bocadillo','wrap','burrito'],['tortilla'],
    ['quinoa'],['gazpacho','salmorejo']
  ];
  var keys=['salmon','avena','batido','tostada','ensalada','pasta','sopa','pollo','pescado','huevo','carne','arroz','verdura','fruta','legumbre','yogur','queso','seta','curry','wok','sandwich','tortilla','quinoa','gazpacho'];
  for(var i=0;i<checks.length;i++){
    for(var j=0;j<checks[i].length;j++){
      if(t.indexOf(checks[i][j])>=0)return keys[i];
    }
  }
  return null;
}
function getPhoto(r){
  var k=photoKey(r);
  if(k)return PHOTOS[k];
  return DEFAULT_POOL[Math.abs(r.id||0)%DEFAULT_POOL.length];
}
function getEmoji(r){
  var k=photoKey(r);
  return k?EMOJIS[k]:'&#x1F37D;';
}
function matchesCat(r,cat){
  if(cat==='all')return true;
  if(r.categoria)return r.categoria===cat;
  var t=((r.nombre||'')+' '+(r.ingredientes||[]).join(' ')).toLowerCase();
  if(cat==='pollo')return /\bpollo\b/.test(t);
  if(cat==='pescado')return /\bpescado\b|salmon|at[uú]n|merluza|dorada|bacalao|marisco|gamba|calamar|lubina|rape/.test(t);
  if(cat==='carne')return /\bres\b|\bcarne\b|ternera|cerdo|cordero|pavo|buey|jam[oó]n|bacon/.test(t);
  if(cat==='vegetariano')return !/\bpollo\b|\bpescado\b|\bres\b|\bcarne\b|salmon|at[uú]n|merluza|bacalao|ternera|cerdo|cordero|pavo|buey|jam[oó]n|bacon|marisco|gamba|calamar/.test(t);
  if(cat==='arroz')return /\barroz\b/.test(t);
  if(cat==='legumbres')return /\bgarbanzo|\blenteja|\balubia|\bjud[ií]a/.test(t);
  if(cat==='pasta')return /\bpasta\b|\bquinoa\b/.test(t);
  if(cat==='desayuno')return /desayuno|avena|tostada|pancake|smoothie/.test(t);
  if(cat==='sopa')return /\bsopa\b|\bcaldo\b|\bcrema\b|minestrone/.test(t);
  if(cat==='ensalada')return /\bensalada\b/.test(t);
  if(cat==='postre')return /\bpostre\b|flan|mousse|tarta|natilla|crema catalana/.test(t);
  return false;
}
function loadGallery(){
  galleryLoaded=true;
  fetch('/api/recipes').then(function(r){return r.json();}).then(function(d){
    allRecipes=(d.recetas||[]);
    allRecipes.forEach(function(r){recipesMap[String(r.id)]=r;});
    renderGallery();
  }).catch(function(){gg.innerHTML='<div class="empty">Error cargando recetas.</div>';});
}
function renderGallery(){
  var filtered=allRecipes.filter(function(r){
    var txt=((r.nombre||'')+' '+(r.ingredientes||[]).join(' ')).toLowerCase();
    return matchesCat(r,activeFilter)&&(!searchTerm||txt.indexOf(searchTerm)>=0);
  });
  if(!filtered.length){gg.innerHTML='<div class="empty">Sin resultados.</div>';return;}
  gg.innerHTML=filtered.map(function(r){
    var tags=(r.ingredientes||[]).slice(0,2).map(function(i){return '<span class="tag">'+i.split(' ')[0]+'</span>';}).join('');
    var id=String(r.id);
    return '<div class="card" onclick="window._om(\''+id+'\')">'+
      '<img class="card-img" src="'+getPhoto(r)+'" alt="" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'+
      '<div class="card-ph">'+getEmoji(r)+'</div>'+
      '<div class="card-body"><div class="card-name">'+r.nombre+'</div>'+
      '<div class="card-cal">'+r.calorias_aprox+' kcal</div>'+
      '<div class="card-tags">'+tags+'</div></div></div>';
  }).join('');
}
document.querySelectorAll('.filter-btn').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.filter-btn').forEach(function(x){x.classList.remove('active');});
    b.classList.add('active');activeFilter=b.dataset.cat;renderGallery();
  });
});
gsearch.addEventListener('input',function(e){searchTerm=e.target.value.toLowerCase().trim();renderGallery();});
function openModal(id){
  var r=recipesMap[id];if(!r)return;
  var ings=(r.ingredientes||[]).map(function(i){return '- '+i;}).join('<br>');
  var steps=(r.instrucciones||[]).map(function(s,i){return '<div class="modal-step"><div class="sn">'+(i+1)+'</div><div>'+s+'</div></div>';}).join('');
  var el=document.getElementById('modal');
  el.innerHTML='<div class="modal-wrap" onclick="if(event.target===this)window._cm()"><div class="modal">'+
    '<img class="modal-img" src="'+getPhoto(r)+'" alt="" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'+
    '<div class="modal-ph">'+getEmoji(r)+'</div>'+
    '<div class="modal-body"><div class="modal-head"><div>'+
    '<div class="modal-name">'+r.nombre+'</div><div class="modal-kcal">'+r.calorias_aprox+' kcal'+(r.tiempo?' &nbsp;·&nbsp; ⏱ '+r.tiempo:'')+(r.dificultad?' &nbsp;·&nbsp; '+r.dificultad:'')+'</div></div>'+
    '<button class="x-btn" onclick="window._cm()">x</button></div>'+
    '<div class="modal-sec"><h3>Ingredientes</h3><div class="modal-ing">'+ings+'</div></div>'+
    '<div class="modal-sec"><h3>Preparacion</h3>'+steps+'</div></div></div></div>';
  el.style.display='block';document.body.style.overflow='hidden';
}
function closeModal(){document.getElementById('modal').style.display='none';document.body.style.overflow='';}
window._om=openModal;window._cm=closeModal;

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
    'banana':['platano','banana'],'apple':['manzana'],'orange':['naranja'],
    'strawberry':['fresa','fresas'],'lemon':['limon'],'pineapple':['pina'],
    'mango':['mango'],'watermelon':['sandia'],'grape':['uvas'],'peach':['melocoton'],
    'pizza':['pizza'],'hamburger':['hamburguesa'],'hot dog':['salchicha'],
    'french fries':['patatas fritas'],'ice cream':['helado'],
    'pretzel':['pan'],'bagel':['pan'],'baguette':['pan','baguette'],
    'croissant':['croissant'],'waffle':['tortita'],'pancake':['tortita'],
    'burrito':['burrito'],'taco':['tacos'],
    'broccoli':['brocoli'],'carrot':['zanahoria'],'corn':['maiz'],
    'mushroom':['champiñon','setas'],'cucumber':['pepino'],
    'tomato':['tomate'],'lettuce':['lechuga'],'avocado':['aguacate'],
    'egg':['huevo','huevos'],'omelette':['tortilla'],
    'cheese':['queso'],'butter':['mantequilla'],
    'milk':['leche'],'yogurt':['yogur'],
    'chicken':['pollo'],'beef':['carne ternera','ternera'],'pork':['cerdo'],
    'salmon':['salmon'],'tuna':['atun'],'shrimp':['gamba','gambas'],
    'lobster':['langosta'],'crab':['cangrejo'],
    'rice':['arroz'],'pasta':['pasta'],'bread':['pan'],
    'oatmeal':['avena'],'granola':['granola'],
    'chocolate':['chocolate'],'cake':['pastel'],
    'coffee':['cafe'],'orange juice':['zumo naranja'],
    'beer':['cerveza'],'wine':['vino'],
    'almond':['almendra','almendras'],'peanut':['cacahuete'],
    'walnut':['nuez','nueces'],'olive':['aceituna'],
    'potato':['patata','patatas'],'sweet potato':['boniato'],
    'soup':['sopa'],'salad':['ensalada'],
    'sushi':['sushi'],'ramen':['ramen'],
    'lentil':['lentejas'],'chickpea':['garbanzo','garbanzos'],
    'tofu':['tofu']
  };

  var mnModel=null,mnLoading=false;
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

  function setStatus(msg){fotoStatus.textContent=msg;}

  function showPreview(file){
    var reader=new FileReader();
    reader.onload=function(e){
      fotoPreview.src=e.target.result;
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

  function preloadModel(){
    if(mnModel||mnLoading)return;
    if(typeof mobilenet==='undefined')return;
    mnLoading=true;
    mobilenet.load().then(function(m){mnModel=m;mnLoading=false;}).catch(function(){mnLoading=false;});
  }
  // Pre-cargar cuando el usuario cambia al tab de foto
  document.querySelectorAll('.tab').forEach(function(t){
    t.addEventListener('click',function(){if(t.dataset.tab==='foto')preloadModel();});
  });

  function findFoodKey(predictions){
    for(var i=0;i<predictions.length;i++){
      var lbl=predictions[i].className.toLowerCase();
      for(var key in FOOD_MAP){
        if(lbl.indexOf(key)>=0)return{key:key,label:lbl,prob:predictions[i].probability};
      }
    }
    return null;
  }

  function renderResult(alimento, gramos){
    var factor=gramos/100;
    var kcal=Math.round((alimento.calorias||0)*factor);
    fotoKcalBig.textContent=kcal+' kcal';
    var macros=[
      {v:Math.round((alimento.proteina||0)*factor),l:'Proteína'},
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
    if(!fotoPreview.src||fotoPreview.src==='about:blank')return;
    fotoResult.style.display='none';
    setStatus('Cargando modelo de IA\u2026');
    fotoGo.disabled=true;

    function doAnalysis(){
      setStatus('Analizando imagen\u2026');
      mnModel.classify(fotoPreview,5).then(function(preds){
        var match=findFoodKey(preds);
        if(!match){
          setStatus('No reconozco el alimento. Intenta con otra foto.');
          fotoGo.disabled=false;return;
        }
        var candidates=FOOD_MAP[match.key];
        var pct=Math.round(match.prob*100);
        // buscar primer candidato que devuelva resultado en /api/calories
        function tryNext(i){
          if(i>=candidates.length){
            setStatus('Alimento detectado ('+match.label+') pero sin datos nutricionales. Prueba otra foto.');
            fotoGo.disabled=false;return;
          }
          fetch('/api/calories?food='+encodeURIComponent(candidates[i])).then(function(r){return r.json();}).then(function(d){
            if(d.found){
              currentAlimento=d;
              var gramos=parseInt(fotoSlider.value);
              fotoFoodName.textContent=d.nombre+' \u2014 confianza '+pct+'%';
              renderResult(d,gramos);
              fotoResult.style.display='block';
              setStatus('');
            } else {
              tryNext(i+1);
            }
          }).catch(function(){tryNext(i+1);});
        }
        tryNext(0);
        fotoGo.disabled=false;
      }).catch(function(){
        setStatus('Error al analizar la imagen. Intenta de nuevo.');
        fotoGo.disabled=false;
      });
    }

    if(mnModel){doAnalysis();return;}
    if(typeof mobilenet==='undefined'){
      setStatus('El modelo aún se está cargando\u2026 espera un momento.');
      fotoGo.disabled=false;return;
    }
    mobilenet.load().then(function(m){mnModel=m;doAnalysis();}).catch(function(){
      setStatus('No se pudo cargar el modelo. Comprueba tu conexión.');
      fotoGo.disabled=false;
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


@app.get("/api/recipes")
async def get_recipes():
    return recipes_db


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
    "description": "Asistente de nutrición con recetas, calorías y calculadora de macros",
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

# SVG icon rendered as PNG placeholder (simple green circle with leaf)
ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">
<rect width="{s}" height="{s}" rx="{r}" fill="#3a9d6e"/>
<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" font-size="{fs}" font-family="system-ui">🥗</text>
</svg>"""


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
    svg = ICON_SVG.format(s=192, r=40, fs=120)
    return Response(content=svg.encode(), media_type="image/svg+xml",
                    headers={"Cache-Control": "public, max-age=604800"})


@app.get("/icon-512.png")
async def get_icon_512():
    from fastapi.responses import Response
    svg = ICON_SVG.format(s=512, r=100, fs=320)
    return Response(content=svg.encode(), media_type="image/svg+xml",
                    headers={"Cache-Control": "public, max-age=604800"})


if __name__ == "__main__":
    import uvicorn
    raw_port = os.environ.get("PORT", "8000")
    clean_port = "".join(filter(str.isdigit, str(raw_port)))
    port = int(clean_port) if clean_port else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
