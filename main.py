import logging
logging.basicConfig(level=logging.INFO, 
                    filename='app.log', 
                    filemode='a', 
                    format='%(asctime)s - %(levelname)s - %(message)s')
# main.py
import scheduler
import ai_services
from datetime import datetime

def print_menu():
    print("\n--- Clínica SaúdeViva ---")
    print("1. Agendar consulta (Linguagem Natural)")
    print("2. Agendar consulta (Manual)")
    print("3. Listar consultas marcadas")
    print("4. Cancelar consulta")
    print("5. Sair")
    return input("Escolha uma opção: ")

def handle_agendamento_natural():
    print("\n--- Agendamento por Linguagem Natural ---")
    solicitacao = input("Digite sua solicitação (ex: 'Marcar para João amanhã às 10h'): ")
    
    dados = ai_services.parse_natural_language(solicitacao)
    
    if not dados:
        print("Desculpe, não consegui entender sua solicitação. Tente novamente.")
        return

    print(f"Dados extraídos: Paciente: {dados['paciente']}, Data: {dados['data']}, Hora: {dados['hora']}")
    confirm = input("Os dados estão corretos? (s/n): ").lower()
    
    if confirm != 's':
        print("Agendamento cancelado.")
        return
        
    agendar_e_confirmar(dados['paciente'], dados['data'], dados['hora'])

def handle_agendamento_manual():
    print("\n--- Agendamento Manual ---")
    paciente = input("Nome do paciente: ")
    data = input("Data (AAAA-MM-DD): ")
    hora = input("Hora (HH:MM): ")
    agendar_e_confirmar(paciente, data, hora)

def agendar_e_confirmar(paciente, data, hora):
    """Função auxiliar para agendar e imprimir confirmação."""
    nova_consulta, msg = scheduler.agendar_consulta(paciente, data, hora)
    
    if nova_consulta:
        print(f"\n[SUCESSO] {msg}")
        # Gerar confirmação com IA
        msg_ia = ai_services.generate_confirmation_message(
            nova_consulta['paciente'],
            nova_consulta['data_hora_inicio']
        )
        print("\n--- Mensagem de Confirmação ---")
        print(msg_ia)
        print("---------------------------------")
    else:
        print(f"\n[ERRO] Não foi possível agendar: {msg}")

def handle_listar_consultas():
    print("\n--- Consultas Marcadas ---")
    consultas = scheduler.listar_consultas()
    if not consultas:
        print("Nenhuma consulta marcada.")
        return
        
    for c in consultas:
        dt = datetime.fromisoformat(c['data_hora_inicio'])
        print(f"ID: {c['id']} | Paciente: {c['paciente']} | Data: {dt.strftime('%d/%m/%Y %H:%M')}")

def handle_cancelar_consulta():
    print("\n--- Cancelar Consulta ---")
    try:
        id_str = input("Digite o ID da consulta a cancelar: ")
        consulta_id = int(id_str)
        success, msg = scheduler.cancelar_consulta(consulta_id)
        print(f"[STATUS] {msg}")
    except ValueError:
        print("[ERRO] ID inválido. Deve ser um número.")

def main():
    while True:
        choice = print_menu()
        
        if choice == '1':
            handle_agendamento_natural()
        elif choice == '2':
            handle_agendamento_manual() # Bônus: ter um modo manual é bom
        elif choice == '3':
            handle_listar_consultas()
        elif choice == '4':
            handle_cancelar_consulta()
        elif choice == '5':
            print("Obrigado por usar o sistema SaúdeViva. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()