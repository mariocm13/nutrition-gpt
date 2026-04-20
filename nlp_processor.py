import re
import unicodedata
from typing import Dict, List, Optional


class NLPProcessor:
    """Procesador de lenguaje natural basado en reglas para NutrIA."""

    def __init__(self):
        self.palabras_recetas = {
            "receta", "recetas", "hacer", "preparar", "prepara",
            "cocinar", "cocino", "cocina", "plato", "platos",
            "desayuno", "almuerzo", "comida", "cena", "merienda",
            "idea", "ideas", "menu", "menus", "ingredientes",
            "cocinamos", "preparo", "hago", "puedo comer",
            "sugerencia", "sugerencias", "opciones", "combinar",
            "aprovechar", "usar", "gastar", "sobra", "sobras",
        }

        self.palabras_calorias = {
            "calorias", "kcal", "energia", "cuantas calorias",
            "cuanto tiene", "cuanto aporta", "valor energetico",
            "que tiene", "cuantos gramos", "composicion",
            "informacion nutricional", "tabla nutricional",
            "engorda", "engordar", "calorico",
        }

        self.palabras_nutricion = {
            "saludable", "sano", "sana", "proteina", "proteinas",
            "fibra", "grasa saludable", "grasas saludables",
            "hidratos", "carbohidratos", "saciedad", "dieta",
            "nutricion", "alimentacion", "adelgazar", "perder grasa",
            "perder peso", "ganar musculo", "masa muscular",
            "hidratar", "hidratacion", "desayuno saludable", "cena ligera",
            "merienda saludable", "pre entreno", "post entreno",
            "beneficios", "aporta", "sirve para", "bueno para",
            "buena para", "azucar", "ultraprocesado", "ultraprocesados",
            "colesterol", "saciante", "hambre", "antojos", "ansiedad",
            "digestivo", "estrenimiento", "omega 3", "agua",
            "deshidratacion", "macros", "macronutrientes",
            "vitaminas", "minerales", "inflamacion",
            "antioxidante", "antioxidantes", "es bueno", "es buena",
        }

        self.palabras_ayuda = {
            "hola", "buenas", "ayuda", "como funciona",
            "que puedes hacer", "quien eres", "inicio", "help",
            "buenos dias", "buenas tardes", "buenas noches",
        }

        self.stopwords = {
            "el", "la", "los", "las", "un", "una", "unos", "unas",
            "de", "del", "y", "o", "u", "a", "al", "en", "para",
            "por", "con", "sin", "que", "me", "mi", "mis", "tu",
            "tus", "quiero", "puedo", "hacer", "preparar", "prepara",
            "cocinar", "cocina", "dame", "busco", "necesito",
            "cuanto", "cuanta", "cuantas", "cuantos", "tiene",
            "tienen", "contiene", "contienen", "hay", "es", "son",
            "esa", "ese", "esta", "este", "bueno", "buena",
            "sirve", "conviene", "mejor", "recomiendas", "dime",
            "como", "sabes", "conoces", "cual", "cuales",
        }

    def _strip_accents(self, texto: str) -> str:
        return "".join(
            c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
        )

    def limpiar_texto(self, texto: str) -> str:
        texto = self._strip_accents(texto.lower())
        texto = re.sub(r"[^a-z0-9,\s]", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    def extraer_palabras_clave(self, texto: str) -> List[str]:
        texto_limpio = self.limpiar_texto(texto)
        palabras = texto_limpio.split()
        return [p for p in palabras if len(p) > 2 and p not in self.stopwords]

    def detectar_intencion(self, texto: str) -> str:
        texto_limpio = self.limpiar_texto(texto)

        puntos_recetas = sum(2 for palabra in self.palabras_recetas if palabra in texto_limpio)
        puntos_calorias = sum(2 for palabra in self.palabras_calorias if palabra in texto_limpio)
        puntos_nutricion = sum(2 for palabra in self.palabras_nutricion if palabra in texto_limpio)
        puntos_ayuda = sum(2 for palabra in self.palabras_ayuda if palabra in texto_limpio)

        if re.search(r"\b(receta|recetas|desayuno|almuerzo|comida|cena|merienda)\b", texto_limpio):
            puntos_recetas += 3

        if re.search(r"\b(calorias|kcal|energia|engorda)\b", texto_limpio):
            puntos_calorias += 4

        if re.search(
            r"\b(proteina|proteinas|fibra|dieta|nutricion|alimentacion|saludable|saciedad|hambre|omega|hidratacion|macros|vitaminas|antioxidante)\b",
            texto_limpio,
        ):
            puntos_nutricion += 4

        if re.search(r"\b(hola|buenas|ayuda)\b", texto_limpio) and len(texto_limpio.split()) <= 5:
            puntos_ayuda += 3

        if re.search(r"\b(tengo|con|usar|aprovechar|cocinar)\b", texto_limpio):
            puntos_recetas += 2

        if re.search(r"\b(que|qu[eé])\s+(hago|puedo|podria|haria|cocino|preparo|como)\b", texto_limpio):
            puntos_recetas += 4

        if re.search(r"\b(ideas?|sugerencias?|opciones?)\s+(para|con|de)\b", texto_limpio):
            puntos_recetas += 4

        if re.search(r"\b(\d+)\s*(g|gramos|kg|ml|unidad|unidades)\b", texto_limpio):
            puntos_calorias += 2

        if re.search(
            r"\b(adelgazar|perder peso|perder grasa|ganar musculo|masa muscular|saciedad|hambre|antojos|ansiedad)\b",
            texto_limpio,
        ):
            puntos_nutricion += 3

        if re.search(r"\b(es bueno|es buena|sirve para|buena opcion|buena fuente)\b", texto_limpio):
            puntos_nutricion += 3

        intenciones = {
            "recetas": puntos_recetas,
            "calorias": puntos_calorias,
            "nutricion": puntos_nutricion,
            "ayuda": puntos_ayuda,
        }

        intencion_principal = max(intenciones, key=intenciones.get)
        if intenciones[intencion_principal] == 0:
            return "general"
        return intencion_principal

    def extraer_cantidad(self, texto: str) -> Dict[str, Optional[float]]:
        texto_limpio = self.limpiar_texto(texto)
        match = re.search(r"(\d+(?:[.,]\d+)?)\s*(kg|g|gramos|gramo|ml|unidad|unidades)", texto_limpio)
        if not match:
            return {"valor": None, "unidad": None}
        valor = float(match.group(1).replace(",", "."))
        unidad = match.group(2)
        return {"valor": valor, "unidad": unidad}

    def extraer_ingredientes(self, texto: str) -> List[str]:
        texto_limpio = self.limpiar_texto(texto)
        if self.detectar_intencion(texto) == "ayuda":
            return []
        candidatos: List[str] = []

        for match in re.finditer(r"(?:con|de|tengo|usar|aprovechar|usando|gastar|sobra(?:n)?)\s+([a-z0-9,\s]+)", texto_limpio):
            fragmento = match.group(1)
            fragmento = re.split(
                r"\b(para|que|porque|pero|aunque|cuantas|calorias|como|sin)\b",
                fragmento,
            )[0]
            for parte in re.split(r",| y | e ", fragmento):
                parte = parte.strip()
                parte = re.sub(
                    r"\b(\d+(?:[.,]\d+)?)\s*(kg|g|gramos|gramo|ml|unidad|unidades)\b",
                    "",
                    parte,
                ).strip()
                if parte and parte not in self.stopwords and len(parte) > 2:
                    candidatos.append(parte)

        if not candidatos:
            candidatos = self.extraer_palabras_clave(texto_limpio)

        vistos: List[str] = []
        for item in candidatos:
            if item not in vistos:
                vistos.append(item)
        return vistos[:6]

    def extraer_alimento(self, texto: str) -> str:
        texto_limpio = self.limpiar_texto(texto)
        ingredientes = self.extraer_ingredientes(texto)
        if self.detectar_intencion(texto) in {"calorias", "nutricion"} and ingredientes:
            return ingredientes[0]

        patrones = [
            r"(?:calorias|proteina|proteinas|fibra|grasas|carbohidratos|nutricional|aporta|tiene|contiene)\s+(?:de|del|de la)?\s*([a-z0-9\s]+)",
            r"(?:cuanto|cuanta|cuantas|cuantos)\s+(?:tiene|aporta|contiene)?\s*(?:de|del|de la)?\s*([a-z0-9\s]+)",
            r"(?:el|la|los|las|un|una)\s+([a-z0-9\s]+)\s+(?:es|son|esta|sirve|aporta|tiene|engorda)",
        ]

        for patron in patrones:
            match = re.search(patron, texto_limpio)
            if match:
                candidato = match.group(1).strip()
                candidato = re.split(r"\b(por|para|si|que|en|es|son)\b", candidato)[0].strip()
                if candidato and candidato not in self.stopwords and len(candidato) > 2:
                    return candidato

        if ingredientes:
            return ingredientes[0]

        palabras = self.extraer_palabras_clave(texto_limpio)
        return " ".join(palabras[:2]).strip()

    def procesar(self, texto: str) -> Dict:
        texto_limpio = self.limpiar_texto(texto)
        return {
            "texto_original": texto,
            "texto_limpio": texto_limpio,
            "intencion": self.detectar_intencion(texto),
            "palabras_clave": self.extraer_palabras_clave(texto_limpio),
            "ingredientes": self.extraer_ingredientes(texto),
            "alimento": self.extraer_alimento(texto),
            "cantidad": self.extraer_cantidad(texto),
        }
