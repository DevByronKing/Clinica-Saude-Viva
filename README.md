# Clínica SaúdeViva - Sistema de Agendamento

Sistema de agendamento de consultas com processamento de linguagem natural para a Clínica SaúdeViva.

## 🌟 Funcionalidades

- Agendamento de consultas via linguagem natural
- Agendamento manual de consultas
- Listagem de consultas marcadas
- Cancelamento de consultas
- Geração automática de mensagens de confirmação
- Log de todas as operações

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API da OpenAI

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/DevByronKing/Clinica-Sa-de-Viva.git
cd Clinica-Sa-de-Viva
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

3. Instale as dependências:
```bash
pip install -e .
```

4. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Adicione sua chave da API OpenAI:
```bash
OPENAI_API_KEY=sua-chave-aqui
```

## 💻 Uso

Para iniciar o sistema:

```bash
python src/main.py
```

O sistema oferece as seguintes opções:
1. Agendar consulta (Linguagem Natural) - Ex: "Marcar para João amanhã às 10h"
2. Agendar consulta (Manual) - Inserção direta de data e hora
3. Listar consultas marcadas
4. Cancelar consulta
5. Sair

## 🧪 Testes

Para executar os testes:

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar testes
pytest

# Executar testes com cobertura
pytest --cov=src tests/
```

## 🔍 Linting e Type Checking

```bash
# Verificar estilo do código
flake8 src/ tests/

# Verificar tipos
mypy src/
```

## 📁 Estrutura do Projeto

- `src/`
  - `main.py` - Ponto de entrada e interface do usuário
  - `scheduler.py` - Lógica de agendamento de consultas
  - `storage.py` - Gerenciamento de persistência de dados
  - `ai_services.py` - Integração com OpenAI para NLP
- `tests/` - Testes automatizados
- `.github/workflows/` - Configuração CI/CD
- `consultas.json` - Arquivo de armazenamento das consultas

## 🔒 Segurança

- Nunca compartilhe sua chave da API OpenAI
- O arquivo `.env` está incluído no `.gitignore`
- Logs são armazenados em `app.log`

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Notas de Desenvolvimento

- O sistema usa a API da OpenAI para processar linguagem natural
- Os dados são persistidos localmente em JSON
- Logs detalhados são mantidos para todas as operações
- Testes cobrem casos de sucesso e falha
- CI/CD configurado com GitHub Actions

## 🐛 Problemas Conhecidos

- O sistema atualmente suporta apenas um arquivo de armazenamento
- As consultas são armazenadas em formato local
- O processamento de linguagem natural pode ter limitações com formatos de data muito complexos

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.