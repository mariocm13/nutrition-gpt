# Guía de Despliegue: Asistente de Nutrición GPT

Para que tu asistente esté disponible en internet de forma permanente y gratuita, te recomiendo utilizar **Render**, ya que se integra directamente con tu repositorio de GitHub y ofrece un plan gratuito excelente para proyectos de Python.

## Opción 1: Despliegue en Render (Recomendado)

Render es muy sencillo y detectará automáticamente tu configuración.

### Pasos para el despliegue:

1.  **Crear cuenta**: Regístrate en [Render.com](https://render.com/) usando tu cuenta de GitHub.
2.  **Nuevo Web Service**: Haz clic en el botón **"New +"** y selecciona **"Web Service"**.
3.  **Conectar Repositorio**: Busca y selecciona tu repositorio `nutria`.
4.  **Configuración del servicio**:
    *   **Name**: `nutria-tu-nombre`
    *   **Environment**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `python app.py` (o mejor: `uvicorn app:app --host 0.0.0.0 --port $PORT`)
5.  **Plan**: Selecciona el plan **"Free"**.
6.  **Desplegar**: Haz clic en **"Create Web Service"**.

> **Nota**: En el plan gratuito de Render, la aplicación "se duerme" tras 15 minutos de inactividad. La primera vez que entres después de un tiempo, puede tardar unos 30 segundos en cargar.

---

## Opción 2: Despliegue en Railway

Railway es otra opción muy rápida y moderna.

1.  Entra en [Railway.app](https://railway.app/) y conecta tu GitHub.
2.  Selecciona **"New Project"** > **"Deploy from GitHub repo"**.
3.  Elige tu repositorio `nutria`.
4.  Railway detectará el archivo `requirements.txt` y desplegará la aplicación automáticamente.

---

## Comparativa de Servicios Gratuitos

| Servicio | Ventajas | Limitaciones |
| :--- | :--- | :--- |
| **Render** | Muy estable, gran interfaz, despliegue automático desde GitHub. | La app se duerme tras inactividad (arranque en frío). |
| **Railway** | Despliegue ultra rápido, excelente para APIs. | Ofrece un crédito limitado gratuito al mes (suficiente para pruebas). |
| **PythonAnywhere** | Especializado en Python, muy fiable. | Configuración un poco más manual, interfaz más antigua. |

## Recomendación Final

Te sugiero empezar con **Render**. Una vez configurado, cada vez que hagas un `git push` a tu repositorio de GitHub, Render actualizará automáticamente tu página web con los nuevos cambios.
