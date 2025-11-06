# scheduler.py
"""
Módulo responsável pela lógica de agendamento de consultas da Clínica SaúdeViva.

Este módulo implementa as regras de negócio para agendamento, incluindo:
- Validação de horário comercial
- Verificação de disponibilidade
- Gerenciamento de consultas (agendamento, cancelamento, listagem)
- Controle de conflitos de horário

As consultas são armazenadas através do módulo storage e seguem as regras:
- Horário de funcionamento: Segunda a Sexta, 08:00-18:00
- Duração padrão: 30 minutos
- Sem sobreposição de horários
"""

import storage
from datetime import datetime, time, timedelta
from typing import Tuple, List, Dict, Optional, Any

# Constantes das regras de negócio
CLINIC_OPEN = time(8, 0)
CLINIC_CLOSE = time(18, 0)
CONSULTA_DURATION = timedelta(minutes=30)


def is_within_working_hours(dt_consulta: datetime) -> Tuple[bool, str]:
    """
    Verifica se o horário solicitado está dentro do período de atendimento da clínica.

    Valida se a consulta:
    1. Está em um dia útil (segunda a sexta)
    2. Começa após o horário de abertura (08:00)
    3. Termina antes do horário de fechamento (18:00)

    Args:
        dt_consulta (datetime): Data e hora da consulta proposta

    Returns:
        Tuple[bool, str]: Uma tupla contendo:
            - bool: True se o horário é válido, False caso contrário
            - str: Mensagem explicativa em caso de horário inválido, ou string vazia
                  se o horário for válido

    Example:
        >>> is_within_working_hours(datetime(2025, 11, 8, 10, 0))  # Sábado
        (False, "Agendamentos são permitidos apenas de segunda a sexta.")
    """
    if dt_consulta.weekday() >= 5:  # 5 = Sábado, 6 = Domingo
        return False, "Agendamentos são permitidos apenas de segunda a sexta."

    start_time = dt_consulta.time()
    end_time = (dt_consulta + CONSULTA_DURATION).time()

    # Verifica se a consulta (início e fim) está dentro do horário
    if start_time >= CLINIC_OPEN and end_time <= CLINIC_CLOSE:
        return True, ""

    msg = (
        f"O horário deve ser entre {CLINIC_OPEN.strftime('%H:%M')} "
        f"e {CLINIC_CLOSE.strftime('%H:%M')}."
    )
    return False, msg


def check_availability(
    consultas: List[Dict[str, Any]], dt_consulta_inicio: datetime
) -> Tuple[bool, str]:
    """
    Verifica disponibilidade do horário, garantindo que não haja sobreposição.

    Analisa todas as consultas existentes (exceto canceladas) para garantir que
    não haja conflito de horário com a nova consulta proposta.

    Args:
        consultas (List[Dict[str, Any]]): Lista de consultas existentes
        dt_consulta_inicio (datetime): Data e hora de início da nova consulta

    Returns:
        Tuple[bool, str]: Uma tupla contendo:
            - bool: True se o horário está disponível, False se há conflito
            - str: Mensagem explicativa em caso de conflito, ou string vazia
                  se o horário estiver disponível

    Note:
        Uma consulta é considerada em conflito se houver qualquer sobreposição
        no período de 30 minutos a partir do horário de início.
    """
    dt_consulta_fim = dt_consulta_inicio + CONSULTA_DURATION

    for consulta in consultas:
        if consulta["status"] == "cancelada":
            continue

        # Converte strings salvas de volta para datetime
        inicio_existente = datetime.fromisoformat(consulta["data_hora_inicio"])
        fim_existente = inicio_existente + CONSULTA_DURATION

        # Lógica de sobreposição
        # (InícioA < FimB) e (FimA > InícioB)
        if (dt_consulta_inicio < fim_existente) and (
            dt_consulta_fim > inicio_existente
        ):
            return (
                False,
                f"Horário em conflito com a consulta de {consulta['paciente']}.",
            )

    return True, ""


def agendar_consulta(
    paciente: str, data_str: str, hora_str: str
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Agenda uma nova consulta com validações de regras de negócio.

    Esta é a função principal do módulo, que coordena todo o processo de
    agendamento, incluindo:
    1. Validação do formato de data e hora
    2. Verificação do horário comercial
    3. Verificação de disponibilidade
    4. Criação e persistência do agendamento

    Args:
        paciente (str): Nome do paciente
        data_str (str): Data no formato AAAA-MM-DD
        hora_str (str): Hora no formato HH:MM

    Returns:
        Tuple[Optional[Dict[str, Any]], str]: Uma tupla contendo:
            - Dict: Dados da consulta criada ou None se houve erro
            - str: Mensagem de sucesso ou descrição do erro

    Examples:
        >>> agendar_consulta("João Silva", "2025-11-07", "14:30")
        ({'id': 1, 'paciente': 'João Silva', ...}, "Consulta agendada com sucesso!")
        >>> agendar_consulta("Maria", "2025-11-09", "10:00")
        (None, "Agendamentos são permitidos apenas de segunda a sexta.")
    """
    try:
        dt_consulta = datetime.fromisoformat(f"{data_str}T{hora_str}")
    except ValueError:
        return None, "Formato de data ou hora inválido. Use AAAA-MM-DD e HH:MM."

    # 1. Validar horário comercial
    is_valid_time, time_msg = is_within_working_hours(dt_consulta)
    if not is_valid_time:
        return None, time_msg

    # 2. Carregar consultas e verificar disponibilidade
    consultas = storage.load_consultas()
    is_available, conflict_msg = check_availability(consultas, dt_consulta)
    if not is_available:
        return None, conflict_msg

    # 3. Tudo certo, criar e salvar
    nova_consulta = {
        "id": len(consultas) + 1,
        "paciente": paciente,
        "data_hora_inicio": dt_consulta.isoformat(),  # Salva em formato padrão
        "duracao_min": 30,
        "status": "marcada",
    }

    consultas.append(nova_consulta)
    storage.save_consultas(consultas)

    return nova_consulta, "Consulta agendada com sucesso!"


def cancelar_consulta(consulta_id: int) -> Tuple[bool, str]:
    """
    Cancela uma consulta existente pelo seu ID.

    Busca uma consulta com status 'marcada' pelo ID fornecido e
    altera seu status para 'cancelada'.

    Args:
        consulta_id (int): ID único da consulta a ser cancelada

    Returns:
        Tuple[bool, str]: Uma tupla contendo:
            - bool: True se a consulta foi cancelada com sucesso,
                   False se não foi encontrada ou já estava cancelada
            - str: Mensagem de confirmação ou erro

    Example:
        >>> cancelar_consulta(1)
        (True, "Consulta 1 de João Silva cancelada.")
    """
    consultas = storage.load_consultas()
    consulta_encontrada = None

    for consulta in consultas:
        if consulta["id"] == consulta_id and consulta["status"] == "marcada":
            consulta["status"] = "cancelada"
            consulta_encontrada = consulta
            break

    if consulta_encontrada:
        storage.save_consultas(consultas)
        return (
            True,
            f"Consulta {consulta_id} de {consulta_encontrada['paciente']} cancelada.",
        )
    else:
        return False, f"Consulta ID {consulta_id} não encontrada ou já cancelada."


def listar_consultas() -> List[Dict[str, Any]]:
    """
    Retorna a lista de todas as consultas com status 'marcada'.

    Returns:
        List[Dict[str, Any]]: Lista de consultas ativas, onde cada consulta é
        um dicionário contendo:
            - id (int): ID único da consulta
            - paciente (str): Nome do paciente
            - data_hora_inicio (str): Data e hora no formato ISO
            - duracao_min (int): Duração em minutos
            - status (str): Status da consulta (sempre 'marcada' neste caso)

    Note:
        Esta função filtra automaticamente consultas canceladas,
        retornando apenas as ativas.
    """
    consultas = storage.load_consultas()
    ativas = [c for c in consultas if c["status"] == "marcada"]
    return ativas
