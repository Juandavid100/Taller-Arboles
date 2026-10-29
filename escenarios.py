"""
escenarios.py
=============
Aquí se CONSTRUYEN los 4 árboles de decisión de CyberTree.

Cada árbol se arma igual que en clase:
    1. se crea la raíz
    2. se insertan los hijos con insertar(padre, "si"/"no", nodo)

Recordatorio:  "si" -> izquierda    "no" -> derecha
"""

from arbol import ArbolDecision, Nodo


def pregunta(id, texto, etiqueta):
    return Nodo(id, texto, etiqueta, tipo="pregunta")


def resultado(id, texto, etiqueta, riesgo, recomendaciones):
    return Nodo(id, texto, etiqueta, tipo="resultado",
                riesgo=riesgo, recomendaciones=recomendaciones)


# ======================================================================
# ESCENARIO 1: Cuenta posiblemente comprometida
# ======================================================================
def construir_cuenta():
    a = ArbolDecision("Cuenta posiblemente comprometida")

    a.insertar_raiz(pregunta(
        "C1", "¿Recibiste una alerta de inicio de sesión que no reconoces o ves cambios en tu cuenta que tú no hiciste?",
        "¿Alerta o cambios extraños?"))

    # --- Rama Sí de C1
    a.insertar("C1", "si", pregunta(
        "C2", "¿Todavía puedes entrar a tu cuenta con tu contraseña?", "¿Aún puedes entrar?"))

    a.insertar("C2", "si", pregunta(
        "C3", "¿Usas esa misma contraseña en otras cuentas (correo, redes, banco)?", "¿Contraseña repetida?"))
    a.insertar("C3", "si", resultado(
        "C4", "Cuenta comprometida con riesgo de efecto dominó: si la contraseña se repite, las otras cuentas también están expuestas.",
        "Riesgo en cadena", "alto", [
            "Cambia YA la contraseña de esta cuenta por una larga y única.",
            "Cambia también la contraseña de cada cuenta donde la repetías, empezando por el correo y el banco.",
            "Cierra todas las sesiones abiertas desde la configuración de seguridad.",
            "Activa la verificación en dos pasos (2FA) con una app autenticadora.",
            "Usa un gestor de contraseñas para no volver a repetirlas.",
        ]))
    a.insertar("C3", "no", resultado(
        "C5", "Acceso sospechoso, pero todavía tienes el control de la cuenta y el daño puede contenerse.",
        "Contener el acceso", "medio", [
            "Cambia la contraseña por una larga y única.",
            "Cierra las sesiones y dispositivos que no reconozcas.",
            "Activa la verificación en dos pasos (2FA).",
            "Revisa el correo y el teléfono de recuperación y las reglas de reenvío de correo.",
        ]))

    a.insertar("C2", "no", pregunta(
        "C6", "¿El correo o el teléfono de recuperación de la cuenta siguen siendo los tuyos?",
        "¿Recuperación es tuya?"))
    a.insertar("C6", "si", resultado(
        "C7", "Perdiste el acceso, pero todavía puedes recuperarlo por los canales oficiales.",
        "Recuperar la cuenta", "alto", [
            "Usa la opción oficial \"¿Olvidaste tu contraseña?\" de la plataforma; no uses enlaces que te lleguen por mensaje.",
            "Al recuperarla, cierra todas las sesiones y activa 2FA.",
            "Avisa a tus contactos que no respondan mensajes enviados desde esa cuenta.",
        ]))
    a.insertar("C6", "no", resultado(
        "C8", "El atacante cambió los datos de recuperación: tomó el control de la cuenta.",
        "Toma de control", "critico", [
            "Usa el formulario oficial de cuenta hackeada o el soporte de la plataforma.",
            "Avisa a tus contactos que tu cuenta fue tomada y que no envíen dinero ni códigos.",
            "Si la cuenta tiene tarjetas o pagos vinculados, llama a tu banco para bloquearlos.",
            "Revisa y asegura tu correo principal: suele ser la puerta a las demás cuentas.",
        ]))

    # --- Rama No de C1
    a.insertar("C1", "no", pregunta(
        "C9", "¿Tienes activada la verificación en dos pasos (2FA) en esta cuenta?", "¿Tienes 2FA?"))
    a.insertar("C9", "si", resultado(
        "C10", "No hay señales de compromiso y tu cuenta tiene una buena capa de protección.",
        "Cuenta protegida", "bajo", [
            "Mantén la verificación en dos pasos activa.",
            "Guarda en un lugar seguro los códigos de respaldo.",
            "Revisa cada cierto tiempo los dispositivos con sesión abierta.",
        ]))
    a.insertar("C9", "no", resultado(
        "C11", "No hay señales de compromiso, pero la cuenta depende solo de la contraseña.",
        "Reforzar prevención", "medio", [
            "Activa la verificación en dos pasos (2FA).",
            "Usa una contraseña larga y diferente para cada cuenta.",
            "Considera un gestor de contraseñas.",
        ]))
    return a


# ======================================================================
# ESCENARIO 2: Correo electrónico sospechoso (phishing)
# ======================================================================
def construir_phishing():
    a = ArbolDecision("Correo electrónico sospechoso")

    a.insertar_raiz(pregunta(
        "P1", "¿El correo te pide actuar con urgencia (pagar, verificar tu cuenta, evitar un bloqueo o reclamar un premio)?",
        "¿Pide urgencia?"))

    a.insertar("P1", "si", pregunta(
        "P2", "¿Ya hiciste clic en algún enlace o abriste un archivo adjunto del correo?", "¿Hiciste clic?"))
    a.insertar("P2", "si", pregunta(
        "P3", "¿Escribiste tu contraseña o datos bancarios en la página que se abrió?", "¿Diste tus datos?"))
    a.insertar("P3", "si", resultado(
        "P4", "Phishing con robo de credenciales: el atacante probablemente ya tiene tus datos.",
        "Datos entregados", "critico", [
            "Cambia de inmediato la contraseña entrando al sitio oficial escribiendo tú la dirección.",
            "Si diste datos bancarios, llama ya a tu banco para bloquear la tarjeta o la cuenta.",
            "Activa la verificación en dos pasos (2FA).",
            "Reporta el correo como phishing en tu servicio de correo.",
        ]))
    a.insertar("P3", "no", resultado(
        "P5", "Interactuaste con el correo, pero no entregaste credenciales. Puede haber un archivo malicioso.",
        "Posible malware", "alto", [
            "No vuelvas a abrir el adjunto ni el enlace.",
            "Haz un análisis completo con tu antivirus actualizado.",
            "Vigila los próximos días tus cuentas por actividad extraña.",
            "Reporta el correo como phishing y elimínalo.",
        ]))
    a.insertar("P2", "no", resultado(
        "P6", "Correo con señales típicas de phishing, sin interacción de tu parte.",
        "Phishing detectado", "medio", [
            "No hagas clic ni respondas.",
            "Si dudas, contacta a la entidad por su canal oficial, no por los datos del correo.",
            "Reporta el correo como phishing y elimínalo.",
        ]))

    a.insertar("P1", "no", pregunta(
        "P7", "¿La dirección del remitente coincide exactamente con el dominio oficial de la entidad?",
        "¿Remitente oficial?"))
    a.insertar("P7", "si", resultado(
        "P8", "No hay señales fuertes de phishing. Aun así, los remitentes pueden falsificarse.",
        "Probablemente legítimo", "bajo", [
            "Para cualquier trámite, entra al sitio escribiendo tú la dirección en el navegador.",
            "Pasa el mouse sobre los enlaces antes de hacer clic para ver a dónde llevan.",
        ]))
    a.insertar("P7", "no", resultado(
        "P9", "El remitente no coincide con la entidad: posible suplantación de identidad.",
        "Suplantación", "medio", [
            "No abras enlaces ni adjuntos.",
            "Compara letra por letra el dominio (ej: banco-co.com en vez de banco.com.co).",
            "Reporta el correo como phishing y elimínalo.",
        ]))
    return a


# ======================================================================
# ESCENARIO 3: Posible infección del equipo
# ======================================================================
def construir_equipo():
    a = ArbolDecision("Posible infección del equipo")

    a.insertar_raiz(pregunta(
        "E1", "¿Aparecen ventanas emergentes, programas o extensiones del navegador que tú no instalaste?",
        "¿Programas extraños?"))

    a.insertar("E1", "si", pregunta(
        "E2", "¿Tus archivos cambiaron de nombre, no se abren o aparece un mensaje pidiendo un pago para recuperarlos?",
        "¿Piden rescate?"))
    a.insertar("E2", "si", resultado(
        "E3", "Señales de ransomware: un programa cifró tus archivos y pide rescate.",
        "Ransomware", "critico", [
            "Desconecta el equipo de internet y de la red (Wi-Fi y cable) ahora.",
            "No pages el rescate: no garantiza recuperar los archivos.",
            "Avisa al área de TI o a un técnico de confianza.",
            "Restaura tus archivos desde una copia de seguridad limpia.",
        ]))
    a.insertar("E2", "no", resultado(
        "E4", "Señales de adware o software no deseado instalado en el equipo.",
        "Software no deseado", "alto", [
            "Desinstala los programas que no reconozcas.",
            "Elimina las extensiones extrañas del navegador.",
            "Haz un análisis completo con el antivirus.",
            "Cambia tus contraseñas desde OTRO equipo que esté limpio.",
        ]))

    a.insertar("E1", "no", pregunta(
        "E5", "¿El equipo está mucho más lento de lo normal o el ventilador trabaja al máximo sin razón?",
        "¿Lentitud extraña?"))
    a.insertar("E5", "si", pregunta(
        "E6", "¿Tu antivirus está activo y actualizado?", "¿Antivirus activo?"))
    a.insertar("E6", "si", resultado(
        "E7", "Comportamiento inusual que conviene revisar, aunque tengas protección activa.",
        "Revisar rendimiento", "medio", [
            "Haz un análisis completo con el antivirus.",
            "Revisa en el Administrador de tareas qué proceso consume más recursos.",
            "Instala las actualizaciones pendientes del sistema operativo.",
        ]))
    a.insertar("E6", "no", resultado(
        "E8", "Comportamiento inusual y el equipo está sin protección.",
        "Equipo desprotegido", "alto", [
            "Activa o actualiza el antivirus y haz un análisis completo.",
            "Instala las actualizaciones del sistema operativo.",
            "No ingreses a tu banco desde este equipo hasta revisarlo.",
        ]))
    a.insertar("E5", "no", resultado(
        "E9", "No hay señales visibles de infección.",
        "Sin señales", "bajo", [
            "Mantén el sistema y el antivirus actualizados.",
            "Haz copias de seguridad periódicas de tus archivos.",
            "Descarga programas solo de sitios oficiales.",
        ]))
    return a


# ======================================================================
# ESCENARIO 4: Actividad desconocida en sesiones y dispositivos
# ======================================================================
def construir_actividad():
    a = ArbolDecision("Actividad desconocida")

    a.insertar_raiz(pregunta(
        "A1", "En la lista de sesiones o dispositivos de tu cuenta, ¿aparece alguno que no reconoces?",
        "¿Dispositivo extraño?"))

    a.insertar("A1", "si", pregunta(
        "A2", "¿Ese dispositivo aparece activo en este momento?", "¿Está activo ahora?"))
    a.insertar("A2", "si", resultado(
        "A3", "Hay alguien usando tu cuenta en este momento.",
        "Intruso activo", "alto", [
            "Cierra esa sesión desde la configuración de seguridad.",
            "Cambia la contraseña de inmediato.",
            "Activa la verificación en dos pasos (2FA).",
        ]))
    a.insertar("A2", "no", pregunta(
        "A4", "¿Notas mensajes enviados, compras o archivos que tú no hiciste?", "¿Acciones que no hiciste?"))
    a.insertar("A4", "si", resultado(
        "A5", "Hubo un acceso no autorizado que ya realizó acciones con tu cuenta.",
        "Acceso con daños", "alto", [
            "Cierra todas las sesiones y cambia la contraseña.",
            "Revisa tus movimientos y reporta a la plataforma o al banco las acciones que no hiciste.",
            "Activa la verificación en dos pasos (2FA).",
        ]))
    a.insertar("A4", "no", resultado(
        "A6", "Sesión desconocida sin daños visibles. Ten en cuenta que la ubicación que muestran las plataformas puede ser aproximada.",
        "Sesión sospechosa", "medio", [
            "Cierra esa sesión por precaución.",
            "Cambia la contraseña.",
            "Revisa si es un equipo tuyo antiguo (celular o computador viejo).",
        ]))

    a.insertar("A1", "no", pregunta(
        "A7", "¿Te han llegado códigos de verificación (SMS o correo) que tú no pediste?", "¿Códigos sin pedir?"))
    a.insertar("A7", "si", resultado(
        "A8", "Alguien está intentando entrar a tu cuenta y podría conocer tu contraseña.",
        "Intento de acceso", "medio", [
            "Nunca compartas esos códigos con nadie, aunque digan ser de soporte.",
            "Cambia la contraseña por una nueva y única.",
            "Mantén activa la verificación en dos pasos.",
        ]))
    a.insertar("A7", "no", resultado(
        "A9", "No se observa actividad desconocida.",
        "Todo en orden", "bajo", [
            "Revisa de vez en cuando las sesiones abiertas.",
            "Cierra sesión en equipos prestados o públicos.",
        ]))
    return a


# Catálogo de escenarios: id -> datos para la interfaz + función constructora
ESCENARIOS = {
    "cuenta": {
        "nombre": "Cuenta comprometida",
        "descripcion": "Alguien pudo haber entrado a tu correo o red social.",
        "icono": "🔐",
        "construir": construir_cuenta,
    },
    "phishing": {
        "nombre": "Correo sospechoso",
        "descripcion": "Recibiste un correo que te pide datos o pagos.",
        "icono": "🎣",
        "construir": construir_phishing,
    },
    "equipo": {
        "nombre": "Equipo infectado",
        "descripcion": "Tu computador se comporta de forma extraña.",
        "icono": "💻",
        "construir": construir_equipo,
    },
    "actividad": {
        "nombre": "Actividad desconocida",
        "descripcion": "Ves sesiones, dispositivos o códigos que no reconoces.",
        "icono": "👁️",
        "construir": construir_actividad,
    },
}

# Construimos los árboles una sola vez al iniciar el programa
ARBOLES = {clave: datos["construir"]() for clave, datos in ESCENARIOS.items()}


if __name__ == "__main__":
    # Ejecuta:  python escenarios.py   para ver los árboles en la consola
    for clave, arbol in ARBOLES.items():
        print("\n" + "=" * 60)
        print(f"ÁRBOL: {arbol.nombre}")
        print("=" * 60)
        arbol.imprimir()
        e = arbol.estadisticas()
        print(f"\nNodos: {e['nodos']} | Hojas: {e['hojas']} | Altura: {e['altura']} niveles")
        print("Preorden: ", " ".join(e["preorden"]))
        print("Inorden:  ", " ".join(e["inorden"]))
        print("Postorden:", " ".join(e["postorden"]))
