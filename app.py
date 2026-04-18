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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f9fafb;--surface:#fff;--border:#e5e7eb;
  --text:#111827;--muted:#6b7280;--accent:#16a34a;
  --accent-light:#dcfce7;--user:#111827;--r:12px;
  --shadow:0 1px 3px rgba(0,0,0,.08);
  --shadow-md:0 4px 14px rgba(0,0,0,.1);
}
html.dark{
  --bg:#0f1117;--surface:#1a1d27;--border:#2d3040;
  --text:#e8eaf0;--muted:#8b90a0;--accent:#22c55e;
  --accent-light:#052e16;--user:#22c55e;
  --shadow:0 1px 3px rgba(0,0,0,.3);
  --shadow-md:0 4px 14px rgba(0,0,0,.4);
}
html,body{height:100%}
body{font-family:'Inter',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5;transition:background .25s,color .25s}
.app{max-width:680px;height:100vh;margin:0 auto;display:flex;flex-direction:column;background:var(--surface);border-left:1px solid var(--border);border-right:1px solid var(--border);transition:background .25s,border-color .25s}
.header{padding:13px 18px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:10px;flex-shrink:0}
.icon{width:28px;height:28px;background:var(--accent);border-radius:7px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.icon svg{width:15px;height:15px;fill:#fff}
.header h1{font-size:15px;font-weight:600}
.header p{font-size:11px;color:var(--muted);margin-top:1px}
.header-end{margin-left:auto}
#dm{width:30px;height:30px;background:none;border:1px solid var(--border);border-radius:7px;padding:0;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--muted);transition:border-color .15s,color .15s}
#dm:hover{border-color:var(--accent);color:var(--accent)}
#dm svg{width:15px;height:15px;fill:currentColor}
.tabs{display:flex;border-bottom:1px solid var(--border);flex-shrink:0;padding:0 18px}
.tab{padding:10px 16px;font-size:13px;font-weight:500;color:var(--muted);background:none;border:none;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;transition:color .15s,border-color .15s;font-family:inherit}
.tab:hover{color:var(--text)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.panel{display:none;flex:1;flex-direction:column;overflow:hidden}
.panel.active{display:flex}
.msgs{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:10px;scrollbar-width:thin;scrollbar-color:var(--border) transparent}
.msgs::-webkit-scrollbar{width:4px}
.msgs::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.m{display:flex;animation:fadeUp .2s ease both}
.m.u{justify-content:flex-end}
.b{max-width:78%;padding:10px 14px;border-radius:var(--r);line-height:1.65;font-size:14px;transition:background .25s,border-color .25s}
.m.bot .b{background:var(--surface);border:1px solid var(--border);box-shadow:var(--shadow)}
.m.u .b{background:var(--user);color:#fff;border-radius:var(--r) var(--r) 3px var(--r)}
.typing .b{color:var(--muted);font-style:italic}
.composer{padding:12px 14px;border-top:1px solid var(--border);display:flex;gap:8px;flex-shrink:0}
input[type=text]{flex:1;padding:9px 13px;border:1px solid var(--border);border-radius:9px;font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;transition:border-color .15s,background .25s,color .25s}
input[type=text]:focus{border-color:var(--accent)}
.send-btn{padding:9px 16px;background:var(--accent);color:#fff;border:none;border-radius:9px;font-size:13px;font-weight:500;cursor:pointer;font-family:inherit;transition:opacity .15s,background .25s;flex-shrink:0}
.send-btn:hover{opacity:.85}
.gallery-top{padding:14px 18px 0;flex-shrink:0}
.gallery-search{width:100%;padding:9px 13px;border:1px solid var(--border);border-radius:9px;font-size:14px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;transition:border-color .15s,background .25s,color .25s;display:block}
.gallery-search:focus{border-color:var(--accent)}
.filters{display:flex;gap:6px;padding:10px 18px;overflow-x:auto;flex-shrink:0;scrollbar-width:none}
.filters::-webkit-scrollbar{display:none}
.filter-btn{padding:5px 12px;border-radius:20px;font-size:12px;font-weight:500;border:1px solid var(--border);background:none;color:var(--muted);cursor:pointer;white-space:nowrap;transition:all .15s;font-family:inherit;flex-shrink:0}
.filter-btn:hover,.filter-btn.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.gallery-grid{flex:1;overflow-y:auto;padding:4px 18px 18px;display:grid;grid-template-columns:1fr 1fr;gap:12px;align-content:start;scrollbar-width:thin;scrollbar-color:var(--border) transparent}
.gallery-grid::-webkit-scrollbar{width:4px}
.gallery-grid::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.card{border:1px solid var(--border);border-radius:12px;overflow:hidden;cursor:pointer;transition:transform .15s,box-shadow .15s,border-color .15s;animation:fadeUp .22s ease both;background:var(--surface)}
.card:hover{transform:translateY(-2px);box-shadow:var(--shadow-md);border-color:var(--accent)}
.card-img{width:100%;height:130px;object-fit:cover;display:block}
.card-ph{width:100%;height:130px;display:none;align-items:center;justify-content:center;font-size:38px;background:linear-gradient(135deg,var(--accent-light),var(--border))}
.card-body{padding:10px 11px 11px}
.card-name{font-size:13px;font-weight:600;line-height:1.3;margin-bottom:4px}
.card-cal{font-size:11px;color:var(--accent);font-weight:600;margin-bottom:6px}
.card-tags{display:flex;gap:4px;flex-wrap:wrap}
.tag{font-size:10px;padding:2px 7px;border-radius:10px;background:var(--accent-light);color:var(--accent);font-weight:500}
.empty{grid-column:1/-1;text-align:center;padding:40px 20px;color:var(--muted);font-size:13px}
.modal-wrap{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:100;display:flex;align-items:flex-end;justify-content:center;animation:fadeIn .2s ease}
.modal{background:var(--surface);border-radius:20px 20px 0 0;max-width:680px;width:100%;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;animation:slideUp .25s ease}
.modal-img{width:100%;height:180px;object-fit:cover;flex-shrink:0;display:block}
.modal-ph{width:100%;height:180px;display:none;align-items:center;justify-content:center;font-size:56px;flex-shrink:0;background:linear-gradient(135deg,var(--accent-light),var(--border))}
.modal-body{padding:18px 20px 28px;overflow-y:auto;flex:1}
.modal-head{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px}
.modal-name{font-size:17px;font-weight:600;line-height:1.3}
.modal-kcal{font-size:13px;color:var(--accent);font-weight:600;margin-top:3px}
.x-btn{width:28px;height:28px;border-radius:50%;border:1px solid var(--border);background:none;cursor:pointer;color:var(--muted);font-size:18px;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:border-color .15s,color .15s;font-family:inherit}
.x-btn:hover{border-color:var(--accent);color:var(--accent)}
.modal-sec{margin-top:16px}
.modal-sec h3{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}
.modal-ing{font-size:13px;line-height:2}
.modal-step{display:flex;gap:10px;margin-bottom:9px;font-size:13px;line-height:1.6}
.sn{width:20px;height:20px;min-width:20px;border-radius:50%;background:var(--accent);color:#fff;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:2px}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes slideUp{from{transform:translateY(60px);opacity:0}to{transform:translateY(0);opacity:1}}
small{font-size:12px}
@media(max-width:680px){.app{border:none}}
@media(max-width:380px){.gallery-grid{grid-template-columns:1fr}}
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
      <input type="text" id="inp" placeholder="Escribe tu pregunta..." autocomplete="off">
      <button id="btn" class="send-btn">Enviar</button>
    </div>
  </div>
  <div id="panel-recetas" class="panel">
    <div class="gallery-top">
      <input type="text" class="gallery-search" id="gsearch" placeholder="Buscar recetas\u2026" autocomplete="off">
    </div>
    <div class="filters">
      <button class="filter-btn active" data-cat="all">Todas</button>
      <button class="filter-btn" data-cat="desayuno">Desayuno</button>
      <button class="filter-btn" data-cat="almuerzo">Almuerzo</button>
      <button class="filter-btn" data-cat="cena">Cena</button>
      <button class="filter-btn" data-cat="snack">Snack</button>
      <button class="filter-btn" data-cat="pollo">Pollo</button>
      <button class="filter-btn" data-cat="pescado">Pescado</button>
      <button class="filter-btn" data-cat="vegetariano">Vegetariano</button>
    </div>
    <div class="gallery-grid" id="gg">
      <div class="empty">Cargando recetas\u2026</div>
    </div>
  </div>
</div>
<div id="modal" style="display:none"></div>
<script>
const dmBtn=document.getElementById('dm'),dmIcon=document.getElementById('dm-icon');
const SUN='<path d="M12 4.5a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0112 4.5zm0 13.5a.75.75 0 01.75.75v.75a.75.75 0 01-1.5 0v-.75A.75.75 0 0112 18zm7.5-6.75a.75.75 0 010 1.5h-.75a.75.75 0 010-1.5h.75zm-15 0a.75.75 0 010 1.5H3.75a.75.75 0 010-1.5H4.5zm12.86-5.61a.75.75 0 010 1.06l-.53.53a.75.75 0 01-1.06-1.06l.53-.53a.75.75 0 011.06 0zm-10.6 10.6a.75.75 0 010 1.06l-.53.53a.75.75 0 01-1.06-1.06l.53-.53a.75.75 0 011.06 0zm10.6 0a.75.75 0 011.06 1.06l-.53.53a.75.75 0 01-1.06-1.06l.53-.53a.75.75 0 010-1.06zM5.86 6.14a.75.75 0 011.06 0l.53.53A.75.75 0 016.39 7.73l-.53-.53a.75.75 0 010-1.06zM12 8.25a3.75 3.75 0 100 7.5 3.75 3.75 0 000-7.5z"/>';
const MOON='<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>';
function setDark(on){document.documentElement.classList.toggle('dark',on);dmIcon.innerHTML=on?SUN:MOON;localStorage.setItem('nutrigpt-dark',on?'1':'0');}
const saved=localStorage.getItem('nutrigpt-dark'),prefersDark=window.matchMedia('(prefers-color-scheme: dark)').matches;
setDark(saved!==null?saved==='1':prefersDark);
dmBtn.addEventListener('click',()=>setDark(!document.documentElement.classList.contains('dark')));

document.querySelectorAll('.tab').forEach(tab=>{
  tab.addEventListener('click',()=>{
    const id=tab.dataset.tab;
    document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t===tab));
    document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.id==='panel-'+id));
    if(id==='recetas'&&!galleryLoaded)loadGallery();
  });
});

const msgs=document.getElementById('msgs'),inp=document.getElementById('inp'),btn=document.getElementById('btn');
let ctx={last_recipe_ids:[],last_selected_recipe_id:null};
function addMsg(html,isUser,cls){
  const m=document.createElement('div');
  m.className='m '+(isUser?'u':'bot')+(cls?' '+cls:'');
  const b=document.createElement('div');b.className='b';b.innerHTML=html;
  m.appendChild(b);msgs.appendChild(m);msgs.scrollTop=msgs.scrollHeight;return m;
}
async function send(){
  const txt=inp.value.trim();if(!txt)return;
  addMsg(txt,true);inp.value='';
  const t=addMsg('Pensando\u2026',false,'typing');
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mensaje:txt,contexto:ctx})});
    const d=await r.json();t.remove();if(d.contexto)ctx=d.contexto;addMsg(d.respuesta);
  }catch(e){t.remove();addMsg('Error al procesar tu mensaje. Intenta de nuevo.');}
}
inp.addEventListener('keypress',e=>{if(e.key==='Enter')send()});
btn.addEventListener('click',send);

const PHOTOS={
  salmon:'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400&h=220&fit=crop&auto=format',
  avena:'https://images.unsplash.com/photo-1517673132405-a56a62b18caf?w=400&h=220&fit=crop&auto=format',
  batido:'https://images.unsplash.com/photo-1553530666-ba11a7da3888?w=400&h=220&fit=crop&auto=format',
  tostada:'https://images.unsplash.com/photo-1484723091739-30990d4d5b21?w=400&h=220&fit=crop&auto=format',
  ensalada:'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=220&fit=crop&auto=format',
  pasta:'https://images.unsplash.com/photo-1551183053-bf91798d454e?w=400&h=220&fit=crop&auto=format',
  sopa:'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=400&h=220&fit=crop&auto=format',
  pollo:'https://images.unsplash.com/photo-1598103442097-8b74394b95c1?w=400&h=220&fit=crop&auto=format',
  pescado:'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=220&fit=crop&auto=format',
  huevo:'https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=400&h=220&fit=crop&auto=format',
  carne:'https://images.unsplash.com/photo-1544025162-d76694265947?w=400&h=220&fit=crop&auto=format',
  arroz:'https://images.unsplash.com/photo-1516684732162-798a0062be99?w=400&h=220&fit=crop&auto=format',
  verdura:'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=220&fit=crop&auto=format',
  fruta:'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=400&h=220&fit=crop&auto=format',
  default:'https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=400&h=220&fit=crop&auto=format'
};
const EMOJIS={salmon:'🐟',avena:'🌾',batido:'🥤',tostada:'🍞',ensalada:'🥗',pasta:'🍝',sopa:'🍜',pollo:'🍗',pescado:'🐠',huevo:'🍳',carne:'🥩',arroz:'🍚',verdura:'🥦',fruta:'🍎',default:'🍽️'};

function photoKey(r){
  const t=((r.nombre||'')+' '+(r.ingredientes||[]).join(' ')).toLowerCase();
  return ['salmon','avena','batido','tostada','ensalada','pasta','sopa','pollo','pescado','huevo','carne','arroz','verdura','fruta'].find(k=>t.includes(k))||'default';
}
function getcat(r){
  const t=((r.nombre||'')+' '+(r.categoria||'')+' '+(r.ingredientes||[]).join(' ')).toLowerCase();
  if(/desayuno|avena|tostada|yogur|granola|muesli/.test(t))return 'desayuno';
  if(/snack|merienda|barrita|batido|smoothie/.test(t))return 'snack';
  if(/sopa|crema de|pur\u00e9|caldo/.test(t))return 'cena';
  if(/pollo/.test(t))return 'pollo';
  if(/salm\u00f3n|salmon|at\u00fan|atun|merluza|dorada|bacalao|pescado/.test(t))return 'pescado';
  if(!/pollo|carne|jam\u00f3n|jamon|bacon|cerdo|ternera|pavo|res|buey|cordero/.test(t))return 'vegetariano';
  return 'almuerzo';
}

let allRecipes=[],recipesMap={},galleryLoaded=false,activeFilter='all',searchTerm='';

async function loadGallery(){
  galleryLoaded=true;
  try{
    const r=await fetch('/api/recipes');
    const d=await r.json();
    allRecipes=(d.recetas||[]).slice(0,100);
    allRecipes.forEach(r=>{ recipesMap[String(r.id)]=r; });
    renderGallery();
  }catch(e){
    document.getElementById('gg').innerHTML='<div class="empty">Error cargando recetas.</div>';
  }
}

function renderGallery(){
  const gg=document.getElementById('gg');
  const filtered=allRecipes.filter(r=>{
    const cat=getcat(r);
    const okCat=activeFilter==='all'||cat===activeFilter;
    const txt=((r.nombre||'')+' '+(r.ingredientes||[]).join(' ')).toLowerCase();
    const okSrch=!searchTerm||txt.includes(searchTerm);
    return okCat&&okSrch;
  });
  if(!filtered.length){gg.innerHTML='<div class="empty">Sin resultados.</div>';return;}
  gg.innerHTML=filtered.slice(0,40).map(r=>{
    const k=photoKey(r);
    const tags=(r.ingredientes||[]).slice(0,2).map(i=>'<span class="tag">'+i.split(' ')[0]+'</span>').join('');
    const id=String(r.id);
    return '<div class="card" onclick="openModal(\''+id+'\')">'+
      '<img class="card-img" src="'+PHOTOS[k]+'" alt="'+r.nombre+'" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'+
      '<div class="card-ph">'+EMOJIS[k]+'</div>'+
      '<div class="card-body">'+
        '<div class="card-name">'+r.nombre+'</div>'+
        '<div class="card-cal">'+r.calorias_aprox+' kcal</div>'+
        '<div class="card-tags">'+tags+'</div>'+
      '</div></div>';
  }).join('');
}

document.querySelectorAll('.filter-btn').forEach(b=>{
  b.addEventListener('click',()=>{
    document.querySelectorAll('.filter-btn').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');activeFilter=b.dataset.cat;renderGallery();
  });
});
document.getElementById('gsearch').addEventListener('input',e=>{
  searchTerm=e.target.value.toLowerCase().trim();renderGallery();
});

function openModal(id){
  const r=recipesMap[id];if(!r)return;
  const k=photoKey(r);
  const ings=(r.ingredientes||[]).map(i=>'\u2014 '+i).join('<br>');
  const steps=(r.instrucciones||[]).map((s,i)=>
    '<div class="modal-step"><div class="sn">'+(i+1)+'</div><div>'+s+'</div></div>'
  ).join('');
  const el=document.getElementById('modal');
  el.innerHTML=
    '<div class="modal-wrap" onclick="if(event.target===this)closeModal()">'+
      '<div class="modal">'+
        '<img class="modal-img" src="'+PHOTOS[k]+'" alt="'+r.nombre+'" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'+
        '<div class="modal-ph">'+EMOJIS[k]+'</div>'+
        '<div class="modal-body">'+
          '<div class="modal-head">'+
            '<div>'+
              '<div class="modal-name">'+r.nombre+'</div>'+
              '<div class="modal-kcal">'+r.calorias_aprox+' kcal aprox.</div>'+
            '</div>'+
            '<button class="x-btn" onclick="closeModal()">\u00d7</button>'+
          '</div>'+
          '<div class="modal-sec"><h3>Ingredientes</h3><div class="modal-ing">'+ings+'</div></div>'+
          '<div class="modal-sec"><h3>Preparaci\u00f3n</h3>'+steps+'</div>'+
        '</div>'+
      '</div>'+
    '</div>';
  el.style.display='block';
  document.body.style.overflow='hidden';
}
function closeModal(){
  document.getElementById('modal').style.display='none';
  document.body.style.overflow='';
}
</script>
</body>
</html>"""


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


def buscar_recetas(terminos):
    if isinstance(terminos, str):
        terminos = tokens_relevantes(terminos)
    resultados = []
    for receta in recipes_db.get("recetas", []):
        contenido = normalizar_texto(" ".join([receta["nombre"]] + receta["ingredientes"]))
        score = 0
        for termino in terminos:
            termino_normalizado = normalizar_texto(termino)
            if not termino_normalizado:
                continue
            if termino_normalizado in contenido:
                score += 3
            else:
                for token in termino_normalizado.split():
                    if token in contenido:
                        score += 1
        if score > 0:
            resultados.append((score, receta))
    resultados.sort(key=lambda item: (-item[0], item[1].get("calorias_aprox", 0)))
    return [receta for _, receta in resultados[:10]]


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
        recetas = buscar_recetas(terminos)

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

        termino_busqueda = ", ".join(terminos) if terminos else "tu consulta"
        return {
            "respuesta": (
                f"No encontr\u00e9 recetas con <strong>{termino_busqueda}</strong>.<br><br>"
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


@app.get("/", response_class=HTMLResponse)
async def get_home():
    return HTML_PAGE


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


if __name__ == "__main__":
    import uvicorn
    raw_port = os.environ.get("PORT", "8000")
    clean_port = "".join(filter(str.isdigit, str(raw_port)))
    port = int(clean_port) if clean_port else 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
