# 🌳 CyberTree — Simulador de decisiones de ciberseguridad

Taller de **Árboles** · Estructuras de Datos · Universidad Cooperativa de Colombia (Pasto)

CyberTree orienta a una persona ante un posible incidente de ciberseguridad haciéndole preguntas de **Sí / No**.
Cada respuesta baja por una rama de un **árbol binario de decisión** hasta llegar a una **hoja** con el
diagnóstico, el nivel de riesgo y las acciones recomendadas.

## Caso de estudio

Muchas personas no saben qué hacer cuando reciben un correo sospechoso, ven un inicio de sesión extraño
o su computador se comporta raro. CyberTree organiza ese conocimiento en 4 árboles de decisión:

| Escenario | Nodos | Hojas | Altura |
|---|---|---|---|
| 🔐 Cuenta comprometida | 11 | 6 | 4 |
| 🎣 Correo sospechoso (phishing) | 9 | 5 | 4 |
| 💻 Equipo infectado | 9 | 5 | 4 |
| 👁️ Actividad desconocida | 9 | 5 | 4 |

## ¿Dónde está el árbol?

```
Nodo
 ├─ dato (pregunta o resultado)
 ├─ izquierda  -> camino si la respuesta es "Sí"
 └─ derecha    -> camino si la respuesta es "No"
```

- **Nodo raíz:** la primera pregunta de cada escenario (C1, P1, E1, A1).
- **Nodos rama:** las preguntas.
- **Nodos hoja:** los resultados (no tienen hijos).

Operaciones implementadas a mano en `arbol.py` (sin librerías):

| Operación | Método |
|---|---|
| Insertar | `insertar_raiz()`, `insertar(padre, "si"/"no", nodo)` |
| Buscar | `buscar(id)` (recursivo) |
| Recorrer según respuestas | `recorrer(["si", "no", ...])` |
| Preorden / Inorden / Postorden | `preorden()`, `inorden()`, `postorden()` |
| Por niveles (usa una cola FIFO) | `por_niveles()` |
| Tamaño, altura, hojas, padre | `contar_nodos()`, `altura()`, `obtener_hojas()`, `padre_de()` |

## Estructura del proyecto

```
Taller-Arboles/
├── arbol.py           # clases Nodo y ArbolDecision (la estructura de datos)
├── escenarios.py      # construcción de los 4 árboles
├── app.py             # servidor Flask (conecta Python con la interfaz)
├── test_arbol.py      # pruebas automáticas
├── requirements.txt
├── templates/index.html
└── static/            # styles.css y app.js (dibuja el árbol en SVG)
```

## Cómo ejecutarlo

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (en Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Abrir en el navegador: **http://127.0.0.1:5055**

Ver los árboles en la consola: `python escenarios.py`
Correr las pruebas: `python -m unittest test_arbol.py -v`

## Tecnologías

Python 3 · Flask · HTML · CSS · JavaScript (SVG)

> CyberTree es un simulador educativo basado en reglas. No analiza equipos ni cuentas reales.
