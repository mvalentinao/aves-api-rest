"""Borde (UI): la API HTTP con Flask.

Traduce HTTP a casos de uso y los resultados del núcleo a JSON y códigos de
estado. No contiene reglas de negocio ni SQL. Recibe el servicio de aplicación
ya armado (no lo construye), así que esta capa no conoce la infraestructura.
"""
from flask import Flask, jsonify, request

from avistamientos.nucleo.modelo_dominio.avistamiento import Avistamiento, ResumenDeEspecie
from avistamientos.nucleo.servicios_aplicacion.errores import AvistamientoNoEncontrado, DatosInvalidos
from avistamientos.nucleo.servicios_aplicacion.servicio_avistamientos import ServicioDeAvistamientos


def _avistamiento_a_json(a: Avistamiento) -> dict:
    # Orden fijo de los campos: id primero, como en la API original.
    return {"id": a.id, "especie": a.especie, "lugar": a.lugar, "fecha": a.fecha, "observador": a.observador}


def _resumen_a_json(r: ResumenDeEspecie) -> dict:
    return {"especie": r.especie, "cantidad": r.cantidad}


def crear_app(servicio: ServicioDeAvistamientos) -> Flask:
    app = Flask(__name__)
    app.json.ensure_ascii = False  # tildes legibles en las respuestas JSON
    app.json.sort_keys = False  # mantiene el orden de los campos (id, especie, lugar, ...)

    @app.errorhandler(DatosInvalidos)
    def _datos_invalidos(e):
        return jsonify({"error": "; ".join(e.errores)}), 400

    @app.errorhandler(AvistamientoNoEncontrado)
    def _no_encontrado(e):
        return jsonify({"error": "Avistamiento no encontrado"}), 404

    @app.get("/avistamientos")
    def listar():
        return jsonify([_avistamiento_a_json(a) for a in servicio.listar()]), 200

    @app.get("/avistamientos/resumen")
    def resumen():
        return jsonify([_resumen_a_json(r) for r in servicio.resumen()]), 200

    @app.get("/avistamientos/<int:id>")
    def ver(id):
        return jsonify(_avistamiento_a_json(servicio.ver(id))), 200

    @app.post("/avistamientos")
    def crear():
        datos = request.get_json(silent=True)
        return jsonify(_avistamiento_a_json(servicio.registrar(datos))), 201

    @app.put("/avistamientos/<int:id>")
    def actualizar(id):
        datos = request.get_json(silent=True)
        return jsonify(_avistamiento_a_json(servicio.actualizar(id, datos))), 200

    @app.delete("/avistamientos/<int:id>")
    def eliminar(id):
        servicio.eliminar(id)
        return "", 204

    return app
