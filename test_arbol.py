"""
Pruebas automáticas de CyberTree.
Ejecutar:  python -m unittest test_arbol.py -v
"""

import unittest

from app import app
from arbol import ArbolDecision, Nodo
from escenarios import ARBOLES


class PruebasArbol(unittest.TestCase):
    def setUp(self):
        # Árbol pequeño de la clase:      A
        #                               /   \
        #                              B     C
        #                             / \
        #                            D   E
        self.a = ArbolDecision("prueba")
        self.a.insertar_raiz(Nodo("A", "¿A?", "A"))
        self.a.insertar("A", "si", Nodo("B", "¿B?", "B"))
        self.a.insertar("A", "no", Nodo("C", "C", "C", tipo="resultado"))
        self.a.insertar("B", "si", Nodo("D", "D", "D", tipo="resultado"))
        self.a.insertar("B", "no", Nodo("E", "E", "E", tipo="resultado"))

    def test_medidas(self):
        self.assertEqual(self.a.contar_nodos(), 5)
        self.assertEqual(self.a.altura(), 3)
        self.assertEqual(self.a.obtener_hojas(), ["D", "E", "C"])

    def test_recorridos(self):
        self.assertEqual(self.a.preorden(), ["A", "B", "D", "E", "C"])
        self.assertEqual(self.a.inorden(), ["D", "B", "E", "A", "C"])
        self.assertEqual(self.a.postorden(), ["D", "E", "B", "C", "A"])
        self.assertEqual(self.a.por_niveles(), [["A"], ["B", "C"], ["D", "E"]])

    def test_buscar_y_padre(self):
        self.assertEqual(self.a.buscar("E").id, "E")
        self.assertIsNone(self.a.buscar("Z"))
        self.assertEqual(self.a.padre_de("D").id, "B")
        self.assertIsNone(self.a.padre_de("A"))

    def test_recorrer_respuestas(self):
        nodo, ruta = self.a.recorrer(["si", "no"])
        self.assertEqual(nodo.id, "E")
        self.assertEqual([n.id for n in ruta], ["A", "B", "E"])

    def test_errores_al_insertar(self):
        with self.assertRaises(ValueError):
            self.a.insertar("A", "si", Nodo("X", "", ""))      # ya tiene hijo Sí
        with self.assertRaises(ValueError):
            self.a.insertar("C", "si", Nodo("X", "", ""))      # C es hoja
        with self.assertRaises(ValueError):
            self.a.insertar("Z", "si", Nodo("X", "", ""))      # padre no existe


class PruebasEscenarios(unittest.TestCase):
    def test_todo_camino_termina_en_resultado(self):
        """Cada pregunta tiene Sí y No, y cada hoja es un resultado con recomendaciones."""
        for clave, arbol in ARBOLES.items():
            ids = arbol.preorden()
            self.assertEqual(len(ids), len(set(ids)), f"ids repetidos en {clave}")
            for id in ids:
                n = arbol.buscar(id)
                if n.tipo == "pregunta":
                    self.assertIsNotNone(n.izquierda, f"{id} sin rama Sí")
                    self.assertIsNotNone(n.derecha, f"{id} sin rama No")
                else:
                    self.assertTrue(n.es_hoja())
                    self.assertIn(n.riesgo, ("bajo", "medio", "alto", "critico"))
                    self.assertTrue(n.recomendaciones)


class PruebasAPI(unittest.TestCase):
    def setUp(self):
        self.cliente = app.test_client()

    def test_inicio(self):
        self.assertEqual(self.cliente.get("/").status_code, 200)

    def test_listar(self):
        datos = self.cliente.get("/api/escenarios").get_json()
        self.assertEqual(len(datos), 4)

    def test_recorrer(self):
        r = self.cliente.post("/api/escenarios/phishing/recorrer",
                              json={"respuestas": ["si", "si", "si"]}).get_json()
        self.assertTrue(r["terminado"])
        self.assertEqual(r["actual"]["riesgo"], "critico")
        self.assertEqual(r["ruta"], ["P1", "P2", "P3", "P4"])

    def test_errores(self):
        self.assertEqual(self.cliente.get("/api/escenarios/nada/arbol").status_code, 404)
        r = self.cliente.post("/api/escenarios/cuenta/recorrer", json={"respuestas": ["quizas"]})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
