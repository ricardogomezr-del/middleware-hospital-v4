# Middleware Hospitalario V4

Proyecto Flask de la V3 ampliado para trabajar con **LABORATORIO, FACTURACION, FARMACIA y RADIOLOGIA**. La integración con cada sistema está simulada, como en el proyecto de clase; esta demo no transmite datos a servidores hospitalarios reales.

## Endpoints

- `GET /`: comprueba el estado del servicio y los destinos.
- `POST /login`: recibe `{"usuario":"hospital","password":"<contraseña configurada>"}` y entrega JWT válido por 30 minutos.
- `POST /middleware`: requiere `Authorization: Bearer <JWT>` y JSON de solicitud.

## Formatos esperados

| Destino | Entrada además de paciente y destino | Datos transformados |
|---|---|---|
| LABORATORIO | examen, urgente (opcional) | id_paciente, tipo_examen, prioridad |
| FACTURACION | concepto, valor | id_paciente, concepto, valor |
| FARMACIA | solicitud, cantidad | id_paciente, medicamento, unidades, requiere_autorizacion |
| RADIOLOGIA | solicitud, urgente | id_paciente, tipo_estudio, prioridad |

Farmacia: `requiere_autorizacion=true` solo cuando `cantidad > 30`. Radiología: `prioridad=URGENTE` si `urgente=true`; `NORMAL` si es falso.

## Desarrollo local

```bash
pip install -r requirements.txt
python app.py
```

Para el entorno local, la V3 usa las credenciales de ejemplo `hospital` / `1234`. **En Render se deben definir HOSPITAL_USER, HOSPITAL_PASSWORD y JWT_SECRET como variables de entorno y utilizar credenciales seguras.** No se deben publicar esos secretos en GitHub.

## Pruebas

1. Iniciar el servidor o usar la URL pública en Render.
2. Realizar `POST /login` y copiar el JWT.
3. Probar los destinos con `POST /middleware` y encabezado `Authorization: Bearer <JWT>`.
4. Confirmar respuestas 200 para solicitudes correctas, 401 cuando falta o falla JWT y 400 para datos incompletos o destinos inexistentes.
5. La colección de pruebas y los ejemplos se distribuyen en el paquete ZIP del taller, para importación en Hoppscotch.

**Nota:** una respuesta de los destinos confirma la transformación y el enrutamiento simulado; no equivale a registrar medicamentos, estudios o facturas en sistemas reales.
