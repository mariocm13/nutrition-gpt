import json, os

recetas = [
    # --- POLLO ---
    {
        "id": 1, "nombre": "Pollo al ajillo", "categoria": "pollo",
        "tiempo": "30 min", "dificultad": "Fácil", "calorias_aprox": 320,
        "ingredientes": ["4 muslos de pollo", "8 dientes de ajo", "100 ml de vino blanco", "50 ml de aceite de oliva", "1 ramita de romero", "Sal y pimienta"],
        "instrucciones": ["Dorar el pollo en aceite a fuego medio-alto 5 min por lado.", "Añadir el ajo laminado y rehogar 2 min.", "Verter el vino blanco y el romero. Tapar y cocinar 20 min a fuego lento.", "Rectificar sal y servir."]
    },
    {
        "id": 2, "nombre": "Pechuga de pollo con verduras al wok", "categoria": "pollo",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 280,
        "ingredientes": ["2 pechugas de pollo en tiras", "1 pimiento rojo", "1 pimiento verde", "1 zanahoria", "2 cucharadas de salsa de soja", "1 diente de ajo", "1 cm de jengibre fresco", "Aceite de sésamo"],
        "instrucciones": ["Cortar todas las verduras en juliana.", "Calentar el wok a fuego muy alto con aceite de sésamo.", "Saltear el pollo 3 min. Añadir ajo y jengibre.", "Incorporar verduras y saltear 4 min más.", "Añadir salsa de soja y remover. Servir inmediatamente."]
    },
    {
        "id": 3, "nombre": "Pollo al horno con limón y tomillo", "categoria": "pollo",
        "tiempo": "55 min", "dificultad": "Fácil", "calorias_aprox": 340,
        "ingredientes": ["1 pollo entero de 1,5 kg", "2 limones", "4 ramas de tomillo fresco", "4 dientes de ajo", "50 ml de aceite de oliva", "Sal y pimienta"],
        "instrucciones": ["Precalentar el horno a 200°C.", "Frotar el pollo con aceite, sal y pimienta.", "Introducir en la cavidad los limones cortados y el tomillo.", "Hornear 45-50 min regando con los jugos cada 15 min.", "Reposar 10 min antes de trinchar."]
    },
    {
        "id": 4, "nombre": "Pollo en salsa de curry y coco", "categoria": "pollo",
        "tiempo": "35 min", "dificultad": "Media", "calorias_aprox": 420,
        "ingredientes": ["500 g de pechuga de pollo en dados", "400 ml de leche de coco", "2 cucharadas de curry en polvo", "1 cebolla", "2 dientes de ajo", "1 cucharadita de jengibre", "Cilantro fresco", "Aceite de oliva"],
        "instrucciones": ["Sofreír la cebolla picada 5 min.", "Añadir ajo, jengibre y curry. Cocinar 1 min.", "Incorporar el pollo y dorar 3 min.", "Verter la leche de coco. Cocer a fuego medio 20 min.", "Servir con cilantro fresco."]
    },
    {
        "id": 5, "nombre": "Ensalada de pollo con aguacate", "categoria": "pollo",
        "tiempo": "15 min", "dificultad": "Fácil", "calorias_aprox": 350,
        "ingredientes": ["200 g de pechuga de pollo cocida", "1 aguacate maduro", "100 g de lechuga romana", "1 tomate", "Zumo de limón", "Aceite de oliva virgen", "Sal y pimienta"],
        "instrucciones": ["Cortar el pollo en tiras y el aguacate en dados.", "Trocear la lechuga y el tomate.", "Mezclar todos los ingredientes.", "Aliñar con aceite, limón, sal y pimienta."]
    },
    {
        "id": 6, "nombre": "Pollo a la plancha con chimichurri", "categoria": "pollo",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 290,
        "ingredientes": ["2 pechugas de pollo", "1 manojo de perejil", "4 dientes de ajo", "1 cucharadita de orégano", "3 cucharadas de vinagre de vino", "6 cucharadas de aceite de oliva", "Sal y pimienta"],
        "instrucciones": ["Preparar el chimichurri: picar perejil y ajo, mezclar con orégano, vinagre y aceite. Salar.", "Hacer las pechugas a la plancha 6 min por lado.", "Servir con el chimichurri por encima."]
    },
    {
        "id": 7, "nombre": "Albóndigas de pollo en salsa de tomate", "categoria": "pollo",
        "tiempo": "40 min", "dificultad": "Media", "calorias_aprox": 360,
        "ingredientes": ["500 g de carne picada de pollo", "1 huevo", "2 dientes de ajo", "Perejil fresco", "400 g de tomate triturado", "1 cebolla", "Aceite de oliva", "Sal y pimienta"],
        "instrucciones": ["Mezclar la carne con huevo, ajo picado, perejil, sal y pimienta.", "Formar albóndigas y freír hasta dorar.", "Sofreír la cebolla 5 min. Añadir tomate y cocer 10 min.", "Introducir las albóndigas en la salsa y cocer 15 min más."]
    },
    {
        "id": 8, "nombre": "Pollo tikka masala", "categoria": "pollo",
        "tiempo": "45 min", "dificultad": "Media", "calorias_aprox": 430,
        "ingredientes": ["600 g de pechuga de pollo", "200 ml de yogur natural", "400 g de tomate triturado", "200 ml de nata para cocinar", "2 cucharadas de garam masala", "1 cucharadita de cúrcuma", "1 cebolla", "3 dientes de ajo"],
        "instrucciones": ["Marinar el pollo en yogur con garam masala y cúrcuma al menos 1 hora.", "Asar el pollo en la plancha.", "Sofreír cebolla y ajo. Añadir tomate y cocer 10 min.", "Incorporar la nata y el pollo. Cocer 10 min más."]
    },

    # --- PESCADO ---
    {
        "id": 9, "nombre": "Salmón al horno con eneldo", "categoria": "pescado",
        "tiempo": "25 min", "dificultad": "Fácil", "calorias_aprox": 380,
        "ingredientes": ["4 lomos de salmón de 150 g", "1 limón", "Eneldo fresco", "2 cucharadas de aceite de oliva", "Sal y pimienta en grano"],
        "instrucciones": ["Precalentar el horno a 200°C.", "Colocar el salmón en bandeja. Salpimentar.", "Rociar con aceite y zumo de limón. Cubrir con eneldo.", "Hornear 15-18 min hasta que esté opaco."]
    },
    {
        "id": 10, "nombre": "Merluza en salsa verde", "categoria": "pescado",
        "tiempo": "30 min", "dificultad": "Media", "calorias_aprox": 260,
        "ingredientes": ["4 filetes de merluza", "4 dientes de ajo", "1 manojo de perejil", "200 ml de caldo de pescado", "100 ml de vino blanco", "2 cucharadas de harina", "Aceite de oliva"],
        "instrucciones": ["Dorar el ajo laminado en aceite.", "Añadir la harina y rehogar 1 min.", "Verter el vino y el caldo. Cocer 5 min.", "Incorporar la merluza y el perejil picado.", "Cocer tapado 8-10 min a fuego medio-bajo."]
    },
    {
        "id": 11, "nombre": "Atún a la plancha con ensalada", "categoria": "pescado",
        "tiempo": "15 min", "dificultad": "Fácil", "calorias_aprox": 310,
        "ingredientes": ["2 filetes de atún de 200 g", "100 g de rúcula", "1 aguacate", "200 g de tomates cherry", "1 limón", "Aceite de oliva virgen extra", "Sal en escamas"],
        "instrucciones": ["Calentar la plancha a fuego muy alto.", "Cocinar el atún 2 min por lado (rosado dentro).", "Montar la ensalada con rúcula, aguacate y tomates.", "Colocar el atún encima. Aliñar con limón, aceite y sal."]
    },
    {
        "id": 12, "nombre": "Bacalao a la vizcaína", "categoria": "pescado",
        "tiempo": "50 min", "dificultad": "Media", "calorias_aprox": 290,
        "ingredientes": ["600 g de bacalao desalado", "4 pimientos choriceros", "2 cebollas", "4 dientes de ajo", "400 g de tomate triturado", "Aceite de oliva", "Sal"],
        "instrucciones": ["Remojar los pimientos choriceros 30 min. Extraer la pulpa.", "Sofreír cebolla y ajo. Añadir pulpa de pimientos y tomate.", "Cocer la salsa 20 min a fuego lento.", "Pasar por el pasapurés.", "Incorporar el bacalao y cocer 10 min."]
    },
    {
        "id": 13, "nombre": "Gambas al ajillo", "categoria": "pescado",
        "tiempo": "10 min", "dificultad": "Fácil", "calorias_aprox": 220,
        "ingredientes": ["500 g de gambas peladas", "6 dientes de ajo", "2 guindillas", "100 ml de aceite de oliva", "Perejil fresco", "Sal"],
        "instrucciones": ["Calentar el aceite en cazuela de barro.", "Dorar el ajo laminado con las guindillas.", "Añadir las gambas. Cocinar 2 min removiendo.", "Espolvorear perejil y servir inmediatamente."]
    },
    {
        "id": 14, "nombre": "Dorada al horno a la sal", "categoria": "pescado",
        "tiempo": "40 min", "dificultad": "Fácil", "calorias_aprox": 240,
        "ingredientes": ["2 doradas de 400 g", "1,5 kg de sal gorda", "2 claras de huevo", "1 limón", "Tomillo fresco"],
        "instrucciones": ["Precalentar el horno a 200°C.", "Mezclar la sal con las claras y un poco de agua.", "Cubrir la base de la bandeja con sal. Poner las doradas con limón y tomillo dentro.", "Cubrir completamente con la sal. Hornear 30 min.", "Romper la costra de sal y servir."]
    },
    {
        "id": 15, "nombre": "Ceviche de corvina", "categoria": "pescado",
        "tiempo": "25 min", "dificultad": "Media", "calorias_aprox": 190,
        "ingredientes": ["400 g de corvina fresca", "Zumo de 6 limas", "1 cebolla roja", "1 ají amarillo", "Cilantro fresco", "Sal", "1 trozo de jengibre"],
        "instrucciones": ["Cortar el pescado en dados de 1 cm.", "Cubrir con zumo de lima y sal. Reposar 10 min.", "Añadir cebolla en juliana fina, ají picado y jengibre rallado.", "Mezclar bien y servir frío con cilantro."]
    },
    {
        "id": 16, "nombre": "Boquerones al limón", "categoria": "pescado",
        "tiempo": "5 min", "dificultad": "Fácil", "calorias_aprox": 150,
        "ingredientes": ["300 g de boquerones en vinagre", "Zumo de 1 limón", "3 dientes de ajo", "Perejil fresco", "Aceite de oliva virgen extra"],
        "instrucciones": ["Escurrir los boquerones.", "Picar el ajo y el perejil finamente.", "Mezclar con zumo de limón y aceite.", "Añadir a los boquerones y servir."]
    },

    # --- CARNE (res/cerdo) ---
    {
        "id": 17, "nombre": "Estofado de ternera con patatas", "categoria": "carne",
        "tiempo": "90 min", "dificultad": "Media", "calorias_aprox": 480,
        "ingredientes": ["700 g de ternera para guisar", "3 patatas medianas", "2 zanahorias", "1 cebolla", "200 ml de vino tinto", "400 ml de caldo de carne", "2 dientes de ajo", "Aceite de oliva", "Tomillo y laurel"],
        "instrucciones": ["Dorar la carne en aceite a fuego fuerte.", "Retirar y sofreír cebolla, ajo y zanahoria.", "Incorporar la carne, el vino y el caldo.", "Añadir hierbas. Cocer tapado 1 hora a fuego lento.", "Agregar las patatas en dados y cocer 20 min más."]
    },
    {
        "id": 18, "nombre": "Chuletas de cerdo a la mostaza", "categoria": "carne",
        "tiempo": "25 min", "dificultad": "Fácil", "calorias_aprox": 410,
        "ingredientes": ["4 chuletas de cerdo", "3 cucharadas de mostaza de Dijon", "2 cucharadas de miel", "1 cucharadita de ajo en polvo", "Romero fresco", "Aceite de oliva"],
        "instrucciones": ["Mezclar mostaza, miel, ajo en polvo y romero.", "Untar las chuletas con la mezcla.", "Cocinar en plancha 6-7 min por lado.", "Reposar 3 min antes de servir."]
    },
    {
        "id": 19, "nombre": "Hamburguesa casera con cheddar", "categoria": "carne",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 550,
        "ingredientes": ["500 g de carne picada de ternera", "4 lonchas de cheddar", "4 panecillos de hamburguesa", "1 cebolla", "Lechuga", "Tomate", "Kétchup y mostaza"],
        "instrucciones": ["Formar 4 hamburguesas con la carne. Salpimentar.", "Cocinar en plancha 3-4 min por lado.", "Añadir el queso encima y fundir 1 min.", "Tostar los panecillos. Montar con lechuga, tomate y salsas."]
    },
    {
        "id": 20, "nombre": "Lomo de cerdo al horno con manzana", "categoria": "carne",
        "tiempo": "60 min", "dificultad": "Media", "calorias_aprox": 380,
        "ingredientes": ["1 kg de lomo de cerdo", "3 manzanas", "200 ml de sidra", "2 ramas de romero", "2 dientes de ajo", "Aceite de oliva", "Sal y pimienta"],
        "instrucciones": ["Precalentar el horno a 180°C.", "Salpimentar el lomo y dorar en sartén.", "Colocar en bandeja con las manzanas en gajos y ajo.", "Verter la sidra y el romero.", "Hornear 45 min regando cada 15 min."]
    },
    {
        "id": 21, "nombre": "Costillas de cerdo a la barbacoa", "categoria": "carne",
        "tiempo": "150 min", "dificultad": "Media", "calorias_aprox": 520,
        "ingredientes": ["1,2 kg de costillas de cerdo", "100 ml de salsa barbacoa", "2 cucharadas de miel", "1 cucharadita de pimentón ahumado", "1 cucharadita de ajo en polvo", "Sal"],
        "instrucciones": ["Sazonar las costillas con sal, pimentón y ajo.", "Envolver en papel de aluminio. Hornear a 160°C durante 2 horas.", "Mezclar barbacoa con miel. Untar las costillas.", "Asar en el horno o barbacoa 15 min más a 200°C."]
    },
    {
        "id": 22, "nombre": "Rabo de toro estofado", "categoria": "carne",
        "tiempo": "180 min", "dificultad": "Alta", "calorias_aprox": 560,
        "ingredientes": ["1,5 kg de rabo de toro", "1 botella de vino tinto", "2 cebollas", "3 zanahorias", "4 dientes de ajo", "400 g de tomate triturado", "Laurel, tomillo, pimienta negra"],
        "instrucciones": ["Marinar el rabo en vino con verduras 12 horas.", "Dorar el rabo en aceite. Retirar.", "Sofreír las verduras de la marinada.", "Incorporar el rabo y el vino de la marinada.", "Añadir tomate. Cocer a fuego muy lento 3 horas."]
    },

    # --- VEGETARIANO ---
    {
        "id": 23, "nombre": "Tortilla española", "categoria": "vegetariano",
        "tiempo": "40 min", "dificultad": "Media", "calorias_aprox": 310,
        "ingredientes": ["6 huevos", "4 patatas medianas", "1 cebolla", "150 ml de aceite de oliva", "Sal"],
        "instrucciones": ["Pelar y laminat las patatas y la cebolla.", "Freír lentamente en aceite abundante 20 min.", "Escurrir el aceite. Batir los huevos con sal.", "Mezclar patatas y huevos. Reposar 5 min.", "Cuajar en sartén antiadherente 3 min por lado."]
    },
    {
        "id": 24, "nombre": "Gazpacho andaluz", "categoria": "vegetariano",
        "tiempo": "15 min", "dificultad": "Fácil", "calorias_aprox": 120,
        "ingredientes": ["1 kg de tomates maduros", "1 pepino", "1 pimiento verde", "1 diente de ajo", "50 ml de aceite de oliva virgen extra", "30 ml de vinagre de Jerez", "Sal", "Agua fría"],
        "instrucciones": ["Lavar y trocear todas las verduras.", "Triturar todo con la batidora.", "Añadir aceite, vinagre y sal. Triturar de nuevo.", "Colar y refrigerar al menos 1 hora.", "Servir bien frío con guarnición."]
    },
    {
        "id": 25, "nombre": "Crema de calabaza", "categoria": "vegetariano",
        "tiempo": "40 min", "dificultad": "Fácil", "calorias_aprox": 180,
        "ingredientes": ["700 g de calabaza", "1 cebolla", "2 patatas", "700 ml de caldo de verduras", "200 ml de nata", "Nuez moscada", "Aceite de oliva"],
        "instrucciones": ["Sofreír la cebolla 5 min.", "Añadir calabaza y patatas en trozos.", "Cubrir con el caldo. Cocer 25 min.", "Triturar hasta obtener crema fina.", "Añadir nata y nuez moscada. Calentar y servir."]
    },
    {
        "id": 26, "nombre": "Pisto manchego", "categoria": "vegetariano",
        "tiempo": "45 min", "dificultad": "Fácil", "calorias_aprox": 200,
        "ingredientes": ["2 calabacines", "1 berenjena", "2 pimientos rojos", "1 cebolla", "400 g de tomate triturado", "3 dientes de ajo", "Aceite de oliva", "Sal y azúcar"],
        "instrucciones": ["Cortar todas las verduras en dados pequeños.", "Sofreír la cebolla y el ajo 5 min.", "Añadir pimientos y cocer 5 min.", "Incorporar berenjena y calabacín. Cocer 10 min.", "Añadir tomate, sal y azúcar. Cocer a fuego lento 20 min."]
    },
    {
        "id": 27, "nombre": "Ensalada griega", "categoria": "vegetariano",
        "tiempo": "10 min", "dificultad": "Fácil", "calorias_aprox": 230,
        "ingredientes": ["3 tomates", "1 pepino", "1 cebolla roja", "100 g de aceitunas Kalamata", "150 g de queso feta", "Orégano seco", "Aceite de oliva virgen extra", "Sal"],
        "instrucciones": ["Cortar tomates, pepino y cebolla en trozos.", "Mezclar en un bol con las aceitunas.", "Desmigar el feta por encima.", "Aliñar con aceite, orégano y sal."]
    },
    {
        "id": 28, "nombre": "Revuelto de espárragos y gambas", "categoria": "vegetariano",
        "tiempo": "15 min", "dificultad": "Fácil", "calorias_aprox": 260,
        "ingredientes": ["6 huevos", "200 g de espárragos trigueros", "150 g de gambas peladas", "2 dientes de ajo", "Aceite de oliva", "Sal y pimienta"],
        "instrucciones": ["Cortar los espárragos en trozos y saltear con ajo 4 min.", "Añadir las gambas y cocinar 2 min.", "Batir los huevos con sal.", "Verter sobre la sartén a fuego bajo y remover constantemente hasta cuajar en cremoso."]
    },
    {
        "id": 29, "nombre": "Berenjenas rellenas de verduras", "categoria": "vegetariano",
        "tiempo": "50 min", "dificultad": "Media", "calorias_aprox": 240,
        "ingredientes": ["2 berenjenas grandes", "1 pimiento rojo", "1 cebolla", "200 g de tomate triturado", "100 g de queso mozzarella", "Aceite de oliva", "Orégano", "Sal"],
        "instrucciones": ["Partir las berenjenas por la mitad. Vaciar y picar la pulpa.", "Sofreír la cebolla, pimiento y pulpa de berenjena.", "Añadir tomate. Cocer 10 min. Rellenar las berenjenas.", "Cubrir con mozzarella. Hornear a 180°C durante 25 min."]
    },
    {
        "id": 30, "nombre": "Wok de tofu con verduras", "categoria": "vegetariano",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 280,
        "ingredientes": ["300 g de tofu firme", "200 g de brócoli", "1 pimiento rojo", "100 g de setas", "3 cucharadas de salsa de soja", "1 cucharadita de aceite de sésamo", "Jengibre", "Ajo"],
        "instrucciones": ["Cortar el tofu en dados y freír hasta dorar.", "Saltear el ajo y jengibre en el wok.", "Añadir las verduras más duras primero. Saltear 3 min.", "Incorporar el tofu y la salsa de soja.", "Rociar con aceite de sésamo al final."]
    },

    # --- ARROZ ---
    {
        "id": 31, "nombre": "Paella valenciana", "categoria": "arroz",
        "tiempo": "60 min", "dificultad": "Alta", "calorias_aprox": 520,
        "ingredientes": ["400 g de arroz bomba", "300 g de pollo en trocos", "300 g de conejo", "200 g de judías verdes", "200 g de garrofón", "100 g de tomate natural rallado", "Azafrán", "Pimentón dulce", "Aceite de oliva", "Sal"],
        "instrucciones": ["Sofreír el pollo y el conejo hasta dorar.", "Añadir las judías y el garrofón. Rehogar.", "Incorporar el tomate y el pimentón. Sofreír 2 min.", "Añadir agua hirviendo (doble volumen que el arroz) y azafrán.", "Distribuir el arroz y cocer 18 min sin remover."]
    },
    {
        "id": 32, "nombre": "Risotto de setas", "categoria": "arroz",
        "tiempo": "35 min", "dificultad": "Media", "calorias_aprox": 420,
        "ingredientes": ["300 g de arroz Arborio", "300 g de setas variadas", "1 cebolla", "100 ml de vino blanco", "800 ml de caldo de verduras caliente", "50 g de parmesano rallado", "30 g de mantequilla", "Aceite de oliva"],
        "instrucciones": ["Sofreír la cebolla en aceite. Añadir las setas.", "Incorporar el arroz y tostar 2 min.", "Verter el vino. Absorber removiendo.", "Añadir el caldo cazo a cazo, removiendo sin parar.", "Fuera del fuego, añadir mantequilla y parmesano."]
    },
    {
        "id": 33, "nombre": "Arroz con leche", "categoria": "arroz",
        "tiempo": "45 min", "dificultad": "Fácil", "calorias_aprox": 280,
        "ingredientes": ["200 g de arroz redondo", "1 L de leche entera", "150 g de azúcar", "1 rama de canela", "Piel de limón", "Canela molida"],
        "instrucciones": ["Hervir el arroz en agua 5 min. Escurrir.", "Calentar la leche con la canela y la piel de limón.", "Añadir el arroz y cocer a fuego bajo 30-35 min removiendo.", "Incorporar el azúcar los últimos 5 min.", "Enfriar y espolvorear con canela molida."]
    },
    {
        "id": 34, "nombre": "Arroz negro con calamar", "categoria": "arroz",
        "tiempo": "50 min", "dificultad": "Media", "calorias_aprox": 450,
        "ingredientes": ["350 g de arroz bomba", "500 g de calamares", "4 sobres de tinta de calamar", "1 cebolla", "3 dientes de ajo", "200 ml de vino blanco", "700 ml de caldo de pescado", "Aceite de oliva"],
        "instrucciones": ["Limpiar y trocear los calamares. Saltear en aceite.", "Sofreír cebolla y ajo. Añadir los calamares.", "Añadir el vino y la tinta. Reducir.", "Incorporar el arroz y el caldo caliente.", "Cocer 18 min a fuego medio."]
    },
    {
        "id": 35, "nombre": "Arroz con verduras al curry", "categoria": "arroz",
        "tiempo": "30 min", "dificultad": "Fácil", "calorias_aprox": 360,
        "ingredientes": ["300 g de arroz basmati", "1 pimiento rojo", "1 calabacín", "1 zanahoria", "200 g de guisantes", "2 cucharaditas de curry", "400 ml de leche de coco", "Aceite de oliva"],
        "instrucciones": ["Sofreír las verduras cortadas en dados.", "Añadir el curry y rehogar 1 min.", "Incorporar el arroz lavado y la leche de coco.", "Añadir agua hasta doble volumen del arroz.", "Cocer 18 min tapado a fuego bajo."]
    },
    {
        "id": 36, "nombre": "Arroz tres delicias", "categoria": "arroz",
        "tiempo": "25 min", "dificultad": "Fácil", "calorias_aprox": 380,
        "ingredientes": ["300 g de arroz cocido del día anterior", "3 huevos", "100 g de guisantes cocidos", "100 g de zanahoria cocida", "100 g de jamón cocido en dados", "Salsa de soja", "Aceite de sésamo"],
        "instrucciones": ["Calentar aceite en wok a fuego alto.", "Scramble los huevos. Retirar.", "Saltear el arroz hasta que esté suelto.", "Añadir guisantes, zanahoria y jamón.", "Incorporar los huevos y la salsa de soja. Mezclar."]
    },

    # --- LEGUMBRES ---
    {
        "id": 37, "nombre": "Cocido madrileño", "categoria": "legumbres",
        "tiempo": "180 min", "dificultad": "Alta", "calorias_aprox": 620,
        "ingredientes": ["400 g de garbanzos secos", "300 g de morcillo de ternera", "200 g de chorizo", "200 g de morcilla", "2 huesos de jamón", "3 patatas", "2 zanahorias", "1 repollo"],
        "instrucciones": ["Remojar los garbanzos 12 horas.", "Cocer las carnes y los huesos en agua fría 1 hora.", "Añadir los garbanzos y verduras. Cocer 1,5 horas más.", "Servir primero el caldo como sopa, luego el resto."]
    },
    {
        "id": 38, "nombre": "Lentejas estofadas con chorizo", "categoria": "legumbres",
        "tiempo": "50 min", "dificultad": "Fácil", "calorias_aprox": 450,
        "ingredientes": ["350 g de lentejas pardinas", "150 g de chorizo", "2 zanahorias", "1 cebolla", "3 dientes de ajo", "1 pimiento verde", "1 hoja de laurel", "Pimentón dulce", "Aceite de oliva"],
        "instrucciones": ["Poner las lentejas con agua fría, verduras, chorizo y laurel.", "Llevar a ebullición. Bajar el fuego.", "Sofreír el ajo con pimentón y añadir a las lentejas.", "Cocer 35-40 min hasta que estén tiernas.", "Rectificar de sal y servir."]
    },
    {
        "id": 39, "nombre": "Hummus casero", "categoria": "legumbres",
        "tiempo": "10 min", "dificultad": "Fácil", "calorias_aprox": 180,
        "ingredientes": ["400 g de garbanzos cocidos", "3 cucharadas de tahini", "Zumo de 2 limones", "2 dientes de ajo", "4 cucharadas de aceite de oliva", "Comino", "Sal", "Agua fría"],
        "instrucciones": ["Triturar el ajo con el tahini y el zumo de limón.", "Añadir los garbanzos y triturar.", "Incorporar el aceite y comino.", "Ajustar textura con agua fría.", "Servir con aceite por encima y pimentón."]
    },
    {
        "id": 40, "nombre": "Alubias blancas con almejas", "categoria": "legumbres",
        "tiempo": "40 min", "dificultad": "Media", "calorias_aprox": 390,
        "ingredientes": ["400 g de alubias blancas cocidas", "500 g de almejas", "4 dientes de ajo", "1 cebolla", "100 ml de vino blanco", "Perejil fresco", "Aceite de oliva", "Sal"],
        "instrucciones": ["Limpiar las almejas en agua con sal.", "Sofreír cebolla y ajo. Añadir las alubias.", "Incorporar el vino y las almejas.", "Tapar y cocer hasta que abran las almejas.", "Espolvorear perejil y servir."]
    },
    {
        "id": 41, "nombre": "Dal de lentejas rojas", "categoria": "legumbres",
        "tiempo": "35 min", "dificultad": "Fácil", "calorias_aprox": 320,
        "ingredientes": ["300 g de lentejas rojas", "400 ml de leche de coco", "400 g de tomate triturado", "1 cebolla", "3 dientes de ajo", "1 cucharadita de cúrcuma", "1 cucharadita de comino", "Cilantro fresco"],
        "instrucciones": ["Sofreír cebolla y ajo con las especias.", "Añadir las lentejas, el tomate y la leche de coco.", "Incorporar 400 ml de agua.", "Cocer 25 min removiendo hasta que estén deshechas.", "Servir con cilantro fresco."]
    },
    {
        "id": 42, "nombre": "Garbanzos con espinacas", "categoria": "legumbres",
        "tiempo": "25 min", "dificultad": "Fácil", "calorias_aprox": 310,
        "ingredientes": ["400 g de garbanzos cocidos", "300 g de espinacas frescas", "4 dientes de ajo", "1 cucharadita de comino", "1 cucharadita de pimentón", "3 cucharadas de aceite de oliva", "Sal"],
        "instrucciones": ["Dorar el ajo en aceite.", "Añadir el comino y pimentón. Rehogar 30 seg.", "Incorporar los garbanzos y rehogar 3 min.", "Añadir las espinacas y cocer hasta que se marchiten.", "Rectificar sal y servir."]
    },

    # --- PASTA / QUINOA ---
    {
        "id": 43, "nombre": "Pasta carbonara", "categoria": "pasta",
        "tiempo": "20 min", "dificultad": "Media", "calorias_aprox": 560,
        "ingredientes": ["400 g de espaguetis", "150 g de panceta o guanciale", "4 yemas de huevo", "80 g de pecorino romano rallado", "Pimienta negra abundante", "Sal"],
        "instrucciones": ["Cocer la pasta en agua con sal al dente.", "Freír la panceta hasta que esté crujiente.", "Mezclar yemas con pecorino y pimienta negra.", "Fuera del fuego, añadir la mezcla a la pasta con agua de cocción.", "Remover hasta obtener una salsa cremosa."]
    },
    {
        "id": 44, "nombre": "Pasta al pesto genovés", "categoria": "pasta",
        "tiempo": "15 min", "dificultad": "Fácil", "calorias_aprox": 480,
        "ingredientes": ["400 g de linguine", "50 g de albahaca fresca", "50 g de piñones", "50 g de parmesano", "2 dientes de ajo", "100 ml de aceite de oliva virgen extra", "Sal"],
        "instrucciones": ["Triturar albahaca, piñones, ajo y sal.", "Añadir parmesano y aceite poco a poco.", "Cocer la pasta al dente.", "Mezclar con el pesto añadiendo agua de cocción.", "Servir con parmesano extra."]
    },
    {
        "id": 45, "nombre": "Lasaña boloñesa", "categoria": "pasta",
        "tiempo": "90 min", "dificultad": "Media", "calorias_aprox": 580,
        "ingredientes": ["12 placas de lasaña", "400 g de carne picada mixta", "400 g de tomate triturado", "1 cebolla", "2 zanahorias", "100 ml de vino tinto", "500 ml de bechamel", "Parmesano rallado"],
        "instrucciones": ["Preparar la boloñesa: sofreír verduras, añadir carne, vino y tomate. Cocer 30 min.", "Hacer la bechamel.", "Montar: capa de boloñesa, pasta, bechamel. Repetir.", "Cubrir con parmesano.", "Hornear a 180°C durante 40 min."]
    },
    {
        "id": 46, "nombre": "Macarrones con tomate y atún", "categoria": "pasta",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 420,
        "ingredientes": ["400 g de macarrones", "2 latas de atún en aceite", "400 g de tomate frito", "1 cebolla", "2 dientes de ajo", "Aceite de oliva", "Sal"],
        "instrucciones": ["Cocer los macarrones al dente.", "Sofreír cebolla y ajo 5 min.", "Añadir el tomate frito. Cocer 5 min.", "Incorporar el atún escurrido.", "Mezclar con la pasta y servir."]
    },
    {
        "id": 47, "nombre": "Pasta con salmón y nata", "categoria": "pasta",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 550,
        "ingredientes": ["400 g de tagliatelle", "200 g de salmón ahumado", "200 ml de nata para cocinar", "1 cebolla morada", "Eneldo fresco", "Zumo de limón", "Aceite de oliva"],
        "instrucciones": ["Sofreír la cebolla morada 4 min.", "Añadir la nata y reducir 3 min.", "Incorporar el salmón en trozos.", "Cocer la pasta al dente.", "Mezclar pasta con la salsa. Añadir eneldo y limón."]
    },
    {
        "id": 48, "nombre": "Quinoa con aguacate y edamame", "categoria": "pasta",
        "tiempo": "25 min", "dificultad": "Fácil", "calorias_aprox": 380,
        "ingredientes": ["200 g de quinoa", "1 aguacate", "150 g de edamame cocido", "100 g de tomates cherry", "Zumo de limón", "Aceite de oliva virgen", "Sal y pimienta", "Cilantro"],
        "instrucciones": ["Lavar la quinoa y cocer con el doble de agua 15 min.", "Enfriar la quinoa.", "Mezclar con edamame, tomates cherry partidos y aguacate en dados.", "Aliñar con limón, aceite, sal y cilantro."]
    },
    {
        "id": 49, "nombre": "Fideuà de marisco", "categoria": "pasta",
        "tiempo": "45 min", "dificultad": "Media", "calorias_aprox": 480,
        "ingredientes": ["400 g de fideos del número 2", "300 g de gambas", "300 g de mejillones", "200 g de calamares", "1 L de caldo de pescado", "3 dientes de ajo", "Pimentón dulce", "Aceite de oliva"],
        "instrucciones": ["Sofreír el marisco. Retirar.", "Tostar los fideos en aceite hasta dorarlos.", "Añadir ajo y pimentón. Rehogar.", "Incorporar el caldo caliente. Cocer 8 min.", "Añadir el marisco y terminar en horno 5 min."]
    },
    {
        "id": 50, "nombre": "Ñoquis con gorgonzola y nueces", "categoria": "pasta",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 490,
        "ingredientes": ["500 g de ñoquis frescos", "150 g de queso gorgonzola", "100 ml de nata", "50 g de nueces", "Pimienta negra", "Sal"],
        "instrucciones": ["Cocer los ñoquis en agua con sal.", "Fundir el gorgonzola con la nata a fuego bajo.", "Triturar groseramente las nueces.", "Mezclar los ñoquis con la salsa.", "Añadir nueces y pimienta negra abundante."]
    },

    # --- DESAYUNO / SNACK ---
    {
        "id": 51, "nombre": "Tostadas con aguacate y huevo pochado", "categoria": "desayuno",
        "tiempo": "15 min", "dificultad": "Media", "calorias_aprox": 380,
        "ingredientes": ["2 rebanadas de pan de masa madre", "1 aguacate maduro", "2 huevos", "Zumo de limón", "Sal en escamas", "Pimiento rojo picado", "Aceite de oliva"],
        "instrucciones": ["Tostar el pan.", "Aplasatar el aguacate con limón y sal.", "Pochar los huevos: calentar agua con vinagre, remolino, verter el huevo 3 min.", "Untar el aguacate en el pan. Colocar el huevo encima.", "Añadir sal en escamas y pimiento."]
    },
    {
        "id": 52, "nombre": "Overnight oats con frutas", "categoria": "desayuno",
        "tiempo": "10 min", "dificultad": "Fácil", "calorias_aprox": 340,
        "ingredientes": ["80 g de copos de avena", "250 ml de leche o bebida vegetal", "1 cucharada de chía", "1 cucharada de miel", "Frutas del bosque", "Plátano en rodajas", "Mantequilla de cacahuete"],
        "instrucciones": ["Mezclar la avena con la leche, la chía y la miel.", "Remover bien.", "Refrigerar toda la noche en un tarro.", "Por la mañana, añadir las frutas y la mantequilla de cacahuete."]
    },
    {
        "id": 53, "nombre": "Smoothie bowl de frutas tropicales", "categoria": "desayuno",
        "tiempo": "10 min", "dificultad": "Fácil", "calorias_aprox": 290,
        "ingredientes": ["1 mango congelado", "1 plátano congelado", "100 ml de leche de coco", "Granola", "Kiwi en rodajas", "Coco rallado", "Semillas de chía"],
        "instrucciones": ["Triturar el mango y el plátano congelados con la leche de coco.", "Verter en un bol.", "Decorar con granola, kiwi, coco rallado y semillas de chía."]
    },
    {
        "id": 54, "nombre": "Pancakes de avena con arándanos", "categoria": "desayuno",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 350,
        "ingredientes": ["100 g de copos de avena molidos", "2 huevos", "150 ml de leche", "1 cucharadita de levadura", "Miel", "Arándanos frescos", "Aceite de coco"],
        "instrucciones": ["Mezclar avena, huevos, leche y levadura.", "Calentar aceite en sartén a fuego medio.", "Verter pequeñas porciones. Cocinar 2 min por lado.", "Servir con miel y arándanos."]
    },

    # --- SOPAS ---
    {
        "id": 55, "nombre": "Sopa de ajo castellana", "categoria": "sopa",
        "tiempo": "25 min", "dificultad": "Fácil", "calorias_aprox": 240,
        "ingredientes": ["6 dientes de ajo", "150 g de pan del día anterior", "2 huevos", "1 L de caldo de pollo", "1 cucharadita de pimentón", "Aceite de oliva", "Sal"],
        "instrucciones": ["Freír el ajo en aceite hasta dorar.", "Añadir el pan en rebanadas y tostar.", "Añadir el pimentón (fuera del fuego 30 seg).", "Verter el caldo caliente. Cocer 10 min.", "Hacer un huevo escalfado dentro. Cocer 2 min."]
    },
    {
        "id": 56, "nombre": "Caldo de verduras reconfortante", "categoria": "sopa",
        "tiempo": "60 min", "dificultad": "Fácil", "calorias_aprox": 80,
        "ingredientes": ["2 zanahorias", "2 ramas de apio", "1 cebolla", "1 puerro", "1 nabo", "Perejil fresco", "Pimienta en grano", "Sal"],
        "instrucciones": ["Lavar y trocear todas las verduras.", "Poner en una olla con 2 L de agua fría.", "Llevar a ebullición y cocer 45 min a fuego lento.", "Colar y ajustar de sal.", "Servir solo o con fideos."]
    },
    {
        "id": 57, "nombre": "Crema de guisantes con menta", "categoria": "sopa",
        "tiempo": "20 min", "dificultad": "Fácil", "calorias_aprox": 190,
        "ingredientes": ["500 g de guisantes congelados", "1 cebolla", "500 ml de caldo de verduras", "Menta fresca", "100 ml de nata", "Aceite de oliva", "Sal y pimienta"],
        "instrucciones": ["Sofreír la cebolla 5 min.", "Añadir los guisantes y el caldo. Cocer 10 min.", "Triturar con la menta hasta obtener una crema.", "Añadir la nata. Calentar sin hervir.", "Servir con unas hojas de menta frescas."]
    },
    {
        "id": 58, "nombre": "Minestrone italiano", "categoria": "sopa",
        "tiempo": "50 min", "dificultad": "Media", "calorias_aprox": 280,
        "ingredientes": ["200 g de judías blancas cocidas", "2 zanahorias", "2 ramas de apio", "1 calabacín", "400 g de tomate triturado", "100 g de pasta pequeña", "1 cebolla", "Albahaca y parmesano"],
        "instrucciones": ["Sofreír cebolla, zanahoria y apio.", "Añadir calabacín y tomate. Cocer 10 min.", "Incorporar las judías y caldo. Cocer 20 min.", "Añadir la pasta y cocer hasta al dente.", "Servir con albahaca y parmesano."]
    },

    # --- ENSALADAS ---
    {
        "id": 59, "nombre": "Ensalada César con pollo", "categoria": "ensalada",
        "tiempo": "20 min", "dificultad": "Media", "calorias_aprox": 400,
        "ingredientes": ["200 g de lechuga romana", "1 pechuga de pollo", "50 g de parmesano", "Crutones de pan", "Para la salsa: 2 anchoas, 1 ajo, zumo de limón, mostaza, mayonesa, parmesano"],
        "instrucciones": ["Asar la pechuga a la plancha. Dejar reposar y laminar.", "Hacer la salsa César triturando todos los ingredientes.", "Cortar la lechuga y mezclar con la salsa.", "Añadir el pollo, parmesano y crutones."]
    },
    {
        "id": 60, "nombre": "Ensalada de quinoa con feta y remolacha", "categoria": "ensalada",
        "tiempo": "25 min", "dificultad": "Fácil", "calorias_aprox": 340,
        "ingredientes": ["150 g de quinoa", "200 g de remolacha cocida", "100 g de queso feta", "50 g de nueces", "Rúcula", "Aceite de oliva", "Vinagre balsámico", "Miel"],
        "instrucciones": ["Cocer la quinoa y enfriar.", "Cortar la remolacha en dados.", "Mezclar quinoa, remolacha y rúcula.", "Añadir feta desmiagdo y nueces.", "Aliñar con aceite, balsámico y miel."]
    },

    # --- POSTRES ---
    {
        "id": 61, "nombre": "Flan de huevo casero", "categoria": "postre",
        "tiempo": "90 min", "dificultad": "Media", "calorias_aprox": 220,
        "ingredientes": ["4 huevos", "4 yemas", "500 ml de leche entera", "150 g de azúcar", "1 vaina de vainilla", "Para el caramelo: 100 g de azúcar"],
        "instrucciones": ["Hacer el caramelo en el molde.", "Calentar la leche con la vainilla.", "Batir huevos y yemas con azúcar. Añadir la leche.", "Verter en el molde.", "Hornear al baño María a 160°C durante 60 min."]
    },
    {
        "id": 62, "nombre": "Mousse de chocolate", "categoria": "postre",
        "tiempo": "30 min", "dificultad": "Media", "calorias_aprox": 380,
        "ingredientes": ["200 g de chocolate negro 70%", "4 huevos", "50 g de azúcar", "Pizca de sal"],
        "instrucciones": ["Fundir el chocolate al baño María.", "Separar claras de yemas. Batir yemas con azúcar.", "Montar las claras a punto de nieve.", "Mezclar el chocolate con las yemas.", "Incorporar las claras con movimientos envolventes. Refrigerar 2 horas."]
    },
    {
        "id": 63, "nombre": "Tarta de queso al horno", "categoria": "postre",
        "tiempo": "60 min", "dificultad": "Media", "calorias_aprox": 420,
        "ingredientes": ["500 g de queso crema", "150 g de azúcar", "3 huevos", "200 ml de nata", "2 cucharadas de harina", "1 cucharadita de esencia de vainilla"],
        "instrucciones": ["Precalentar el horno a 200°C.", "Mezclar todos los ingredientes hasta obtener una crema lisa.", "Verter en molde forrado con papel.", "Hornear 35 min (debe quedar tembloroso en el centro).", "Enfriar completamente antes de desmoldar."]
    },
    {
        "id": 64, "nombre": "Natillas de vainilla", "categoria": "postre",
        "tiempo": "25 min", "dificultad": "Media", "calorias_aprox": 200,
        "ingredientes": ["500 ml de leche", "4 yemas de huevo", "100 g de azúcar", "2 cucharadas de maicena", "1 vaina de vainilla", "Canela molida"],
        "instrucciones": ["Calentar la leche con la vainilla.", "Batir yemas con azúcar y maicena.", "Verter la leche caliente poco a poco sobre las yemas.", "Cocinar a fuego bajo removiendo hasta espesar.", "Verter en cuencos y espolvorear canela."]
    },
    {
        "id": 65, "nombre": "Crema catalana", "categoria": "postre",
        "tiempo": "30 min", "dificultad": "Media", "calorias_aprox": 250,
        "ingredientes": ["500 ml de leche entera", "6 yemas de huevo", "120 g de azúcar", "40 g de maicena", "Piel de limón", "1 rama de canela", "Azúcar para quemar"],
        "instrucciones": ["Infusionar la leche con limón y canela 10 min.", "Batir las yemas con azúcar y maicena.", "Añadir la leche colada poco a poco.", "Cocer a fuego bajo removiendo hasta espesar.", "Enfriar. Espolvorear azúcar y quemar con soplete."]
    },
]

output = {"recetas": recetas}
path = os.path.join(os.path.dirname(__file__), "data", "recipes_large.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"OK: {len(recetas)} recetas reales guardadas en {path}")
