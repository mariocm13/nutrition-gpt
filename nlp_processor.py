import re
from typing import Dict, List, Tuple

class NLPProcessor:
    """Procesador avanzado de lenguaje natural para NutriGPT."""
    
    def __init__(self):
        # Palabras clave para cada intención
        self.palabras_recetas = {
            'receta', 'recetas', 'puedo hacer', 'cómo hago', 'quiero', 'busco', 'dame', 
            'muestra', 'con', 'haz', 'prepara', 'cocina', 'plato', 'comida', 'cena', 
            'desayuno', 'almuerzo', 'merienda', 'idea', 'sugerencia', 'recomendación',
            'qué puedo', 'qué hago', 'cómo preparo', 'cómo cocino', 'ingredientes'
        }
        
        self.palabras_calorias = {
            'calorías', 'calorias', 'cuántas calorías', 'cuantas calorias', 'valor nutricional',
            'energía', 'kcal', 'kilocalorías', 'kilocalories', 'cuánto tiene', 'cuanto tiene',
            'información nutricional', 'nutrientes', 'proteínas', 'grasas', 'carbohidratos',
            'cuántas', 'cuantas', 'cuánto', 'cuanto', 'tiene', 'contiene'
        }
        
        self.palabras_ayuda = {
            'hola', 'qué puedes', 'que puedes', 'ayuda', 'cómo funciona', 'como funciona',
            'cuéntame', 'cuentame', 'quién eres', 'quien eres', 'qué eres', 'que eres',
            'instrucciones', 'tutorial', 'guía', 'guia', 'inicio', 'bienvenida'
        }
        
        self.palabras_descarte = {
            'el', 'la', 'de', 'del', 'una', 'un', 'unos', 'unas', 'los', 'las',
            'por', 'para', 'en', 'a', 'al', 'con', 'sin', 'que', 'y', 'o', 'u',
            'es', 'son', 'está', 'están', 'estoy', 'soy', 'eres', 'somos'
        }
    
    def limpiar_texto(self, texto: str) -> str:
        """Limpia y normaliza el texto de entrada."""
        # Convertir a minúsculas
        texto = texto.lower()
        # Remover puntuación innecesaria pero mantener espacios
        texto = re.sub(r'[¿?¡!]', '', texto)
        # Remover espacios múltiples
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    
    def extraer_palabras_clave(self, texto: str) -> List[str]:
        """Extrae palabras clave relevantes del texto."""
        palabras = texto.split()
        # Filtrar palabras muy cortas y palabras de descarte
        palabras_clave = [
            p for p in palabras 
            if len(p) > 2 and p not in self.palabras_descarte
        ]
        return palabras_clave
    
    def detectar_intencion(self, texto: str) -> str:
        """Detecta la intención principal del usuario."""
        texto_limpio = self.limpiar_texto(texto)
        
        # Contar coincidencias por intención
        puntos_recetas = sum(1 for palabra in self.palabras_recetas if palabra in texto_limpio)
        puntos_calorias = sum(1 for palabra in self.palabras_calorias if palabra in texto_limpio)
        puntos_ayuda = sum(1 for palabra in self.palabras_ayuda if palabra in texto_limpio)
        
        # Determinar intención por puntuación
        intenciones = {
            'recetas': puntos_recetas,
            'calorias': puntos_calorias,
            'ayuda': puntos_ayuda
        }
        
        intencion_principal = max(intenciones, key=intenciones.get)
        
        # Si no hay coincidencias claras, usar heurísticas adicionales
        if intenciones[intencion_principal] == 0:
            # Buscar números (posible búsqueda de calorías)
            if re.search(r'\d+', texto):
                return 'calorias'
            # Buscar verbos de acción (posible búsqueda de recetas)
            if any(verbo in texto_limpio for verbo in ['hacer', 'preparar', 'cocinar', 'haz', 'prepara']):
                return 'recetas'
            return 'general'
        
        return intencion_principal
    
    def extraer_ingredientes(self, texto: str) -> List[str]:
        """Extrae ingredientes mencionados en el texto."""
        palabras_clave = self.extraer_palabras_clave(self.limpiar_texto(texto))
        # Filtrar palabras que probablemente sean ingredientes (más de 3 caracteres)
        ingredientes = [p for p in palabras_clave if len(p) > 3]
        return ingredientes
    
    def extraer_alimento(self, texto: str) -> str:
        """Extrae el alimento principal del que se pregunta."""
        # Buscar patrones comunes
        patrones = [
            r'(?:de|tiene|contiene|cuántas|cuantas)\s+([a-záéíóúñ]+)',
            r'([a-záéíóúñ]+)(?:\s+tiene|\s+contiene)',
            r'(?:un|una|el|la)\s+([a-záéíóúñ]+)'
        ]
        
        texto_limpio = self.limpiar_texto(texto)
        
        for patron in patrones:
            match = re.search(patron, texto_limpio)
            if match:
                alimento = match.group(1)
                if alimento not in self.palabras_descarte and len(alimento) > 2:
                    return alimento
        
        # Si no encuentra patrón, devolver la última palabra significativa
        palabras = self.extraer_palabras_clave(texto_limpio)
        return palabras[-1] if palabras else ""
    
    def procesar(self, texto: str) -> Dict:
        """Procesa el texto y devuelve un diccionario con información extraída."""
        return {
            'texto_original': texto,
            'texto_limpio': self.limpiar_texto(texto),
            'intencion': self.detectar_intencion(texto),
            'palabras_clave': self.extraer_palabras_clave(self.limpiar_texto(texto)),
            'ingredientes': self.extraer_ingredientes(texto),
            'alimento': self.extraer_alimento(texto)
        }
