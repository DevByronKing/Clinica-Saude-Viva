# main.py
"""
Módulo principal do sistema de agendamento da Clínica SaúdeViva.

Este módulo implementa a interface de linha de comando para o sistema,
permitindo que os usuários:
- Agendem consultas usando linguagem natural
- Agendem consultas manualmente
- Listem consultas existentes
- Cancelem consultas

O módulo também configura o sistema de logging para rastrear todas as operações.

Note:
    Todas as operações são registradas no arquivo 'app.log' para
    fins de auditoria e debug.
"""

import logging
import scheduler
import ai_services
from datetime import datetime
# typing imports removed (unused) to satisfy lint


logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def print_menu() -> str:
    """
    Exibe o menu principal do sistema e captura a escolha do usuário.

    O menu apresenta todas as operações disponíveis no sistema de forma
    clara e organizada.

    Returns:
        str: A opção escolhida pelo usuário (1-5)
    """
    print("\n--- Clínica SaúdeViva ---")
    print("1. Agendar consulta (Linguagem Natural)")
    print("2. Agendar consulta (Manual)")
    print("3. Listar consultas marcadas")
    print("4. Cancelar consulta")
    print("5. Sair")
    return input("Escolha uma opção: ")


def handle_agendamento_natural() -> None:
    """
    Processa o agendamento de consulta usando linguagem natural.

    Esta função permite que o usuário digite sua solicitação em linguagem
    natural (ex: "Marcar para João amanhã às 10h"), utiliza IA para
    extrair as informações relevantes e confirma os dados antes de
    realizar o agendamento.

    Note:
        - Utiliza o módulo ai_services para processar a linguagem natural
        - Pede confirmação do usuário antes de agendar
        - Em caso de erro na interpretação, permite nova tentativa
    """
    print("\n--- Agendamento por Linguagem Natural ---")
    solicitacao = input(
        "Digite sua solicitação (ex: 'Marcar para João amanhã às 10h'): "
    )

    dados = ai_services.parse_natural_language(solicitacao)

    if not dados:
        print("Desculpe, não consegui entender sua solicitação. Tente novamente.")
        return

    info = (
        f"Dados extraídos: Paciente: {dados['paciente']}, "
        f"Data: {dados['data']}, Hora: {dados['hora']}"
    )
    print(info)
    confirm = input("Os dados estão corretos? (s/n): ").lower()

    if confirm != "s":
        print("Agendamento cancelado.")
        return

    agendar_e_confirmar(dados["paciente"], dados["data"], dados["hora"])


def handle_agendamento_manual() -> None:
    """
    Processa o agendamento manual de consulta.

    Solicita ao usuário que insira diretamente:
    - Nome do paciente
    - Data (formato AAAA-MM-DD)
    - Hora (formato HH:MM)

    Note:
        Esta função oferece uma alternativa ao agendamento por linguagem
        natural, útil quando se deseja mais controle sobre o formato
        dos dados ou quando o processamento de linguagem natural
        não está funcionando como esperado.
    """
    print("\n--- Agendamento Manual ---")
    paciente = input("Nome do paciente: ")
    data = input("Data (AAAA-MM-DD): ")
    hora = input("Hora (HH:MM): ")
    agendar_e_confirmar(paciente, data, hora)


def agendar_e_confirmar(paciente: str, data: str, hora: str) -> None:
    """
    Função auxiliar para realizar o agendamento e gerar confirmação.

    Esta função centraliza a lógica comum de agendamento, sendo utilizada
    tanto pelo agendamento natural quanto manual. Ela:
    1. Tenta criar o agendamento
    2. Exibe o resultado (sucesso ou erro)
    3. Em caso de sucesso, gera e exibe mensagem personalizada de confirmação

    Args:
        paciente (str): Nome do paciente
        data (str): Data no formato AAAA-MM-DD
        hora (str): Hora no formato HH:MM

    Note:
        Em caso de sucesso, uma mensagem amigável é gerada pela IA
        para confirmar o agendamento.
    """
    nova_consulta, msg = scheduler.agendar_consulta(paciente, data, hora)

    if nova_consulta:
        print(f"\n[SUCESSO] {msg}")
        # Gerar confirmação com IA
        msg_ia = ai_services.generate_confirmation_message(
            nova_consulta["paciente"], nova_consulta["data_hora_inicio"]
        )
        print("\n--- Mensagem de Confirmação ---")
        print(msg_ia)
        print("---------------------------------")
    else:
        print(f"\n[ERRO] Não foi possível agendar: {msg}")


def handle_listar_consultas() -> None:
    """
    Lista todas as consultas ativas do sistema.

    Exibe uma lista formatada das consultas marcadas, mostrando:
    - ID da consulta
    - Nome do paciente
    - Data e hora formatadas de forma amigável

    Note:
        Apenas consultas com status 'marcada' são exibidas.
        A data é formatada no padrão brasileiro (DD/MM/AAAA).
    """
    print("\n--- Consultas Marcadas ---")
    consultas = scheduler.listar_consultas()
    if not consultas:
        print("Nenhuma consulta marcada.")
        return

    for c in consultas:
        dt = datetime.fromisoformat(c["data_hora_inicio"])
        info = (
            f"ID: {c['id']} | Paciente: {c['paciente']} | "
            f"Data: {dt.strftime('%d/%m/%Y %H:%M')}"
        )
        print(info)


def handle_cancelar_consulta() -> None:
    """
    Processa o cancelamento de uma consulta.

    Solicita o ID da consulta ao usuário e tenta realizar o cancelamento.
    Lida com erros de entrada (IDs inválidos) e exibe o resultado da
    operação de forma clara.

    Note:
        - Aceita apenas números inteiros como ID
        - Exibe mensagem específica para IDs inválidos
        - Confirma o cancelamento com o nome do paciente
    """
    print("\n--- Cancelar Consulta ---")
    try:
        id_str = input("Digite o ID da consulta a cancelar: ")
        consulta_id = int(id_str)
        success, msg = scheduler.cancelar_consulta(consulta_id)
        print(f"[STATUS] {msg}")
    except ValueError:
        print("[ERRO] ID inválido. Deve ser um número.")


def main() -> None:
    """
    Função principal do sistema de agendamento.

    Implementa o loop principal do programa, que:
    1. Exibe o menu de opções
    2. Captura a escolha do usuário
    3. Direciona para a função apropriada
    4. Repete até que o usuário escolha sair

    Note:
        O sistema continua rodando até que a opção 5 (Sair)
        seja selecionada.
    """
    while True:
        choice = print_menu()

        if choice == "1":
            handle_agendamento_natural()
        elif choice == "2":
            handle_agendamento_manual()  # Bônus: ter um modo manual é bom
        elif choice == "3":
            handle_listar_consultas()
        elif choice == "4":
            handle_cancelar_consulta()
        elif choice == "5":
            print("Obrigado por usar o sistema SaúdeViva. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
