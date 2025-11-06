# storage.py
import json

FILE_PATH = 'consultas.json'

def load_consultas():
    """Carrega as consultas do arquivo JSON."""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Retorna lista vazia se o arquivo não existir

def save_consultas(consultas):
    """Salva a lista de consultas no arquivo JSON."""
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(consultas, f, indent=4, ensure_ascii=False)