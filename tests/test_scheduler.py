# test_scheduler.py

import sys
# Adiciona o diretório pai (clinica_saudeviva) ao caminho do Python
sys.path.append("..") 
import scheduler # Agora o Python consegue encontrar 'scheduler.py'
# ... o restante do seu código de teste ...# tests/test_scheduler.py
from datetime import datetime
import scheduler # Importa seu módulo

def test_horario_comercial_valido():
    # Segunda-feira às 10:00
    dt = datetime(2025, 11, 10, 10, 0) 
    is_valid, _ = scheduler.is_within_working_hours(dt)
    assert is_valid == True

def test_horario_comercial_invalido_fds():
    # Sábado às 10:00
    dt = datetime(2025, 11, 8, 10, 0)
    is_valid, msg = scheduler.is_within_working_hours(dt)
    assert is_valid == False
    assert "apenas de segunda a sexta" in msg

def test_horario_comercial_invalido_noite():
    # Segunda-feira às 19:00
    dt = datetime(2025, 11, 10, 19, 0)
    is_valid, msg = scheduler.is_within_working_hours(dt)
    assert is_valid == False
    assert "deve ser entre 08:00 e 18:00" in msg

def test_conflito_de_horario():
    consulta_existente = {
        "id": 1, "paciente": "Ana",
        "data_hora_inicio": "2025-11-10T10:00:00",
        "status": "marcada"
    }
    consultas = [consulta_existente]
    # Tenta marcar no mesmo horário
    nova_dt = datetime(2025, 11, 10, 10, 0)
    
    is_available, msg = scheduler.check_availability(consultas, nova_dt)
    assert is_available == False
    assert "Horário em conflito" in msg

def test_sem_conflito_de_horario():
    consulta_existente = {
        "id": 1, "paciente": "Ana",
        "data_hora_inicio": "2025-11-10T10:00:00",
        "status": "marcada"
    }
    consultas = [consulta_existente]
    # Tenta marcar às 10:30 (válido)
    nova_dt = datetime(2025, 11, 10, 10, 30)
    
    is_available, _ = scheduler.check_availability(consultas, nova_dt)
    assert is_available == True