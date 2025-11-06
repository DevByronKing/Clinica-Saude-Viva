# scheduler.py
import storage
from datetime import datetime, time, timedelta

# Constantes das regras de negócio
CLINIC_OPEN = time(8, 0)
CLINIC_CLOSE = time(18, 0)
CONSULTA_DURATION = timedelta(minutes=30)

def is_within_working_hours(dt_consulta):
    """Verifica se está dentro do horário comercial (Seg-Sex, 08:00-18:00)."""
    if dt_consulta.weekday() >= 5:  # 5 = Sábado, 6 = Domingo
        return False, "Agendamentos são permitidos apenas de segunda a sexta."
    
    start_time = dt_consulta.time()
    end_time = (dt_consulta + CONSULTA_DURATION).time()
    
    # Verifica se a consulta (início e fim) está dentro do horário
    if start_time >= CLINIC_OPEN and end_time <= CLINIC_CLOSE:
        return True, ""
    
    return False, f"O horário deve ser entre {CLINIC_OPEN.strftime('%H:%M')} e {CLINIC_CLOSE.strftime('%H:%M')}."

def check_availability(consultas, dt_consulta_inicio):
    """Verifica se o horário está livre, sem sobreposições."""
    dt_consulta_fim = dt_consulta_inicio + CONSULTA_DURATION
    
    for consulta in consultas:
        if consulta['status'] == 'cancelada':
            continue
            
        # Converte strings salvas de volta para datetime
        inicio_existente = datetime.fromisoformat(consulta['data_hora_inicio'])
        fim_existente = inicio_existente + CONSULTA_DURATION
        
        # Lógica de sobreposição
        # (InícioA < FimB) e (FimA > InícioB)
        if (dt_consulta_inicio < fim_existente) and (dt_consulta_fim > inicio_existente):
            return False, f"Horário em conflito com a consulta de {consulta['paciente']}."
            
    return True, ""

def agendar_consulta(paciente, data_str, hora_str):
    """Função principal para criar um novo agendamento."""
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
        "data_hora_inicio": dt_consulta.isoformat(), # Salva em formato padrão
        "duracao_min": 30,
        "status": "marcada"
    }
    
    consultas.append(nova_consulta)
    storage.save_consultas(consultas)
    
    return nova_consulta, "Consulta agendada com sucesso!"

def cancelar_consulta(consulta_id):
    """Cancela uma consulta por ID."""
    consultas = storage.load_consultas()
    consulta_encontrada = None
    
    for consulta in consultas:
        if consulta['id'] == consulta_id and consulta['status'] == 'marcada':
            consulta['status'] = 'cancelada'
            consulta_encontrada = consulta
            break
            
    if consulta_encontrada:
        storage.save_consultas(consultas)
        return True, f"Consulta {consulta_id} de {consulta_encontrada['paciente']} cancelada."
    else:
        return False, f"Consulta ID {consulta_id} não encontrada ou já cancelada."

def listar_consultas():
    """Retorna todas as consultas ativas."""
    consultas = storage.load_consultas()
    ativas = [c for c in consultas if c['status'] == 'marcada']
    return ativas