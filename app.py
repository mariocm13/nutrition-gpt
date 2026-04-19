from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import os
import re
import unicodedata
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
.icon{width:46px;height:46px;background:linear-gradient(135deg,#42b87a 0%,#1f8c4e 100%);border-radius:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:5px 5px 12px rgba(31,140,78,.45),-3px -3px 8px rgba(255,255,255,.65)}
html.dark .icon{box-shadow:4px 4px 10px rgba(0,0,0,.5),-2px -2px 6px rgba(74,222,128,.15)}
.icon svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.header h1{font-size:17px;font-weight:700;letter-spacing:-.4px}
.header p{font-size:11px;color:var(--muted);margin-top:2px}
.header-end{margin-left:auto}
#dm{width:40px;height:40px;background:var(--bg);border:none;border-radius:12px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--muted);box-shadow:var(--sh-sm);transition:box-shadow .2s,color .2s}
#dm:active{box-shadow:var(--sh-press);color:var(--accent)}
#dm svg{width:17px;height:17px;fill:currentColor}
.tabs{display:flex;gap:12px;padding:0 22px 16px;flex-shrink:0}
.tab{flex:1;padding:8px 6px 9px;font-size:11px;font-weight:600;color:var(--muted);background:var(--bg);border:none;border-radius:14px;cursor:pointer;font-family:inherit;box-shadow:var(--sh-sm);transition:box-shadow .2s,color .2s,background .3s;display:flex;flex-direction:column;align-items:center;gap:3px}
.tab-ic{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
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
.chips{display:flex;gap:7px;padding:0 22px 14px;overflow-x:auto;flex-shrink:0;scrollbar-width:none}
.chips::-webkit-scrollbar{display:none}
.chip{padding:8px 14px;border-radius:18px;font-size:12px;font-weight:600;background:var(--bg);color:var(--accent);border:none;cursor:pointer;font-family:inherit;box-shadow:var(--sh-sm);transition:box-shadow .15s,transform .1s;flex-shrink:0;white-space:nowrap}
.chip:active{box-shadow:var(--sh-press);transform:scale(.97)}
.typing-dots{display:inline-flex;gap:5px;align-items:center;padding:2px 0}
.typing-dots span{width:8px;height:8px;border-radius:50%;background:var(--muted);display:block;animation:tdot .85s ease-in-out infinite}
.typing-dots span:nth-child(2){animation-delay:.17s}
.typing-dots span:nth-child(3){animation-delay:.34s}
@keyframes tdot{0%,100%{transform:translateY(0);opacity:.3}50%{transform:translateY(-5px);opacity:1}}
.mbar-wrap{margin-bottom:16px}
.mbar-row{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.mbar-lbl{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;width:80px;flex-shrink:0}
.mbar-bg{flex:1;height:10px;border-radius:5px;background:var(--bg);box-shadow:var(--sh-in);overflow:hidden}
.mbar-fill{height:100%;border-radius:5px;width:0;transition:width .7s cubic-bezier(.4,0,.2,1)}
.mbar-prot{background:linear-gradient(90deg,#4ade80,#16a34a)}
.mbar-carb{background:linear-gradient(90deg,#60a5fa,#2563eb)}
.mbar-fat{background:linear-gradient(90deg,#fbbf24,#d97706)}
.mbar-val{font-size:12px;font-weight:700;color:var(--text);width:54px;text-align:right;flex-shrink:0;line-height:1.3}
.mbar-g{font-size:10px;color:var(--muted);font-weight:600}
.res-box.accent{background:linear-gradient(135deg,var(--accent-light) 0%,var(--bg) 80%)}
@media(max-width:600px){
  .header{padding:14px 16px 10px}
  .tabs{padding:0 16px 12px;gap:8px}
  .msgs{padding:8px 14px 12px}
  .composer{padding:10px 14px 18px;gap:8px}
  #btn{padding:13px 16px;font-size:12px}
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
/* ── DIARIO ── */
.diary-wrap{flex:1;overflow-y:auto;padding:16px 22px 24px;display:flex;flex-direction:column;gap:14px;-webkit-overflow-scrolling:touch}
.diary-nav-row{display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.diary-date-lbl{font-size:13px;font-weight:700;color:var(--muted)}
.diary-nav-btn{width:32px;height:32px;border:none;border-radius:10px;background:var(--bg);box-shadow:var(--sh-sm);color:var(--muted);cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;font-family:inherit;transition:box-shadow .15s}
.diary-nav-btn:active{box-shadow:var(--sh-press)}
.diary-nav-btns{display:flex;gap:6px}
.cal-progress-card{background:var(--bg);border-radius:18px;padding:18px;box-shadow:var(--sh)}
.cal-progress-top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
.cal-progress-eaten{font-size:24px;font-weight:800;color:var(--accent);line-height:1}
.cal-progress-goal{font-size:12px;color:var(--muted);font-weight:600}
.cal-bar-bg{height:12px;border-radius:6px;background:var(--bg);box-shadow:var(--sh-in);overflow:hidden;margin-bottom:12px}
.cal-bar-fill{height:100%;border-radius:6px;background:linear-gradient(90deg,#4ade80,#16a34a);transition:width .5s ease;max-width:100%}
.cal-bar-fill.over{background:linear-gradient(90deg,#f87171,#dc2626)}
.cal-macros-row{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.cal-macro-box{text-align:center;padding:8px 4px;background:var(--bg);border-radius:10px;box-shadow:var(--sh-sm)}
.cal-macro-val{font-size:13px;font-weight:700;color:var(--text)}
.cal-macro-lbl{font-size:9px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-top:2px}
.diary-search-wrap{position:relative}
.diary-search{width:100%;padding:13px 16px;border:none;border-radius:14px;font-size:16px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);transition:box-shadow .2s;user-select:auto;-webkit-user-select:auto}
.diary-search:focus{box-shadow:var(--sh-in),0 0 0 2px var(--accent)}
.diary-search::placeholder{color:var(--muted)}
.diary-results{position:absolute;top:calc(100% + 6px);left:0;right:0;background:var(--bg);border-radius:14px;box-shadow:var(--sh);z-index:50;max-height:210px;overflow-y:auto;display:none;scrollbar-width:thin}
.diary-res-item{padding:11px 16px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-size:13px;border-bottom:1px solid rgba(163,177,198,.1);transition:background .15s}
.diary-res-item:last-child{border-bottom:none}
.diary-res-item:hover,.diary-res-item:active{background:var(--accent-light)}
.diary-res-name{font-weight:600}
.diary-res-cal{font-size:11px;color:var(--accent);font-weight:700}
.diary-scan-btn{position:absolute;right:12px;top:50%;transform:translateY(-50%);width:34px;height:34px;border:none;border-radius:10px;background:var(--bg);box-shadow:var(--sh-sm);color:var(--accent);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:box-shadow .15s}
.diary-scan-btn:active{box-shadow:var(--sh-press)}
.diary-scan-btn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.diary-add-row{display:flex;gap:8px}
.diary-grams{flex:1;padding:12px 14px;border:none;border-radius:12px;font-size:16px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);-webkit-appearance:none;user-select:auto;-webkit-user-select:auto}
.diary-add-btn{padding:12px 20px;background:var(--accent);color:#fff;border:none;border-radius:12px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:4px 4px 10px rgba(58,157,110,.4),-2px -2px 6px rgba(255,255,255,.3);flex-shrink:0;transition:box-shadow .15s,transform .1s}
.diary-add-btn:active{transform:scale(.97)}
.diary-add-btn:disabled{opacity:.5;cursor:default}
.diary-selected-food{font-size:12px;color:var(--accent);font-weight:600;padding:6px 0 0 2px;display:none}
.diary-entries-card{background:var(--bg);border-radius:18px;box-shadow:var(--sh);overflow:hidden}
.diary-entries-header{padding:13px 16px 11px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(163,177,198,.12)}
.diary-entries-title{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.diary-clear-btn{font-size:11px;color:var(--muted);background:none;border:none;cursor:pointer;font-family:inherit;font-weight:600;padding:0}
.diary-entry{display:flex;align-items:center;gap:10px;padding:11px 16px;border-bottom:1px solid rgba(163,177,198,.08)}
.diary-entry:last-child{border-bottom:none}
.diary-entry-info{flex:1;min-width:0}
.diary-entry-name{font-size:13px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.diary-entry-sub{font-size:11px;color:var(--muted);margin-top:2px}
.diary-entry-cal{font-size:13px;font-weight:700;color:var(--accent);flex-shrink:0}
.diary-entry-del{width:28px;height:28px;border:none;border-radius:8px;background:var(--bg);box-shadow:var(--sh-sm);color:var(--muted);cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:box-shadow .15s,color .15s}
.diary-entry-del:active{box-shadow:var(--sh-press);color:#ef4444}
.diary-empty{padding:28px 16px;text-align:center;color:var(--muted);font-size:13px}
/* ── PERFIL ── */
.prof-btn{width:38px;height:38px;border:none;border-radius:12px;background:var(--bg);box-shadow:var(--sh-sm);color:var(--muted);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:box-shadow .15s,color .15s;flex-shrink:0}
.prof-btn:active{box-shadow:var(--sh-press);color:var(--accent)}
.prof-btn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:200;display:flex;align-items:flex-end;justify-content:center;animation:fadeIn .2s}
.modal-sheet{background:var(--bg);border-radius:24px 24px 0 0;width:100%;max-width:480px;max-height:88vh;overflow-y:auto;padding:0 0 34px;animation:slideUp .25s ease;box-shadow:0 -8px 40px rgba(0,0,0,.2)}
.modal-sheet-handle{width:36px;height:4px;border-radius:2px;background:var(--nm-d);margin:14px auto 18px}
.modal-sheet-title{font-size:17px;font-weight:700;padding:0 24px 18px;border-bottom:1px solid rgba(163,177,198,.12);margin-bottom:18px}
.prof-form{padding:0 24px}
.prof-row{display:flex;gap:12px;margin-bottom:16px}
.prof-group{flex:1;min-width:0}
.prof-label{display:block;font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:7px}
.prof-inp{width:100%;padding:12px 14px;border:none;border-radius:12px;font-size:16px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);-webkit-appearance:none;user-select:auto;-webkit-user-select:auto}
.prof-inp:focus{box-shadow:var(--sh-in),0 0 0 2px var(--accent)}
.prof-sel{width:100%;padding:12px 14px;border:none;border-radius:12px;font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);-webkit-appearance:none;cursor:pointer}
.prof-save{width:100%;padding:14px;background:var(--accent);color:#fff;border:none;border-radius:14px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:4px 4px 10px rgba(58,157,110,.4),-2px -2px 6px rgba(255,255,255,.3);margin-top:6px;transition:box-shadow .15s,transform .1s}
.prof-save:active{transform:scale(.98)}
/* ── BARCODE ── */
.scan-overlay{position:fixed;inset:0;background:#000;z-index:300;display:flex;flex-direction:column}
.scan-header{padding:20px 20px 0;display:flex;align-items:center;gap:14px;flex-shrink:0}
.scan-close{width:38px;height:38px;border:none;border-radius:12px;background:rgba(255,255,255,.12);color:#fff;cursor:pointer;font-size:20px;display:flex;align-items:center;justify-content:center}
.scan-title{font-size:15px;font-weight:700;color:#fff}
.scan-video-wrap{flex:1;position:relative;overflow:hidden}
#scan-video{width:100%;height:100%;object-fit:cover}
.scan-frame{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none}
.scan-frame-box{width:260px;height:130px;border:2px solid var(--accent);border-radius:12px;box-shadow:0 0 0 9999px rgba(0,0,0,.5)}
.scan-hint{position:absolute;bottom:80px;left:0;right:0;text-align:center;font-size:13px;color:rgba(255,255,255,.7);font-weight:600}
.scan-manual-row{padding:16px 20px;background:#000;flex-shrink:0;display:flex;gap:8px}
.scan-manual-inp{flex:1;padding:12px 14px;border:none;border-radius:12px;font-size:16px;font-family:inherit;background:rgba(255,255,255,.1);color:#fff;outline:none;user-select:auto;-webkit-user-select:auto}
.scan-manual-inp::placeholder{color:rgba(255,255,255,.4)}
.scan-manual-btn{padding:12px 18px;background:var(--accent);color:#fff;border:none;border-radius:12px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit;flex-shrink:0}
.scan-result-card{position:absolute;bottom:0;left:0;right:0;background:var(--bg);border-radius:24px 24px 0 0;padding:22px 22px 34px;animation:slideUp .25s ease}
.scan-res-name{font-size:17px;font-weight:700;margin-bottom:4px}
.scan-res-brand{font-size:12px;color:var(--muted);margin-bottom:14px}
.scan-res-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:18px}
.scan-res-box{background:var(--bg);border-radius:12px;box-shadow:var(--sh-sm);padding:10px 6px;text-align:center}
.scan-res-val{font-size:16px;font-weight:700;color:var(--accent)}
.scan-res-lbl{font-size:9px;color:var(--muted);font-weight:700;text-transform:uppercase;margin-top:3px}
.scan-add-diary{width:100%;padding:14px;background:var(--accent);color:#fff;border:none;border-radius:14px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:4px 4px 10px rgba(58,157,110,.4)}
/* ── PREDICCIONES FOTO ── */
.pred-options{display:flex;flex-direction:column;gap:8px;margin:12px 0 4px}
.pred-opt{background:var(--bg);border-radius:14px;padding:12px 14px;box-shadow:var(--sh-sm);cursor:pointer;display:flex;align-items:center;gap:10px;border:2px solid transparent;transition:box-shadow .15s,border-color .15s;animation:fadeUp .2s ease both}
.pred-opt.selected{box-shadow:var(--sh-press);border-color:var(--accent)}
.pred-opt-info{flex:1;min-width:0}
.pred-opt-name{font-size:13px;font-weight:700;color:var(--text);margin-bottom:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pred-opt-bar{height:3px;border-radius:2px;background:linear-gradient(90deg,var(--accent),#27855c);transition:width .4s ease}
.pred-opt-pct{font-size:12px;font-weight:800;color:var(--accent);flex-shrink:0}
.pred-hint{font-size:11px;color:var(--muted);margin-bottom:8px;font-weight:600}
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
      <p>Asistente de nutrici\u00f3n</p>
    </div>
    <div class="header-end" style="display:flex;gap:8px">
      <button id="prof-btn" class="prof-btn" title="Mi perfil" aria-label="Perfil de usuario">
        <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      </button>
      <button id="dm" title="Modo oscuro" aria-label="Alternar modo oscuro">
        <svg id="dm-icon" viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
      </button>
    </div>
  </div>
  <nav class="tabs">
    <button class="tab active" data-tab="chat"><svg class="tab-ic" viewBox="0 0 24 24"><path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.42-4.03 8-9 8a9.86 9.86 0 01-4.26-.95L3 20l1.4-3.72C3.51 15.04 3 13.57 3 12c0-4.42 4.03-8 9-8s9 3.58 9 8z"/></svg>Chat</button>
    <button class="tab" data-tab="diario"><svg class="tab-ic" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/></svg>Diario</button>
    <button class="tab" data-tab="calc"><svg class="tab-ic" viewBox="0 0 24 24"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 7h6M8 12h2M14 12h2M8 16h2M14 16h2"/></svg>Calcular</button>
    <button class="tab" data-tab="foto"><svg class="tab-ic" viewBox="0 0 24 24"><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></svg>Foto</button>
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
    <div class="chips" id="chips">
      <button class="chip" data-q="\u00bfCu\u00e1ntas calor\u00edas tiene el pollo?">Calor\u00edas del pollo</button>
      <button class="chip" data-q="\u00bfQu\u00e9 desayuno saludable me recomiendas?">Desayuno saludable</button>
      <button class="chip" data-q="\u00bfCu\u00e1nta prote\u00edna necesito al d\u00eda?">Prote\u00edna diaria</button>
      <button class="chip" data-q="Receta con arroz y verduras">Arroz y verduras</button>
      <button class="chip" data-q="Alimentos ricos en fibra">Alimentos con fibra</button>
      <button class="chip" data-q="\u00bfQu\u00e9 comer antes de entrenar?">Antes del entreno</button>
    </div>
    <div class="composer">
      <input type="text" id="inp" placeholder="Escribe tu pregunta..." autocomplete="off" enterkeyhint="send" inputmode="text">
      <button id="btn">Enviar</button>
    </div>
  </div>
  <div id="panel-diario" class="panel">
    <div class="diary-wrap">
      <div class="diary-nav-row">
        <span class="diary-date-lbl" id="diary-date-lbl"></span>
        <div class="diary-nav-btns">
          <button class="diary-nav-btn" id="diary-prev" title="D\u00eda anterior">&#8592;</button>
          <button class="diary-nav-btn" id="diary-today" title="Hoy">Hoy</button>
          <button class="diary-nav-btn" id="diary-next" title="D\u00eda siguiente">&#8594;</button>
        </div>
      </div>
      <div class="cal-progress-card">
        <div class="cal-progress-top">
          <div><span class="cal-progress-eaten" id="diary-eaten">0</span> <span style="font-size:13px;font-weight:700;color:var(--text)">kcal</span></div>
          <div class="cal-progress-goal">de <span id="diary-goal">2000</span> kcal</div>
        </div>
        <div class="cal-bar-bg"><div class="cal-bar-fill" id="diary-bar" style="width:0%"></div></div>
        <div class="cal-macros-row">
          <div class="cal-macro-box"><div class="cal-macro-val" id="d-prot">0g</div><div class="cal-macro-lbl">Prote\u00edna</div></div>
          <div class="cal-macro-box"><div class="cal-macro-val" id="d-carb">0g</div><div class="cal-macro-lbl">Carbos</div></div>
          <div class="cal-macro-box"><div class="cal-macro-val" id="d-fat">0g</div><div class="cal-macro-lbl">Grasas</div></div>
        </div>
      </div>
      <div class="diary-search-wrap">
        <input type="text" class="diary-search" id="diary-search" placeholder="Buscar alimento para a\u00f1adir..." autocomplete="off" style="padding-right:52px">
        <button class="diary-scan-btn" id="diary-scan-btn" title="Escanear c\u00f3digo de barras">
          <svg viewBox="0 0 24 24"><path d="M3 9V5a2 2 0 012-2h4M15 3h4a2 2 0 012 2v4M21 15v4a2 2 0 01-2 2h-4M9 21H5a2 2 0 01-2-2v-4"/><line x1="7" y1="12" x2="7" y2="12.01"/><line x1="12" y1="7" x2="12" y2="17"/><line x1="17" y1="12" x2="17" y2="12.01"/></svg>
        </button>
        <div class="diary-results" id="diary-results"></div>
      </div>
      <div class="diary-selected-food" id="diary-selected-lbl"></div>
      <div class="diary-add-row">
        <input type="number" class="diary-grams" id="diary-grams" placeholder="Gramos (100g)" min="1" max="2000" value="100">
        <button class="diary-add-btn" id="diary-add-btn">A\u00f1adir</button>
      </div>
      <div class="diary-entries-card" id="diary-entries-card">
        <div class="diary-entries-header">
          <span class="diary-entries-title">Registro del d\u00eda</span>
          <button class="diary-clear-btn" id="diary-clear-btn">Limpiar todo</button>
        </div>
        <div id="diary-entries-list"><div class="diary-empty">A\u00fan no hay alimentos registrados hoy</div></div>
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
        <div class="mbar-wrap">
          <div class="mbar-row">
            <div class="mbar-lbl">Prote\u00edna</div>
            <div class="mbar-bg"><div class="mbar-fill mbar-prot" id="r-prot-bar"></div></div>
            <div class="mbar-val"><span id="r-prot"></span><br><span class="mbar-g" id="r-prot-g"></span></div>
          </div>
          <div class="mbar-row">
            <div class="mbar-lbl">Carbohidratos</div>
            <div class="mbar-bg"><div class="mbar-fill mbar-carb" id="r-carb-bar"></div></div>
            <div class="mbar-val"><span id="r-carb"></span><br><span class="mbar-g" id="r-carb-g"></span></div>
          </div>
          <div class="mbar-row">
            <div class="mbar-lbl">Grasas</div>
            <div class="mbar-bg"><div class="mbar-fill mbar-fat" id="r-fat-bar"></div></div>
            <div class="mbar-val"><span id="r-fat"></span><br><span class="mbar-g" id="r-fat-g"></span></div>
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

<div id="prof-modal" style="display:none">
  <div class="modal-overlay" onclick="if(event.target===this)closeProfModal()">
    <div class="modal-sheet">
      <div class="modal-sheet-handle"></div>
      <div class="modal-sheet-title">Mi Perfil</div>
      <div class="prof-form">
        <div class="prof-row">
          <div class="prof-group">
            <label class="prof-label">Nombre</label>
            <input class="prof-inp" type="text" id="p-nombre" placeholder="Tu nombre">
          </div>
        </div>
        <div class="prof-row">
          <div class="prof-group">
            <label class="prof-label">Sexo</label>
            <select class="prof-sel" id="p-sexo"><option value="h">Hombre</option><option value="m">Mujer</option></select>
          </div>
          <div class="prof-group">
            <label class="prof-label">Edad</label>
            <input class="prof-inp" type="number" id="p-edad" placeholder="25" min="10" max="100">
          </div>
        </div>
        <div class="prof-row">
          <div class="prof-group">
            <label class="prof-label">Peso (kg)</label>
            <input class="prof-inp" type="number" id="p-peso" placeholder="70" min="30" max="300">
          </div>
          <div class="prof-group">
            <label class="prof-label">Altura (cm)</label>
            <input class="prof-inp" type="number" id="p-altura" placeholder="170" min="100" max="250">
          </div>
        </div>
        <div class="prof-row">
          <div class="prof-group">
            <label class="prof-label">Actividad</label>
            <select class="prof-sel" id="p-act">
              <option value="1.2">Sedentario</option>
              <option value="1.375">Poco activo</option>
              <option value="1.55" selected>Moderado</option>
              <option value="1.725">Activo</option>
              <option value="1.9">Muy activo</option>
            </select>
          </div>
          <div class="prof-group">
            <label class="prof-label">Objetivo</label>
            <select class="prof-sel" id="p-obj">
              <option value="cut">Perder grasa</option>
              <option value="mant" selected>Mantener</option>
              <option value="bulk">Ganar m\u00fasculo</option>
            </select>
          </div>
        </div>
        <button class="prof-save" id="prof-save-btn">Guardar perfil</button>
      </div>
    </div>
  </div>
</div>

<div id="scan-overlay" style="display:none">
  <div class="scan-overlay">
    <div class="scan-header">
      <button class="scan-close" onclick="closeScan()">&#x2715;</button>
      <span class="scan-title">Escanear c\u00f3digo de barras</span>
    </div>
    <div class="scan-video-wrap">
      <video id="scan-video" autoplay playsinline muted></video>
      <div class="scan-frame"><div class="scan-frame-box"></div></div>
      <div class="scan-hint">Centra el c\u00f3digo de barras en el recuadro</div>
      <div id="scan-result-card" style="display:none" class="scan-result-card">
        <div class="scan-res-name" id="scan-res-name"></div>
        <div class="scan-res-brand" id="scan-res-brand"></div>
        <div class="scan-res-row">
          <div class="scan-res-box"><div class="scan-res-val" id="scan-r-cal">-</div><div class="scan-res-lbl">kcal</div></div>
          <div class="scan-res-box"><div class="scan-res-val" id="scan-r-prot">-</div><div class="scan-res-lbl">Prote\u00edna</div></div>
          <div class="scan-res-box"><div class="scan-res-val" id="scan-r-carb">-</div><div class="scan-res-lbl">Carbos</div></div>
          <div class="scan-res-box"><div class="scan-res-val" id="scan-r-fat">-</div><div class="scan-res-lbl">Grasas</div></div>
        </div>
        <button class="scan-add-diary" id="scan-add-diary-btn">A\u00f1adir al diario (100g)</button>
      </div>
    </div>
    <div class="scan-manual-row">
      <input class="scan-manual-inp" type="text" id="scan-manual-inp" placeholder="O introduce el c\u00f3digo manualmente..." inputmode="numeric">
      <button class="scan-manual-btn" id="scan-manual-btn">Buscar</button>
    </div>
  </div>
</div>

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


def load_json_file(path, empty_value):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return empty_value


recipes_db = load_json_file("data/recipes_large.json", {"recetas": []})
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
var chipsEl=document.getElementById('chips');
function addMsg(html,isUser,cls){
  var m=document.createElement('div');
  m.className='m '+(isUser?'u':'bot')+(cls?' '+cls:'');
  var b=document.createElement('div');b.className='b';b.innerHTML=html;
  m.appendChild(b);msgs.appendChild(m);msgs.scrollTop=msgs.scrollHeight;return m;
}
function send(){
  var txt=inp.value.trim();if(!txt)return;
  if(chipsEl)chipsEl.style.display='none';
  addMsg(txt,true);inp.value='';
  var t=addMsg('<div class="typing-dots"><span></span><span></span><span></span></div>',false,'typing');
  fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensaje:txt,contexto:ctx})})
    .then(function(r){return r.json();})
    .then(function(d){t.remove();if(d.contexto)ctx=d.contexto;addMsg(d.respuesta);})
    .catch(function(){t.remove();addMsg('Error de conexion. Intenta de nuevo.');});
}
inp.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
btn.addEventListener('click',send);
if(chipsEl){chipsEl.querySelectorAll('.chip').forEach(function(c){c.addEventListener('click',function(){inp.value=c.dataset.q;send();});});}

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
  document.getElementById('r-prot-g').textContent=protG+'g/d\u00eda';
  document.getElementById('r-carb').textContent=pct(carbG,4)+'%';
  document.getElementById('r-carb-g').textContent=carbG+'g/d\u00eda';
  document.getElementById('r-fat').textContent=pct(fatG,9)+'%';
  document.getElementById('r-fat-g').textContent=fatG+'g/d\u00eda';
  var pb=document.getElementById('r-prot-bar'),cb=document.getElementById('r-carb-bar'),fb=document.getElementById('r-fat-bar');
  if(pb){pb.style.width='0';cb.style.width='0';fb.style.width='0';}
  setTimeout(function(){if(pb){pb.style.width=pct(protG,4)+'%';cb.style.width=pct(carbG,4)+'%';fb.style.width=pct(fatG,9)+'%';}},60);
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

  // ── Tabla nutricional Food-101 (por 100g): {n:nombre,c:kcal,p:prot,hc:carbos,f:grasas}
  var F101={
    'apple_pie':{n:'Pastel de manzana',c:237,p:2.4,hc:34,f:11},
    'baby_back_ribs':{n:'Costillas de cerdo',c:291,p:25,hc:0,f:21},
    'baklava':{n:'Baklava',c:428,p:6,hc:48,f:25},
    'beef_carpaccio':{n:'Carpaccio de ternera',c:150,p:20,hc:2,f:7},
    'beef_tartare':{n:'Tartar de ternera',c:168,p:20,hc:3,f:9},
    'beet_salad':{n:'Ensalada de remolacha',c:88,p:3,hc:14,f:3},
    'beignets':{n:'Bu\u00f1uelos',c:350,p:5,hc:42,f:18},
    'bibimbap':{n:'Bibimbap',c:115,p:8,hc:15,f:3},
    'bread_pudding':{n:'Pud\u00edn de pan',c:285,p:9,hc:38,f:11},
    'breakfast_burrito':{n:'Burrito de desayuno',c:290,p:16,hc:28,f:13},
    'bruschetta':{n:'Bruschetta',c:165,p:5,hc:22,f:7},
    'caesar_salad':{n:'Ensalada C\u00e9sar',c:155,p:7,hc:6,f:13},
    'cannoli':{n:'Cannoli',c:390,p:8,hc:47,f:19},
    'caprese_salad':{n:'Ensalada Caprese',c:135,p:8,hc:4,f:10},
    'carrot_cake':{n:'Pastel de zanahoria',c:371,p:5,hc:53,f:17},
    'ceviche':{n:'Ceviche',c:95,p:18,hc:5,f:1},
    'cheese_plate':{n:'Tabla de quesos',c:380,p:22,hc:3,f:31},
    'cheesecake':{n:'Tarta de queso',c:321,p:6,hc:26,f:23},
    'chicken_curry':{n:'Curry de pollo',c:165,p:17,hc:7,f:8},
    'chicken_quesadilla':{n:'Quesadilla de pollo',c:255,p:18,hc:22,f:10},
    'chicken_wings':{n:'Alitas de pollo',c:260,p:27,hc:0,f:17},
    'chocolate_cake':{n:'Tarta de chocolate',c:371,p:5,hc:54,f:16},
    'chocolate_mousse':{n:'Mousse de chocolate',c:248,p:5,hc:23,f:15},
    'churros':{n:'Churros',c:358,p:6,hc:44,f:18},
    'clam_chowder':{n:'Sopa de almejas',c:147,p:10,hc:17,f:5},
    'club_sandwich':{n:'Club s\u00e1ndwich',c:210,p:16,hc:18,f:8},
    'crab_cakes':{n:'Pastelillos de cangrejo',c:185,p:13,hc:13,f:9},
    'creme_brulee':{n:'Cr\u00e8me br\u00fcl\u00e9e',c:268,p:6,hc:25,f:16},
    'croque_madame':{n:'Croque madame',c:260,p:16,hc:22,f:12},
    'cup_cakes':{n:'Cupcakes',c:370,p:5,hc:54,f:15},
    'deviled_eggs':{n:'Huevos rellenos',c:185,p:13,hc:2,f:14},
    'donuts':{n:'Donuts',c:390,p:5,hc:53,f:18},
    'dumplings':{n:'Dumplings',c:175,p:9,hc:22,f:6},
    'edamame':{n:'Edamame',c:122,p:11,hc:9,f:5},
    'eggs_benedict':{n:'Huevos benedictinos',c:247,p:14,hc:16,f:15},
    'escargots':{n:'Caracoles',c:90,p:16,hc:2,f:1},
    'falafel':{n:'Falafel',c:333,p:13,hc:32,f:18},
    'filet_mignon':{n:'Filete de ternera',c:224,p:28,hc:0,f:12},
    'fish_and_chips':{n:'Fish and chips',c:290,p:17,hc:28,f:12},
    'foie_gras':{n:'Foie gras',c:462,p:11,hc:5,f:44},
    'french_fries':{n:'Patatas fritas',c:274,p:3,hc:36,f:14},
    'french_onion_soup':{n:'Sopa de cebolla',c:107,p:5,hc:16,f:3},
    'french_toast':{n:'Torrijas',c:210,p:9,hc:26,f:8},
    'fried_calamari':{n:'Calamares fritos',c:175,p:15,hc:10,f:8},
    'fried_rice':{n:'Arroz frito',c:163,p:5,hc:27,f:4},
    'frozen_yogurt':{n:'Yogur helado',c:127,p:4,hc:26,f:1},
    'garlic_bread':{n:'Pan de ajo',c:296,p:8,hc:38,f:13},
    'gnocchi':{n:'Gnocchi',c:130,p:3,hc:28,f:1},
    'greek_salad':{n:'Ensalada griega',c:95,p:4,hc:7,f:7},
    'grilled_cheese_sandwich':{n:'S\u00e1ndwich de queso',c:285,p:12,hc:26,f:14},
    'grilled_salmon':{n:'Salm\u00f3n a la plancha',c:208,p:28,hc:0,f:10},
    'guacamole':{n:'Guacamole',c:155,p:2,hc:9,f:14},
    'gyoza':{n:'Gyoza',c:165,p:8,hc:20,f:6},
    'hamburger':{n:'Hamburguesa',c:295,p:17,hc:24,f:14},
    'hot_and_sour_soup':{n:'Sopa agripicante',c:65,p:5,hc:8,f:2},
    'hot_dog':{n:'Hot dog',c:240,p:11,hc:20,f:13},
    'huevos_rancheros':{n:'Huevos rancheros',c:220,p:13,hc:18,f:11},
    'hummus':{n:'H\u00fammus',c:177,p:8,hc:14,f:10},
    'ice_cream':{n:'Helado',c:207,p:4,hc:24,f:11},
    'lasagna':{n:'Lasa\u00f1a',c:181,p:11,hc:18,f:7},
    'lobster_bisque':{n:'Bisque de langosta',c:195,p:12,hc:14,f:11},
    'lobster_roll_sandwich':{n:'S\u00e1ndwich de langosta',c:310,p:20,hc:32,f:11},
    'macaroni_and_cheese':{n:'Macarrones con queso',c:172,p:8,hc:21,f:6},
    'macarons':{n:'Macarons',c:413,p:7,hc:72,f:12},
    'miso_soup':{n:'Sopa miso',c:40,p:3,hc:5,f:1},
    'mussels':{n:'Mejillones',c:172,p:24,hc:7,f:5},
    'nachos':{n:'Nachos',c:300,p:10,hc:34,f:15},
    'omelette':{n:'Tortilla francesa',c:155,p:11,hc:1,f:12},
    'onion_rings':{n:'Aros de cebolla',c:280,p:4,hc:34,f:15},
    'oysters':{n:'Ostras',c:68,p:7,hc:4,f:2},
    'pad_thai':{n:'Pad Thai',c:193,p:12,hc:26,f:5},
    'paella':{n:'Paella',c:185,p:16,hc:20,f:5},
    'pancakes':{n:'Tortitas',c:227,p:7,hc:38,f:7},
    'panna_cotta':{n:'Panna cotta',c:170,p:4,hc:14,f:11},
    'peking_duck':{n:'Pato pek\u00edn',c:337,p:22,hc:6,f:26},
    'pho':{n:'Pho',c:82,p:8,hc:9,f:2},
    'pizza':{n:'Pizza',c:266,p:11,hc:33,f:10},
    'pork_chop':{n:'Chuleta de cerdo',c:222,p:29,hc:0,f:11},
    'poutine':{n:'Poutine',c:316,p:11,hc:35,f:16},
    'prime_rib':{n:'Costilla de ternera',c:355,p:27,hc:0,f:27},
    'pulled_pork_sandwich':{n:'S\u00e1ndwich de cerdo',c:285,p:22,hc:22,f:10},
    'ramen':{n:'Ramen',c:188,p:8,hc:26,f:6},
    'ravioli':{n:'Ravioli',c:180,p:10,hc:23,f:6},
    'red_velvet_cake':{n:'Tarta red velvet',c:355,p:5,hc:52,f:14},
    'risotto':{n:'Risotto',c:166,p:5,hc:29,f:4},
    'samosa':{n:'Samosa',c:308,p:8,hc:35,f:16},
    'sashimi':{n:'Sashimi',c:135,p:23,hc:0,f:4},
    'scallops':{n:'Vieiras',c:111,p:21,hc:5,f:1},
    'seaweed_salad':{n:'Ensalada de algas',c:70,p:2,hc:11,f:2},
    'shrimp_and_grits':{n:'Gambas con s\u00e9mola',c:295,p:22,hc:25,f:11},
    'spaghetti_bolognese':{n:'Espaguetis a la bolo\u00f1esa',c:195,p:12,hc:22,f:7},
    'spaghetti_carbonara':{n:'Espaguetis carbonara',c:288,p:14,hc:29,f:13},
    'spring_rolls':{n:'Rollitos de primavera',c:195,p:6,hc:22,f:9},
    'steak':{n:'Filete de ternera',c:256,p:26,hc:0,f:17},
    'strawberry_shortcake':{n:'Tarta de fresas',c:234,p:4,hc:35,f:9},
    'sushi':{n:'Sushi',c:143,p:7,hc:26,f:2},
    'tacos':{n:'Tacos',c:210,p:13,hc:20,f:8},
    'takoyaki':{n:'Takoyaki',c:201,p:10,hc:24,f:8},
    'tiramisu':{n:'Tir\u00e0mis\u00fa',c:299,p:7,hc:28,f:17},
    'tuna_tartare':{n:'Tartar de at\u00fan',c:122,p:21,hc:3,f:3},
    'waffles':{n:'Gofres',c:291,p:8,hc:37,f:13}
  };

  function normLabel(s){return (s||'').toLowerCase().replace(/\s+/g,'_');}

  function resizeToBlob(img,maxW,cb){
    var c=document.createElement('canvas');
    var w=img.naturalWidth,h=img.naturalHeight;
    var scale=Math.min(1,maxW/Math.max(w,h,1));
    c.width=Math.round(w*scale);c.height=Math.round(h*scale);
    c.getContext('2d').drawImage(img,0,0,c.width,c.height);
    c.toBlob(cb,'image/jpeg',0.82);
  }

  var xPipeline=null,xPromise=null,xFailed=false;
  function getXPipeline(){
    if(xFailed)return Promise.reject(new Error('unavailable'));
    if(xPipeline)return Promise.resolve(xPipeline);
    if(xPromise)return xPromise;
    xPromise=import('https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2')
      .then(function(mod){
        setStatus('Descargando modelo IA\u2026 (primera vez)');
        return mod.pipeline('image-classification','Xenova/nateraw-food',{quantized:true});
      })
      .then(function(p){xPipeline=p;xPromise=null;return p;})
      .catch(function(e){xFailed=true;xPromise=null;throw e;});
    return xPromise;
  }
  function analyzeXenova(imgEl){
    setStatus('Cargando modelo IA\u2026');
    return getXPipeline().then(function(classifier){
      setStatus('Reconociendo alimento\u2026');
      var c=document.createElement('canvas');
      var s=Math.min(1,512/Math.max(imgEl.naturalWidth,imgEl.naturalHeight,1));
      c.width=Math.round(imgEl.naturalWidth*s);c.height=Math.round(imgEl.naturalHeight*s);
      c.getContext('2d').drawImage(imgEl,0,0,c.width,c.height);
      return classifier(c.toDataURL('image/jpeg',0.92),{topk:10});
    }).then(function(results){
      return results.map(function(r){return{label:r.label,score:r.score};});
    });
  }

  function clearPredOpts(){var e=document.getElementById('pred-opts');if(e)e.remove();}

  function applyFood101(info){
    currentAlimento={calorias:info.c,proteina:info.p,carbohidratos:info.hc,grasa:info.f,nombre:info.n};
    fotoFoodName.textContent=info.n;
    renderResult(currentAlimento,parseInt(fotoSlider.value));
    fotoResult.style.display='block';
    setStatus('');
  }

  function showPredictions(preds){
    clearPredOpts();
    var top=preds.filter(function(p){return F101[normLabel(p.label)];}).slice(0,3);
    if(!top.length){setStatus('No se pudo identificar el plato. Prueba otra foto.');fotoGo.disabled=false;return;}
    var wrap=document.createElement('div');
    wrap.id='pred-opts';
    wrap.innerHTML='<div class="pred-hint">Toca para confirmar el alimento detectado:</div>';
    top.forEach(function(p,i){
      var key=normLabel(p.label);
      var info=F101[key];
      var pct=Math.min(100,Math.round(p.score*100));
      var el=document.createElement('div');
      el.className='pred-opt'+(i===0?' selected':'');
      el.innerHTML='<div class="pred-opt-info"><div class="pred-opt-name">'+info.n+'</div><div class="pred-opt-bar" style="width:'+pct+'%"></div></div><div class="pred-opt-pct">'+pct+'%</div>';
      el.addEventListener('click',function(){
        document.querySelectorAll('.pred-opt').forEach(function(x){x.classList.remove('selected');});
        el.classList.add('selected');applyFood101(info);
      });
      wrap.appendChild(el);
    });
    fotoResult.parentNode.insertBefore(wrap,fotoResult);
    applyFood101(F101[normLabel(top[0].label)]);
    fotoGo.disabled=false;
  }

  function doMobileNetFallback(){
    setStatus('Usando modelo local\u2026');
    function run(){
      mnModel.classify(fotoPreview,5).then(function(preds){
        var match=findFoodKey(preds);
        if(!match){setStatus('No se pudo identificar el alimento.');fotoGo.disabled=false;return;}
        var candidates=FOOD_MAP[match.key];
        var pct=Math.round(match.prob*100);
        function tryNext(i){
          if(i>=candidates.length){setStatus('Detectado ('+match.key+') pero sin datos. Prueba otra foto.');fotoGo.disabled=false;return;}
          fetch('/api/calories?food='+encodeURIComponent(candidates[i])).then(function(r){return r.json();}).then(function(d){
            if(d.found){currentAlimento=d;fotoFoodName.textContent=d.nombre+' \u2014 '+pct+'%';renderResult(d,parseInt(fotoSlider.value));fotoResult.style.display='block';setStatus('');}
            else tryNext(i+1);
          }).catch(function(){tryNext(i+1);});
        }
        tryNext(0);fotoGo.disabled=false;
      }).catch(function(){setStatus('Error de an\u00e1lisis local.');fotoGo.disabled=false;});
    }
    if(mnModel){run();return;}
    if(typeof mobilenet==='undefined'){setStatus('Modelo no disponible. Comprueba tu conexi\u00f3n.');fotoGo.disabled=false;return;}
    mobilenet.load().then(function(m){mnModel=m;run();}).catch(function(){setStatus('No se pudo cargar el modelo.');fotoGo.disabled=false;});
  }

  fotoGo.addEventListener('click',function(){
    if(!fotoPreview.src||fotoPreview.src==='about:blank')return;
    fotoResult.style.display='none';clearPredOpts();
    fotoGo.disabled=true;
    analyzeXenova(fotoPreview).then(function(preds){
      if(!Array.isArray(preds)||!preds.length)throw new Error('empty');
      showPredictions(preds);
    }).catch(function(){
      doMobileNetFallback();
    });
  });
})();

/* ═══════════════════════════════════════════
   PARTE 1: DIARIO ALIMENTARIO
═══════════════════════════════════════════ */
(function(){
var allFoods=[];var diaryDate=new Date();var diaryDb={};var selectedFood=null;
var GOAL_DEFAULT=2000;

function dateKey(d){return d.toISOString().slice(0,10);}
function fmtDate(d){var days=['Dom','Lun','Mar','Mié','Jue','Vie','Sáb'];var months=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];return days[d.getDay()]+' '+d.getDate()+' '+months[d.getMonth()];}
function loadDiaryDb(){try{var s=localStorage.getItem('ng-diary');return s?JSON.parse(s):{}}catch(e){return {};}}
function saveDiaryDb(){try{localStorage.setItem('ng-diary',JSON.stringify(diaryDb));}catch(e){}}
function getDayEntries(d){return diaryDb[dateKey(d)]||[];}
function setDayEntries(d,arr){diaryDb[dateKey(d)]=arr;saveDiaryDb();}
function getProfile(){try{var s=localStorage.getItem('ng-profile');return s?JSON.parse(s):null;}catch(e){return null;}}
function getTdee(){var p=getProfile();if(!p||!p.peso||!p.altura||!p.edad)return GOAL_DEFAULT;var bmr=p.sexo==='h'?(10*p.peso+6.25*p.altura-5*p.edad+5):(10*p.peso+6.25*p.altura-5*p.edad-161);var act=parseFloat(p.act)||1.55;var tdee=Math.round(bmr*act);var obj=p.obj||'mant';if(obj==='cut')tdee=Math.max(tdee-500,1200);if(obj==='bulk')tdee+=300;return tdee;}

diaryDb=loadDiaryDb();
fetch('/api/foods').then(function(r){return r.json();}).then(function(d){allFoods=d.alimentos||[];}).catch(function(){});

function renderDiary(){
  var entries=getDayEntries(diaryDate);
  var goal=getTdee();
  var totalCal=0,totalProt=0,totalCarb=0,totalFat=0;
  entries.forEach(function(e){totalCal+=e.cal||0;totalProt+=e.prot||0;totalCarb+=e.carb||0;totalFat+=e.fat||0;});
  var pct=Math.min(Math.round(totalCal/goal*100),200);
  document.getElementById('diary-date-lbl').textContent=fmtDate(diaryDate);
  document.getElementById('diary-eaten').textContent=Math.round(totalCal);
  document.getElementById('diary-goal').textContent=goal;
  var bar=document.getElementById('diary-bar');
  bar.style.width=pct+'%';
  bar.className='cal-bar-fill'+(totalCal>goal?' over':'');
  document.getElementById('d-prot').textContent=Math.round(totalProt)+'g';
  document.getElementById('d-carb').textContent=Math.round(totalCarb)+'g';
  document.getElementById('d-fat').textContent=Math.round(totalFat)+'g';
  var list=document.getElementById('diary-entries-list');
  if(!entries.length){list.innerHTML='<div class="diary-empty">Aún no hay alimentos registrados</div>';return;}
  list.innerHTML=entries.map(function(e,i){
    return '<div class="diary-entry"><div class="diary-entry-info"><div class="diary-entry-name">'+e.nombre+'</div><div class="diary-entry-sub">'+e.gramos+'g</div></div><div class="diary-entry-cal">'+Math.round(e.cal)+' kcal</div><button class="diary-entry-del" onclick="diaryDel('+i+')">&#xD7;</button></div>';
  }).join('');
}
window.diaryDel=function(i){var arr=getDayEntries(diaryDate);arr.splice(i,1);setDayEntries(diaryDate,arr);renderDiary();};

function normalize(s){return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
var dSearch=document.getElementById('diary-search');
var dResults=document.getElementById('diary-results');
var dSelectedLbl=document.getElementById('diary-selected-lbl');
var dAddBtn=document.getElementById('diary-add-btn');

dSearch.addEventListener('input',function(){
  var q=normalize(dSearch.value.trim());
  selectedFood=null;dSelectedLbl.style.display='none';
  if(!q||q.length<2){dResults.style.display='none';return;}
  var hits=allFoods.filter(function(f){return normalize(f.nombre||'').indexOf(q)>=0;}).slice(0,10);
  if(!hits.length){dResults.style.display='none';return;}
  dResults.innerHTML=hits.map(function(f,i){
    var cal=f.calorias_por_100g||f.calorias||0;
    return '<div class="diary-res-item" onclick="diarySelectFood('+i+')"><span class="diary-res-name">'+f.nombre+'</span><span class="diary-res-cal">'+cal+' kcal/100g</span></div>';
  }).join('');
  dResults.style.display='block';
  window._diaryHits=hits;
});
window.diarySelectFood=function(i){
  selectedFood=window._diaryHits[i];
  dSearch.value=selectedFood.nombre;
  dResults.style.display='none';
  dSelectedLbl.textContent=selectedFood.nombre+' seleccionado';
  dSelectedLbl.style.display='block';
};
document.addEventListener('click',function(e){if(!e.target.closest('.diary-search-wrap'))dResults.style.display='none';});

dAddBtn.addEventListener('click',function(){
  if(!selectedFood){dSearch.focus();return;}
  var gramos=parseFloat(document.getElementById('diary-grams').value)||100;
  var factor=gramos/100;
  var cal=(selectedFood.calorias_por_100g||selectedFood.calorias||0)*factor;
  var macros=selectedFood.macros||{};
  var entry={nombre:selectedFood.nombre,gramos:gramos,cal:cal,prot:(macros.proteinas||0)*factor,carb:(macros.carbohidratos||0)*factor,fat:(macros.grasas||0)*factor};
  var arr=getDayEntries(diaryDate);arr.push(entry);setDayEntries(diaryDate,arr);
  dSearch.value='';selectedFood=null;dSelectedLbl.style.display='none';
  document.getElementById('diary-grams').value=100;
  renderDiary();
});
document.getElementById('diary-prev').addEventListener('click',function(){diaryDate.setDate(diaryDate.getDate()-1);renderDiary();});
document.getElementById('diary-next').addEventListener('click',function(){diaryDate.setDate(diaryDate.getDate()+1);renderDiary();});
document.getElementById('diary-today').addEventListener('click',function(){diaryDate=new Date();renderDiary();});
document.getElementById('diary-clear-btn').addEventListener('click',function(){if(confirm('¿Limpiar el registro de hoy?')){setDayEntries(diaryDate,[]);renderDiary();}});
renderDiary();
})();

/* ═══════════════════════════════════════════
   PARTE 2: PERFIL DE USUARIO
═══════════════════════════════════════════ */
(function(){
function loadProfile(){try{var s=localStorage.getItem('ng-profile');return s?JSON.parse(s):{};}catch(e){return{};}}
function saveProfile(p){try{localStorage.setItem('ng-profile',JSON.stringify(p));}catch(e){}}

function openProfModal(){
  var p=loadProfile();
  document.getElementById('p-nombre').value=p.nombre||'';
  document.getElementById('p-sexo').value=p.sexo||'h';
  document.getElementById('p-edad').value=p.edad||'';
  document.getElementById('p-peso').value=p.peso||'';
  document.getElementById('p-altura').value=p.altura||'';
  document.getElementById('p-act').value=p.act||'1.55';
  document.getElementById('p-obj').value=p.obj||'mant';
  document.getElementById('prof-modal').style.display='block';
}
window.closeProfModal=function(){document.getElementById('prof-modal').style.display='none';};

document.getElementById('prof-btn').addEventListener('click',openProfModal);
document.getElementById('prof-save-btn').addEventListener('click',function(){
  var p={
    nombre:document.getElementById('p-nombre').value.trim(),
    sexo:document.getElementById('p-sexo').value,
    edad:parseFloat(document.getElementById('p-edad').value)||0,
    peso:parseFloat(document.getElementById('p-peso').value)||0,
    altura:parseFloat(document.getElementById('p-altura').value)||0,
    act:document.getElementById('p-act').value,
    obj:document.getElementById('p-obj').value
  };
  saveProfile(p);
  /* Auto-rellenar calculadora */
  if(p.sexo){var sSeg=document.getElementById('sexo-seg');if(sSeg){sSeg.querySelectorAll('.seg-btn').forEach(function(b){b.classList.toggle('active',b.dataset.val===p.sexo);});}}
  if(p.edad)document.getElementById('c-edad').value=p.edad;
  if(p.peso)document.getElementById('c-peso').value=p.peso;
  if(p.altura)document.getElementById('c-altura').value=p.altura;
  if(p.act)document.getElementById('c-act').value=p.act;
  if(p.obj){var gSeg=document.getElementById('goal-seg');if(gSeg){gSeg.querySelectorAll('.seg-btn').forEach(function(b){b.classList.toggle('active',b.dataset.val===p.obj);});}}
  /* Saludo personalizado */
  if(p.nombre){var sub=document.querySelector('.header p');if(sub)sub.textContent='Hola, '+p.nombre+'!';}
  closeProfModal();
  /* Refrescar diario con nuevo TDEE */
  if(typeof renderDiary==='function')renderDiary();
});

/* Aplicar perfil al cargar */
(function(){
  var p=loadProfile();
  if(p.nombre){var sub=document.querySelector('.header p');if(sub)sub.textContent='Hola, '+p.nombre+'!';}
})();
})();

/* ═══════════════════════════════════════════
   PARTE 3: BARCODE SCANNER
═══════════════════════════════════════════ */
(function(){
var scanStream=null;var scanInterval=null;var scanPendingFood=null;

function openScan(){
  document.getElementById('scan-overlay').style.display='block';
  document.getElementById('scan-result-card').style.display='none';
  document.getElementById('scan-manual-inp').value='';
  startCamera();
}
window.closeScan=function(){
  stopCamera();
  document.getElementById('scan-overlay').style.display='none';
  scanPendingFood=null;
};
function startCamera(){
  if(!navigator.mediaDevices)return;
  navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false}).then(function(stream){
    scanStream=stream;
    var v=document.getElementById('scan-video');
    v.srcObject=stream;
    v.play();
    startBarcodeDetection(v);
  }).catch(function(){alert('No se pudo acceder a la cámara. Usa el campo manual.');});
}
function stopCamera(){
  if(scanInterval){clearInterval(scanInterval);scanInterval=null;}
  if(scanStream){scanStream.getTracks().forEach(function(t){t.stop();});scanStream=null;}
}
function startBarcodeDetection(video){
  if(!('BarcodeDetector' in window))return;
  var detector=new BarcodeDetector({formats:['ean_13','ean_8','upc_a','upc_e','code_128','code_39']});
  scanInterval=setInterval(function(){
    if(video.readyState!==4)return;
    detector.detect(video).then(function(codes){
      if(codes.length>0){clearInterval(scanInterval);scanInterval=null;lookupBarcode(codes[0].rawValue);}
    }).catch(function(){});
  },600);
}
function lookupBarcode(code){
  document.getElementById('scan-result-card').style.display='none';
  fetch('https://world.openfoodfacts.org/api/v2/product/'+code+'.json?fields=product_name,brands,nutriments').then(function(r){return r.json();}).then(function(d){
    if(d.status!==1||!d.product){alert('Producto no encontrado. Prueba con otro código.');return;}
    var pr=d.product;var n=pr.nutriments||{};
    var food={
      nombre:pr.product_name||'Producto escaneado',
      marca:pr.brands||'',
      cal:Math.round(n['energy-kcal_100g']||n['energy_100g']/4.184||0),
      prot:Math.round((n.proteins_100g||0)*10)/10,
      carb:Math.round((n.carbohydrates_100g||0)*10)/10,
      fat:Math.round((n.fat_100g||0)*10)/10
    };
    scanPendingFood=food;
    document.getElementById('scan-res-name').textContent=food.nombre;
    document.getElementById('scan-res-brand').textContent=food.marca;
    document.getElementById('scan-r-cal').textContent=food.cal;
    document.getElementById('scan-r-prot').textContent=food.prot+'g';
    document.getElementById('scan-r-carb').textContent=food.carb+'g';
    document.getElementById('scan-r-fat').textContent=food.fat+'g';
    document.getElementById('scan-result-card').style.display='block';
  }).catch(function(){alert('Error al buscar el producto. Comprueba tu conexión.');});
}

document.getElementById('diary-scan-btn').addEventListener('click',openScan);
document.getElementById('scan-manual-btn').addEventListener('click',function(){
  var code=document.getElementById('scan-manual-inp').value.trim();
  if(code)lookupBarcode(code);
});
document.getElementById('scan-manual-inp').addEventListener('keydown',function(e){if(e.key==='Enter')document.getElementById('scan-manual-btn').click();});
document.getElementById('scan-add-diary-btn').addEventListener('click',function(){
  if(!scanPendingFood)return;
  var f=scanPendingFood;
  var entry={nombre:f.nombre,gramos:100,cal:f.cal,prot:f.prot,carb:f.carb,fat:f.fat};
  var key=new Date().toISOString().slice(0,10);
  var stored={};try{var s=localStorage.getItem('ng-diary');stored=s?JSON.parse(s):{};}catch(e){}
  if(!stored[key])stored[key]=[];
  stored[key].push(entry);
  try{localStorage.setItem('ng-diary',JSON.stringify(stored));}catch(e){}
  closeScan();
  /* Cambiar al tab Diario */
  document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('active',t.dataset.tab==='diario');});
  document.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('active',p.id==='panel-diario');});
  /* Refrescar diario */
  var diary=document.getElementById('panel-diario');
  if(diary){window.location.reload();}
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


@app.get("/api/calories")
async def get_calories(food: str):
    alimento = buscar_alimento(food)
    if alimento:
        return {"found": True, **alimento}
    return {"found": False}


@app.get("/api/foods")
async def get_foods():
    return {"alimentos": calories_db.get("alimentos", [])}


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
