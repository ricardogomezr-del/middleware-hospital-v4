import os
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"]=True
    return app.test_client()

@pytest.fixture
def jwt_header(client):
    r=client.post("/login",json={"usuario":os.environ.get("HOSPITAL_USER","hospital"),"password":os.environ.get("HOSPITAL_PASSWORD","1234")})
    assert r.status_code==200
    return {"Authorization":"Bearer "+r.get_json()["token"]}

@pytest.mark.parametrize("destino,body,campo,esperado",[
    ("LABORATORIO",{"paciente":101,"examen":"HEMOGRAMA"},"tipo_examen","HEMOGRAMA"),
    ("FACTURACION",{"paciente":205,"concepto":"CONSULTA","valor":85000},"valor",85000),
    ("FARMACIA",{"paciente":620,"solicitud":"AMOXICILINA","cantidad":20},"requiere_autorizacion",False),
    ("FARMACIA",{"paciente":711,"solicitud":"ACETAMINOFEN","cantidad":50},"requiere_autorizacion",True),
    ("RADIOLOGIA",{"paciente":845,"solicitud":"RADIOGRAFIA DE TORAX","urgente":False},"prioridad","NORMAL"),
    ("RADIOLOGIA",{"paciente":846,"solicitud":"TOMOGRAFIA","urgente":True},"prioridad","URGENTE")
])
def test_destinos(client,jwt_header,destino,body,campo,esperado):
    r=client.post("/middleware",headers=jwt_header,json={**body,"destino":destino})
    assert r.status_code==200
    assert r.get_json()["datos_transformados"][campo]==esperado

def test_sin_jwt(client):
    r=client.post("/middleware",json={"paciente":1,"destino":"LABORATORIO","examen":"A"})
    assert r.status_code==401

def test_jwt_invalido(client):
    r=client.post("/middleware",headers={"Authorization":"Bearer invalido"},json={"paciente":1,"destino":"LABORATORIO","examen":"A"})
    assert r.status_code==401

def test_incompleto(client,jwt_header):
    r=client.post("/middleware",headers=jwt_header,json={"paciente":620,"destino":"FARMACIA","solicitud":"A"})
    assert r.status_code==400

def test_destino_desconocido(client,jwt_header):
    r=client.post("/middleware",headers=jwt_header,json={"paciente":1,"destino":"CARDIOLOGIA"})
    assert r.status_code==400
