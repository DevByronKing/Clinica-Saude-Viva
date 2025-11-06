# ai_services.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Carrega a chave do .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define a "ferramenta" que a IA pode usar
tools = [
    {
        "type": "function",
        "function": {
            "name": "extrair_info_agendamento",
            "description": "Extrai nome do paciente, data e hora de uma solicitação de agendamento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paciente": {
                        "type": "string",
                        "description": "O nome do paciente."
                    },
                    "data": {
                        "type": "string",
                        "description": "A data da consulta no formato AAAA-MM-DD."
                    },
                    "hora": {
                        "type": "string",
                        "description": "A hora da consulta no formato HH:MM (24h)."
                    }
                },
                "required": ["paciente", "data", "hora"]
            }
        }
    }
]

def parse_natural_language(text):
    """Usa a IA para converter linguagem natural em dados estruturados."""
    
    # Informar a data de "hoje" é vital para a IA entender "amanhã"
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    system_prompt = f"""
    Você é um assistente de agendamento para a Clínica SaúdeViva.
    Sua tarefa é extrair o nome do paciente, a data e a hora da solicitação do usuário.
    Hoje é {hoje}. O médico é o Dr. Carlos (Clínico Geral).
    Converta datas relativas (como 'amanhã', 'hoje', 'próxima sexta') para o formato AAAA-MM-DD.
    Converta horas (como '3 da tarde', '10h') para o formato HH:MM (24h).
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Ou gpt-4, se permitido
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            tools=tools,
            tool_choice="auto" # Força a IA a usar a ferramenta
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            # A IA decidiu usar a ferramenta, ótimo!
            tool_call = message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            return function_args
        else:
            # A IA não conseguiu extrair os dados
            return None
            
    except Exception as e:
        print(f"Erro na API da OpenAI: {e}")
        return None

def generate_confirmation_message(paciente, data_hora_inicio):
    """Usa a IA para gerar uma mensagem de confirmação amigável."""
    
    # Formata a data para a mensagem
    dt_obj = datetime.fromisoformat(data_hora_inicio)
    data_formatada = dt_obj.strftime("%d/%m/%Y")
    hora_formatada = dt_obj.strftime("%H:%M")
    
    prompt = f"""
    Escreva uma mensagem de confirmação de consulta curta e cordial para o paciente {paciente}.
    A consulta é com o Dr. Carlos (Clínico Geral).
    A data é {data_formatada}.
    O horário é {hora_formatada}.
    Peça para chegar com 10 minutos de antecedência.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de clínica, simpático e eficiente."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na API da OpenAI: {e}")
        return "Erro ao gerar mensagem de confirmação."