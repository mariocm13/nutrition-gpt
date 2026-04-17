import re
import unicodedata
from typing import Dict, List, Optional


class NLPProcessor:
    """Procesador de lenguaje natural basado en reglas para NutriGPT."""

    def __init__(self):
        self.palabras_recetas = {
            "receta",
            "recetas",
            "hacer",
            "preparar",
            "prepara",
            "cocinar",
            "cocino",
            "cocina",
            "plato",
            "platos",
            "desayuno",
            "almuerzo",
            "comida",
            "cena",
            "merienda",
            "idea",
            "ideas",
            "menu",
            "menus",
            "ingredientes",
        }

        self.palabras_calorias = {
            "calorias",
            "kcal",
            "energia",
            "valor nutricional",
            "informacion nutricional",
            "proteinas",
            "grasas",
            "carbohidratos",
            "macros",
            "nutrientes",
            "cuantas calorias",
            "cuanto tiene",
            "cuanto aporta",
            "cuantas tiene",
        }

        self.palabras_ayuda = {
            "hola",
            "buenas",
            "ayuda",
            "como funciona",
            "que puedes hacer",
            "quien eres",
            "inicio",
            "help",
        }

        self.stopwords = {
            "el",
            "la",
            "los",
            "las",
            "un",
            "una",
            "unos",
            "unas",
            "de",
            "del",
            "y",
            "o",
            "u",
            "a",
            "al",
            "en",
            "para",
            "por",
            "con",
            "sin",
            "que",
            "me",
            "mi",
            "mis",
            "tu",
            "tus",
            "quiero",
            "puedo",
            "hacer",
            "preparar",
            "prepara",
            "cocinar",
            "cocina",
            "dame",
            "busco",
            "necesito",
            "cuanto",
            "cuanta",
            "cuantas",
            "cuantos",
            "tiene",
            "tienen",
            "contiene",
            "contienen",
            "hay",
            "es",
            "son",
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
        puntos_ayuda = sum(2 for palabra in self.palabras_ayuda if palabra in texto_limpio)

        if re.search(r"\b(receta|recetas|desayuno|almuerzo|comida|cena)\b", texto_limpio):
            puntos_recetas += 3

        if re.search(r"\b(calorias|kcal|proteinas|grasas|carbohidratos|nutricional)\b", texto_limpio):
            puntos_calorias += 3

        if re.search(r"\b(hola|buenas|ayuda)\b", texto_limpio) and len(texto_limpio.split()) <= 5:
            puntos_ayuda += 3

        if re.search(r"\b(tengo|con|usar|aprovechar)\b", texto_limpio):
            puntos_recetas += 2

        if re.search(r"\b(\d+)\s*(g|gramos|kg|ml|unidad|unidades)\b", texto_limpio):
            puntos_calorias += 1

        intenciones = {
            "recetas": puntos_recetas,
            "calorias": puntos_calorias,
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

        patrones = [
            r"(?:con|de|tengo|usar|aprovechar)\s+([a-z0-9,\s]+)",
        ]

        for patron in patrones:
            for match in re.finditer(patron, texto_limpio):
                fragmento = match.group(1)
                fragmento = re.split(r"\b(para|que|porque|pero|aunque|cuantas|calorias)\b", fragmento)[0]
                partes = re.split(r",| y ", fragmento)
                for parte in partes:
                    parte = parte.strip()
                    parte = re.sub(r"\b(\d+(?:[.,]\d+)?)\s*(kg|g|gramos|gramo|ml|unidad|unidades)\b", "", parte).strip()
                    if parte and parte not in self.stopwords and len(parte) > 2:
                        candidatos.append(parte)

        if not candidatos:
            candidatos = self.extraer_palabras_clave(texto_limpio)

        vistos = []
        for item in candidatos:
            if item not in vistos:
                vistos.append(item)
        return vistos[:6]

    def extraer_alimento(self, texto: str) -> str:
        texto_limpio = self.limpiar_texto(texto)

        ingredientes = self.extraer_ingredientes(texto)
        if self.detectar_intencion(texto) == "calorias" and ingredientes:
            return ingredientes[0]

        patrones = [
            r"(?:calorias|proteinas|grasas|carbohidratos|nutricional)\s+(?:de|del|de la)?\s*([a-z0-9\s]+)",
            r"(?:cuanto|cuanta|cuantas|cuantos)\s+(?:tiene|aporta|contiene)?\s*(?:de|del|de la)?\s*([a-z0-9\s]+)",
            r"(?:el|la|los|las|un|una)\s+([a-z0-9\s]+)",
        ]

        for patron in patrones:
            match = re.search(patron, texto_limpio)
            if match:
                candidato = match.group(1).strip()
                candidato = re.split(r"\b(por|para|si|que|en)\b", candidato)[0].strip()
                if candidato and candidato not in self.stopwords:
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
