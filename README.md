# API REST de avistamientos de aves

Trabajo en clase de Ingeniería de Software 2 (ISW-2), Sesión 17. Trabajo individual.

API REST pequeña para registrar avistamientos de aves. Está hecha con **Python + Flask** y guarda los datos en **SQLite** (módulo `sqlite3` de la librería estándar). Recibe y responde JSON.

Incluye los dos puntos opcionales del enunciado: el endpoint `GET /avistamientos/resumen` y pruebas automáticas con `pytest`.

**Taller de pruebas:** la regla de negocio de los avistamientos está separada en `validador.py` y se prueba en dos niveles (unitarias e integración) con medición de cobertura. El análisis completo está en [`docs/justificacion-pruebas.md`](docs/justificacion-pruebas.md). Comandos rápidos:

```bash
pytest                                                                    # correr todas las pruebas
pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing   # cobertura
```

## Requisitos previos

Antes de instalar o ejecutar nada, necesitas tener esto en tu computador:

| Tecnología | Versión        | Para qué se usa                          | Cómo verificarla                                   |
|------------|----------------|------------------------------------------|----------------------------------------------------|
| Python     | 3.9 o superior | Lenguaje en el que está hecha la API     | `python --version`                                 |
| pip        | Viene con Python | Instalar las librerías del proyecto    | `pip --version`                                    |
| Git        | Cualquiera reciente | Clonar el repositorio               | `git --version`                                    |
| curl       | Cualquiera reciente | Probar los endpoints desde la terminal | `curl --version` (en Windows: `curl.exe --version`) |

**Se instalan con `pip install -r requirements.txt`** (no hay que instalarlas a mano):

- **Flask** 3.0 o superior: framework web de la API.
- **pytest** 8.0 o superior: pruebas automáticas.
- **pytest-cov** 5.0 o superior: medición de cobertura de las pruebas.

**Ya viene con Python, no hay que instalar nada:**

- **SQLite** (módulo `sqlite3`): base de datos embebida. El archivo `avistamientos.db` se crea solo al ejecutar la API.

Notas:

- **Windows:** al instalar Python marca la casilla **"Add Python to PATH"**. En PowerShell usa `curl.exe` y no `curl`, porque `curl` es un alias de otro comando.
- **Linux / macOS:** el comando puede ser `python3` y `pip3` en lugar de `python` y `pip`.
- **Opcional:** Postman o la extensión Thunder Client de VS Code, si prefieres probar con interfaz gráfica en lugar de curl.

## Instalación y ejecución

Sigue los pasos en orden, desde una terminal. Con los requisitos previos ya instalados, tarda unos minutos.

### Paso 1. Clonar el repositorio

```bash
git clone https://github.com/mvalentinao/aves-api-rest.git
cd aves-api-rest
```

### Paso 2. Crear el entorno virtual

El entorno virtual mantiene las librerías del proyecto separadas del resto de tu computador. Es recomendado, no obligatorio.

```bash
python -m venv .venv
```

### Paso 3. Activar el entorno virtual

| Sistema                | Comando                      |
|------------------------|------------------------------|
| Linux / macOS          | `source .venv/bin/activate`  |
| Windows (CMD)          | `.venv\Scripts\activate`     |
| Windows (PowerShell)   | `.venv\Scripts\Activate.ps1` |

Sabrás que quedó activo porque el inicio de la línea de la terminal muestra `(.venv)`.

> Si PowerShell bloquea el script de activación, usa CMD o salta este paso y continúa con el Paso 4.

### Paso 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Al final debe aparecer una línea `Successfully installed ...` con Flask, pytest y pytest-cov.

### Paso 5. Verificar con las pruebas (opcional, recomendado)

```bash
pytest
```

Debe terminar con `63 passed`. Las pruebas usan una base de datos temporal, así que no afectan tus datos.

### Paso 6. Cargar datos de ejemplo (opcional)

Para llenar la base de datos con 22 avistamientos de ejemplo y tener qué consultar:

```bash
python seed.py
```

Si la base ya tiene datos, no hace nada y avisa. Para borrar todo y volver a cargar los ejemplos: `python seed.py --reiniciar`.

### Paso 7. Ejecutar la API

```bash
python app.py
```

Debe aparecer una línea como `Running on http://127.0.0.1:5000`. El aviso de "development server" que la acompaña es normal. **Deja esta terminal abierta**: la API funciona mientras esté corriendo. Para detenerla, presiona `Ctrl+C`.

El archivo de base de datos `avistamientos.db` se crea solo la primera vez que se ejecuta.

### Paso 8. Comprobar que funciona

Con la API corriendo, abre en el navegador:

```
http://127.0.0.1:5000/avistamientos
```

Debe mostrar la lista en JSON (`[]` si la base está vacía). Abrir solo `http://127.0.0.1:5000/` muestra "Not Found": es normal, la API no tiene nada en esa ruta.

Para probar el resto de endpoints, abre **otra terminal** (deja la primera corriendo) y sigue la sección [Endpoints](#endpoints).

## Modelo

| Campo        | Descripción                                   |
|--------------|-----------------------------------------------|
| `id`         | Lo asigna el sistema                          |
| `especie`    | Nombre de la especie (ej. `"colibrí"`)        |
| `lugar`      | Dónde se observó                              |
| `fecha`      | Texto en formato `AAAA-MM-DD`                 |
| `observador` | Quién lo registró                             |

En `POST` y `PUT` los cuatro campos (`especie`, `lugar`, `fecha`, `observador`) son obligatorios y deben ser texto no vacío. La regla de negocio (en `validador.py`) es:

- La `especie` tiene entre **3 y 50 caracteres** (sin contar los espacios del inicio y del final).
- La `fecha` tiene formato `AAAA-MM-DD`, es una fecha real (no `2026-02-30`) y **no es posterior a hoy**.
- `lugar` y `observador` no están vacíos.

Si algo no se cumple, la API responde `400` con un mensaje que indica qué campo falló (si fallan varios, los junta separados por `;`). Si el cuerpo trae un `id`, se ignora: lo asigna el sistema.

## Endpoints

| Operación                  | Petición                     | Respuesta                                   |
|----------------------------|------------------------------|---------------------------------------------|
| Listar todos               | `GET /avistamientos`         | `200` con la lista en JSON                  |
| Ver uno                    | `GET /avistamientos/{id}`    | `200` con el avistamiento, o `404`          |
| Registrar                  | `POST /avistamientos`        | `201` con el avistamiento creado, o `400`   |
| Actualizar                 | `PUT /avistamientos/{id}`    | `200` con el avistamiento, o `404` (`400` si los datos no son válidos) |
| Eliminar                   | `DELETE /avistamientos/{id}` | `204` sin contenido, o `404`                |
| Resumen (bonus)            | `GET /avistamientos/resumen` | `200` con el conteo de avistamientos por especie |

### Ejemplos con curl (Linux, macOS, Git Bash)

**Listar todos** (`200`)

```bash
curl -i http://127.0.0.1:5000/avistamientos
```

**Ver uno** (`200`, o `404` si no existe)

```bash
curl -i http://127.0.0.1:5000/avistamientos/1
```

**Registrar** (`201`, o `400` si faltan datos)

```bash
curl -i -X POST http://127.0.0.1:5000/avistamientos \
  -H "Content-Type: application/json" \
  -d '{"especie": "colibrí", "lugar": "Parque Nacional Chingaza", "fecha": "2026-09-29", "observador": "Pablo"}'
```

**Actualizar** (`200`, o `404` si no existe)

```bash
curl -i -X PUT http://127.0.0.1:5000/avistamientos/1 \
  -H "Content-Type: application/json" \
  -d '{"especie": "colibrí", "lugar": "Jardín Botánico de Bogotá", "fecha": "2026-09-30", "observador": "Pablo"}'
```

**Eliminar** (`204`, o `404` si no existe)

```bash
curl -i -X DELETE http://127.0.0.1:5000/avistamientos/1
```

**Resumen por especie** (`200`)

```bash
curl -i http://127.0.0.1:5000/avistamientos/resumen
```

### Ejemplos en Windows (PowerShell)

PowerShell rompe las comillas del JSON y no envía bien las tildes si el JSON se escribe en la línea de `curl.exe`. Lo más seguro es guardar el JSON en un archivo y enviarlo con `--data-binary`. Los comandos sin cuerpo (`GET` y `DELETE`) son iguales que arriba, usando `curl.exe` en lugar de `curl`.

**Registrar**

```powershell
@'
{"especie": "colibrí", "lugar": "Parque Nacional Chingaza", "fecha": "2026-09-29", "observador": "Pablo"}
'@ | Set-Content -Encoding utf8 body.json

curl.exe -i -X POST http://127.0.0.1:5000/avistamientos -H "Content-Type: application/json" --data-binary "@body.json"
```

**Actualizar**

```powershell
@'
{"especie": "colibrí", "lugar": "Jardín Botánico de Bogotá", "fecha": "2026-09-30", "observador": "Pablo"}
'@ | Set-Content -Encoding utf8 cambio.json

curl.exe -i -X PUT http://127.0.0.1:5000/avistamientos/1 -H "Content-Type: application/json" --data-binary "@cambio.json"
```

**Listar, ver, eliminar y resumen**

```powershell
curl.exe -i http://127.0.0.1:5000/avistamientos
curl.exe -i http://127.0.0.1:5000/avistamientos/1
curl.exe -i -X DELETE http://127.0.0.1:5000/avistamientos/1
curl.exe -i http://127.0.0.1:5000/avistamientos/resumen
```

### Ejemplos de respuesta

Un avistamiento:

```json
{
  "id": 1,
  "especie": "colibrí",
  "lugar": "Parque Nacional Chingaza",
  "fecha": "2026-09-29",
  "observador": "Pablo"
}
```

Resumen, ordenado de mayor a menor cantidad:

```json
[
  {"especie": "colibrí", "cantidad": 3},
  {"especie": "águila", "cantidad": 1}
]
```

Los errores también se devuelven en JSON, por ejemplo:

```json
{"error": "Faltan datos o son inválidos: lugar, observador"}
{"error": "especie: debe tener entre 3 y 50 caracteres (tiene 2)"}
{"error": "fecha: no puede ser posterior a hoy"}
```

## Pruebas

Con las dependencias instaladas (`pip install -r requirements.txt`), desde la carpeta del proyecto:

**Correr todas las pruebas**

```bash
pytest
```

**Generar la cobertura** (resumen en la terminal, con el número de las líneas que faltan por cubrir)

```bash
pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing
```

El resultado guardado de la última corrida está en `docs/cobertura.txt`. El análisis completo de las pruebas está en [`docs/justificacion-pruebas.md`](docs/justificacion-pruebas.md).

**Correr solo un nivel**

```bash
pytest tests/test_validador.py     # unitarias: regla de negocio y reloj simulado
pytest tests/test_integracion.py   # integración por HTTP: app Flask + SQLite
pytest test_api.py                 # pruebas de la versión anterior de la API
```

Qué hay en cada archivo:

- `tests/test_validador.py`: pruebas unitarias del validador, con partición de equivalencia y valores límite sobre `especie` y `fecha`. Usan un reloj fijo (`RelojFijo`, un stub) para que "hoy" sea siempre el mismo día.
- `tests/test_integracion.py`: pruebas por HTTP de los seis endpoints (`200`, `201`, `204`, `400`, `404`). Verifican el cuerpo completo y el efecto (por ejemplo, después de un `POST`, el `GET` del nuevo id lo devuelve; después de un `DELETE`, da `404`).
- `test_api.py`: las pruebas de la versión anterior de la API (26 pruebas). Se corren aparte con `pytest test_api.py`.

Cada prueba usa una base de datos temporal, así que no tocan `avistamientos.db`.

## Estructura

```
app.py                       # API (endpoints y acceso a SQLite)
validador.py                 # Regla de negocio + interfaz Reloj (sin Flask ni SQLite)
test_api.py                  # Pruebas de la versión anterior (pytest test_api.py)
seed.py                      # Carga datos de ejemplo (opcional)
requirements.txt             # Dependencias (Flask, pytest y pytest-cov)
pytest.ini                   # Configuración de pytest
tests/
  conftest.py                # Fixtures: cliente HTTP, base temporal y reloj fijo
  relojes.py                 # RelojFijo (stub)
  test_validador.py          # Pruebas unitarias
  test_integracion.py        # Pruebas de integración por HTTP
docs/
  justificacion-pruebas.md   # Documento de justificación
  cobertura.txt              # Resultado de la cobertura
.gitignore                   # Excluye la base de datos, caché y entorno virtual
README.md
```

## Uso de IA

Se usó **Claude (Anthropic), modelo Sonnet 5.5**, como apoyo para generar y revisar el código, las pruebas, posteriormente a esto se revisa el codigo y se termina de afianzar el conocimiento sobre el mismo. 