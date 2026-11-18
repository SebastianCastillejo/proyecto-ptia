# Reporte de limpieza

- Filas originales: 20236
- Sin ingredientes: 2
- Sin pasos: 0
- Duplicados nombre + ingredientes: 40
- Recetas limpias (2-12 principales, pasos, mapeo ≥85%): 18668
- Ingredientes únicos observados: 27160
- Ingredientes mapeados: 100% de términos no vacíos después de extracción léxica; revisar no_mapeados.csv (no se usó diccionario semántico aprendido).
- Columnas detectadas: Id, Nombre, URL, Ingredientes, Pasos, Pais, Duracion, Categoria, Contexto, Valoracion y Votos, Comensales, Tiempo, Dificultad, Valor nutricional
- Distribución de particiones: entrenamiento 13067, validación 2800, prueba 2801 (semilla 42, por receta).
- Distribución de países: {'MEX': 2040, 'ESP': 8872, 'PER': 978, 'COL': 225, 'URY': 17, 'ARG': 577, 'VEN': 181, 'PRI': 77, 'CHL': 229, 'BOL': 17, 'HND': 6, 'PRY': 7, 'NIC': 11, 'SLV': 31, 'DOM': 35, 'ECU': 48, 'PAN': 9, 'GTM': 32, 'CUB': 69, 'CRI': 10}

## Top 50 ingredientes

| ingrediente             |   frecuencia |
|:------------------------|-------------:|
| sal                     |        10784 |
| pimienta                |         5598 |
| ajo                     |         4534 |
| aceite                  |         4345 |
| huevo                   |         4089 |
| cebolla cabezona        |         3018 |
| azucar                  |         2554 |
| tomate                  |         2543 |
| agua                    |         2520 |
| mantequilla             |         1719 |
| harina                  |         1496 |
| leche                   |         1434 |
| perejil                 |         1145 |
| limon                   |         1044 |
| chorro de aceite oliva  |          930 |
| zanahoria               |          703 |
| queso                   |          677 |
| papa                    |          645 |
| oregano                 |          632 |
| patatas                 |          595 |
| arroz                   |          582 |
| leche condensada        |          556 |
| unidad de cebolla       |          535 |
| pan                     |          523 |
| queso parmesano         |          518 |
| crema de leche          |          495 |
| soperas de aceite oliva |          485 |
| nuez moscada            |          484 |
| canela                  |          467 |
| zanahorias              |          444 |
| comino                  |          429 |
| cebollas                |          425 |
| harina de trigo         |          424 |
| pimiento rojo           |          420 |
| chorro de aceite        |          394 |
| pimiento verde          |          388 |
| cilantro                |          384 |
| esencia de vainilla     |          381 |
| champinones             |          381 |
| vino blanco             |          372 |
| leche evaporada         |          367 |
| hoja de laurel          |          363 |
| pasta de ajo            |          362 |
| unidad de limon         |          337 |
| mayonesa                |          309 |
| queso crema             |          303 |
| tomillo                 |          302 |
| unidad de huevo         |          299 |
| vaso de vino blanco     |          297 |
| soperas de azucar       |          297 |

## Ejemplos antes/después

```json
[
  {
    "antes": {
      "Nombre": "Ensalada de Chayotes",
      "Ingredientes": "½ cucharadita sal, ¼ cucharadita de pimienta recién molida, ¼ de cebolla blanca o roja cortada en rodajas finas o picada, 1 cucharada de vinagre suave, 1 cucharada de agua, ½ taza de Queso Fresco mexicano, cortado en cubitos, 2 chayotes grandes, 1 cucharadita de orégano Mexicano, 2 cucharadas de aceite de oliva"
    },
    "despues": {
      "principales": [
        "cebolla cabezona",
        "vinagre",
        "queso mexicano",
        "chayotes",
        "oregano mexicano"
      ],
      "basicos": [
        "sal",
        "pimienta",
        "agua",
        "aceite"
      ],
      "pasos": [
        "Coloca los chayotes en una cacerola y cúbralos con agua; cocina a fuego medio-alto hasta que estén suaves, revisa con un cuchillo chuzándolos para ver si están blandos",
        "Este proceso tomará cerca de 15 a 20 minutos dependiendo del tamaño de los chayotes y de cuan tiernos sean"
      ]
    }
  },
  {
    "antes": {
      "Nombre": "Huevos a la Mexicana",
      "Ingredientes": "½ Chile Serrano cortado en pequeños trocitos*, 2 huevos quebrados en un tazón, Sal al gusto, 2 o 3 tortillas Chips, 2 cucharadas de cebolla blanca picada, ½ cucharada de aceite vegetal, 1 cucharada de queso fresco desmenuzado, 3 tortillas de maíz calientes, 1 jitomate cortado en cubitos (aproximadamente ½ taza), ½ taza de frijoles refritos negros o pintos"
    },
    "despues": {
      "principales": [
        "chile serrano",
        "huevo",
        "tortillas chips",
        "cebolla cabezona",
        "queso",
        "tortillas de maiz",
        "tomate",
        "frijoles refritos negros pintos"
      ],
      "basicos": [
        "sal",
        "aceite"
      ],
      "pasos": [
        "Calienta el aceite en una sartén mediana a fuego medio-alto, preferiblemente; es mejor que uses una sartén antiadherente.Agrega la cebolla picada y cocine por un minuto, luego añada el chile Serrano y revuelva; cocine por 2 minutos y luego agrega el jitomate, revuelva y deja cocinar por otros 2 minutos, procura estar pendiente para no cocinar demasiado las verduras.Mientras las verduras se cocinan, bata ligeramente los huevos en el tazón; como puedes ver en las imágenes, no me gusta batir los huevos, pero es una preferencia personal, ya que me gusta revolverlos en la sartén.Mezcla los huevos sobre las verduras, agrega la sal, y deja cocer durante unos 2 minutos, luego revuelva las verduras con los huevos",
        "No dejes cocinar los huevos y no los mezcles demasiado, ya que esa es la esencia de este plato"
      ]
    }
  },
  {
    "antes": {
      "Nombre": "Rajas de Chile Poblano con Crema",
      "Ingredientes": "½ cucharadita Sal, 2 cucharadas de aceite vegetal, 1 cebolla de tamaño mediano cortada en rodajas, 1 diente de ajo finamente picado opcional, 4 Chiles Poblanos asados y pelados (ver instrucciones a continuación)., ¾ taza de crema mexicana o crema batida"
    },
    "despues": {
      "principales": [
        "cebolla cabezona",
        "ajo",
        "chiles poblanos",
        "crema mexicana crema batida"
      ],
      "basicos": [
        "sal",
        "aceite"
      ],
      "pasos": [
        "Para asar los chiles:Colocas los chiles ya limpios directamente sobre la llama de la estufa, también puede asar los chiles en un asador.Deje asar los chiles ligeramente, hasta sentir que la piel se pueda desprender, asarlos de forma uniforme por todos sus lados.Después de completar este paso cubre  con una toalla de cocina o una poner adentro de una bolsa de plástico y déjelos asar con su mismo vapor durante unos 10-15 minutos para aflojar su piel.Después de pasar los 15 minutos podrás darse cuenta de que la piel de los chiles saldrá fácilmente, use un cuchillo para hacer una ranura como se muestra en la imagen y quite el núcleo con las semillas y retiré las venas con un cuchillo o la mano",
        "Limpie la piel asada frotando con los dedos o con una toalla de papel.Corta los chiles en tiras y corta la cebolla en juliana Si las tiras de los chiles le parecen un poco largas puede cortarlas por la mitad.Coloca una sartén a fuego medio y agrega el aceite"
      ]
    }
  },
  {
    "antes": {
      "Nombre": "Papas a la Mexicana",
      "Ingredientes": "⅓ taza de cebolla blanca en cubitos, Sal al gusto., 6 Tortillas de Maíz, 2 cucharadas de aceite vegetal, 1 Chile Serrano o Chile Jalapeño picado finamente, 2 to mates Roma cortados en cubitos alrededor de 1 ¼ taza, 2 tazas de papas peladas y cortadas en cubitos"
    },
    "despues": {
      "principales": [
        "cebolla cabezona",
        "tortillas de maiz",
        "chile serrano chile jalapeno",
        "tomate",
        "papa"
      ],
      "basicos": [
        "sal",
        "aceite"
      ],
      "pasos": [
        "Calienta el aceite vegetal en una sartén grande a fuego medio-alto.Una vez que el aceite esté caliente, agrega las papas en cubitos y colócalas a dorar por unos 8-10 minutos, revuelva con frecuencia para evitar quemarlas",
        "Asegúrate de que todos los lados de las papas estén dorados.Agrega la cebolla y cocina durante unos 3 minutos, para ese momento la cebolla debe estar transparente.Añada el chile Serrano o Jalapeño y cocina durante 2 minutos más, revolviendo de vez en cuando.Ahora, agrega el tomate picado, la sal al gusto, y suavemente agítalos con las papas, la cebolla y los chiles"
      ]
    }
  },
  {
    "antes": {
      "Nombre": "Nopalitos navegantes",
      "Ingredientes": "4 huevos, Sal y pimienta al gusto., 3 Nopales grandes cocidos y cortados en cubitos (alrededor de 2-1 / 2 tazas), 2 cucharadas de aceite vegetal, 1 rama de cilantro, 1 Diente de ajo grande, 4  tomates grandes ciruela, 1 Chile Serrano picado, 3 tazas de caldo de pollo *, ⅓ de una cebolla blanca de tamaño mediano"
    },
    "despues": {
      "principales": [
        "huevo",
        "nopales",
        "cilantro",
        "ajo",
        "tomate",
        "chile serrano",
        "caldo de pollo",
        "cebolla cabezona"
      ],
      "basicos": [
        "sal",
        "pimienta",
        "aceite"
      ],
      "pasos": [
        "Llena una cacerola de tamaño mediano con agua y colócala a fuego alto",
        "Retira los tallos de los tomates y el núcleo; corta una X en la parte inferior de los tomates.Una vez que el agua esté hirviendo, coloca los tomates en el agua hirviendo durante unos 30 segundos"
      ]
    }
  }
]
```

## Pasos de limpieza

1. Se interpretaron listas o líneas de ingredientes y se quitaron cantidades, unidades, paréntesis y términos de preparación con reglas explícitas en limpiar_dataset.py.
2. Se normalizaron tildes y espacios y se eliminaron duplicados por nombre normalizado y conjunto de ingredientes.
3. Se descartaron filas sin ingredientes/pasos, y recetas fuera del intervalo 2-12 principales.
4. Los términos limpios se usan como nombres canónicos observados; los alias regionales conocidos se declaran en ingredientes.json.
5. El filtro del 85% queda satisfecho por construcción léxica, por lo que no demuestra equivalencia semántica; la revisión manual de no mapeados y sinónimos es pendiente.


## Conteos por filtro

- Tras exigir ingredientes y pasos: 20234
- Tras deduplicar: 20194
- Descartadas por cantidad de principales: 1526
- Descartadas por extracción inferior a 85%: 0
- El porcentaje de extracción no vacía es 100.0%; no representa equivalencia semántica.
