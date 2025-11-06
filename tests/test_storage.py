import json
from pathlib import Path
import storage


def test_load_consultas_file_missing(tmp_path, monkeypatch):
    # Ensure load_consultas returns empty list when file doesn't exist
    monkeypatch.setattr(storage, "FILE_PATH", str(tmp_path / "no_consultas.json"))
    assert storage.load_consultas() == []


def test_save_and_load_consultas(tmp_path, monkeypatch):
    p = tmp_path / "consultas_test.json"
    monkeypatch.setattr(storage, "FILE_PATH", str(p))

    consultas = [
        {
            "id": 1,
            "paciente": "Teste",
            "data_hora_inicio": "2025-11-01T10:00:00",
            "duracao_min": 30,
            "status": "marcada",
        }
    ]

    storage.save_consultas(consultas)

    # File should exist and contain the saved content
    assert p.exists()
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == consultas

    # load_consultas should return the same data
    loaded = storage.load_consultas()
    assert loaded == consultas
