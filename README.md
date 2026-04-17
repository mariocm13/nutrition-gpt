# Asistente de Nutrición GPT

Este es un asistente de nutrición accesible vía web, diseñado para proporcionar recetas saludables y contar calorías de diversos alimentos. Puedes acceder a través de un navegador web sin necesidad de instalación adicional.

## Características

- **Recetario Interactivo**: Una colección de recetas saludables con ingredientes e instrucciones detalladas.
- **Contador de Calorías**: Búsqueda de información nutricional de alimentos comunes por cada 100g.
- **Interfaz Web Moderna**: Aplicación web responsiva y fácil de usar.
- **API RESTful**: Endpoints para integración con otras aplicaciones.

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/mariocm13/nutrition-gpt.git
   cd nutrition-gpt
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Ejecutar la aplicación web

```bash
python app.py
```

Luego abre tu navegador y ve a: **http://localhost:8000**

### Ejecutar la versión CLI (línea de comandos)

```bash
python main.py
```

## Estructura del Proyecto

- `app.py`: Aplicación web con FastAPI
- `main.py`: Versión CLI del asistente
- `data/`: Archivos JSON con información de recetas y calorías
- `requirements.txt`: Dependencias del proyecto

## API Endpoints

- `GET /` - Página principal de la aplicación web
- `GET /api/calories?food=<nombre>` - Buscar calorías de un alimento
- `GET /api/recipes` - Obtener todas las recetas
- `GET /api/recipes/<index>` - Obtener una receta específica
