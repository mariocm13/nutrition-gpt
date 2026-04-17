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

### Opción 1: Acceso en Línea (Recomendado)

Tu NutriGPT está desplegado en línea y es accesible desde cualquier lugar:

**URL Pública**: [https://nutrigpt.onrender.com](https://nutrigpt.onrender.com)

Simplemente abre el enlace en tu navegador desde cualquier dispositivo.

### Opción 2: Actualización y Despliegue Automático

He incluido un script para facilitar las actualizaciones. Solo tienes que ejecutar:

```bash
./deploy.sh "Descripción de tus cambios"
```

Este script validará tu código y lo subirá a GitHub, lo que activará automáticamente el despliegue en Render.

### Opción 3: Ejecutar Localmente

Si quieres ejecutar la aplicación en tu ordenador:

```bash
python app.py
```

Luego abre tu navegador y ve a: **http://localhost:8000**

### Opción 3: Ejecutar la Versión CLI (Línea de Comandos)

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
