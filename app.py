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
NUTRITION_KNOWLEDGE_PATH = "data/nutrition_knowledge.json"

ORDINALES = {
    "primera": 1,
    "primero": 1,
    "segunda": 2,
    "segundo": 2,
    "tercera": 3,
    "tercero": 3,
    "cuarta": 4,
    "cuarto": 4,
    "quinta": 5,
    "quinto": 5,
    "ultima": -1,
    "ultimo": -1,
}

MEDICAL_RISK_KEYWORDS = {
    "diabetes",
    "embarazo",
    "embarazada",
    "renal",
    "rinon",
    "hipertension",
    "alergia",
    "medicacion",
    "trigliceridos",
    "colesterol",
    "trastorno alimentario",
    "anemia",
}


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
        "esa",
        "ese",
        "esta",
        "este",
    }
    return [t for t in normalizar_texto(texto).split() if len(t) > 2 and t not in stopwords]


def construir_lista_html(items, limit=3):
    return "".join(f"- {item}<br>" for item in items[:limit])


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
    pasos = "".join(f"{i}. {paso}<br>" for i, paso in enumerate(receta["instrucciones"][:5], 1))
    return (
        f"<strong>{receta['nombre']}</strong><br><br>"
        f"Es una opcion de unas <strong>{receta['calorias_aprox']} kcal</strong> aproximadamente.<br><br>"
        f"<strong>Ingredientes:</strong><br>{ingredientes}<br>"
        f"<strong>Preparacion:</strong><br>{pasos}"
    )


def formatear_ingredientes_receta(receta):
    ingredientes = "".join(f"- {ing}<br>" for ing in receta["ingredientes"][:10])
    return f"<strong>Ingredientes de {receta['nombre']}:</strong><br><br>{ingredientes}"


def formatear_preparacion_receta(receta):
    pasos = "".join(f"{i}. {paso}<br>" for i, paso in enumerate(receta["instrucciones"][:8], 1))
    return f"<strong>Asi se prepara {receta['nombre']}:</strong><br><br>{pasos}"


def explicar_capacidades():
    return """Hola. Soy <strong>NutriGPT</strong>.

Puedo ayudarte con:

<strong>Recetas</strong><br>
- \"Que puedo cocinar con pollo y espinacas\"<br>
- \"Dame una cena alta en proteina\"<br><br>

<strong>Calorias</strong><br>
- \"Cuantas calorias tiene el arroz\"<br>
- \"Cuantas calorias tienen 250 g de salmon\"<br><br>

<strong>Nutricion practica</strong><br>
- \"La avena es buena para desayunar?\"<br>
- \"Que me conviene para perder grasa sin pasar hambre?\"<br><br>

Despues de darte recetas, puedes seguir con \"la 2\", \"dame ingredientes\" o \"como se hace\"."""


def es_pregunta_sobre_receta(texto_normalizado):
    pistas = [
        "la receta",
        "esa receta",
        "ese plato",
        "esa opcion",
        "la opcion",
        "ingredientes",
        "como se hace",
        "preparacion",
        "pasos",
        "primera",
        "segunda",
        "tercera",
        "cuarta",
        "quinta",
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
    return [recipes_by_id[recipe_id] for recipe_id in recipe_ids if recipe_id in recipes_by_id]


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
        "esa" in texto_normalizado
        or "ese" in texto_normalizado
        or "receta" in texto_normalizado
        or "ingredientes" in texto_normalizado
        or "pasos" in texto_normalizado
        or "preparacion" in texto_normalizado
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
            keyword_normalizado = normalizar_texto(keyword)
            if keyword_normalizado and keyword_normalizado in texto_normalizado:
                score += 2
        if score > 0:
            resultados.append((score, topic))
    resultados.sort(key=lambda item: -item[0])
    return [topic for _, topic in resultados[:3]]


def buscar_perfil_alimento(texto, alimento=""):
    candidatos = [texto, alimento]
    candidatos_normalizados = [normalizar_texto(c) for c in candidatos if c]

    for profile in nutrition_knowledge.get("food_profiles", []):
        aliases = [normalizar_texto(profile["name"])] + [
            normalizar_texto(alias) for alias in profile.get("aliases", [])
        ]
        for candidato in candidatos_normalizados:
            for alias in aliases:
                if alias and (alias in candidato or candidato in alias):
                    return profile
    return None


def detectar_riesgo_medico(texto):
    texto_normalizado = normalizar_texto(texto)
    return any(normalizar_texto(keyword) in texto_normalizado for keyword in MEDICAL_RISK_KEYWORDS)


def pide_macros_exactos(texto):
    texto_normalizado = normalizar_texto(texto)
    pistas = [
        "cuanta proteina",
        "cuantas proteinas",
        "gramos de proteina",
        "cuanta fibra",
        "cuantos carbohidratos",
        "macros",
    ]
    return any(pista in texto_normalizado for pista in pistas)


def responder_nutricion(mensaje, analisis):
    texto_normalizado = normalizar_texto(mensaje)
    perfil = buscar_perfil_alimento(mensaje, analisis.get("alimento", ""))
    temas = buscar_temas_nutricion(mensaje)
    partes = []

    if perfil:
        partes.append(f"Si te refieres a <strong>{perfil['name']}</strong>, diria que {perfil['summary']}")
        alimento_info = buscar_alimento(perfil["name"])
        if alimento_info:
            partes.append(
                f"<br><br>A nivel energetico, suele rondar las <strong>{alimento_info['calorias']} kcal</strong> por {alimento_info['unidad']}."
            )
        if pide_macros_exactos(mensaje):
            partes.append(
                "<br><br>No tengo el dato exacto de gramos de proteina o fibra en esta base, pero si una orientacion practica bastante util."
            )
        if perfil.get("highlights"):
            partes.append(
                "<br><strong>Lo mas util en la practica:</strong><br>"
                + construir_lista_html(perfil["highlights"], limit=3)
            )
        if perfil.get("watchouts"):
            partes.append(f"<br><strong>Ten en cuenta:</strong> {perfil['watchouts']}")

    if temas:
        tema_principal = temas[0]
        if not perfil:
            partes.append(tema_principal["summary"])
        partes.append(
            "<br><br><strong>En la practica, te puede ayudar:</strong><br>"
            + construir_lista_html(tema_principal["tips"], limit=3)
        )

    if not perfil and not temas:
        partes.append(
            "Si quieres comer mejor sin complicarte demasiado, la base suele ser bastante simple: una fuente de proteina, "
            "fruta o verdura a diario, alimentos poco procesados y cantidades que puedas sostener en el tiempo."
        )
        partes.append(
            "Una forma muy util de pensarlo es montar cada comida con tres piezas: proteina, vegetal o fruta y un carbohidrato ajustado a tu actividad."
        )

    if detectar_riesgo_medico(texto_normalizado):
        partes.append(
            "<br>Si hay una condicion medica, embarazo, medicacion o un problema digestivo importante, conviene personalizarlo con un profesional."
        )

    partes.append(
        "<br><br>Si quieres, te lo adapto a un objetivo concreto: <em>perder grasa</em>, <em>ganar musculo</em>, "
        "<em>desayuno</em>, <em>cena</em> o <em>comida pre/post entreno</em>."
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
            contexto["last_recipe_ids"] = [receta["id"] for receta in recetas_top]
            contexto["last_selected_recipe_id"] = recetas_top[0]["id"]

            if len(recetas_top) == 1 or "detalle" in texto_normalizado or "ingredientes" in texto_normalizado:
                return {
                    "respuesta": formatear_detalle_receta(recetas_top[0]),
                    "contexto": contexto,
                }

            partes = ["Estas son las opciones que mejor encajan con lo que me has pedido:<br><br>"]
            for i, receta in enumerate(recetas_top, 1):
                contenido = normalizar_texto(" ".join([receta["nombre"]] + receta["ingredientes"]))
                coincidencias = [t for t in terminos if normalizar_texto(t) in contenido]
                motivo = f" Me encaja por: {', '.join(coincidencias[:3])}." if coincidencias else ""
                partes.append(
                    f"<strong>{i}. {receta['nombre']}</strong> ({receta['calorias_aprox']} kcal).{motivo}<br>"
                )
            partes.append(
                "<br>Ahora puedes seguir con <em>la 2</em>, <em>la primera</em>, <em>dame los ingredientes de la 3</em> "
                "o <em>como se hace la receta 1</em>."
            )
            return {"respuesta": "".join(partes), "contexto": contexto}

        termino_busqueda = ", ".join(terminos) if terminos else "tu consulta"
        return {
            "respuesta": (
                f"No he encontrado recetas claras con <strong>{termino_busqueda}</strong>.<br><br>"
                "Si quieres, dime uno o dos ingredientes principales o el objetivo de la comida, por ejemplo "
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
            partes = [
                f"<strong>{principal['nombre']}</strong><br><br>",
                f"Suele rondar las <strong>{principal['calorias']} kcal</strong> por {principal['unidad']}.<br>",
            ]

            calorias_estimadas = calcular_calorias_estimadas(principal, cantidad)
            if calorias_estimadas is not None:
                partes.append(
                    f"Para la cantidad que indicas ({cantidad['valor']} {cantidad['unidad']}), el estimado seria "
                    f"<strong>{calorias_estimadas} kcal</strong>.<br>"
                )

            if len(candidatos) > 1:
                partes.append(
                    "<br>Tambien podria encajar con: "
                    + ", ".join(item["nombre"] for item in candidatos[1:4])
                    + "."
                )

            partes.append("<br><br>Si quieres, tambien puedo explicarte si este alimento encaja mejor para saciedad, deporte o una comida mas ligera.")
            return {"respuesta": "".join(partes), "contexto": contexto}

        return {
            "respuesta": (
                "No encuentro ese alimento en mi base de datos.<br><br>"
                "Prueba con un nombre mas concreto, por ejemplo: <em>pechuga de pollo</em>, "
                "<em>arroz blanco</em>, <em>salmon</em> o <em>manzana</em>."
            ),
            "contexto": contexto,
        }

    if intencion == "nutricion" or buscar_temas_nutricion(mensaje) or buscar_perfil_alimento(mensaje, alimento):
        return {
            "respuesta": responder_nutricion(mensaje, analisis),
            "contexto": contexto,
        }

    return {
        "respuesta": (
            "No he terminado de entender lo que buscas.<br><br>"
            "Puedo ayudarte con recetas, calorias o nutricion practica. Por ejemplo:<br>"
            "- <em>Que puedo cocinar con pollo y espinacas</em><br>"
            "- <em>Cuantas calorias tiene el arroz</em><br>"
            "- <em>La avena es buena para desayunar?</em>"
        ),
        "contexto": contexto,
    }


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
                font-family: Georgia, "Times New Roman", serif;
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
                    <p>Recetas, nutricion practica y respuestas mas naturales.</p>
                </div>
                <div class="messages" id="messages">
                    <div class="message">
                        <div class="bubble">
                            Soy <strong>NutriGPT</strong>.<br><br>
                            Puedo ayudarte con recetas, calorias y dudas de nutricion.<br>
                            Prueba algo como:<br>
                            - <em>Que puedo cocinar con pollo y arroz</em><br>
                            - <em>La avena es buena para desayunar?</em><br>
                            - <em>Que me conviene para perder grasa sin pasar hambre?</em>
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
            let chatContext = { last_recipe_ids: [], last_selected_recipe_id: null };

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
                        body: JSON.stringify({ mensaje: message, contexto: chatContext })
                    });
                    const data = await response.json();
                    typing.remove();
                    if (data.contexto) {
                        chatContext = data.contexto;
                    }
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
