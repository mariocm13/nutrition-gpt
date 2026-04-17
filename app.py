from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import json
import os

app = FastAPI(title="Asistente de Nutrición")

# Cargar datos
def load_data(file_path):
    """Carga datos desde un archivo JSON."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

calories_data = load_data('data/calories.json')
recipes_data = load_data('data/recipes.json')

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Sirve la página principal."""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Asistente de Nutrición GPT</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 800px;
                width: 100%;
                padding: 40px;
            }
            
            h1 {
                color: #333;
                margin-bottom: 10px;
                text-align: center;
            }
            
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 30px;
                border-bottom: 2px solid #eee;
            }
            
            .tab-button {
                padding: 12px 20px;
                border: none;
                background: none;
                cursor: pointer;
                font-size: 16px;
                color: #666;
                border-bottom: 3px solid transparent;
                transition: all 0.3s ease;
            }
            
            .tab-button.active {
                color: #667eea;
                border-bottom-color: #667eea;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .input-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            
            input[type="text"],
            select {
                width: 100%;
                padding: 12px;
                border: 2px solid #eee;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s ease;
            }
            
            input[type="text"]:focus,
            select:focus {
                outline: none;
                border-color: #667eea;
            }
            
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            
            button:hover {
                transform: translateY(-2px);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            .result {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                border-left: 4px solid #667eea;
            }
            
            .result-title {
                font-size: 18px;
                font-weight: 600;
                color: #333;
                margin-bottom: 10px;
            }
            
            .result-content {
                color: #666;
                line-height: 1.6;
            }
            
            .recipe-item {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            
            .recipe-item:hover {
                border-color: #667eea;
                background: #f0f2ff;
            }
            
            .recipe-name {
                font-weight: 600;
                color: #333;
                margin-bottom: 5px;
            }
            
            .recipe-cals {
                font-size: 14px;
                color: #999;
            }
            
            .recipe-details {
                margin-top: 15px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                border: 1px solid #eee;
            }
            
            .recipe-details h3 {
                color: #667eea;
                margin-top: 15px;
                margin-bottom: 10px;
                font-size: 16px;
            }
            
            .recipe-details ul {
                margin-left: 20px;
                color: #666;
            }
            
            .recipe-details li {
                margin-bottom: 8px;
            }
            
            .error {
                color: #e74c3c;
                padding: 12px;
                background: #fadbd8;
                border-radius: 8px;
                margin-top: 10px;
            }
            
            .success {
                color: #27ae60;
                padding: 12px;
                background: #d5f4e6;
                border-radius: 8px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 Asistente de Nutrición GPT</h1>
            <p class="subtitle">Tu compañero para una alimentación saludable</p>
            
            <div class="tabs">
                <button class="tab-button active" onclick="switchTab('calories')">Calorías</button>
                <button class="tab-button" onclick="switchTab('recipes')">Recetas</button>
            </div>
            
            <!-- Tab de Calorías -->
            <div id="calories" class="tab-content active">
                <div class="input-group">
                    <label for="food-input">Buscar alimento:</label>
                    <input type="text" id="food-input" placeholder="Ej: Manzana, Pollo, Arroz...">
                </div>
                <button onclick="searchCalories()">Buscar Calorías</button>
                <div id="calories-result"></div>
            </div>
            
            <!-- Tab de Recetas -->
            <div id="recipes" class="tab-content">
                <button onclick="loadRecipes()">Ver todas las recetas</button>
                <div id="recipes-result"></div>
            </div>
        </div>
        
        <script>
            function switchTab(tabName) {
                // Ocultar todos los tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                
                // Mostrar el tab seleccionado
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }
            
            async function searchCalories() {
                const food = document.getElementById('food-input').value.trim();
                if (!food) {
                    document.getElementById('calories-result').innerHTML = '<div class="error">Por favor ingresa un alimento.</div>';
                    return;
                }
                
                try {
                    const response = await fetch(`/api/calories?food=${encodeURIComponent(food)}`);
                    const data = await response.json();
                    
                    if (data.found) {
                        document.getElementById('calories-result').innerHTML = `
                            <div class="result">
                                <div class="result-title">${data.nombre}</div>
                                <div class="result-content">
                                    <strong>Calorías:</strong> ${data.calorias} kcal por ${data.unidad}
                                </div>
                            </div>
                        `;
                    } else {
                        document.getElementById('calories-result').innerHTML = '<div class="error">No se encontró información para ese alimento.</div>';
                    }
                } catch (error) {
                    document.getElementById('calories-result').innerHTML = '<div class="error">Error al buscar. Intenta de nuevo.</div>';
                }
            }
            
            async function loadRecipes() {
                try {
                    const response = await fetch('/api/recipes');
                    const data = await response.json();
                    
                    let html = '';
                    data.recetas.forEach((recipe, index) => {
                        html += `
                            <div class="recipe-item" onclick="toggleRecipeDetails(${index})">
                                <div class="recipe-name">${recipe.nombre}</div>
                                <div class="recipe-cals">${recipe.calorias_aprox} kcal</div>
                            </div>
                            <div id="recipe-${index}" class="recipe-details" style="display: none;">
                                <h3>Ingredientes:</h3>
                                <ul>
                                    ${recipe.ingredientes.map(ing => `<li>${ing}</li>`).join('')}
                                </ul>
                                <h3>Instrucciones:</h3>
                                <ul>
                                    ${recipe.instrucciones.map(inst => `<li>${inst}</li>`).join('')}
                                </ul>
                                <p><strong>Calorías aproximadas:</strong> ${recipe.calorias_aprox} kcal</p>
                            </div>
                        `;
                    });
                    
                    document.getElementById('recipes-result').innerHTML = html;
                } catch (error) {
                    document.getElementById('recipes-result').innerHTML = '<div class="error">Error al cargar las recetas.</div>';
                }
            }
            
            function toggleRecipeDetails(index) {
                const details = document.getElementById(`recipe-${index}`);
                details.style.display = details.style.display === 'none' ? 'block' : 'none';
            }
            
            // Permitir buscar con Enter
            document.addEventListener('DOMContentLoaded', function() {
                document.getElementById('food-input').addEventListener('keypress', function(event) {
                    if (event.key === 'Enter') {
                        searchCalories();
                    }
                });
            });
        </script>
    </body>
    </html>
    """

@app.get("/api/calories")
async def get_calories(food: str):
    """API para buscar calorías de un alimento."""
    for item in calories_data.get('alimentos', []):
        if food.lower() in item['nombre'].lower():
            return {"found": True, **item}
    return {"found": False, "message": f"No se encontró información para '{food}'"}

@app.get("/api/recipes")
async def get_recipes():
    """API para obtener todas las recetas."""
    return recipes_data

@app.get("/api/recipes/{recipe_index}")
async def get_recipe(recipe_index: int):
    """API para obtener una receta específica."""
    recipes = recipes_data.get('recetas', [])
    if 0 <= recipe_index < len(recipes):
        return {"found": True, **recipes[recipe_index]}
    return {"found": False, "message": "Receta no encontrada"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
