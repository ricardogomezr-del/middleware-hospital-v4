"""Middleware Hospitalario V4: laboratorio, facturación, farmacia y radiología."""
import datetime
import os
import jwt
from flask import Flask, jsonify, request
from transformaciones import DESTINOS_PERMITIDOS, ErrorValidacion, transformar

app = Flask(__name__)
JWT_SECRET = os.environ.get("JWT_SECRET", "clave_temporal_solo_desarrollo_no_produccion_2026")
USUARIO = os.environ.get("HOSPITAL_USER", "hospital")
PASSWORD = os.environ.get("HOSPITAL_PASSWORD", "1234")

def _destino_simulado(sistema, datos):
    return {"sistema": sistema, "estado": "RECIBIDO", "datos_recibidos": datos}

def laboratorio(datos):
    return _destino_simulado("LABORATORIO", datos)

def facturacion(datos):
    return _destino_simulado("FACTURACION", datos)

def farmacia(datos):
    return _destino_simulado("FARMACIA", datos)

def radiologia(datos):
    return _destino_simulado("RADIOLOGIA", datos)

SISTEMAS = {"LABORATORIO": laboratorio, "FACTURACION": facturacion,
            "FARMACIA": farmacia, "RADIOLOGIA": radiologia}

def validar_token():
    auth = request.headers.get("Authorization")
    if not auth:
        return False, "Token no enviado"
    partes = auth.split()
    if len(partes) != 2 or partes[0].lower() != "bearer":
        return False, "Formato de autorización incorrecto"
    try:
        payload = jwt.decode(partes[1], JWT_SECRET, algorithms=["HS256"])
        if not isinstance(payload.get("usuario"), str) or not payload["usuario"]:
            return False, "Token inválido"
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token vencido"
    except jwt.InvalidTokenError:
        return False, "Token inválido"

@app.get("/")
def inicio():
    return jsonify({"aplicacion": "Middleware Hospitalario V4", "arquitectura": "API REST + JWT",
                    "estado": "ACTIVO", "destinos": DESTINOS_PERMITIDOS,
                    "endpoints": {"login": "POST /login", "middleware": "POST /middleware"}})

@app.post("/login")
def login():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or not datos:
        return jsonify({"error": "Debe enviar información en formato JSON"}), 400
    if datos.get("usuario") != USUARIO or datos.get("password") != PASSWORD:
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401
    ahora = datetime.datetime.now(datetime.timezone.utc)
    token = jwt.encode({"usuario": USUARIO, "iat": ahora,
                        "exp": ahora + datetime.timedelta(minutes=30)}, JWT_SECRET, algorithm="HS256")
    return jsonify({"mensaje": "Autenticación correcta", "token": token,
                    "tipo": "Bearer", "vigencia_minutos": 30}), 200

@app.post("/middleware")
def middleware():
    valido, resultado_token = validar_token()
    if not valido:
        return jsonify({"etapa": "SEGURIDAD", "error": resultado_token}), 401
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or not datos:
        return jsonify({"etapa": "RECEPCION", "error": "Debe enviar información en formato JSON"}), 400
    if "paciente" not in datos or "destino" not in datos:
        return jsonify({"etapa": "VALIDACION", "error": "Se requieren los campos paciente y destino"}), 400
    destino = datos["destino"].strip().upper() if isinstance(datos["destino"], str) else ""
    if destino not in SISTEMAS:
        return jsonify({"etapa": "ENRUTAMIENTO", "error": "Destino no reconocido",
                        "destinos_permitidos": DESTINOS_PERMITIDOS}), 400
    try:
        transformados = transformar(destino, datos)
    except ErrorValidacion as error:
        return jsonify({"etapa": "VALIDACION", "error": str(error)}), 400
    respuesta = SISTEMAS[destino](transformados)
    return jsonify({"mensaje": "Solicitud procesada correctamente",
                    "usuario_autenticado": resultado_token["usuario"],
                    "destino_seleccionado": destino, "datos_originales": datos,
                    "datos_transformados": transformados, "respuesta_destino": respuesta}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
