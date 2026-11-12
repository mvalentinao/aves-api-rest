"""Imprime las respuestas de la API a un escenario fijo, para comparar antes y después del refactor.

Uso:
    python scripts/muestra_api.py > salida.json

Usa una base temporal y solo fechas que no dependen del día real (2024-02-29
es válida; 2999-01-01 siempre es futura), así que la salida es idéntica en
cualquier fecha. Solo depende de `app.app` (la aplicación Flask de la raíz).
"""
import json
import os
import sys
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "muestra.db")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402

VALIDO = {"especie": "colibrí", "lugar": "Chingaza", "fecha": "2024-02-29", "observador": "Pablo"}

PASOS = [
    ("GET", "/avistamientos", None),
    ("POST", "/avistamientos", VALIDO),
    ("POST", "/avistamientos", {**VALIDO, "especie": "  águila  ", "lugar": " Sumapaz ", "id": 99}),
    ("POST", "/avistamientos", {**VALIDO, "especie": "águila"}),
    ("POST", "/avistamientos", {**VALIDO, "especie": "ab", "fecha": "2999-01-01"}),
    ("POST", "/avistamientos", {**VALIDO, "fecha": "2025-02-29"}),
    ("POST", "/avistamientos", {"especie": "colibrí"}),
    ("POST", "/avistamientos", ["no", "es", "objeto"]),
    ("GET", "/avistamientos", None),
    ("GET", "/avistamientos/1", None),
    ("GET", "/avistamientos/999", None),
    ("GET", "/avistamientos/resumen", None),
    ("PUT", "/avistamientos/1", {**VALIDO, "lugar": "Jardín Botánico"}),
    ("PUT", "/avistamientos/1", {"lugar": "otro"}),
    ("PUT", "/avistamientos/999", VALIDO),
    ("PUT", "/avistamientos/999", {"lugar": "otro"}),
    ("DELETE", "/avistamientos/2", None),
    ("DELETE", "/avistamientos/2", None),
    ("GET", "/avistamientos", None),
    ("GET", "/avistamientos/resumen", None),
    ("GET", "/avistamientos/abc", None),
    ("GET", "/", None),
]


def main():
    cliente = app.test_client()
    salida = []
    for metodo, ruta, cuerpo in PASOS:
        r = cliente.open(ruta, method=metodo, json=cuerpo) if cuerpo is not None else cliente.open(ruta, method=metodo)
        try:
            texto = r.get_json()
        except Exception:
            texto = None
        salida.append({
            "peticion": f"{metodo} {ruta}" + (f" {json.dumps(cuerpo, ensure_ascii=False)}" if cuerpo is not None else ""),
            "status": r.status_code,
            "content_type": r.content_type,
            "cuerpo": texto if texto is not None else r.get_data(as_text=True)[:60],
        })
    print(json.dumps(salida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
