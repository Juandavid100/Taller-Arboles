// ============================================================
// CyberTree - lógica del frontend
// El árbol vive en Python. Aquí solo:
//   1) pedimos los datos al servidor (fetch)
//   2) enviamos las respuestas del usuario
//   3) dibujamos el árbol y resaltamos la ruta
// ============================================================

const estado = {
  clave: null,        // escenario elegido
  respuestas: [],     // ["si", "no", ...]
  arbol: null,        // árbol completo (para dibujarlo)
  ruta: [],           // ids de los nodos visitados
  actual: null,       // nodo donde estamos
};

const $ = (id) => document.getElementById(id);

const NOMBRE_RIESGO = { bajo: "Riesgo bajo", medio: "Riesgo medio", alto: "Riesgo alto", critico: "Riesgo crítico" };

// ---------- Pantalla de inicio ----------
async function cargarEscenarios() {
  const res = await fetch("/api/escenarios");
  const escenarios = await res.json();
  const contenedor = $("lista-escenarios");
  contenedor.innerHTML = "";
  escenarios.forEach((e) => {
    const tarjeta = document.createElement("button");
    tarjeta.className = "escenario";
    tarjeta.innerHTML = `
      <div class="icono">${e.icono}</div>
      <h3>${e.nombre}</h3>
      <p>${e.descripcion}</p>
      <div class="chips">
        <span class="chip">${e.nodos} nodos</span>
        <span class="chip">${e.hojas} hojas</span>
        <span class="chip">altura ${e.altura}</span>
      </div>`;
    tarjeta.addEventListener("click", () => abrirEscenario(e.id, e.nombre, e.icono));
    contenedor.appendChild(tarjeta);
  });
}

// ---------- Abrir un escenario ----------
async function abrirEscenario(clave, nombre, icono) {
  estado.clave = clave;
  estado.respuestas = [];
  const res = await fetch(`/api/escenarios/${clave}/arbol`);
  const datos = await res.json();
  estado.arbol = datos.arbol;
  mostrarEstadisticas(datos.estadisticas);

  $("titulo-escenario").textContent = `${icono} ${nombre}`;
  $("pantalla-inicio").classList.add("oculto");
  $("pantalla-evaluacion").classList.remove("oculto");
  window.scrollTo({ top: 0 });
  await avanzar();
}

// ---------- Pedir a Python que recorra el árbol ----------
async function avanzar() {
  const res = await fetch(`/api/escenarios/${estado.clave}/recorrer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ respuestas: estado.respuestas }),
  });
  const datos = await res.json();
  estado.ruta = datos.ruta;
  estado.actual = datos.actual;
  pintarDecision(datos);
  dibujarArbol();
}

function responder(respuesta) {
  if (!estado.actual || estado.actual.tipo === "resultado") return;
  estado.respuestas.push(respuesta);
  avanzar();
}

function deshacer() {
  if (estado.respuestas.length === 0) return;
  estado.respuestas.pop();
  avanzar();
}

function reiniciar() {
  estado.respuestas = [];
  avanzar();
}

// ---------- Panel de pregunta / resultado ----------
function pintarDecision(datos) {
  const nodo = datos.actual;
  if (datos.terminado) {
    $("tarjeta-pregunta").classList.add("oculto");
    $("tarjeta-resultado").classList.remove("oculto");
    $("resultado-id").textContent = nodo.id;
    const r = $("riesgo");
    r.className = `riesgo ${nodo.riesgo}`;
    r.textContent = NOMBRE_RIESGO[nodo.riesgo];
    $("resultado-titulo").textContent = nodo.etiqueta;
    $("resultado-texto").textContent = nodo.texto;
    $("resultado-recomendaciones").innerHTML = nodo.recomendaciones.map((t) => `<li>${t}</li>`).join("");
  } else {
    $("tarjeta-resultado").classList.add("oculto");
    $("tarjeta-pregunta").classList.remove("oculto");
    $("pregunta-id").textContent = nodo.id;
    $("pregunta-nivel").textContent = datos.nivel;
    $("pregunta-texto").textContent = nodo.texto;
  }

  // Historial: cada nodo visitado con la respuesta que se dio
  const lista = $("historial");
  if (estado.respuestas.length === 0) {
    lista.innerHTML = `<li class="vacio">Estás en la raíz (${datos.ruta[0]}). Responde para bajar por el árbol.</li>`;
  } else {
    lista.innerHTML = estado.respuestas.map((resp, i) => {
      const n = buscarNodo(estado.arbol, datos.ruta[i]);
      return `<li><span class="id">${n.id}</span><span>${n.etiqueta}</span>
              <span class="resp ${resp}">${resp === "si" ? "Sí" : "No"}</span></li>`;
    }).join("");
  }
  $("btn-atras").disabled = estado.respuestas.length === 0;
}

function buscarNodo(nodo, id) {
  if (!nodo) return null;
  if (nodo.id === id) return nodo;
  return buscarNodo(nodo.si, id) || buscarNodo(nodo.no, id);
}

// ---------- Estadísticas ----------
function mostrarEstadisticas(e) {
  $("m-nodos").textContent = e.nodos;
  $("m-internos").textContent = e.internos;
  $("m-hojas").textContent = e.hojas;
  $("m-altura").textContent = e.altura;
  $("m-raiz").textContent = e.raiz;
  $("r-preorden").textContent = e.preorden.join(" ");
  $("r-inorden").textContent = e.inorden.join(" ");
  $("r-postorden").textContent = e.postorden.join(" ");
  $("r-niveles").textContent = e.niveles.map((n, i) => `N${i}: ${n.join(" ")}`).join("  |  ");
}

// ---------- Dibujo del árbol en SVG ----------
const ANCHO_NODO = 132, ALTO_NODO = 50, SEP_X = 150, SEP_Y = 105, MARGEN = 20;

// Coloca las hojas de izquierda a derecha y centra cada padre sobre sus hijos
function calcularPosiciones(raiz) {
  const pos = {};
  let siguienteX = 0;
  function colocar(nodo, nivel) {
    if (!nodo) return null;
    const xi = colocar(nodo.si, nivel + 1);
    const xd = colocar(nodo.no, nivel + 1);
    let x;
    if (xi === null && xd === null) { x = siguienteX; siguienteX += SEP_X; }
    else if (xi === null) x = xd;
    else if (xd === null) x = xi;
    else x = (xi + xd) / 2;
    pos[nodo.id] = { x, y: nivel * SEP_Y, nodo };
    return x;
  }
  colocar(raiz, 0);
  return pos;
}

function partirTexto(texto, max = 18) {
  if (texto.length <= max) return [texto];
  const palabras = texto.split(" ");
  const lineas = [""];
  palabras.forEach((p) => {
    const ultima = lineas[lineas.length - 1];
    if ((ultima + " " + p).trim().length > max && ultima) lineas.push(p);
    else lineas[lineas.length - 1] = (ultima + " " + p).trim();
  });
  return lineas.slice(0, 2);
}

function dibujarArbol() {
  const svg = $("svg-arbol");
  const pos = calcularPosiciones(estado.arbol);
  const lista = Object.values(pos);
  const maxX = Math.max(...lista.map((p) => p.x));
  const maxY = Math.max(...lista.map((p) => p.y));
  const ancho = maxX + ANCHO_NODO + MARGEN * 2;
  const alto = maxY + ALTO_NODO + MARGEN * 2;
  svg.setAttribute("viewBox", `0 0 ${ancho} ${alto}`);

  const enRuta = new Set(estado.ruta);
  const cx = (p) => p.x + MARGEN + ANCHO_NODO / 2;
  const cy = (p) => p.y + MARGEN;
  let aristas = "", nodos = "";

  lista.forEach((p) => {
    [["si", "Sí"], ["no", "No"]].forEach(([lado, texto]) => {
      const hijo = p.nodo[lado];
      if (!hijo) return;
      const h = pos[hijo.id];
      const x1 = cx(p), y1 = cy(p) + ALTO_NODO, x2 = cx(h), y2 = cy(h);
      const activa = enRuta.has(p.nodo.id) && enRuta.has(hijo.id) ? "activa" : "";
      const ym = (y1 + y2) / 2;
      aristas += `<path class="arista ${activa}" d="M${x1},${y1} C${x1},${ym} ${x2},${ym} ${x2},${y2}"/>`;
      aristas += `<text class="arista-etiqueta ${activa}" x="${(x1 + x2) / 2 + (lado === "si" ? -14 : 6)}" y="${ym}">${texto}</text>`;
    });
  });

  lista.forEach((p) => {
    const n = p.nodo;
    const clases = ["nodo", n.tipo, n.riesgo || ""];
    if (enRuta.has(n.id)) clases.push("en-ruta");
    else if (estado.respuestas.length > 0) clases.push("atenuado");
    if (estado.actual && estado.actual.id === n.id) clases.push("actual");
    const x = p.x + MARGEN, y = p.y + MARGEN;
    const lineas = partirTexto(n.etiqueta);
    const textoY = y + (lineas.length === 1 ? 33 : 27);
    const tspans = lineas.map((l, i) =>
      `<tspan x="${x + ANCHO_NODO / 2}" dy="${i === 0 ? 0 : 14}">${l}</tspan>`).join("");
    nodos += `
      <g class="${clases.join(" ")}">
        <title>${n.id}: ${n.texto}</title>
        <rect x="${x}" y="${y}" width="${ANCHO_NODO}" height="${ALTO_NODO}" rx="9"/>
        <text class="nodo-id" x="${x + 8}" y="${y + 13}">${n.id}</text>
        <text x="${x + ANCHO_NODO / 2}" y="${textoY}" text-anchor="middle">${tspans}</text>
      </g>`;
  });

  svg.innerHTML = aristas + nodos;
}

// ---------- Eventos ----------
document.querySelectorAll("[data-respuesta]").forEach((b) =>
  b.addEventListener("click", () => responder(b.dataset.respuesta)));
$("btn-atras").addEventListener("click", deshacer);
$("btn-reiniciar").addEventListener("click", reiniciar);
$("btn-volver").addEventListener("click", () => {
  $("pantalla-evaluacion").classList.add("oculto");
  $("pantalla-inicio").classList.remove("oculto");
});

cargarEscenarios();
