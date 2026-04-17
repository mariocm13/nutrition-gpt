# Guía de Despliegue en Render - NutriGPT

Esta guía te mostrará cómo desplegar tu **NutriGPT** en **Render** para que sea accesible desde cualquier lugar del mundo de forma **completamente gratuita**.

## Paso 1: Preparar tu Repositorio en GitHub

Tu repositorio ya está listo en: `https://github.com/mariocm13/nutrition-gpt`

Asegúrate de que todos los cambios estén subidos:
```bash
git status
git add .
git commit -m "Ready for deployment"
git push origin main
```

## Paso 2: Crear una Cuenta en Render

1. Ve a [https://render.com](https://render.com)
2. Haz clic en **"Sign Up"** (Registrarse)
3. Conecta tu cuenta de **GitHub**
4. Autoriza a Render para acceder a tus repositorios

## Paso 3: Crear un Nuevo Web Service

1. En el dashboard de Render, haz clic en **"New +"** (arriba a la derecha)
2. Selecciona **"Web Service"**
3. Busca y selecciona tu repositorio **`nutrition-gpt`**
4. Haz clic en **"Connect"**

## Paso 4: Configurar el Servicio

Completa los campos con la siguiente información:

| Campo | Valor |
| :--- | :--- |
| **Name** | `nutrigpt` (o el nombre que prefieras) |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` (Plan Gratuito) |

## Paso 5: Desplegar

1. Haz clic en **"Create Web Service"**
2. Render comenzará a compilar y desplegar tu aplicación (esto tarda 2-3 minutos)
3. Cuando veas el estado **"Live"**, ¡tu aplicación está en línea!

## Paso 6: Obtener tu URL Pública

Una vez desplegado, Render te proporcionará una URL como:
```
https://nutrigpt.onrender.com
```

**¡Esta es tu URL pública!** Puedes compartirla con cualquiera y acceder a NutriGPT desde cualquier dispositivo.

## Información Importante sobre el Plan Gratuito

- ✅ **Totalmente Gratuito**: No hay costos
- ✅ **Siempre Activo**: Tu aplicación estará disponible 24/7
- ⚠️ **Tiempo de Inicio**: La primera vez que accedas después de inactividad, puede tardar 30 segundos en cargar (esto es normal)
- ✅ **Actualizaciones Automáticas**: Cada vez que hagas `git push` a tu repositorio, Render actualizará automáticamente tu aplicación

## Paso 7: Actualizar tu Aplicación

Cada vez que quieras hacer cambios:

1. Realiza los cambios en tu ordenador
2. Sube a GitHub:
   ```bash
   git add .
   git commit -m "Descripción del cambio"
   git push origin main
   ```
3. Render detectará automáticamente los cambios y desplegará la nueva versión

## Solución de Problemas

### "Build failed" (Error en la compilación)
- Verifica que todos los archivos estén en GitHub
- Comprueba que `requirements.txt` está actualizado
- Revisa los logs en Render para más detalles

### La aplicación es muy lenta
- Esto es normal en el plan gratuito
- Si necesitas mejor rendimiento, considera actualizar a un plan de pago

### No puedo conectarme a Google Drive
- Verifica que el ID de Google Drive en `app.py` sea correcto
- Asegúrate de que el archivo en Drive esté compartido públicamente

## Próximos Pasos

Una vez desplegado, puedes:
- Compartir tu URL con amigos y familia
- Añadir más recetas a tu base de datos en Google Drive
- Personalizar el nombre del dominio (con plan de pago)
- Integrar con otras herramientas

¡Tu NutriGPT está listo para el mundo! 🌍
