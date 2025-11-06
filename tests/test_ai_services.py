from datetime import datetime
import json
from types import SimpleNamespace
import ai_services


def _fake_parse_response(args_dict):
    # Builds an object similar to the OpenAI response expected by parse_natural_language
    message = SimpleNamespace(
        tool_calls=[
            SimpleNamespace(function=SimpleNamespace(arguments=json.dumps(args_dict)))
        ]
    )
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_parse_natural_language_data_explicita(monkeypatch):
    """Testa o parsing de uma solicitação com data explícita."""
    solicitacao = "Marcar consulta para Maria Silva no dia 2025-11-10 às 14:30"

    expected = {"paciente": "Maria Silva", "data": "2025-11-10", "hora": "14:30"}
    monkeypatch.setattr(
        ai_services.client.chat.completions,
        "create",
        lambda **kw: _fake_parse_response(expected),
    )

    resultado = ai_services.parse_natural_language(solicitacao)

    assert resultado is not None
    assert resultado["paciente"] == "Maria Silva"
    assert resultado["data"] == "2025-11-10"
    assert resultado["hora"] == "14:30"


def test_parse_natural_language_data_relativa(monkeypatch):
    """Testa o parsing de uma solicitação com data relativa."""
    hoje = datetime.now().strftime("%Y-%m-%d")
    solicitacao = "Marcar consulta para João hoje às 10:00"
    expected = {"paciente": "João", "data": hoje, "hora": "10:00"}
    monkeypatch.setattr(
        ai_services.client.chat.completions,
        "create",
        lambda **kw: _fake_parse_response(expected),
    )

    resultado = ai_services.parse_natural_language(solicitacao)

    assert resultado is not None
    assert resultado["paciente"] == "João"
    assert resultado["data"] == hoje
    assert resultado["hora"] == "10:00"


def test_parse_natural_language_hora_informal(monkeypatch):
    """Testa o parsing de uma solicitação com hora em formato informal."""
    solicitacao = "Marcar consulta para Pedro amanhã às 2 da tarde"
    expected = {"paciente": "Pedro", "data": "2025-11-26", "hora": "14:00"}
    monkeypatch.setattr(
        ai_services.client.chat.completions,
        "create",
        lambda **kw: _fake_parse_response(expected),
    )

    resultado = ai_services.parse_natural_language(solicitacao)

    assert resultado is not None
    assert resultado["paciente"] == "Pedro"
    assert resultado["hora"] == "14:00"


def test_parse_natural_language_invalido(monkeypatch):
    """Testa o parsing de uma solicitação inválida."""
    solicitacao = "Esta não é uma solicitação de agendamento válida"

    # Simula resposta sem tool_calls (IA não chamou a ferramenta)
    message = SimpleNamespace(tool_calls=[])
    fake = SimpleNamespace(choices=[SimpleNamespace(message=message)])
    monkeypatch.setattr(
        ai_services.client.chat.completions, "create", lambda **kw: fake
    )

    resultado = ai_services.parse_natural_language(solicitacao)

    assert resultado is None


def test_generate_confirmation_message(monkeypatch):
    """Testa a geração de mensagem de confirmação (mock da API)."""
    paciente = "Ana Silva"
    data_hora = "2025-11-15T09:30:00"

    fake_message = SimpleNamespace(
        content="Olá Ana Silva, sua consulta está marcada. Chegue 10 minutos antes. Dr. Carlos"
    )
    fake = SimpleNamespace(choices=[SimpleNamespace(message=fake_message)])
    monkeypatch.setattr(
        ai_services.client.chat.completions, "create", lambda **kw: fake
    )

    mensagem = ai_services.generate_confirmation_message(paciente, data_hora)

    assert mensagem is not None
    assert len(mensagem) > 0
    assert "Ana Silva" in mensagem
    assert "10 minutos" in mensagem
    assert "Dr. Carlos" in mensagem
