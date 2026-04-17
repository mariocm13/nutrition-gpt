import json
import os

def load_data(file_path):
    """Carga datos desde un archivo JSON."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def show_calories(food_name, calories_data):
    """Busca y muestra las calorias de un alimento."""
    for item in calories_data.get('alimentos', []):
        if food_name.lower() in item['nombre'].lower():
            print(f"Alimento: {item['nombre']}")
            print(f"Calorias: {item['calorias']} kcal por {item['unidad']}")
            return
    print(f"No se encontro informacion para '{food_name}'.")

def show_recipes(recipes_data):
    """Muestra todas las recetas disponibles."""
    print("\n--- Recetas Disponibles ---")
    for i, recipe in enumerate(recipes_data.get('recetas', []), 1):
        print(f"{i}. {recipe['nombre']} ({recipe['calorias_aprox']} kcal)")

def show_recipe_details(recipe_index, recipes_data):
    """Muestra los detalles de una receta especifica."""
    recipes = recipes_data.get('recetas', [])
    if 0 <= recipe_index < len(recipes):
        recipe = recipes[recipe_index]
        print(f"\n--- {recipe['nombre']} ---")
        print("Ingredientes:")
        for ing in recipe['ingredientes']:
            print(f"- {ing}")
        print("\nInstrucciones:")
        for step in recipe['instrucciones']:
            print(f"- {step}")
        print(f"\nCalorias aproximadas: {recipe['calorias_aprox']} kcal")
    else:
        print("Indice de receta no valido.")

def main():
    calories_data = load_data('data/calories.json')
    recipes_data = load_data('data/recipes_large.json')

    print("Bienvenido a tu Asistente de Nutricion GPT!")
    
    while True:
        print("\nQue te gustaria hacer?")
        print("1. Consultar calorias de un alimento")
        print("2. Ver recetas saludables")
        print("3. Salir")
        
        choice = input("Selecciona una opcion (1-3): ")
        
        if choice == '1':
            food = input("Introduce el nombre del alimento: ")
            show_calories(food, calories_data)
        elif choice == '2':
            show_recipes(recipes_data)
            recipe_choice = input("\nIntroduce el numero de la receta para ver detalles (o Enter para volver): ")
            if recipe_choice.isdigit():
                show_recipe_details(int(recipe_choice) - 1, recipes_data)
        elif choice == '3':
            print("Hasta luego! Mantente saludable.")
            break
        else:
            print("Opcion no valida. Intentalo de nuevo.")

if __name__ == "__main__":
    main()
