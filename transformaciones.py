"""Validaciones y transformaciones de solicitudes hospitalarias."""
import math
DESTINOS_PERMITIDOS = ["LABORATORIO", "FACTURACION", "FARMACIA", "RADIOLOGIA"]

class ErrorValidacion(ValueError):
    pass

def _texto(datos, campo, mensaje):
    valor = datos.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorValidacion(mensaje)
    return valor.strip()

def _paciente(datos):
    paciente = datos.get("paciente")
    if isinstance(paciente, bool) or not isinstance(paciente, int) or paciente <= 0:
        raise ErrorValidacion("paciente debe ser un entero positivo")
    return paciente

def _booleano(datos, campo, obligatorio=False):
    if campo not in datos:
        if obligatorio:
            raise ErrorValidacion(f"Se requiere el campo {campo}")
        return False
    if not isinstance(datos[campo], bool):
        raise ErrorValidacion(f"{campo} debe ser true o false")
    return datos[campo]

def transformar(destino, datos):
    paciente = _paciente(datos)
    if destino == "LABORATORIO":
        examen = _texto(datos, "examen", "No se especificó el examen")
        urgente = _booleano(datos, "urgente")
        return {"id_paciente": paciente, "tipo_examen": examen, "prioridad": "URGENTE" if urgente else "NORMAL"}
    if destino == "FACTURACION":
        if "concepto" not in datos or "valor" not in datos:
            raise ErrorValidacion("Se requieren concepto y valor")
        concepto = _texto(datos, "concepto", "concepto no puede estar vacío")
        valor = datos["valor"]
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor) or valor <= 0:
            raise ErrorValidacion("valor debe ser un número mayor que cero")
        return {"id_paciente": paciente, "concepto": concepto, "valor": valor}
    if destino == "FARMACIA":
        if "solicitud" not in datos or "cantidad" not in datos:
            raise ErrorValidacion("Se requieren solicitud y cantidad para Farmacia")
        medicamento = _texto(datos, "solicitud", "solicitud debe indicar un medicamento")
        cantidad = datos["cantidad"]
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
            raise ErrorValidacion("cantidad debe ser un entero positivo")
        return {"id_paciente": paciente, "medicamento": medicamento, "unidades": cantidad, "requiere_autorizacion": cantidad > 30}
    if destino == "RADIOLOGIA":
        if "solicitud" not in datos or "urgente" not in datos:
            raise ErrorValidacion("Se requieren solicitud y urgente para Radiología")
        estudio = _texto(datos, "solicitud", "solicitud debe indicar el estudio")
        urgente = _booleano(datos, "urgente", obligatorio=True)
        return {"id_paciente": paciente, "tipo_estudio": estudio, "prioridad": "URGENTE" if urgente else "NORMAL"}
    raise ErrorValidacion("Destino no reconocido")
