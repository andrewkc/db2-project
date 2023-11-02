Grupo 4 | Proyecto 2 de Base de Datos II (CS2042) | UTEC
# Búsqueda y Recuperación de la Información
## Integrantes y roles
|            Integrante           |  Rol  |
|:-----------------------------------:|:---------:|
|  Arteaga Montes, Stuart Diego [@SDAM26](https://github.com/SDAM26)     |  Backend  |
|    Cahuana Condori, Kelvin Andreí [@andrewkc](https://github.com/andrewkc) |  Backend  |
|   Callinapa Chunga, Johan Fabian [@johancalli](https://github.com/johancalli)     |  Frontend  |
|   Rivas Chavez, Dimael Antonio [@artrivas](https://github.com/artrivas)       | Backend  |

## 1. Introducción
### Descripción de los datos
Los datos obtendidos para este proyecto han sido obtenidos de la plataforma de Kaggle [Fashion Product Images Dataset](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset/data).
Este dataset cuenta con imágenes, múltiples atributos de etiqueta que describen el producto que se ingresó y también con texto descriptivo que comenta las características del producto.

### Librerías utilizadas
* Pandas: Para procesar la data de los archivos csv.
* Psycopg2: Para la conexión entre nuestro backend con la base de datos.
* Nltk: Nos proporciona herramientas y recursos para trabajar con datos de lenguaje natural.
* Fastapi: Para el desarrollo del backend
  
## 2. Backend:
### Construcción del índice invertido
retrieve_k_nearest
### Manejo de memoria secundaria
### Ejecución óptima de consultas o Análisis de la maldición de la dimensionalidad y como mitigarlo
### Incluir imágenes/diagramas para una mejor comprensión.

### Diseño del índice con PostgreSQL
```python
def create_index(tablename='product'):
    conn = psycopg2.connect(
        host=getenv("HOST"),
        port=getenv("PORT"),
        dbname=getenv("DBNAME"),
        user=getenv("USER"),
        password=getenv("PASSWORD")
    )

    cursor = conn.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')

    cursor.execute(f"ALTER TABLE {tablename} ADD COLUMN indexed tsvector;")
    cursor.execute(f"""UPDATE {tablename} SET indexed = T.indexed FROM (
                    SELECT id, setweight(to_tsvector('english', name), 'A') || setweight(to_tsvector('english', content), 'B') AS indexed FROM {tablename}
                   ) AS T WHERE {tablename}.id = T.id;""")
    cursor.execute('CREATE INDEX IF NOT EXISTS content_idx_gin ON product USING gin (indexed);')

    conn.commit()
    cursor.close()
    conn.close()
```
## 3. Frontend:
### Screenshots de la GUI
![gui](assets/gui.png)
![gui2](assets/gui2.png)
![gui3](assets/gui3.png)

## 4. Experimentación
### Tablas y gráficos de los resultados
Tiempo de ejecución promedio en ms.
| N (registros) | PostgreSQL Index | MyIndex |
|-----------|-----------|-----------|
| 1000   |  1.351 ms   |  141.44 ms |
| 2000   |  2.664 ms  |  154.774 ms   |
| 4000   |  4.060 ms |  162.761 ms |
| 8000   |  9.645 ms  |  169.530 ms  |
| 16000   | 17.976 ms  | 175.382 ms|
| 32000   |  34.365 ms |   182.124 ms|
| 38000   |  39.454 ms|   186.397 ms|
| 44424   |  45.033 ms |  190.282 ms  |

![comparacion_time](assets/comparacion_time.png)

### Conclusión
* Se realizó un uso de memoria eficiente para la construción del índice invertido
* Se creo el índice de postgres considerando distintos pesos, se dio más peso al nombre del producto que al contenido (todos los demás campos concatenados).
* Al realizar la comparación de tiempos de ejecución se evidencio que el índice de postgres es mejor que el nuestro.
