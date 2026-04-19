"""One-time script: add ~100 new entries to data/calories.json."""
import json

with open('data/calories.json', encoding='utf-8') as f:
    db = json.load(f)

existing = {a['nombre'].lower() for a in db['alimentos']}

new_entries = [
    # ── Frutas adicionales ──────────────────────────────────────────────────
    {"nombre": "Lichi", "calorias": 66, "unidad": "100g", "proteina": 0.8, "carbohidratos": 16.5, "grasas": 0.4, "fibra": 1.3},
    {"nombre": "Maracuya", "calorias": 97, "unidad": "100g", "proteina": 2.2, "carbohidratos": 23.4, "grasas": 0.7, "fibra": 10.4},
    {"nombre": "Albaricoque", "calorias": 48, "unidad": "100g", "proteina": 1.4, "carbohidratos": 11.1, "grasas": 0.4, "fibra": 2.0},
    # ── Lácteos y derivados ─────────────────────────────────────────────────
    {"nombre": "Helado", "calorias": 207, "unidad": "100g", "proteina": 3.5, "carbohidratos": 23.6, "grasas": 11.0, "fibra": 0.0},
    {"nombre": "Cafe con leche", "calorias": 38, "unidad": "100ml", "proteina": 1.8, "carbohidratos": 4.4, "grasas": 1.5, "fibra": 0.0},
    {"nombre": "Batido", "calorias": 85, "unidad": "100ml", "proteina": 2.5, "carbohidratos": 14.0, "grasas": 2.0, "fibra": 0.5},
    {"nombre": "Batido con leche", "calorias": 112, "unidad": "100ml", "proteina": 3.5, "carbohidratos": 18.0, "grasas": 3.0, "fibra": 0.0},
    {"nombre": "Nata montada", "calorias": 257, "unidad": "100ml", "proteina": 2.0, "carbohidratos": 3.5, "grasas": 26.0, "fibra": 0.0},
    # ── Panadería y bollería ────────────────────────────────────────────────
    {"nombre": "Croissant", "calorias": 406, "unidad": "100g", "proteina": 8.2, "carbohidratos": 45.8, "grasas": 21.0, "fibra": 2.1},
    {"nombre": "Gofre", "calorias": 291, "unidad": "100g", "proteina": 7.9, "carbohidratos": 42.6, "grasas": 10.0, "fibra": 1.3},
    {"nombre": "Crepe", "calorias": 200, "unidad": "100g", "proteina": 5.9, "carbohidratos": 25.7, "grasas": 8.5, "fibra": 0.9},
    {"nombre": "Donut", "calorias": 452, "unidad": "100g", "proteina": 7.5, "carbohidratos": 51.0, "grasas": 25.0, "fibra": 1.5},
    {"nombre": "Magdalena", "calorias": 393, "unidad": "100g", "proteina": 6.0, "carbohidratos": 54.0, "grasas": 18.0, "fibra": 1.2},
    {"nombre": "Galleta", "calorias": 458, "unidad": "100g", "proteina": 6.2, "carbohidratos": 65.0, "grasas": 20.0, "fibra": 2.0},
    {"nombre": "Churro", "calorias": 380, "unidad": "100g", "proteina": 5.5, "carbohidratos": 50.0, "grasas": 18.0, "fibra": 1.8},
    {"nombre": "Torrija", "calorias": 245, "unidad": "100g", "proteina": 7.0, "carbohidratos": 33.0, "grasas": 9.0, "fibra": 1.0},
    # ── Repostería y postres ────────────────────────────────────────────────
    {"nombre": "Pastel", "calorias": 350, "unidad": "100g", "proteina": 5.0, "carbohidratos": 52.0, "grasas": 14.0, "fibra": 1.0},
    {"nombre": "Tarta de queso", "calorias": 321, "unidad": "100g", "proteina": 5.5, "carbohidratos": 29.0, "grasas": 20.0, "fibra": 0.4},
    {"nombre": "Brownie", "calorias": 415, "unidad": "100g", "proteina": 5.5, "carbohidratos": 55.0, "grasas": 20.0, "fibra": 2.5},
    {"nombre": "Tiramisu", "calorias": 283, "unidad": "100g", "proteina": 5.5, "carbohidratos": 25.0, "grasas": 17.0, "fibra": 0.5},
    {"nombre": "Flan", "calorias": 140, "unidad": "100g", "proteina": 4.5, "carbohidratos": 20.0, "grasas": 4.5, "fibra": 0.0},
    {"nombre": "Natillas", "calorias": 120, "unidad": "100g", "proteina": 4.0, "carbohidratos": 18.0, "grasas": 3.5, "fibra": 0.0},
    {"nombre": "Mousse de chocolate", "calorias": 250, "unidad": "100g", "proteina": 5.0, "carbohidratos": 22.0, "grasas": 16.0, "fibra": 1.5},
    # ── Snacks y aperitivos ─────────────────────────────────────────────────
    {"nombre": "Nachos", "calorias": 503, "unidad": "100g", "proteina": 7.0, "carbohidratos": 63.0, "grasas": 25.0, "fibra": 4.5},
    {"nombre": "Aceituna", "calorias": 145, "unidad": "100g", "proteina": 1.0, "carbohidratos": 3.8, "grasas": 15.0, "fibra": 3.3},
    # ── Platos mediterráneos ─────────────────────────────────────────────────
    {"nombre": "Paella", "calorias": 180, "unidad": "100g", "proteina": 12.0, "carbohidratos": 22.0, "grasas": 5.0, "fibra": 1.0},
    {"nombre": "Risotto", "calorias": 170, "unidad": "100g", "proteina": 6.0, "carbohidratos": 26.0, "grasas": 5.0, "fibra": 0.8},
    {"nombre": "Tortilla española", "calorias": 185, "unidad": "100g", "proteina": 9.0, "carbohidratos": 10.5, "grasas": 11.5, "fibra": 0.8},
    {"nombre": "Croqueta", "calorias": 255, "unidad": "100g", "proteina": 10.0, "carbohidratos": 22.0, "grasas": 14.0, "fibra": 0.8},
    {"nombre": "Ensalada", "calorias": 55, "unidad": "100g", "proteina": 2.5, "carbohidratos": 6.5, "grasas": 2.5, "fibra": 2.0},
    {"nombre": "Sopa", "calorias": 60, "unidad": "100g", "proteina": 3.5, "carbohidratos": 8.0, "grasas": 1.5, "fibra": 1.0},
    {"nombre": "Gazpacho", "calorias": 50, "unidad": "100g", "proteina": 1.5, "carbohidratos": 7.0, "grasas": 2.0, "fibra": 1.5},
    {"nombre": "Hummus", "calorias": 177, "unidad": "100g", "proteina": 8.0, "carbohidratos": 14.0, "grasas": 9.0, "fibra": 6.0},
    {"nombre": "Guacamole", "calorias": 150, "unidad": "100g", "proteina": 2.0, "carbohidratos": 8.5, "grasas": 12.0, "fibra": 5.0},
    # ── Cocina asiática ─────────────────────────────────────────────────────
    {"nombre": "Sushi", "calorias": 143, "unidad": "100g", "proteina": 6.5, "carbohidratos": 20.0, "grasas": 3.5, "fibra": 0.5},
    {"nombre": "Ramen", "calorias": 130, "unidad": "100g", "proteina": 6.0, "carbohidratos": 20.0, "grasas": 2.5, "fibra": 0.5},
    {"nombre": "Pad thai", "calorias": 200, "unidad": "100g", "proteina": 8.0, "carbohidratos": 27.0, "grasas": 7.0, "fibra": 1.5},
    {"nombre": "Arroz frito", "calorias": 163, "unidad": "100g", "proteina": 5.0, "carbohidratos": 27.0, "grasas": 4.5, "fibra": 1.0},
    {"nombre": "Rollitos primavera", "calorias": 225, "unidad": "100g", "proteina": 7.0, "carbohidratos": 25.0, "grasas": 10.5, "fibra": 2.0},
    {"nombre": "Dumpling", "calorias": 195, "unidad": "100g", "proteina": 9.0, "carbohidratos": 24.0, "grasas": 7.0, "fibra": 1.5},
    {"nombre": "Fideos cocidos", "calorias": 138, "unidad": "100g", "proteina": 4.5, "carbohidratos": 27.0, "grasas": 1.0, "fibra": 1.5},
    {"nombre": "Curry", "calorias": 195, "unidad": "100g", "proteina": 12.0, "carbohidratos": 18.0, "grasas": 8.0, "fibra": 2.0},
    # ── Medio Oriente y México ───────────────────────────────────────────────
    {"nombre": "Kebab", "calorias": 245, "unidad": "100g", "proteina": 19.0, "carbohidratos": 8.0, "grasas": 15.0, "fibra": 1.0},
    {"nombre": "Shawarma", "calorias": 230, "unidad": "100g", "proteina": 17.0, "carbohidratos": 14.0, "grasas": 12.0, "fibra": 1.0},
    {"nombre": "Falafel", "calorias": 333, "unidad": "100g", "proteina": 13.3, "carbohidratos": 31.8, "grasas": 17.8, "fibra": 4.9},
    {"nombre": "Burrito", "calorias": 218, "unidad": "100g", "proteina": 11.0, "carbohidratos": 26.0, "grasas": 8.0, "fibra": 2.5},
    {"nombre": "Tacos", "calorias": 226, "unidad": "100g", "proteina": 11.0, "carbohidratos": 21.0, "grasas": 11.0, "fibra": 3.0},
    {"nombre": "Quesadilla", "calorias": 307, "unidad": "100g", "proteina": 15.0, "carbohidratos": 26.0, "grasas": 15.0, "fibra": 2.0},
    # ── Bocadillos ──────────────────────────────────────────────────────────
    {"nombre": "Sandwich", "calorias": 270, "unidad": "100g", "proteina": 13.0, "carbohidratos": 30.0, "grasas": 10.0, "fibra": 2.0},
    {"nombre": "Wrap", "calorias": 245, "unidad": "100g", "proteina": 12.0, "carbohidratos": 27.0, "grasas": 9.5, "fibra": 2.5},
    # ── Bebidas alcohólicas ─────────────────────────────────────────────────
    {"nombre": "Cerveza", "calorias": 43, "unidad": "100ml", "proteina": 0.5, "carbohidratos": 3.6, "grasas": 0.0, "fibra": 0.0},
    {"nombre": "Vino", "calorias": 82, "unidad": "100ml", "proteina": 0.1, "carbohidratos": 2.7, "grasas": 0.0, "fibra": 0.0},
    {"nombre": "Vino tinto", "calorias": 85, "unidad": "100ml", "proteina": 0.1, "carbohidratos": 2.6, "grasas": 0.0, "fibra": 0.0},
    {"nombre": "Cava", "calorias": 76, "unidad": "100ml", "proteina": 0.3, "carbohidratos": 1.8, "grasas": 0.0, "fibra": 0.0},
    # ── Bebidas sin alcohol ─────────────────────────────────────────────────
    {"nombre": "Refresco cola", "calorias": 42, "unidad": "100ml", "proteina": 0.0, "carbohidratos": 10.6, "grasas": 0.0, "fibra": 0.0},
    {"nombre": "Zumo de manzana", "calorias": 47, "unidad": "100ml", "proteina": 0.1, "carbohidratos": 11.7, "grasas": 0.1, "fibra": 0.2},
    {"nombre": "Batido de frutas", "calorias": 75, "unidad": "100ml", "proteina": 1.5, "carbohidratos": 16.0, "grasas": 0.5, "fibra": 1.0},
    # ── Cereales de desayuno ────────────────────────────────────────────────
    {"nombre": "Muesli", "calorias": 370, "unidad": "100g", "proteina": 10.0, "carbohidratos": 61.0, "grasas": 8.0, "fibra": 7.5},
    {"nombre": "Cereales con leche", "calorias": 155, "unidad": "100g", "proteina": 4.5, "carbohidratos": 30.0, "grasas": 2.5, "fibra": 2.0},
    # ── Embutidos adicionales ───────────────────────────────────────────────
    {"nombre": "Salchichas", "calorias": 301, "unidad": "100g", "proteina": 12.0, "carbohidratos": 3.0, "grasas": 27.0, "fibra": 0.0},
    {"nombre": "Salami", "calorias": 336, "unidad": "100g", "proteina": 22.0, "carbohidratos": 1.2, "grasas": 27.0, "fibra": 0.0},
    {"nombre": "Jamon cocido", "calorias": 145, "unidad": "100g", "proteina": 19.0, "carbohidratos": 1.5, "grasas": 7.0, "fibra": 0.0},
    {"nombre": "Mortadela", "calorias": 311, "unidad": "100g", "proteina": 15.0, "carbohidratos": 3.0, "grasas": 27.0, "fibra": 0.0},
    {"nombre": "Fuet", "calorias": 430, "unidad": "100g", "proteina": 27.0, "carbohidratos": 1.5, "grasas": 35.0, "fibra": 0.0},
    # ── Platos de arroz ─────────────────────────────────────────────────────
    {"nombre": "Arroz con leche", "calorias": 130, "unidad": "100g", "proteina": 3.0, "carbohidratos": 25.0, "grasas": 2.5, "fibra": 0.3},
    # ── Proteína vegetal ────────────────────────────────────────────────────
    {"nombre": "Seitan", "calorias": 185, "unidad": "100g", "proteina": 25.0, "carbohidratos": 14.0, "grasas": 1.9, "fibra": 0.6},
    # ── Salsas ──────────────────────────────────────────────────────────────
    {"nombre": "Salsa de tomate", "calorias": 82, "unidad": "100g", "proteina": 1.5, "carbohidratos": 18.0, "grasas": 0.5, "fibra": 1.5},
    {"nombre": "Pesto", "calorias": 370, "unidad": "100g", "proteina": 6.0, "carbohidratos": 5.0, "grasas": 37.0, "fibra": 2.0},
    {"nombre": "Tahini", "calorias": 595, "unidad": "100g", "proteina": 17.0, "carbohidratos": 21.2, "grasas": 53.8, "fibra": 9.3},
    {"nombre": "Mostaza", "calorias": 66, "unidad": "100g", "proteina": 4.4, "carbohidratos": 5.8, "grasas": 3.3, "fibra": 3.3},
    # ── Bebidas vegetales adicionales ───────────────────────────────────────
    {"nombre": "Yogur de soja", "calorias": 62, "unidad": "100g", "proteina": 3.6, "carbohidratos": 6.5, "grasas": 2.2, "fibra": 0.5},
    # ── Suplementos ─────────────────────────────────────────────────────────
    {"nombre": "Barrita proteica", "calorias": 385, "unidad": "100g", "proteina": 30.0, "carbohidratos": 38.0, "grasas": 12.0, "fibra": 4.0},
]

added = 0
for entry in new_entries:
    if entry['nombre'].lower() not in existing:
        db['alimentos'].append(entry)
        existing.add(entry['nombre'].lower())
        added += 1

with open('data/calories.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"Added {added} new entries. Total now: {len(db['alimentos'])}")
