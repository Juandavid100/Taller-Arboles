"""
app.py
======
Servidor web de CyberTree (Flask).
Conecta el árbol de decisión (Python) con la interfaz (HTML, CSS, JS).

Para ejecutar:
    python app.py
y abrir en el navegador:  http://127.0.0.1:5055
"""

from flask import Flask, jsonify, render_template, request

from escenarios import ARBOLES, ESCENARIOS

app = Flask(__name__)


def nodo_a_json(nodo):
    return {
        "id": nodo.id,
        "texto": nodo.texto,
        "etiqueta": nodo.etiqueta,
        "tipo": nodo.tipo,
        "riesgo": nodo.riesgo,
        "recomendaciones": nodo.recomendaciones,
    }


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/api/escenarios")
def listar_escenarios():
    """Lista de escenarios con las medidas de cada árbol."""
    lista = []
    for clave, datos in ESCENARIOS.items():
        arbol = ARBOLES[clave]
        lista.append({
            "id": clave,
            "nombre": datos["nombre"],
            "descripcion": datos["descripcion"],
            "icono": datos["icono"],
            "nodos": arbol.contar_nodos(),
            "hojas": len(arbol.obtener_hojas()),
            "altura": arbol.altura(),
        })
    return jsonify(lista)


@app.route("/api/escenarios/<clave>/arbol")
def ver_arbol(clave):
    """Devuelve el árbol completo y sus estadísticas (para dibujarlo)."""
    arbol = ARBOLES.get(clave)
    if arbol is None:
        return jsonify({"error": "Escenario no encontrado"}), 404
    return jsonify({
        "nombre": arbol.nombre,
        "arbol": arbol.a_diccionario(),
        "estadisticas": arbol.estadisticas(),
    })


@app.route("/api/escenarios/<clave>/recorrer", methods=["POST"])
def recorrer(clave):
    """
    Recibe las respuestas del usuario, ej: {"respuestas": ["si", "no"]}
    y Python recorre el árbol desde la raíz.
    Devuelve el nodo donde quedó (pregunta o resultado) y la ruta recorrida.
    """
    arbol = ARBOLES.get(clave)
    if arbol is None:
        return jsonify({"error": "Escenario no encontrado"}), 404

    datos = request.get_json(silent=True) or {}
    respuestas = datos.get("respuestas", [])
    if not isinstance(respuestas, list) or any(r not in ("si", "no") for r in respuestas):
        return jsonify({"error": "Las respuestas deben ser 'si' o 'no'"}), 400

    actual, ruta = arbol.recorrer(respuestas)
    return jsonify({
        "actual": nodo_a_json(actual),
        "ruta": [n.id for n in ruta],
        "terminado": actual.es_hoja(),
        "nivel": len(ruta) - 1,
    })


if __name__ == "__main__":
    # Puerto 5055 para no chocar con otros proyectos que usan el 5000
    app.run(debug=True, port=5055)
