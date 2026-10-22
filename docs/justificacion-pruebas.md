# Justificación de las pruebas: API de avistamientos de aves

Taller de pruebas, ISW-2. Python + Flask + SQLite, pruebas con `pytest`.
Resultado: 63 pruebas (35 unitarias y 28 de integración), todas en verde, con 99 % de cobertura de sentencias y ramas.

Dos decisiones de especificación: tomé "AAAAMM-DD" del enunciado como un error de tipeo de `AAAA-MM-DD` (el formato que ya usaba la API), y el largo de la especie se mide sin los espacios de los extremos, porque eso es lo que se guarda.

---

## 1. Qué cambió en el código y por qué lo hace más testeable

| Antes | Después |
|---|---|
| La validación era la función `validar()` dentro de `app.py`, mezclada con rutas y SQL. | Clase `ValidadorDeAvistamiento` en `validador.py`, sin Flask ni `sqlite3`. Devuelve la lista de errores. |
| Solo se revisaba que los campos no estuvieran vacíos y el formato de la fecha. | Reglas nuevas: especie de 3 a 50 caracteres y fecha no posterior a hoy. Cada error nombra el campo que falló. |
| No había forma de controlar "hoy": la regla habría llamado a `datetime.now()` directamente. | Interfaz `Reloj` con `hoy()`, implementación real `RelojSistema` e inyección por constructor. Las pruebas usan un `RelojFijo`. |
| `app.py` armaba el 400 en cada ruta. | `app.py` tiene un objeto `validador` a nivel de módulo (reemplazable en pruebas) y `respuesta_400()`. |
| `get_db()` abría la conexión SQLite y no la cerraba. | `get_db()` confirma y cierra. No era parte del taller, pero llenaba la salida de `ResourceWarning`. |

Por qué es más testeable. Una regla pura (datos de entrada → lista de errores) se prueba en milisegundos sin servidor ni base de datos, y si falla señala la regla exacta. Sacar el reloj de la regla vuelve determinista una entrada que dependía del día real: sin eso no hay una prueba repetible de "la fecha de mañana se rechaza".

Repositorio. No creé una capa de repositorio: el acceso a datos son cinco sentencias SQL sin decisiones, y se prueban mejor con SQLite real (un archivo temporal por prueba) que contra un fake que habría que mantener igual al real. Por eso el único doble es el reloj (sección 4).

---

## 2. Tabla de casos de la Parte A

Técnicas: partición de equivalencia (una prueba por clase) y valores límite, es decir, las fronteras de cada clase (mín−1, mín, mín+1, máx−1, máx, máx+1). "Hoy" está fijo en `2026-10-21` con `RelojFijo`.

Especie (válida entre 3 y 50 caracteres):

| Valor | Tipo | Esperado | Por qué este valor |
|---|---|---|---|
| 2 caracteres | Límite (mín−1) | Error | Fuera de la frontera inferior. |
| 3 caracteres | Límite (mín) | Válida | Primer valor aceptado. |
| 50 caracteres | Límite (máx) | Válida | Último valor aceptado. |
| 51 caracteres | Límite (máx+1) | Error | Fuera de la frontera superior. |
| `"colibrí"` (7) | Representativo | Válida | Centro de la clase válida. |
| `""`, `"   "`, `12345` | Inválido | Error | Vacío, solo espacios y tipo incorrecto. |

Fecha (válida si es AAAA-MM-DD, real y no posterior a hoy):

| Valor | Tipo | Esperado | Por qué este valor |
|---|---|---|---|
| `2026-10-21` (hoy) | Límite | Válida | Hoy no es "posterior a hoy". |
| `2026-10-22` (mañana) | Límite (+1) | Error | Primer día que se rechaza. |
| `29/09/2026` | Inválido (formato) | Error | Clase "formato incorrecto". |
| `2026-02-30` | Inválido (irreal) | Error | Formato correcto, pero la fecha no existe. |
| `2025-02-29` y `2024-02-29` | Inválido (no bisiesto) y representativo (bisiesto) | Error y válida | El 29 de febrero solo existe en años bisiestos. |

Las pruebas incluyen además las otras fronteras (ayer, 4 y 49 caracteres), una fecha futura lejana, más formatos inválidos, lugar y observador vacíos, cuerpos que no son JSON y varios errores a la vez; son variantes de las mismas clases.

---

## 3. Por qué cada nivel

Unitaria: `test_especie_de_51_caracteres_es_rechazada_por_superar_el_maximo`. La regla es una función pura, sin red, archivos ni estado. Cada caso límite cuesta microsegundos (las 35 pruebas corren en 0,05 s), así que puedo cubrir todas las fronteras de la tabla, y si una falla sé que el problema está en la regla y no en Flask ni en SQLite.

Integración: `test_crear_un_avistamiento_valido_responde_201_y_luego_se_puede_consultar`. Cruza la frontera HTTP: ruta, lectura del JSON, validador, INSERT en SQLite y serialización, y comprueba el efecto con un `GET` al id nuevo. Ninguna prueba unitaria verifica que esas piezas estén conectadas.

Integración: `test_crear_con_especie_de_2_caracteres_responde_400_y_no_guarda_nada`. Responde la pregunta clave: ¿qué detecta la integración del POST que la unitaria del validador no?

- Que `crear()` realmente llama al validador y corta antes del INSERT. Si alguien borrara el `if errores:`, las 35 unitarias seguirían en verde y la API guardaría datos inválidos; las de integración fallan (lo comprobé: 10 de 28 se ponen en rojo).
- Que la lista de errores se traduce a status 400 y a un JSON `{"error": "…"}`.
- Detalles que solo existen al integrar: el recorte de espacios antes de guardar, que el `id` del cliente se ignora y que un cuerpo que no es JSON da 400.

Además, `test_con_el_reloj_real_…` usa el cableado de producción (`RelojSistema`) con fechas de 2999 y 2000, para no depender del día de ejecución y comprobar que `app.py` sí inyecta un reloj real.

---

## 4. Los dobles

| Doble | Tipo | Dónde | Por qué |
|---|---|---|---|
| `RelojFijo(date)` | Stub | `tests/relojes.py`; todas las unitarias y el fixture `client` de integración | Entrega una respuesta enlatada a `hoy()`. Solo controlo la entrada; no verifico cómo se llamó. |

Por qué un stub y no otro tipo. El reloj es una entrada indirecta (la regla le pide un dato al entorno), no una salida: no hay interacción que verificar, y un *mock* o un *spy* acoplaría la prueba a la implementación. Un *fake* (versión simplificada pero funcional) tampoco hacía falta: una fecha constante basta.

Sin el doble habría calculado "mañana" con `date.today() + 1 día`:

1. La prueba sería intermitente: cerca de la medianoche, el "hoy" de la prueba y el del validador pueden ser días distintos.
2. Los valores de la tabla no serían fijos (`2026-10-22` hoy, otro valor mañana), y no podría reproducir un fallo.
3. No podría escribir `test_el_resultado_depende_del_reloj_inyectado_…`, que muestra que la misma fecha es válida con un reloj y no con otro.

Lo que no es un doble. La base SQLite temporal es la tecnología real, aislada por prueba (`tmp_path`): aísla el estado, no sustituye una dependencia. La API no llama a nada externo, así que no hizo falta un servidor simulado.

---

## 5. Lo que no probé

1. `RelojSistema.hoy() == date.today()`. Solo verifica una función de la librería estándar y fallaría de forma intermitente cerca de la medianoche, el mismo problema que justifica el stub. Su única línea ya la ejerce la prueba de integración con reloj real.
2. Más longitudes de especie (0 a 60 una por una, o 1000 caracteres). La partición dice que los valores de una misma clase se comportan igual. Ya tengo un representante por clase y los seis valores en las fronteras; el resto repetiría lo mismo sin información nueva.
3. Una prueba que arranque el servidor con `python app.py`. Probaría Flask y el sistema operativo, no mi lógica; el cliente de pruebas ya ejercita todas las rutas. Costo alto (puerto, proceso bloqueante) y beneficio casi nulo; ese arranque se verifica a mano (Paso 8 del README).

---

## 6. Lectura de la cobertura

Comando: `pytest --cov=app --cov=validador --cov-branch --cov-report=term-missing`. Resultado guardado en `docs/cobertura.txt`:

```
Name           Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------
app.py            74      1     12      1    98%   128
validador.py      38      0     16      0   100%
----------------------------------------------------------
TOTAL            112      1     28      1    99%
63 passed
```

Criterio de cobertura: sentencias y ramas (`--cov-branch`, que verifica que cada `if` se haya evaluado como verdadero y como falso). Medí solo `app.py` y `validador.py`; `seed.py` es una utilidad de datos de ejemplo.

Línea sin cubrir: `app.py`, línea 128 (`app.run(host="127.0.0.1", port=5000)`, dentro de `if __name__ == "__main__":`). Esa condición es también la rama parcial. Solo se ejecuta cuando alguien lanza el servidor a mano, nunca al importar la app desde las pruebas. No vale la pena probarla: no tiene lógica propia y exigiría arrancar un servidor bloqueante dentro de la prueba (sección 5, punto 3).

Lo que la cobertura no dice. Un 100 % en `validador.py` prueba que cada línea se ejecutó, no que las pruebas comprueben algo útil: podría haberlo logrado sin una sola prueba de frontera. Por eso la tabla de casos, y no el porcentaje, guía las pruebas. Como control adicional cambié a mano siete operadores o constantes del validador (`<=`→`<` en mínimo y máximo, `3`→`2`, `50`→`51`, `>`→`>=` en la fecha, largo `10`→`11` y quitar el `.strip()`), y cada cambio hizo fallar al menos una prueba.