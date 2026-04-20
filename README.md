# NutrIA

Asistente de nutrición web con chat inteligente, galería de recetas con fotos y base de datos nutricional completa.

**Demo en vivo:** [https://nutria.onrender.com](https://nutria.onrender.com)

---

## Características

### Chat inteligente
- Pregunta por recetas con los ingredientes que tengas
- Consulta calorías y macros de cualquier alimento
- Consejos de nutrición práctica adaptados a tus objetivos
- Memoria de contexto: pide detalles de una receta sin repetir el nombre

### Galería de recetas
- Más de 100 recetas con fotos y filtros por categoría
- Filtros: Todas, Desayuno, Almuerzo, Cena, Snack, Pollo, Pescado, Vegetariano
- Buscador en tiempo real
- Modal con foto, ingredientes y pasos de preparación numerados

### Base de datos nutricional
- 157 alimentos con calorías, proteína, carbohidratos, grasas y fibra
- Cálculo automático por cantidad (ej. "250g de salmón")
- Categorías: frutas, verduras, carnes, pescados, lácteos, legumbres, cereales, frutos secos, bebidas, condimentos y snacks

### Diseño
- Interfaz minimalista con modo oscuro
- Animaciones suaves y transiciones
- Responsive — funciona en móvil y escritorio

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.8+, FastAPI |
| Frontend | HTML/CSS/JS vanilla (sin frameworks) |
| NLP | Procesador propio en `nlp_processor.py` |
| Datos | JSON local + Google Drive (recetas) |
| Despliegue | Render |

---

## Instalación local

```bash
git clone https://github.com/mariocm13/nutria.git
cd nutria
pip install -r requirements.txt
python app.py
```

Abre **http://localhost:8000** en tu navegador.

---

## API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Interfaz web |
| `POST` | `/api/chat` | Chat con contexto |
| `GET` | `/api/recipes` | Todas las recetas |
| `GET` | `/api/calories?food=<nombre>` | Buscar alimento |
| `GET` | `/api/stats` | Total de recetas y alimentos |

### Ejemplo `/api/chat`

```json
POST /api/chat
{
  "mensaje": "cuántas calorías tiene el salmón",
  "contexto": {}
}
```

---

## Estructura

```
nutria/
├── app.py                 # Servidor FastAPI + HTML embebido
├── nlp_processor.py       # Procesamiento del lenguaje natural
├── main.py                # Versión CLI
├── data/
│   ├── calories.json      # 157 alimentos con macros
│   ├── recipes_large.json # Base de datos de recetas
│   └── nutrition_knowledge.json
└── requirements.txt
```

---

## Despliegue

El proyecto se despliega automáticamente en Render al hacer push a `main`.

```bash
./deploy.sh "descripción del cambio"
```
