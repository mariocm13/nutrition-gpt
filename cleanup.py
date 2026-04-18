"""One-time script: remove Recetas section from app.py and expand FOOD_MAP."""
import ast

with open('app.py', encoding='utf-8') as f:
    src = f.read()

# 1. Remove `import requests`
src = src.replace('import requests\n', '')

# 2. Remove DRIVE_FILE_ID and RECIPES_DATA_PATH constants
src = src.replace('DRIVE_FILE_ID = "1pMn-MyxfEaag0rzZbwYSzSciYnRDOodw"\n', '')
src = src.replace('RECIPES_DATA_PATH = "data/recipes_large.json"\n', '')

# 3. Update subtitle
src = src.replace(
    'Asistente de nutrici\\u00f3n y recetas',
    'Asistente de nutrici\\u00f3n'
)

# 4. Remove gallery/modal CSS block
CSS_BLOCK = (
    '.gallery-top{padding:6px 22px 0;flex-shrink:0}\n'
    '#gsearch{width:100%;padding:13px 16px;border:none;border-radius:14px;font-size:16px;font-family:inherit;background:var(--bg);color:var(--text);outline:none;box-shadow:var(--sh-in);transition:box-shadow .2s,background .3s,color .3s;display:block;user-select:auto;-webkit-user-select:auto}\n'
    '#gsearch:focus{box-shadow:var(--sh-in),0 0 0 2px var(--accent)}\n'
    '#gsearch::placeholder{color:var(--muted)}\n'
    '.filters{display:flex;gap:8px;padding:14px 22px;overflow-x:auto;flex-shrink:0;scrollbar-width:none}\n'
    '.filters::-webkit-scrollbar{display:none}\n'
    '.filter-btn{padding:8px 15px;border-radius:22px;font-size:12px;font-weight:600;border:none;background:var(--bg);color:var(--muted);cursor:pointer;white-space:nowrap;font-family:inherit;flex-shrink:0;box-shadow:var(--sh-sm);transition:box-shadow .2s,color .2s,background .3s}\n'
    '.filter-btn.active{box-shadow:var(--sh-press);color:var(--accent)}\n'
    '.gallery-grid{flex:1;min-height:0;overflow-y:auto;padding:2px 22px 22px;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:18px;align-content:start;scrollbar-width:thin;scrollbar-color:var(--nm-d) transparent;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}\n'
    '.gallery-grid::-webkit-scrollbar{width:4px}\n'
    '.gallery-grid::-webkit-scrollbar-thumb{background:var(--nm-d);border-radius:4px}\n'
    '.card{border-radius:20px;overflow:hidden;cursor:pointer;box-shadow:var(--sh);transition:box-shadow .2s,transform .2s,background .3s;animation:fadeUp .25s ease both;background:var(--bg)}\n'
    '.card:hover{transform:translateY(-3px);box-shadow:8px 8px 18px var(--nm-d),-8px -8px 18px var(--nm-l)}\n'
    '.card:active{transform:scale(.98);box-shadow:var(--sh-press)}\n'
    '.card-img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block}\n'
    '.card-ph{width:100%;aspect-ratio:4/3;display:none;align-items:center;justify-content:center;font-size:42px;background:linear-gradient(135deg,var(--accent-light),var(--bg))}\n'
    '.card-body{padding:11px 13px 13px}\n'
    '.card-name{font-size:13px;font-weight:700;line-height:1.35;margin-bottom:5px;color:var(--text)}\n'
    '.card-cal{font-size:11px;color:var(--accent);font-weight:700;margin-bottom:7px}\n'
    '.card-tags{display:flex;gap:5px;flex-wrap:wrap}\n'
    '.tag{font-size:10px;padding:3px 9px;border-radius:10px;background:var(--bg);box-shadow:var(--sh-press);color:var(--accent);font-weight:600}\n'
    '.empty{grid-column:1/-1;text-align:center;padding:50px 20px;color:var(--muted);font-size:13px}\n'
    '.modal-wrap{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:100;display:flex;align-items:flex-end;justify-content:center;animation:fadeIn .2s ease}\n'
    '.modal{background:var(--bg);border-radius:28px 28px 0 0;max-width:960px;width:100%;max-height:88vh;display:flex;flex-direction:column;overflow:hidden;animation:slideUp .28s ease;box-shadow:0 -8px 40px rgba(0,0,0,.18)}\n'
    '.modal-img{width:100%;height:190px;object-fit:cover;flex-shrink:0;display:block}\n'
    '.modal-ph{width:100%;height:190px;display:none;align-items:center;justify-content:center;font-size:64px;flex-shrink:0;background:linear-gradient(135deg,var(--accent-light),var(--bg))}\n'
    '.modal-body{padding:22px 24px 34px;overflow-y:auto;flex:1}\n'
    '.modal-head{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:18px}\n'
    '.modal-name{font-size:19px;font-weight:700;line-height:1.3}\n'
    '.modal-kcal{font-size:13px;color:var(--accent);font-weight:700;margin-top:4px}\n'
    '.x-btn{width:36px;height:36px;border-radius:50%;border:none;background:var(--bg);cursor:pointer;color:var(--muted);font-size:19px;display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:var(--sh-sm);transition:box-shadow .15s,color .15s;font-family:inherit}\n'
    '.x-btn:active{box-shadow:var(--sh-press);color:var(--accent)}\n'
    '.modal-sec{margin-top:20px}\n'
    '.modal-sec h3{font-size:10px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px}\n'
    '.modal-ing{font-size:13px;line-height:2.2}\n'
    '.modal-step{display:flex;gap:12px;margin-bottom:11px;font-size:13px;line-height:1.65}\n'
    '.sn{width:24px;height:24px;min-width:24px;border-radius:50%;background:var(--bg);box-shadow:var(--sh-sm);color:var(--accent);font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;margin-top:1px}\n'
)
src = src.replace(CSS_BLOCK, '')

# 5. Remove responsive gallery/modal lines
RESPONSIVE = (
    '  .gallery-top{padding:6px 14px 0}\n'
    '  .filters{padding:12px 14px}\n'
    '  .gallery-grid{padding:2px 14px 18px;gap:12px;grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}\n'
    '  .card-name{font-size:12px}\n'
    '  .modal-body{padding:18px 18px 28px}\n'
)
src = src.replace(RESPONSIVE, '')

# 6. Remove Recetas tab button
src = src.replace('    <button class="tab" data-tab="recetas">Recetas</button>\n', '')

# 7. Remove panel-recetas HTML
PANEL_RECETAS = (
    '  <div id="panel-recetas" class="panel">\n'
    '    <div class="gallery-top">\n'
    '      <input type="text" id="gsearch" placeholder="Buscar recetas\\u2026" autocomplete="off">\n'
    '    </div>\n'
    '    <div class="filters">\n'
    '      <button class="filter-btn active" data-cat="all">Todas</button>\n'
    '      <button class="filter-btn" data-cat="pollo">Pollo</button>\n'
    '      <button class="filter-btn" data-cat="pescado">Pescado</button>\n'
    '      <button class="filter-btn" data-cat="carne">Carne</button>\n'
    '      <button class="filter-btn" data-cat="vegetariano">Vegetariano</button>\n'
    '      <button class="filter-btn" data-cat="arroz">Arroz</button>\n'
    '      <button class="filter-btn" data-cat="legumbres">Legumbres</button>\n'
    '      <button class="filter-btn" data-cat="pasta">Pasta</button>\n'
    '      <button class="filter-btn" data-cat="desayuno">Desayuno</button>\n'
    '      <button class="filter-btn" data-cat="sopa">Sopas</button>\n'
    '      <button class="filter-btn" data-cat="ensalada">Ensaladas</button>\n'
    '      <button class="filter-btn" data-cat="postre">Postres</button>\n'
    '    </div>\n'
    '    <div class="gallery-grid" id="gg">\n'
    '      <div class="empty">Cargando recetas\\u2026</div>\n'
    '    </div>\n'
    '  </div>\n'
)
src = src.replace(PANEL_RECETAS, '')

# 8. Fix panel-foto being outside .app and remove orphan modal div
# panel-foto was outside </div> that closed .app
src = src.replace(
    '</div>\n  <div id="panel-foto" class="panel">',
    '  <div id="panel-foto" class="panel">'
)
src = src.replace('<div id="modal" style="display:none"></div>\n', '')

# 9. Remove gallery JS variables
src = src.replace("var gg=document.getElementById('gg');\n", '')
src = src.replace("var gsearch=document.getElementById('gsearch');\n", '')
src = src.replace("var galleryLoaded=false,allRecipes=[],recipesMap={},activeFilter='all',searchTerm='';\n", '')
src = src.replace("    if(id==='recetas'&&!galleryLoaded)loadGallery();\n", '')

# 10. Remove everything from PHOTOS/DEFAULT_POOL/EMOJIS through all gallery functions
marker_start = "var Q='?w=800&h=600&fit=crop&auto=format';"
marker_end = "\nvar sexoSeg=document.getElementById('sexo-seg');"
i0 = src.find(marker_start)
i1 = src.find(marker_end)
if i0 != -1 and i1 != -1:
    src = src[:i0] + src[i1:]
    print(f"Gallery JS block removed ({i1-i0} chars)")
else:
    print(f"WARNING gallery block not found: start={i0} end={i1}")

# Remove window._om/_cm if it survived
src = src.replace("window._om=openModal;window._cm=closeModal;\n\n", '')
src = src.replace("window._om=openModal;window._cm=closeModal;\n", '')
src = src.replace("gsearch.addEventListener('input',function(e){searchTerm=e.target.value.toLowerCase().trim();renderGallery();});\n", '')

# 11. Expand FOOD_MAP
OLD_FOOD_MAP_START = "  var FOOD_MAP = {\n    'banana':['platano','banana']"
OLD_FOOD_MAP_END = "    'tofu':['tofu']\n  };"
i0 = src.find(OLD_FOOD_MAP_START)
i1 = src.find(OLD_FOOD_MAP_END)
if i0 != -1 and i1 != -1:
    NEW_FOOD_MAP = """  var FOOD_MAP = {
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
  };"""
    src = src[:i0] + NEW_FOOD_MAP + src[i1 + len(OLD_FOOD_MAP_END):]
    print("FOOD_MAP expanded")
else:
    print(f"WARNING FOOD_MAP not found: start={i0} end={i1}")

# 12. Remove load_recipes_from_drive function
OLD_FN = (
    'def load_recipes_from_drive():\n'
    '    url = f"https://docs.google.com/uc?export=download&id={DRIVE_FILE_ID}"\n'
    '    try:\n'
    '        response = requests.get(url, timeout=10)\n'
    '        if response.status_code == 200:\n'
    '            return response.json()\n'
    '    except Exception as exc:\n'
    '        print(f"Error cargando recetas desde Drive: {exc}")\n'
    '    if os.path.exists(RECIPES_DATA_PATH):\n'
    '        with open(RECIPES_DATA_PATH, "r", encoding="utf-8") as file:\n'
    '            return json.load(file)\n'
    '    return {"recetas": []}\n'
    '\n'
    '\n'
)
src = src.replace(OLD_FN, '')

# 13. Simplify recipes_db loading
src = src.replace(
    'recipes_db = load_recipes_from_drive()',
    'recipes_db = load_json_file("data/recipes_large.json", {"recetas": []})'
)

# 14. Remove /api/recipes endpoint
src = src.replace(
    '\n\n@app.get("/api/recipes")\nasync def get_recipes():\n    return recipes_db\n',
    ''
)

# 15. Update manifest description
src = src.replace(
    '"description": "Asistente de nutrici\u00f3n con recetas, calor\u00edas y calculadora de macros"',
    '"description": "Asistente de nutrici\u00f3n: calor\u00edas, macros, calculadora TDEE y estimaci\u00f3n por foto"'
)

# Final syntax check
try:
    ast.parse(src)
    print("Syntax OK")
except SyntaxError as e:
    print("SYNTAX ERROR:", e)
    import sys; sys.exit(1)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(src)

print(f"Done. Lines: {src.count(chr(10))}")
