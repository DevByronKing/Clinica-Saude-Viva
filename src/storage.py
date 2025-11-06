# storage.py
"""
Módulo responsável pelo armazenamento persistente de dados do sistema.

Este módulo gerencia a persistência das consultas em arquivo JSON, fornecendo
funções para carregar e salvar os dados. O arquivo é mantido em formato UTF-8
para suportar caracteres especiais nos nomes dos pacientes.

Attributes:
    FILE_PATH (str): Caminho do arquivo JSON onde as consultas são armazenadas
"""

import json
from typing import List, Dict, Any

FILE_PATH = "consultas.json"


def load_consultas() -> List[Dict[str, Any]]:
    """
    Carrega a lista de consultas do arquivo JSON.

    Returns:
        List[Dict[str, Any]]: Lista de consultas onde cada consulta é um
        dicionário contendo:
            - id (int): ID único da consulta
            - paciente (str): Nome do paciente
            - data_hora_inicio (str): Data e hora no formato ISO
            - duracao_min (int): Duração em minutos
            - status (str): Status da consulta ('marcada' ou 'cancelada')

    Note:
        Se o arquivo não existir, retorna uma lista vazia, permitindo
        que o sistema inicie sem dados prévios.
    """
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Retorna lista vazia se o arquivo não existir


def save_consultas(consultas: List[Dict[str, Any]]) -> None:
    """
    Salva a lista de consultas em arquivo JSON.

    Args:
        consultas (List[Dict[str, Any]]): Lista de consultas a serem salvas

    Note:
        - O arquivo é salvo com indentação para melhor legibilidade
        - Utiliza codificação UTF-8 para suportar caracteres especiais
        - Se o arquivo não existir, será criado automaticamente
        - Se existir, será sobrescrito completamente

    Raises:
        IOError: Se houver problemas de permissão ou disco cheio
        Exception: Para outros erros de I/O não esperados
    """
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(consultas, f, indent=4, ensure_ascii=False)
