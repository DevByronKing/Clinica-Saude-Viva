# tests/test_scheduler.py
import pytest
from datetime import datetime
from scheduler import (
    is_within_working_hours,
    check_availability,
    agendar_consulta,
    cancelar_consulta,
    listar_consultas,
)


# --- Testes para is_within_working_hours ---


def test_horario_valido_dentro_do_expediente():
    # Uma quarta-feira às 10:00
    dt_valida = datetime(2025, 11, 12, 10, 0)
    is_valid, msg = is_within_working_hours(dt_valida)
    assert is_valid is True
    assert msg == ""


def test_horario_invalido_antes_do_expediente():
    # Uma quarta-feira às 07:00
    dt_invalida = datetime(2025, 11, 12, 7, 0)
    is_valid, msg = is_within_working_hours(dt_invalida)
    assert is_valid is False
    assert "O horário deve ser entre 08:00 e 18:00" in msg


def test_horario_invalido_depois_do_expediente():
    # Uma quarta-feira às 18:00 (terminaria 18:30)
    dt_invalida = datetime(2025, 11, 12, 18, 0)
    is_valid, msg = is_within_working_hours(dt_invalida)
    assert is_valid is False
    assert "O horário deve ser entre 08:00 e 18:00" in msg


def test_horario_invalido_fim_de_semana():
    # Um sábado às 10:00
    dt_invalida = datetime(2025, 11, 15, 10, 0)
    is_valid, msg = is_within_working_hours(dt_invalida)
    assert is_valid is False
    assert "permitidos apenas de segunda a sexta" in msg


# --- Testes para check_availability ---


@pytest.fixture
def consultas_exemplo():
    """Fornece uma lista de consultas de exemplo para os testes."""
    return [
        {
            "id": 1,
            "paciente": "Maria Silva",
            "data_hora_inicio": "2025-11-14T15:00:00",  # Sexta
            "duracao_min": 30,
            "status": "marcada",
        },
        {
            "id": 2,
            "paciente": "Jose",
            "data_hora_inicio": "2025-11-17T09:00:00",  # Segunda
            "duracao_min": 30,
            "status": "cancelada",  # Esta não deve bloquear o horário
        },
    ].copy()


def test_disponibilidade_com_horario_livre(consultas_exemplo):
    # Tentar marcar na Segunda às 10:00 (Maria é na Sexta)
    dt_nova = datetime(2025, 11, 17, 10, 0)
    is_available, msg = check_availability(consultas_exemplo, dt_nova)
    assert is_available is True
    assert msg == ""


def test_disponibilidade_com_horario_ocupado(consultas_exemplo):
    # Tentar marcar no mesmo horário de Maria
    dt_conflito = datetime(2025, 11, 14, 15, 0)
    is_available, msg = check_availability(consultas_exemplo, dt_conflito)
    assert is_available is False
    assert "Horário em conflito com a consulta de Maria Silva" in msg


def test_disponibilidade_com_horario_sobreposto_inicio(consultas_exemplo):
    # Tentar marcar às 14:45 (termina 15:15, conflita com Maria às 15:00)
    dt_conflito = datetime(2025, 11, 14, 14, 45)
    is_available, msg = check_availability(consultas_exemplo, dt_conflito)
    assert is_available is False
    assert "Horário em conflito com a consulta de Maria Silva" in msg


def test_disponibilidade_com_horario_sobreposto_fim(consultas_exemplo):
    # Tentar marcar às 15:15 (começa antes de Maria terminar às 15:30)
    dt_conflito = datetime(2025, 11, 14, 15, 15)
    is_available, msg = check_availability(consultas_exemplo, dt_conflito)
    assert is_available is False
    assert "Horário em conflito com a consulta de Maria Silva" in msg


def test_disponibilidade_com_horario_cancelado(consultas_exemplo):
    # Tentar marcar no horário de Jose (que está cancelado)
    dt_livre = datetime(2025, 11, 17, 9, 0)
    is_available, msg = check_availability(consultas_exemplo, dt_livre)
    assert is_available is True
    assert msg == ""


# --- Testes para agendar_consulta (usando Mocker) ---


def test_agendar_consulta_sucesso(mocker, consultas_exemplo):
    """Testa o agendamento de uma consulta válida, simulando o storage."""

    # Cria uma cópia da lista de consultas para o teste
    consultas_teste = consultas_exemplo.copy()

    # Simula (mock) as funções do storage
    # Queremos que `load_consultas` retorne nossa lista de exemplo
    mocker.patch("storage.load_consultas", return_value=consultas_teste)
    # Apenas observamos `save_consultas`, não precisa retornar nada
    mock_save = mocker.patch("storage.save_consultas")

    # Dados do novo agendamento
    paciente = "Novo Paciente"
    data_str = "2025-11-18"
    hora_str = "14:00"

    nova_consulta, msg = agendar_consulta(paciente, data_str, hora_str)

    # Verifica se a consulta foi criada
    assert nova_consulta is not None
    assert nova_consulta["paciente"] == paciente
    assert msg == "Consulta agendada com sucesso!"

    # Verifica se a função save_consultas foi chamada 1 vez
    mock_save.assert_called_once()
    # Pega os argumentos com que `save_consultas` foi chamada
    args_chamada = mock_save.call_args[0]
    lista_salva = args_chamada[0]

    # Verifica se a nova consulta está na lista que foi salva
    assert len(lista_salva) == len(consultas_exemplo) + 1
    assert lista_salva[-1]["paciente"] == "Novo Paciente"


def test_agendar_consulta_falha_horario_comercial(mocker):
    """Testa se o agendamento falha se for fora do horário comercial."""
    # Não precisamos simular o storage, pois a falha deve ocorrer antes

    paciente = "Paciente Noturno"
    data_str = "2025-11-18"
    hora_str = "07:00"  # Fora do horário

    nova_consulta, msg = agendar_consulta(paciente, data_str, hora_str)

    assert nova_consulta is None
    assert "O horário deve ser entre 08:00 e 18:00" in msg


def test_agendar_consulta_falha_conflito(mocker, consultas_exemplo):
    """Testa se o agendamento falha se houver conflito."""
    # Simula `load_consultas` para retornar nossa lista
    mocker.patch("storage.load_consultas", return_value=consultas_exemplo)

    # Tenta marcar no mesmo horário de Maria
    paciente = "Paciente Atrasado"
    data_str = "2025-11-14"
    hora_str = "15:00"

    nova_consulta, msg = agendar_consulta(paciente, data_str, hora_str)

    assert nova_consulta is None
    assert "Horário em conflito com a consulta de Maria Silva" in msg


# --- Testes para cancelamento de consultas ---


def test_cancelar_consulta_sucesso(mocker, consultas_exemplo):
    """Testa o cancelamento de uma consulta existente."""
    # Configura o mock para retornar nossa lista de exemplo
    mocker.patch("storage.load_consultas", return_value=consultas_exemplo)
    mock_save = mocker.patch("storage.save_consultas")

    # Tenta cancelar a consulta da Maria (ID 1)
    success, msg = cancelar_consulta(1)

    assert success is True
    assert "Maria Silva cancelada" in msg
    mock_save.assert_called_once()

    # Verifica se o status foi atualizado na lista salva
    args_chamada = mock_save.call_args[0]
    lista_salva = args_chamada[0]
    consulta_cancelada = next(c for c in lista_salva if c["id"] == 1)
    assert consulta_cancelada["status"] == "cancelada"


def test_cancelar_consulta_inexistente(mocker, consultas_exemplo):
    """Testa tentativa de cancelar uma consulta que não existe."""
    mocker.patch("storage.load_consultas", return_value=consultas_exemplo)
    mock_save = mocker.patch("storage.save_consultas")

    # Tenta cancelar uma consulta com ID inexistente
    success, msg = cancelar_consulta(999)

    assert success is False
    assert "não encontrada" in msg
    mock_save.assert_not_called()


def test_cancelar_consulta_ja_cancelada(mocker, consultas_exemplo):
    """Testa tentativa de cancelar uma consulta já cancelada."""
    mocker.patch("storage.load_consultas", return_value=consultas_exemplo)
    mock_save = mocker.patch("storage.save_consultas")

    # Tenta cancelar a consulta do Jose (ID 2) que já está cancelada
    success, msg = cancelar_consulta(2)

    assert success is False
    assert "não encontrada ou já cancelada" in msg
    mock_save.assert_not_called()


# --- Testes para listagem de consultas ---


def test_listar_consultas_ativas(mocker, consultas_exemplo):
    """Testa a listagem de consultas ativas."""
    mocker.patch("storage.load_consultas", return_value=consultas_exemplo)

    consultas_ativas = listar_consultas()

    # Deve retornar apenas a consulta da Maria (status='marcada')
    assert len(consultas_ativas) == 1
    assert consultas_ativas[0]["paciente"] == "Maria Silva"
    assert consultas_ativas[0]["status"] == "marcada"


# --- Testes adicionais de validação ---


def test_agendar_consulta_formato_data_invalido():
    """Testa agendamento com formato de data inválido."""
    paciente = "Paciente Teste"
    data_str = "25/11/2025"  # Formato incorreto
    hora_str = "14:00"

    nova_consulta, msg = agendar_consulta(paciente, data_str, hora_str)

    assert nova_consulta is None
    assert "Formato de data ou hora inválido" in msg


def test_agendar_consulta_formato_hora_invalido():
    """Testa agendamento com formato de hora inválido."""
    paciente = "Paciente Teste"
    data_str = "2025-11-25"
    hora_str = "2pm"  # Formato incorreto

    nova_consulta, msg = agendar_consulta(paciente, data_str, hora_str)

    assert nova_consulta is None
    assert "Formato de data ou hora inválido" in msg


def test_agendar_consulta_horario_limite_manha(mocker):
    """Testa agendamento no primeiro horário do dia."""
    paciente = "Paciente Madrugador"
    data_str = "2025-11-25"
    hora_str = "08:00"  # Primeiro horário permitido

    # Evita tocar no arquivo real durante o teste
    mocker.patch("storage.load_consultas", return_value=[])
    mocker.patch("storage.save_consultas")

    nova_consulta, msg = agendar_consulta(paciente, data_str, hora_str)

    assert nova_consulta is not None
    assert msg == "Consulta agendada com sucesso!"


def test_agendar_consulta_horario_limite_tarde(mocker):
    """Testa agendamento no último horário possível do dia."""
    paciente = "Paciente Tardio"
    data_str = "2025-11-25"
    hora_str = "17:30"  # Último horário possível (termina às 18:00)

    # Evita tocar no arquivo real durante o teste
    mocker.patch("storage.load_consultas", return_value=[])
    mocker.patch("storage.save_consultas")

    nova_consulta, msg = agendar_consulta(paciente, data_str, hora_str)

    assert nova_consulta is not None
    assert msg == "Consulta agendada com sucesso!"
