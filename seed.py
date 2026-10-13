"""Carga datos de ejemplo en la base de datos.

Uso:
    python seed.py              # carga los ejemplos solo si la base está vacía
    python seed.py --reiniciar  # borra todo y vuelve a cargar los ejemplos
"""
import sys

import app

DATOS = [
    ("colibrí", "Parque Nacional Chingaza", "2026-09-01", "Pablo"),
    ("colibrí", "Jardín Botánico de Bogotá", "2026-09-02", "Pablo"),
    ("colibrí", "Reserva La Conejera", "2026-09-05", "Ana"),
    ("colibrí", "Parque Nacional Chingaza", "2026-09-12", "Luis"),
    ("águila", "Páramo de Sumapaz", "2026-09-03", "Ana"),
    ("águila", "Páramo de Sumapaz", "2026-09-14", "Camila"),
    ("águila", "Cerros Orientales", "2026-09-21", "Pablo"),
    ("garza", "Humedal Jaboque", "2026-09-04", "Luis"),
    ("garza", "Humedal Córdoba", "2026-09-10", "Camila"),
    ("garza", "Humedal La Conejera", "2026-09-18", "Ana"),
    ("cóndor andino", "Páramo de Sumapaz", "2026-09-06", "Pablo"),
    ("cóndor andino", "Parque Nacional Los Nevados", "2026-09-19", "Sofía"),
    ("tucán", "Reserva Río Ñambí", "2026-09-07", "Sofía"),
    ("tucán", "Reserva Río Ñambí", "2026-09-08", "Sofía"),
    ("mirla", "Parque Simón Bolívar", "2026-09-09", "Luis"),
    ("mirla", "Parque El Virrey", "2026-09-15", "Camila"),
    ("mirla", "Jardín Botánico de Bogotá", "2026-09-22", "Ana"),
    ("colibrí", "Reserva La Conejera", "2026-09-25", "Sofía"),
    ("loro orejiamarillo", "Jardín, Antioquia", "2026-09-11", "Pablo"),
    ("guacamaya", "Parque Nacional Tayrona", "2026-09-16", "Luis"),
    ("pato andino", "Laguna de Tota", "2026-09-23", "Camila"),
    ("carpintero", "Parque Nacional Chingaza", "2026-09-27", "Ana"),
]


def main():
    reiniciar = "--reiniciar" in sys.argv[1:]
    app.init_db()
    with app.get_db() as conn:
        if reiniciar:
            conn.execute("DELETE FROM avistamientos")
            conn.execute("DELETE FROM sqlite_sequence WHERE name = 'avistamientos'")
        existentes = conn.execute("SELECT COUNT(*) FROM avistamientos").fetchone()[0]
        if existentes > 0:
            print(f"La base ya tiene {existentes} avistamientos. No se cargó nada.")
            print("Para borrar todo y volver a cargar los ejemplos: python seed.py --reiniciar")
            return
        conn.executemany(
            "INSERT INTO avistamientos (especie, lugar, fecha, observador) VALUES (?, ?, ?, ?)",
            DATOS,
        )
    print(f"Base poblada con {len(DATOS)} avistamientos.")


if __name__ == "__main__":
    main()
