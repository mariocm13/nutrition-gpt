from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import requests
import re
from typing import Optional

app = FastAPI(title="NutriGPT - Asistente de Nutrición")

# Agregar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Google Drive
DRIVE_FILE_ID = "1pMn-MyxfEaag0rzZbwYSzSciYnRDOodw"
CALORIES_DATA_PATH = 'data/calories.json'

def load_recipes_from_drive():
    """Carga las recetas desde Google Drive."""
    url = f"https://docs.google.com/uc?export=download&id={DRIVE_FILE_ID}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error cargando desde Drive: {e}")
    return {"recetas": []}

def load_calories():
    """Carga datos de calorías localmente."""
    if os.path.exists(CALORIES_DATA_PATH):
        with open(CALORIES_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"alimentos": []}

# Carga inicial
recipes_db = load_recipes_from_drive()
calories_db = load_calories()

def buscar_recetas(termino):
    """Busca recetas por nombre o ingredientes."""
    termino = termino.lower()
    resultados = []
    for receta in recipes_db.get('recetas', []):
        if (termino in receta['nombre'].lower() or 
            any(termino in ing.lower() for ing in receta['ingredientes'])):
            resultados.append(receta)
    return resultados[:10]  # Limitar a 10 resultados

def buscar_alimento(termino):
    """Busca información de calorías de un alimento."""
    termino = termino.lower()
    for alimento in calories_db.get('alimentos', []):
        if termino in alimento['nombre'].lower():
            return alimento
    return None

def generar_respuesta(mensaje):
    """Genera una respuesta conversacional basada en el mensaje del usuario."""
    mensaje_lower = mensaje.lower()
    
    # Detectar intención: búsqueda de recetas
    if any(palabra in mensaje_lower for palabra in ['receta', 'puedo hacer', 'cómo hago', 'quiero', 'busco', 'dame', 'muestra', 'con']):
        # Extraer ingredientes principales
        palabras_clave = re.findall(r'\b\w+\b', mensaje_lower)
        recetas = buscar_recetas(' '.join(palabras_clave))
        
        if recetas:
            respuesta = f"🍳 Encontré {len(recetas)} receta(s) que te podrían interesar:\n\n"
            for i, receta in enumerate(recetas[:5], 1):
                respuesta += f"**{i}. {receta['nombre']}** ({receta['calorias_aprox']} kcal)\n"
            respuesta += "\n¿Te gustaría conocer los detalles de alguna receta? Pregúntame por el número o el nombre."
            return respuesta
        else:
            return "No encontré recetas con esos ingredientes. 😕 ¿Podrías ser más específico? Por ejemplo: 'Recetas con pollo' o 'Qué puedo hacer con arroz'."
    
    # Detectar intención: búsqueda de calorías
    elif any(palabra in mensaje_lower for palabra in ['calorías', 'calorias', 'cuántas calorías', 'cuantas calorias', 'valor nutricional', 'energía', 'kcal']):
        palabras_clave = re.findall(r'\b\w+\b', mensaje_lower)
        for palabra in palabras_clave:
            alimento = buscar_alimento(palabra)
            if alimento:
                return f"📊 **{alimento['nombre']}**\n\n🔥 Calorías: **{alimento['calorias']} kcal** por {alimento['unidad']}\n\nEsta información es por cada {alimento['unidad']}. ¿Hay algo más que quieras saber?"
        
        return "No encontré información de calorías para ese alimento. 🤔 Intenta con alimentos comunes como 'pollo', 'manzana', 'arroz', etc."
    
    # Detectar intención: información general
    elif any(palabra in mensaje_lower for palabra in ['hola', 'qué puedes', 'ayuda', 'cómo funciona', 'cuéntame']):
        return """👋 ¡Hola! Soy **NutriGPT**, tu asistente de nutrición inteligente.

Puedo ayudarte de varias formas:

🍽️ **Buscar Recetas**: Pregúntame "¿Qué puedo hacer con pollo?" o "Recetas con verduras"
🔥 **Calorías**: Pregúntame "¿Cuántas calorías tiene una manzana?"
📋 **Información Nutricional**: Dime el nombre de un alimento y te diré sus calorías

Tengo acceso a **1000+ recetas** y una base de datos nutricional completa. ¿En qué puedo ayudarte?"""
    
    # Respuesta por defecto
    else:
        return """No estoy seguro de lo que preguntas. 🤔

Puedo ayudarte con:
- 🍽️ Buscar recetas (ej: "Recetas con pollo")
- 🔥 Información de calorías (ej: "¿Cuántas calorías tiene un huevo?")
- 📋 Detalles nutricionales de alimentos

¿Qué te gustaría saber?"""

@app.get("/", response_class=HTMLResponse)
async def get_home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NutriGPT - Asistente de Nutrición</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
            .chat-container { display: flex; flex-direction: column; height: 100vh; }
            .messages-container { flex: 1; overflow-y: auto; padding: 20px; }
            .message { margin-bottom: 16px; animation: slideIn 0.3s ease; }
            @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            .user-message { display: flex; justify-content: flex-end; }
            .user-message .bubble { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .bot-message { display: flex; justify-content: flex-start; }
            .bot-message .bubble { background: #f0f0f0; color: #333; }
            .bubble { max-width: 70%; padding: 12px 16px; border-radius: 18px; word-wrap: break-word; line-height: 1.4; }
            .input-area { padding: 20px; background: white; border-top: 1px solid #e0e0e0; }
            .input-group { display: flex; gap: 10px; }
            #message-input { flex: 1; padding: 12px 16px; border: 1px solid #ddd; border-radius: 24px; outline: none; transition: all 0.3s; }
            #message-input:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
            #send-btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 12px 24px; border-radius: 24px; cursor: pointer; font-weight: 600; transition: transform 0.2s; }
            #send-btn:hover { transform: scale(1.05); }
            #send-btn:active { transform: scale(0.95); }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
            .header h1 { margin: 0; font-size: 24px; font-weight: bold; }
            .header p { margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }
            .typing { display: flex; gap: 4px; align-items: center; }
            .typing span { width: 8px; height: 8px; background: #999; border-radius: 50%; animation: typing 1.4s infinite; }
            .typing span:nth-child(2) { animation-delay: 0.2s; }
            .typing span:nth-child(3) { animation-delay: 0.4s; }
            @keyframes typing { 0%, 60%, 100% { opacity: 0.3; } 30% { opacity: 1; } }
            .recipe-link { color: #667eea; cursor: pointer; text-decoration: underline; }
            .recipe-link:hover { text-decoration: none; }
        </style>
    </head>
    <body class="bg-gray-100">
        <div class="chat-container">
            <div class="header">
                <h1><i class="fas fa-utensils mr-2"></i>NutriGPT</h1>
                <p>Tu asistente de nutrición inteligente • 1000+ recetas</p>
            </div>

            <div class="messages-container" id="messages">
                <div class="message bot-message">
                    <div class="bubble">
                        👋 ¡Hola! Soy <strong>NutriGPT</strong>, tu asistente de nutrición. Puedo ayudarte a:
                        <br><br>
                        🍽️ <strong>Buscar recetas</strong> - Pregúntame "¿Qué puedo hacer con pollo?"
                        <br>🔥 <strong>Calorías</strong> - Pregúntame "¿Cuántas calorías tiene una manzana?"
                        <br>📋 <strong>Información nutricional</strong> - Dime un alimento
                        <br><br>
                        ¿En qué puedo ayudarte hoy?
                    </div>
                </div>
            </div>

            <div class="input-area">
                <div class="input-group">
                    <input type="text" id="message-input" placeholder="Escribe tu pregunta aquí..." autocomplete="off">
                    <button id="send-btn" onclick="sendMessage()"><i class="fas fa-paper-plane mr-2"></i>Enviar</button>
                </div>
            </div>
        </div>

        <script>
            const messagesDiv = document.getElementById('messages');
            const input = document.getElementById('message-input');
            const sendBtn = document.getElementById('send-btn');

            function scrollToBottom() {
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            function addMessage(text, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.innerHTML = text;
                messageDiv.appendChild(bubble);
                messagesDiv.appendChild(messageDiv);
                scrollToBottom();
            }

            function showTyping() {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message bot-message';
                messageDiv.id = 'typing-indicator';
                const bubble = document.createElement('div');
                bubble.className = 'bubble';
                bubble.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
                messageDiv.appendChild(bubble);
                messagesDiv.appendChild(messageDiv);
                scrollToBottom();
            }

            function removeTyping() {
                const typing = document.getElementById('typing-indicator');
                if (typing) typing.remove();
            }

            async function sendMessage() {
                const message = input.value.trim();
                if (!message) return;

                addMessage(message, true);
                input.value = '';
                input.focus();

                showTyping();

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mensaje: message })
                    });
                    const data = await response.json();
                    removeTyping();
                    addMessage(data.respuesta, false);
                } catch (error) {
                    removeTyping();
                    addMessage('❌ Error al procesar tu mensaje. Intenta de nuevo.', false);
                }
            }

            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });

            sendBtn.addEventListener('click', sendMessage);
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def chat(data: dict):
    """Endpoint para procesar mensajes de chat."""
    mensaje = data.get('mensaje', '')
    respuesta = generar_respuesta(mensaje)
    return {"respuesta": respuesta}

@app.get("/api/recipes")
async def get_recipes():
    """Endpoint para obtener todas las recetas."""
    return recipes_db

@app.get("/api/calories")
async def get_calories(food: str):
    """Endpoint para buscar calorías de un alimento."""
    alimento = buscar_alimento(food)
    if alimento:
        return {"found": True, **alimento}
    return {"found": False}

@app.get("/api/stats")
async def get_stats():
    """Endpoint para obtener estadísticas."""
    return {
        "total_recetas": len(recipes_db.get('recetas', [])),
        "total_alimentos": len(calories_db.get('alimentos', []))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
