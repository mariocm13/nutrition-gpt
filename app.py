from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import os
import re
import unicodedata

import requests

from nlp_processor import NLPProcessor

app = FastAPI(title="NutriGPT - Asistente de Nutricion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = NLPProcessor()

DRIVE_FILE_ID = "1pMn-MyxfEaag0rzZbwYSzSciYnRDOodw"
CALORIES_DATA_PATH = "data/calories.json"
RECIPES_DATA_PATH = "data/recipes_large.json"


def normalizar_texto(texto):
    texto = texto.lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def tokens_relevantes(texto):
    stopwords = {
        "de",
        "del",
        "la",
        "el",
        "los",
        "las",
        "con",
        "sin",
        "para",
        "por",
        "un",
        "una",
        "y",
        "o",
        "que",
        "en",
    }
    return [t for t in normalizar_texto(texto).split() if len(t) > 2 and t not in stopwords]


def load_recipes_from_drive():
    """Carga las recetas desde Google Drive."""
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


def load_calories():
    """Carga datos de calorias localmente."""
    if os.path.exists(CALORIES_DATA_PATH):
        with open(CALORIES_DATA_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"alimentos": []}


recipes_db = load_recipes_from_drive()
calories_db = load_calories()


def buscar_recetas(terminos):
    """Busca recetas por nombre o ingredientes con un ranking simple."""
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
    """Busca alimentos por coincidencia exacta, parcial y por tokens."""
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
        return None

    calorias_base = alimento_info["calorias"]
    unidad_base = normalizar_texto(alimento_info["unidad"])
    unidad = normalizar_texto(unidad)

    if "100g" in unidad_base:
        if unidad in {"g", "gramo", "gramos"}:
            return round((calorias_base * valor) / 100, 1)
        if unidad == "kg":
            return round(calorias_base * valor * 10, 1)

    return None


def formatear_detalle_receta(receta):
    ingredientes = "".join(f"- {ing}<br>" for ing in receta["ingredientes"][:8])
    pasos = "".join(f"{i}. {paso}<br>" for i, paso in enumerate(receta["instrucciones"][:4], 1))
    return (
        f"<strong>{receta['nombre']}</strong><br><br>"
        f"<strong>Calorias aproximadas:</strong> {receta['calorias_aprox']} kcal<br><br>"
        f"<strong>Ingredientes:</strong><br>{ingredientes}<br>"
        f"<strong>Pasos principales:</strong><br>{pasos}"
    )


def explicar_capacidades():
    return """Hola. Soy <strong>NutriGPT</strong>.

Puedo ayudarte con:

<strong>Recetas</strong><br>
- \"Que puedo cocinar con pollo y espinacas\"<br>
- \"Dame una cena alta en proteina\"<br><br>

<strong>Calorias e informacion nutricional basica</strong><br>
- \"Cuantas calorias tiene el arroz\"<br>
- \"Cuantas calorias tienen 250 g de salmon\"<br><br>

<strong>Consejo</strong><br>
Si me das un alimento, una cantidad o varios ingredientes, suelo responder mejor."""


def generar_respuesta(mensaje):
    """Genera una respuesta conversacional segun la intencion detectada."""
    analisis = nlp.procesar(mensaje)
    intencion = analisis["intencion"]
    palabras_clave = analisis["palabras_clave"]
    ingredientes = analisis["ingredientes"]
    alimento = analisis["alimento"]
    cantidad = analisis["cantidad"]
    texto_normalizado = normalizar_texto(mensaje)

    if intencion == "ayuda":
        return explicar_capacidades()

    if intencion == "recetas":
        terminos = ingredientes if ingredientes else palabras_clave
        recetas = buscar_recetas(terminos)

        if recetas:
            if len(recetas) == 1 or "detalle" in texto_normalizado or "ingredientes" in texto_normalizado:
                return formatear_detalle_receta(recetas[0])

            partes = [f"Encontre {len(recetas)} receta(s) que encajan con tu consulta:<br><br>"]
            for i, receta in enumerate(recetas[:5], 1):
                contenido = normalizar_texto(" ".join([receta["nombre"]] + receta["ingredientes"]))
                coincidencias = [t for t in terminos if normalizar_texto(t) in contenido]
                motivo = f" Coincide con: {', '.join(coincidencias[:3])}." if coincidencias else ""
                partes.append(
                    f"<strong>{i}. {receta['nombre']}</strong> ({receta['calorias_aprox']} kcal).{motivo}<br>"
                )
            partes.append(
                "<br>Si quieres, te doy el detalle de una receta concreta o te busco opciones mas ligeras o mas proteicas."
            )
            return "".join(partes)

        termino_busqueda = ", ".join(terminos) if terminos else "tu consulta"
        return (
            f"No encontre recetas claras con <strong>{termino_busqueda}</strong>.<br><br>"
            "Prueba con 1 o 2 ingredientes principales, por ejemplo: <em>pollo y arroz</em>, "
            "<em>salmon</em> o <em>desayuno con avena</em>."
        )

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
            partes = [
                f"<strong>{principal['nombre']}</strong><br><br>",
                f"<strong>{principal['calorias']} kcal</strong> por {principal['unidad']}.<br>",
            ]

            calorias_estimadas = calcular_calorias_estimadas(principal, cantidad)
            if calorias_estimadas is not None:
                partes.append(
                    f"Para la cantidad indicada ({cantidad['valor']} {cantidad['unidad']}), el estimado es "
                    f"<strong>{calorias_estimadas} kcal</strong>.<br>"
                )

            if len(candidatos) > 1:
                partes.append(
                    "<br>Tambien podria referirte a: "
                    + ", ".join(item["nombre"] for item in candidatos[1:4])
                    + "."
                )

            partes.append("<br><br>Si quieres, tambien puedo sugerirte recetas con este alimento.")
            return "".join(partes)

        return (
            "No encontre ese alimento en mi base de datos.<br><br>"
            "Prueba con un nombre mas concreto, por ejemplo: <em>pechuga de pollo</em>, "
            "<em>arroz blanco</em>, <em>salmon</em> o <em>manzana</em>."
        )

    return (
        "No he entendido del todo tu consulta.<br><br>"
        "Puedo ayudarte con recetas y calorias. Prueba algo como:<br>"
        "- <em>Que puedo cocinar con pollo y espinacas</em><br>"
        "- <em>Cuantas calorias tienen 200 g de arroz</em>"
    )


@app.get("/", response_class=HTMLResponse)
async def get_home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NutriGPT - Asistente de Nutricion</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            :root {
                --bg: #f6f1e8;
                --panel: #fffaf2;
                --line: #d7c9b0;
                --text: #2f2419;
                --muted: #6b5a46;
                --accent: #b85c38;
                --accent-2: #355c4b;
            }
            * { box-sizing: border-box; }
            body {
                margin: 0;
                font-family: Georgia, \"Times New Roman\", serif;
                background:
                    radial-gradient(circle at top left, rgba(184, 92, 56, 0.12), transparent 30%),
                    radial-gradient(circle at bottom right, rgba(53, 92, 75, 0.14), transparent 35%),
                    var(--bg);
                color: var(--text);
            }
            .layout {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }
            .chat-shell {
                width: min(980px, 100%);
                height: min(90vh, 860px);
                display: grid;
                grid-template-rows: auto 1fr auto;
                background: rgba(255, 250, 242, 0.92);
                border: 1px solid var(--line);
                border-radius: 28px;
                overflow: hidden;
                box-shadow: 0 30px 80px rgba(47, 36, 25, 0.14);
                backdrop-filter: blur(12px);
            }
            .header {
                padding: 28px 28px 18px;
                border-bottom: 1px solid var(--line);
                background: linear-gradient(135deg, rgba(184, 92, 56, 0.08), rgba(53, 92, 75, 0.1));
            }
            .header h1 {
                margin: 0 0 8px;
                font-size: clamp(30px, 5vw, 42px);
                line-height: 1;
            }
            .header p {
                margin: 0;
                color: var(--muted);
                font-size: 15px;
            }
            .messages {
                padding: 24px;
                overflow-y: auto;
            }
            .message {
                display: flex;
                margin-bottom: 16px;
            }
            .message.user { justify-content: flex-end; }
            .bubble {
                max-width: min(760px, 82%);
                padding: 14px 16px;
                border-radius: 20px;
                line-height: 1.5;
                font-size: 16px;
                border: 1px solid var(--line);
                background: var(--panel);
            }
            .user .bubble {
                background: linear-gradient(135deg, var(--accent), #cf7a4f);
                color: white;
                border-color: transparent;
            }
            .composer {
                padding: 18px;
                border-top: 1px solid var(--line);
                background: rgba(255,255,255,0.55);
            }
            .row {
                display: flex;
                gap: 12px;
            }
            input {
                flex: 1;
                border: 1px solid var(--line);
                border-radius: 18px;
                padding: 14px 16px;
                font-size: 16px;
                background: #fffdf8;
                color: var(--text);
                outline: none;
            }
            input:focus {
                border-color: var(--accent);
                box-shadow: 0 0 0 3px rgba(184, 92, 56, 0.12);
            }
            button {
                border: none;
                border-radius: 18px;
                padding: 14px 20px;
                font-size: 15px;
                font-weight: 700;
                cursor: pointer;
                color: white;
                background: linear-gradient(135deg, var(--accent-2), #4b7f68);
            }
            .typing {
                opacity: 0.75;
                font-style: italic;
                color: var(--muted);
            }
            @media (max-width: 720px) {
                .layout { padding: 0; }
                .chat-shell {
                    height: 100vh;
                    border-radius: 0;
                }
                .bubble { max-width: 90%; }
                .row { flex-direction: column; }
                button { width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="layout">
            <div class="chat-shell">
                <div class="header">
                    <h1>NutriGPT</h1>
                    <p>Recetas, calorias y respuestas mas utiles con lenguaje natural.</p>
                </div>
                <div class="messages" id="messages">
                    <div class="message">
                        <div class="bubble">
                            Soy <strong>NutriGPT</strong>.<br><br>
                            Puedo ayudarte con recetas y calorias.<br>
                            Prueba algo como:<br>
                            - <em>Que puedo cocinar con pollo y arroz</em><br>
                            - <em>Cuantas calorias tienen 250 g de salmon</em>
                        </div>
                    </div>
                </div>
                <div class="composer">
                    <div class="row">
                        <input id="message-input" type="text" placeholder="Escribe tu pregunta..." autocomplete="off">
                        <button id="send-btn">Enviar</button>
                    </div>
                </div>
            </div>
        </div>
        <script>
            const messagesDiv = document.getElementById("messages");
            const input = document.getElementById("message-input");
            const button = document.getElementById("send-btn");

            function addMessage(text, isUser = false, extraClass = "") {
                const message = document.createElement("div");
                message.className = `message ${isUser ? "user" : ""} ${extraClass}`.trim();
                const bubble = document.createElement("div");
                bubble.className = "bubble";
                bubble.innerHTML = text;
                message.appendChild(bubble);
                messagesDiv.appendChild(message);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                return message;
            }

            async function sendMessage() {
                const message = input.value.trim();
                if (!message) return;

                addMessage(message, true);
                input.value = "";

                const typing = addMessage("NutriGPT esta pensando...", false, "typing");

                try {
                    const response = await fetch("/api/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ mensaje: message })
                    });
                    const data = await response.json();
                    typing.remove();
                    addMessage(data.respuesta, false);
                } catch (error) {
                    typing.remove();
                    addMessage("No pude procesar tu mensaje. Intentalo de nuevo.", false);
                }
            }

            input.addEventListener("keypress", (event) => {
                if (event.key === "Enter") sendMessage();
            });
            button.addEventListener("click", sendMessage);
        </script>
    </body>
    </html>
    """


@app.post("/api/chat")
async def chat(data: dict):
    mensaje = data.get("mensaje", "")
    return {"respuesta": generar_respuesta(mensaje)}


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
