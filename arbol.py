"""
arbol.py
========
Estructura de datos principal de CyberTree: un ÁRBOL BINARIO DE DECISIÓN.

Idea clave:
    - Cada nodo es una PREGUNTA (nodo interno / rama) o un RESULTADO (nodo hoja).
    - En las listas usábamos  siguiente / anterior.
    - En el árbol usamos      izquierda / derecha.
          izquierda  ->  camino cuando el usuario responde "Sí"
          derecha    ->  camino cuando el usuario responde "No"

Implementamos las clases a mano (sin librerías externas) para poder explicar
cómo funciona el árbol por dentro: insertar, buscar, recorrer, contar,
calcular la altura y encontrar las hojas.
"""


class Nodo:
    """Un nodo del árbol: guarda un dato y dos referencias (izquierda y derecha)."""

    def __init__(self, id, texto, etiqueta, tipo="pregunta",
                 riesgo=None, recomendaciones=None):
        self.id = id                  # identificador único, ej: "C1"
        self.texto = texto            # la pregunta o el diagnóstico completo
        self.etiqueta = etiqueta      # texto corto para dibujar el nodo
        self.tipo = tipo              # "pregunta" (rama) o "resultado" (hoja)
        self.riesgo = riesgo          # solo en hojas: bajo, medio, alto, critico
        self.recomendaciones = recomendaciones or []
        self.izquierda = None         # hijo cuando la respuesta es "Sí"
        self.derecha = None           # hijo cuando la respuesta es "No"

    def es_hoja(self):
        """Un nodo hoja es el que no tiene hijos."""
        return self.izquierda is None and self.derecha is None

    def __repr__(self):
        return f"Nodo({self.id})"


class ArbolDecision:
    """Árbol binario de decisión. Solo guarda la referencia a la raíz."""

    def __init__(self, nombre):
        self.nombre = nombre
        self.raiz = None

    # ------------------------------------------------------------------
    # 1. INSERTAR
    # ------------------------------------------------------------------
    def insertar_raiz(self, nodo):
        """La raíz es el primer nodo: no tiene padre."""
        self.raiz = nodo
        return nodo

    def insertar(self, id_padre, respuesta, nodo):
        """
        Conecta 'nodo' como hijo del nodo 'id_padre'.
        respuesta = "si" -> se conecta a la izquierda
        respuesta = "no" -> se conecta a la derecha
        """
        padre = self.buscar(id_padre)
        if padre is None:
            raise ValueError(f"No existe el nodo padre {id_padre}")
        if padre.tipo == "resultado":
            raise ValueError(f"{id_padre} es una hoja (resultado): no puede tener hijos")

        if respuesta == "si":
            if padre.izquierda is not None:
                raise ValueError(f"{id_padre} ya tiene hijo izquierdo (Sí)")
            padre.izquierda = nodo
        elif respuesta == "no":
            if padre.derecha is not None:
                raise ValueError(f"{id_padre} ya tiene hijo derecho (No)")
            padre.derecha = nodo
        else:
            raise ValueError("La respuesta debe ser 'si' o 'no'")
        return nodo

    # ------------------------------------------------------------------
    # 2. BUSCAR  (recursivo, en preorden)
    # ------------------------------------------------------------------
    def buscar(self, id, nodo="inicio"):
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return None
        if nodo.id == id:
            return nodo
        encontrado = self.buscar(id, nodo.izquierda)
        if encontrado is not None:
            return encontrado
        return self.buscar(id, nodo.derecha)

    # ------------------------------------------------------------------
    # 3. RECORRER SEGÚN LAS RESPUESTAS DEL USUARIO
    # ------------------------------------------------------------------
    def recorrer(self, respuestas):
        """
        Parte de la raíz y baja por el árbol según la lista de respuestas.
        Devuelve (nodo_actual, ruta), donde ruta es la lista de nodos visitados.
        """
        actual = self.raiz
        ruta = [actual]
        for respuesta in respuestas:
            if actual.es_hoja():
                break                       # ya llegamos a un resultado
            if respuesta == "si":
                actual = actual.izquierda
            elif respuesta == "no":
                actual = actual.derecha
            else:
                raise ValueError("La respuesta debe ser 'si' o 'no'")
            ruta.append(actual)
        return actual, ruta

    # ------------------------------------------------------------------
    # 4. RECORRIDOS CLÁSICOS
    # ------------------------------------------------------------------
    def preorden(self, nodo="inicio", lista=None):
        """Raíz -> Izquierda -> Derecha"""
        if nodo == "inicio":
            nodo, lista = self.raiz, []
        if nodo is not None:
            lista.append(nodo.id)
            self.preorden(nodo.izquierda, lista)
            self.preorden(nodo.derecha, lista)
        return lista

    def inorden(self, nodo="inicio", lista=None):
        """Izquierda -> Raíz -> Derecha"""
        if nodo == "inicio":
            nodo, lista = self.raiz, []
        if nodo is not None:
            self.inorden(nodo.izquierda, lista)
            lista.append(nodo.id)
            self.inorden(nodo.derecha, lista)
        return lista

    def postorden(self, nodo="inicio", lista=None):
        """Izquierda -> Derecha -> Raíz"""
        if nodo == "inicio":
            nodo, lista = self.raiz, []
        if nodo is not None:
            self.postorden(nodo.izquierda, lista)
            self.postorden(nodo.derecha, lista)
            lista.append(nodo.id)
        return lista

    def por_niveles(self):
        """Recorrido por niveles (usa una COLA, la estructura FIFO que ya vimos)."""
        niveles = []
        if self.raiz is None:
            return niveles
        cola = [(self.raiz, 0)]
        while cola:
            nodo, nivel = cola.pop(0)          # sale el primero que entró
            if len(niveles) <= nivel:
                niveles.append([])
            niveles[nivel].append(nodo.id)
            if nodo.izquierda:
                cola.append((nodo.izquierda, nivel + 1))
            if nodo.derecha:
                cola.append((nodo.derecha, nivel + 1))
        return niveles

    # ------------------------------------------------------------------
    # 5. MEDIDAS DEL ÁRBOL
    # ------------------------------------------------------------------
    def contar_nodos(self, nodo="inicio"):
        """Tamaño del árbol: cantidad total de nodos."""
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return 0
        return 1 + self.contar_nodos(nodo.izquierda) + self.contar_nodos(nodo.derecha)

    def altura(self, nodo="inicio"):
        """Altura contada en NIVELES (la convención que usó el profesor)."""
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return 0
        return 1 + max(self.altura(nodo.izquierda), self.altura(nodo.derecha))

    def obtener_hojas(self, nodo="inicio", lista=None):
        """Lista de nodos hoja (los resultados finales)."""
        if nodo == "inicio":
            nodo, lista = self.raiz, []
        if nodo is not None:
            if nodo.es_hoja():
                lista.append(nodo.id)
            self.obtener_hojas(nodo.izquierda, lista)
            self.obtener_hojas(nodo.derecha, lista)
        return lista

    def padre_de(self, id, nodo="inicio"):
        """Devuelve el nodo padre de 'id' (la raíz no tiene padre)."""
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return None
        for hijo in (nodo.izquierda, nodo.derecha):
            if hijo is not None and hijo.id == id:
                return nodo
        return self.padre_de(id, nodo.izquierda) or self.padre_de(id, nodo.derecha)

    def estadisticas(self):
        total = self.contar_nodos()
        hojas = self.obtener_hojas()
        return {
            "nodos": total,
            "hojas": len(hojas),
            "internos": total - len(hojas),
            "altura": self.altura(),
            "raiz": self.raiz.id if self.raiz else None,
            "preorden": self.preorden(),
            "inorden": self.inorden(),
            "postorden": self.postorden(),
            "niveles": self.por_niveles(),
        }

    # ------------------------------------------------------------------
    # 6. CONVERTIR A DICCIONARIO (para enviarlo al frontend como JSON)
    # ------------------------------------------------------------------
    def a_diccionario(self, nodo="inicio"):
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return None
        return {
            "id": nodo.id,
            "texto": nodo.texto,
            "etiqueta": nodo.etiqueta,
            "tipo": nodo.tipo,
            "riesgo": nodo.riesgo,
            "si": self.a_diccionario(nodo.izquierda),
            "no": self.a_diccionario(nodo.derecha),
        }

    def imprimir(self, nodo="inicio", prefijo="", rama=""):
        """Dibuja el árbol en la consola (útil para la sustentación)."""
        if nodo == "inicio":
            nodo = self.raiz
        if nodo is None:
            return
        print(f"{prefijo}{rama}[{nodo.id}] {nodo.etiqueta}")
        self.imprimir(nodo.izquierda, prefijo + "    ", "Sí -> ")
        self.imprimir(nodo.derecha, prefijo + "    ", "No -> ")
