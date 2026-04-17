from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
import json
import os
import requests
from typing import Optional

app = FastAPI(title="Asistente de Nutrición Pro")

# Configuración de la base de datos
# Reemplaza este ID con el ID de tu archivo de Google Drive cuando lo tengas
DRIVE_FILE_ID = "1_REEMPLAZA_CON_TU_ID_DE_GOOGLE_DRIVE"
LOCAL_DATA_PATH = 'data/recipes_large.json'
CALORIES_DATA_PATH = 'data/calories.json'

def load_data():
    """Carga datos desde Google Drive o localmente como respaldo."""
    # Intentar cargar desde Google Drive si hay un ID configurado
    if DRIVE_FILE_ID and "REEMPLAZA" not in DRIVE_FILE_ID:
        url = f"https://docs.google.com/uc?export=download&id={DRIVE_FILE_ID}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error cargando desde Drive: {e}")
    
    # Respaldo: Cargar localmente
    if os.path.exists(LOCAL_DATA_PATH):
        with open(LOCAL_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"recetas": []}

def load_calories():
    if os.path.exists(CALORIES_DATA_PATH):
        with open(CALORIES_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"alimentos": []}

# Carga inicial
recipes_db = load_data()
calories_db = load_calories()

@app.get("/", response_class=HTMLResponse)
async def get_home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NutriGPT Pro - 1000+ Recetas</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            .recipe-card:hover { transform: translateY(-5px); transition: all 0.3s; }
            .loader { border-top-color: #3498db; animation: spinner 1.5s linear infinite; }
            @keyframes spinner { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body class="bg-gray-50 min-h-screen">
        <nav class="bg-green-600 text-white p-4 shadow-lg">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-2xl font-bold"><i class="fas fa-utensils mr-2"></i>NutriGPT Pro</h1>
                <span class="bg-green-700 px-3 py-1 rounded-full text-sm">1000+ Recetas Activas</span>
            </div>
        </nav>

        <main class="container mx-auto p-6">
            <div class="flex flex-wrap gap-4 mb-8">
                <button onclick="showSection('calories')" class="flex-1 bg-white p-4 rounded-xl shadow hover:bg-green-50 transition border-b-4 border-green-500 font-bold text-green-700">
                    <i class="fas fa-fire mr-2"></i>Contador de Calorías
                </button>
                <button onclick="showSection('recipes')" class="flex-1 bg-white p-4 rounded-xl shadow hover:bg-blue-50 transition border-b-4 border-blue-500 font-bold text-blue-700">
                    <i class="fas fa-book-open mr-2"></i>Explorar 1000 Recetas
                </button>
            </div>

            <!-- Sección Calorías -->
            <div id="section-calories" class="section">
                <div class="bg-white p-6 rounded-2xl shadow-sm mb-6">
                    <div class="flex gap-2">
                        <input type="text" id="food-search" placeholder="¿Qué alimento buscas?" class="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none">
                        <button onclick="searchCalories()" class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700">Buscar</button>
                    </div>
                    <div id="calories-result" class="mt-4"></div>
                </div>
            </div>

            <!-- Sección Recetas -->
            <div id="section-recipes" class="section hidden">
                <div class="bg-white p-6 rounded-2xl shadow-sm mb-6">
                    <div class="flex gap-2 mb-4">
                        <input type="text" id="recipe-search" onkeyup="filterRecipes()" placeholder="Filtrar por ingrediente o nombre..." class="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none">
                    </div>
                    <div id="recipes-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <!-- Las recetas se cargarán aquí -->
                    </div>
                    <div id="loading" class="flex justify-center my-10">
                        <div class="loader ease-linear rounded-full border-4 border-t-4 border-gray-200 h-12 w-12"></div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Modal de Receta -->
        <div id="recipe-modal" class="fixed inset-0 bg-black bg-opacity-50 hidden flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-8 relative">
                <button onclick="closeModal()" class="absolute top-4 right-4 text-gray-500 hover:text-gray-800 text-2xl">&times;</button>
                <div id="modal-content"></div>
            </div>
        </div>

        <script>
            let allRecipes = [];

            function showSection(name) {
                document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
                document.getElementById('section-' + name).classList.remove('hidden');
            }

            async function searchCalories() {
                const food = document.getElementById('food-search').value;
                const res = await fetch(`/api/calories?food=${food}`);
                const data = await res.json();
                const container = document.getElementById('calories-result');
                
                if(data.found) {
                    container.innerHTML = `
                        <div class="bg-green-50 p-4 rounded-lg border border-green-200">
                            <h3 class="font-bold text-lg text-green-800">${data.nombre}</h3>
                            <p class="text-green-700">${data.calorias} kcal por ${data.unidad}</p>
                        </div>`;
                } else {
                    container.innerHTML = `<p class="text-red-500">No encontrado. Prueba con 'Pollo' o 'Manzana'.</p>`;
                }
            }

            async function loadRecipes() {
                const res = await fetch('/api/recipes');
                const data = await res.json();
                allRecipes = data.recetas;
                document.getElementById('loading').classList.add('hidden');
                displayRecipes(allRecipes.slice(0, 50)); // Mostrar primeras 50 inicialmente
            }

            function displayRecipes(recipes) {
                const grid = document.getElementById('recipes-grid');
                grid.innerHTML = recipes.map(r => `
                    <div class="bg-white border rounded-xl p-4 recipe-card cursor-pointer shadow-sm" onclick="openRecipe(${r.id})">
                        <div class="text-blue-600 font-bold mb-2">#${r.id}</div>
                        <h3 class="font-bold text-gray-800 mb-2">${r.nombre}</h3>
                        <div class="flex justify-between text-sm text-gray-500">
                            <span><i class="fas fa-fire mr-1"></i>${r.calorias_aprox} kcal</span>
                            <span><i class="fas fa-list mr-1"></i>${r.ingredientes.length} ing.</span>
                        </div>
                    </div>
                `).join('');
            }

            function filterRecipes() {
                const term = document.getElementById('recipe-search').value.toLowerCase();
                const filtered = allRecipes.filter(r => 
                    r.nombre.toLowerCase().includes(term) || 
                    r.ingredientes.some(i => i.toLowerCase().includes(term))
                );
                displayRecipes(filtered.slice(0, 50));
            }

            function openRecipe(id) {
                const r = allRecipes.find(recipe => recipe.id === id);
                const modal = document.getElementById('recipe-modal');
                const content = document.getElementById('modal-content');
                
                content.innerHTML = `
                    <h2 class="text-3xl font-bold text-gray-800 mb-4">${r.nombre}</h2>
                    <div class="bg-blue-50 p-4 rounded-xl mb-6 flex justify-around">
                        <div class="text-center">
                            <div class="text-blue-600 font-bold text-xl">${r.calorias_aprox}</div>
                            <div class="text-xs text-blue-400 uppercase">Calorías</div>
                        </div>
                        <div class="text-center">
                            <div class="text-blue-600 font-bold text-xl">${r.ingredientes.length}</div>
                            <div class="text-xs text-blue-400 uppercase">Ingredientes</div>
                        </div>
                    </div>
                    <h3 class="font-bold text-lg mb-2 text-gray-700">Ingredientes</h3>
                    <ul class="list-disc ml-5 mb-6 text-gray-600">
                        ${r.ingredientes.map(i => `<li>${i}</li>`).join('')}
                    </ul>
                    <h3 class="font-bold text-lg mb-2 text-gray-700">Instrucciones</h3>
                    <ol class="list-decimal ml-5 text-gray-600 space-y-2">
                        ${r.instrucciones.map(i => `<li>${i}</li>`).join('')}
                    </ol>
                `;
                modal.classList.remove('hidden');
            }

            function closeModal() {
                document.getElementById('recipe-modal').classList.add('hidden');
            }

            window.onload = loadRecipes;
        </script>
    </body>
    </html>
    """

@app.get("/api/calories")
async def get_calories(food: str):
    for item in calories_db.get('alimentos', []):
        if food.lower() in item['nombre'].lower():
            return {"found": True, **item}
    return {"found": False}

@app.get("/api/recipes")
async def get_recipes():
    return recipes_db

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
