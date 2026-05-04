from mangum import Mangum
import sys
import os

# Añadir el directorio raíz al path para que pueda importar app.py y otros módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import app

handler = Mangum(app)
