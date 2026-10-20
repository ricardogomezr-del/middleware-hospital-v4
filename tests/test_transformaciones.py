import pytest
from transformaciones import transformar, ErrorValidacion

@pytest.mark.parametrize("cantidad,esperado", [(20,False),(30,False),(31,True),(50,True)])
def test_regla_farmacia(cantidad, esperado):
    salida=transformar("FARMACIA", {"paciente":620,"solicitud":"AMOXICILINA","cantidad":cantidad})
    assert salida == {"id_paciente":620,"medicamento":"AMOXICILINA","unidades":cantidad,"requiere_autorizacion":esperado}

@pytest.mark.parametrize("urgente,prioridad", [(True,"URGENTE"),(False,"NORMAL")])
def test_radiologia(urgente,prioridad):
    salida=transformar("RADIOLOGIA",{"paciente":845,"solicitud":"RADIOGRAFIA DE TORAX","urgente":urgente})
    assert salida["tipo_estudio"]=="RADIOGRAFIA DE TORAX"
    assert salida["prioridad"]==prioridad

def test_laboratorio_existente():
    assert transformar("LABORATORIO",{"paciente":101,"examen":"HEMOGRAMA"})["prioridad"]=="NORMAL"

def test_facturacion_existente():
    assert transformar("FACTURACION",{"paciente":205,"concepto":"CONSULTA","valor":85000})["valor"]==85000

@pytest.mark.parametrize("destino,datos",[("FARMACIA",{"paciente":620,"solicitud":"A"}),("RADIOLOGIA",{"paciente":845,"solicitud":"R"}),("FARMACIA",{"paciente":620,"solicitud":"A","cantidad":-1})])
def test_incompletos(destino,datos):
    with pytest.raises(ErrorValidacion):
        transformar(destino,datos)
