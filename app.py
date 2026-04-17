from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import requests
import re
from typing import Optional
from nlp_processor import NLPProcessor

app = FastAPI(title="NutriGPT - Asistente de Nutrición")

# Agregar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar procesador NLP
nlp = NLPProcessor()

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
    return resultados[:10]

def buscar_alimento(termino):
    """Busca información de calorías de un alimento."""
    termino = termino.lower()
    for alimento in calories_db.get('alimentos', []):
        if termino in alimento['nombre'].lower():
            return alimento
    return None

def generar_respuesta(mensaje):
    """Genera una respuesta conversacional inteligente."""
    # Procesar el mensaje con NLP
    analisis = nlp.procesar(mensaje)
    intencion = analisis['intencion']
    palabras_clave = analisis['palabras_clave']
    ingredientes = analisis['ingredientes']
    alimento = analisis['alimento']
    
    # Responder según la intención detectada
    if intencion == 'recetas':
        # Buscar recetas con los ingredientes/palabras clave
        termino_busqueda = ' '.join(ingredientes) if ingredientes else ' '.join(palabras_clave)
        
        if termino_busqueda:
            recetas = buscar_recetas(termino_busqueda)
            
            if recetas:
                respuesta = f"🍳 Encontré {len(recetas)} receta(s) deliciosa(s) para ti:\n\n"
                for i, receta in enumerate(recetas[:5], 1):
                    respuesta += f"**{i}. {receta['nombre']}** ({receta['calorias_aprox']} kcal)\n"
                respuesta += "\n¿Te gustaría conocer los detalles de alguna? Pregúntame por el nombre."
                return respuesta
            else:
                return f"Hmm, no encontré recetas con '{termino_busqueda}'. 🤔\n\nIntenta con ingredientes más comunes como 'pollo', 'arroz', 'verduras', etc."
        else:
            return "¿Qué ingredientes tienes en mente? Dime qué te gustaría cocinar y te sugiero recetas. 👨‍🍳"
    
    elif intencion == 'calorias':
        # Buscar información de calorías
        if alimento:
            alimento_info = buscar_alimento(alimento)
            if alimento_info:
                return f"📊 **{alimento_info['nombre']}**\n\n🔥 Calorías: **{alimento_info['calorias']} kcal** por {alimento_info['unidad']}\n\nEsta información es por cada {alimento_info['unidad']}. ¿Hay algo más que quieras saber?"
        
        # Si no encontró el alimento específico, buscar en las palabras clave
        for palabra in palabras_clave:
            alimento_info = buscar_alimento(palabra)
            if alimento_info:
                return f"📊 **{alimento_info['nombre']}**\n\n🔥 Calorías: **{alimento_info['calorias']} kcal** por {alimento_info['unidad']}\n\nEsta información es por cada {alimento_info['unidad']}. ¿Hay algo más que quieras saber?"
        
        return "No encontré información de calorías para ese alimento. 🤔\n\nIntenta con alimentos comunes como 'pollo', 'manzana', 'arroz', 'huevo', etc."
    
    elif intencion == 'ayuda':
        return """👋 ¡Hola! Soy **NutriGPT**, tu asistente de nutrición inteligente.

Puedo ayudarte de varias formas:

🍽️ **Buscar Recetas** 
   - "¿Qué puedo hacer con pollo?"
   - "Recetas con verduras"
   - "Cómo preparo un desayuno saludable"

🔥 **Información de Calorías**
   - "¿Cuántas calorías tiene una manzana?"
   - "Calorías del salmón"
   - "Valor nutricional del arroz"

📋 **Información Nutricional**
   - Dime el nombre de un alimento y te daré sus calorías

Tengo acceso a **1000+ recetas** y una base de datos nutricional completa. ¿En qué puedo ayudarte?"""
    
    else:
        # Respuesta por defecto para intenciones no claras
        return """No estoy completamente seguro de lo que preguntas. 🤔

¿Puedo ayudarte con alguno de estos temas?

🍽️ **Recetas** - Pregúntame "¿Qué puedo hacer con...?"
🔥 **Calorías** - Pregúntame "¿Cuántas calorías tiene...?"
📋 **Nutrición** - Dime un alimento

¿Qué necesitas?"""

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
            :root {
                --bg-primary: #ffffff;
                --bg-secondary: #f0f0f0;
                --text-primary: #333333;
                --text-secondary: #666666;
                --border-color: #e0e0e0;
                --header-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }

            body.dark-mode {
                --bg-primary: #1a1a1a;
                --bg-secondary: #2d2d2d;
                --text-primary: #ffffff;
                --text-secondary: #b0b0b0;
                --border-color: #404040;
            }

            * {
                color: var(--text-primary);
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: var(--bg-primary);
                transition: background-color 0.3s ease, color 0.3s ease;
            }

            .chat-container {
                display: flex;
                flex-direction: column;
                height: 100vh;
                background-color: var(--bg-primary);
            }

            .messages-container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background-color: var(--bg-primary);
            }

            .message {
                margin-bottom: 16px;
                animation: slideIn 0.3s ease;
            }

            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .user-message {
                display: flex;
                justify-content: flex-end;
            }

            .user-message .bubble {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .bot-message {
                display: flex;
                justify-content: flex-start;
            }

            .bot-message .bubble {
                background-color: var(--bg-secondary);
                color: var(--text-primary);
                border: 1px solid var(--border-color);
            }

            .bubble {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
                line-height: 1.4;
            }

            .input-area {
                padding: 20px;
                background-color: var(--bg-primary);
                border-top: 1px solid var(--border-color);
            }

            .input-group {
                display: flex;
                gap: 10px;
            }

            #message-input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid var(--border-color);
                border-radius: 24px;
                outline: none;
                background-color: var(--bg-secondary);
                color: var(--text-primary);
                transition: all 0.3s;
            }

            #message-input:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            #message-input::placeholder {
                color: var(--text-secondary);
            }

            #send-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 24px;
                cursor: pointer;
                font-weight: 600;
                transition: transform 0.2s;
            }

            #send-btn:hover {
                transform: scale(1.05);
            }

            #send-btn:active {
                transform: scale(0.95);
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .header-title {
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }

            .header-subtitle {
                margin: 5px 0 0 0;
                font-size: 14px;
                opacity: 0.9;
            }

            .theme-toggle {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 12px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 18px;
                transition: all 0.3s;
            }

            .theme-toggle:hover {
                background: rgba(255, 255, 255, 0.3);
            }

            .typing {
                display: flex;
                gap: 4px;
                align-items: center;
            }

            .typing span {
                width: 8px;
                height: 8px;
                background: #999;
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }

            .typing span:nth-child(2) {
                animation-delay: 0.2s;
            }

            .typing span:nth-child(3) {
                animation-delay: 0.4s;
            }

            @keyframes typing {
                0%, 60%, 100% { opacity: 0.3; }
                30% { opacity: 1; }
            }

            /* Scrollbar personalizada */
            .messages-container::-webkit-scrollbar {
                width: 8px;
            }

            .messages-container::-webkit-scrollbar-track {
                background: var(--bg-secondary);
            }

            .messages-container::-webkit-scrollbar-thumb {
                background: #667eea;
                border-radius: 4px;
            }

            .messages-container::-webkit-scrollbar-thumb:hover {
                background: #764ba2;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">
                <div>
                    <h1 class="header-title"><i class="fas fa-utensils mr-2"></i>NutriGPT</h1>
                    <p class="header-subtitle">Tu asistente de nutrición inteligente • 1000+ recetas</p>
                </div>
                <button class="theme-toggle" onclick="toggleTheme()" title="Cambiar tema">
                    <i class="fas fa-moon"></i>
                </button>
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
            const html = document.documentElement;

            // Cargar tema guardado
            const savedTheme = localStorage.getItem('theme') || 'light';
            if (savedTheme === 'dark') {
                html.classList.add('dark-mode');
            }

            function toggleTheme() {
                html.classList.toggle('dark-mode');
                const theme = html.classList.contains('dark-mode') ? 'dark' : 'light';
                localStorage.setItem('theme', theme);
            }

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
    # Usar el puerto de la variable de entorno PORT (necesario para Render) o 8000 por defecto
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
