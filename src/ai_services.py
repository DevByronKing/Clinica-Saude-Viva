# ai_services.py
"""
Módulo responsável pela integração com a API da OpenAI para processamento de linguagem natural
e geração de mensagens no sistema de agendamento da Clínica SaúdeViva.

Este módulo fornece funcionalidades para:
- Processamento de linguagem natural para extrair informações de agendamento
- Geração de mensagens de confirmação personalizadas
- Integração com a API GPT-3.5-turbo da OpenAI

Attributes:
    tools (list): Lista de ferramentas disponíveis para a IA, definindo o formato
                 esperado das informações de agendamento.
    client (OpenAI): Cliente inicializado da API da OpenAI.
"""

import os
import json
from typing import Optional, Dict, List
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionNamedToolChoiceParam
)
from dotenv import load_dotenv
from datetime import datetime

# Carrega a chave do .env
load_dotenv()
_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=_api_key)

# Define a "ferramenta" que a IA pode usar
tools: List[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "extrair_info_agendamento",
            "description": (
                "Extrai nome do paciente, data e hora de uma "
                "solicitação de agendamento."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "paciente": {
                        "type": "string",
                        "description": "O nome do paciente.",
                    },
                    "data": {
                        "type": "string",
                        "description": ("A data da consulta no formato AAAA-MM-DD."),
                    },
                    "hora": {
                        "type": "string",
                        "description": ("A hora da consulta no formato HH:MM (24h)."),
                    },
                },
                "required": ["paciente", "data", "hora"],
            },
        },
    }
]


def parse_natural_language(text: str) -> Optional[Dict[str, str]]:
    """
    Processa texto em linguagem natural para extrair informações de agendamento.

    Utiliza a API da OpenAI para analisar o texto do usuário e extrair o nome do
    paciente, data e hora do agendamento. O processamento leva em consideração
    expressões relativas de tempo (como "amanhã", "próxima segunda") e diversos
    formatos de hora.

    Args:
        text (str): Texto em linguagem natural contendo a solicitação de agendamento.

    Returns:
        Optional[Dict[str, str]]: Um dicionário contendo as chaves 'paciente', 'data' e 'hora'
            se o processamento for bem-sucedido, ou None se não for possível extrair todas
            as informações necessárias.

    Examples:
        >>> parse_natural_language("Marcar para João amanhã às 10h")
        {'paciente': 'João', 'data': '2025-11-07', 'hora': '10:00'}
        >>> parse_natural_language("Consulta pra semana que vem")
        None  # Informações incompletas
    """

    # Informar a data de "hoje" é vital para a IA entender "amanhã"
    # Em ai_services.py

    hoje = datetime.now().strftime("%Y-%m-%d")

    system_prompt_parts = [
        "Você é um assistente de agendamento para a Clínica SaúdeViva.",
        "Sua tarefa é extrair nome, data e hora da solicitação do usuário.",
        f"Hoje é {hoje}.",
        "Dr. Carlos (Clínico Geral).",
        "Converta datas relativas para AAAA-MM-DD.",
        "Converta horas para HH:MM (24h).",
        "IMPORTANTE: hora em HH:MM (ex: '07:00').",
        "Se o usuário disser '7h', extraia '07:00'.",
        f"Se o usuário disser 'hoje', use {hoje}.",
        "Se não for possível extrair AAAA-MM-DD e HH:MM, não chame a ferramenta.",
    ]
    system_prompt = "\n".join(system_prompt_parts)

    try:
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
        tool_choice: ChatCompletionNamedToolChoiceParam = {
            "type": "function",
            "function": {"name": "extrair_info_agendamento"}
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Ou gpt-4, se permitido
            messages=messages,
            tools=tools,
            tool_choice=tool_choice
        )

        message = response.choices[0].message

        if not (message.tool_calls and len(message.tool_calls) > 0):
            return None

        # A IA decidiu usar a ferramenta, ótimo!
        tool_call = message.tool_calls[0]
        if tool_call.type != "function":
            return None

        function_args = json.loads(tool_call.function.arguments)

        # Valida que os campos exigidos existem e não estão vazios
        for key in ("paciente", "data", "hora"):
            if key not in function_args or not str(function_args[key]).strip():
                return None

        return function_args

    except Exception as e:
        print(f"Erro na API da OpenAI: {e}")
        return None


def generate_confirmation_message(paciente: str, data_hora_inicio: str) -> str:
    """
    Gera uma mensagem personalizada de confirmação de consulta.

    Utiliza a API da OpenAI para criar uma mensagem amigável e profissional
    confirmando o agendamento da consulta. A mensagem inclui os detalhes do
    agendamento e instruções importantes para o paciente.

    Args:
        paciente (str): Nome do paciente.
        data_hora_inicio (str): Data e hora da consulta no formato ISO
            (YYYY-MM-DDTHH:MM:SS).

    Returns:
        str: Mensagem de confirmação personalizada ou mensagem de erro em
            caso de falha na geração.

    Example:
        >>> generate_confirmation_message("João Silva", "2025-11-07T10:00:00")
        "Olá João Silva! Sua consulta está confirmada para o dia 07/11/2025..."
    """

    # Formata a data para a mensagem
    dt_obj = datetime.fromisoformat(data_hora_inicio)
    data_formatada = dt_obj.strftime("%d/%m/%Y")
    hora_formatada = dt_obj.strftime("%H:%M")

    prompt_lines = [
        "Escreva uma mensagem de confirmação de consulta curta e cordial.",
        f"Paciente: {paciente}.",
        "A consulta é com o Dr. Carlos (Clínico Geral).",
        f"Data: {data_formatada}.",
        f"Horário: {hora_formatada}.",
        "Peça para chegar com 10 minutos de antecedência.",
    ]
    prompt = "\n".join(prompt_lines)

    try:
        messages: List[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "Você é um assistente de clínica, simpático.",
            },
            {"role": "user", "content": prompt},
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=100
        )
        content = response.choices[0].message.content
        if content is None:
            return "Não foi possível gerar uma mensagem de confirmação."
        return content
    except Exception as e:
        print(f"Erro na API da OpenAI: {e}")
        return "Erro ao gerar mensagem de confirmação. Por favor, tente novamente mais tarde."
