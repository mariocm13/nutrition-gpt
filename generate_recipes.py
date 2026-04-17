import json
import random

def generate_recipes(count=1000):
    bases = ["Pollo", "Res", "Pescado", "Tofu", "Lentejas", "Garbanzos", "Pasta", "Arroz", "Quinoa", "Verduras"]
    metodos = ["a la plancha", "al horno", "al vapor", "salteado", "en ensalada", "estofado", "con salsa", "al curry"]
    acompanamientos = ["con brócoli", "con espárragos", "con patatas", "con ensalada mixta", "con aguacate", "con espinacas", "con tomate"]
    
    recetas = []
    
    for i in range(count):
        base = random.choice(bases)
        metodo = random.choice(metodos)
        acompanamiento = random.choice(acompanamientos)
        
        nombre = f"{base} {metodo} {acompanamiento}"
        calorias = random.randint(250, 750)
        
        ingredientes = [
            f"200g de {base.lower()}",
            f"150g de {acompanamiento.replace('con ', '').lower()}",
            "1 cucharada de aceite de oliva",
            "Sal y pimienta al gusto",
            "Especias variadas"
        ]
        
        instrucciones = [
            f"Prepara el {base.lower()} limpiándolo adecuadamente.",
            f"Cocina el {base.lower()} {metodo}.",
            f"Prepara el acompañamiento ({acompanamiento.replace('con ', '').lower()}).",
            "Mezcla todo en un plato y sirve caliente.",
            "Añade especias al gusto para mejorar el sabor."
        ]
        
        recetas.append({
            "id": i + 1,
            "nombre": nombre,
            "ingredientes": ingredientes,
            "instrucciones": instrucciones,
            "calorias_aprox": calorias
        })
    
    return {"recetas": recetas}

if __name__ == "__main__":
    data = generate_recipes(1000)
    with open('data/recipes_large.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Generadas {len(data['recetas'])} recetas en data/recipes_large.json")
