<p align="center">🏥 Clínica Saúde Viva - Sistema de Agendamento  </p>
<p align="center"> <img alt="Status da CI" src="https://github.com/DevByronKing/Clinica-Saude-Viva/actions/workflows/ci.yml/badge.svg"> </p>

🎯 Objetivo:
Este projeto é um desafio técnico que simula um sistema de agendamento de consultas para a Clínica SaúdeViva. O objetivo é criar uma aplicação de console (CLI) em Python que gerencia agendamentos, com um diferencial principal: a integração com a API da OpenAI para processamento de linguagem natural e geração de mensagens.



✨ Principais Funcionalidades:

🧠 Agendamento com IA: Faça agendamentos usando linguagem natural (ex: "Marcar para João amanhã às 3 da tarde").

🤖 Confirmações Geradas por IA: Receba mensagens de confirmação amigáveis e personalizadas, geradas pela OpenAI.

⌨️ Agendamento Manual: Um modo de fallback para inserir dados manualmente (data, hora, paciente).

📋 Listagem de Consultas: Visualize todos os agendamentos marcados.

❌ Cancelamento de Consultas: Remova agendamentos existentes pelo ID.

⚖️ Regras de Negócio: O sistema valida o horário comercial (Seg-Sex, 08:00-18:00) e impede conflitos de horário.




🛠️ Stack Tecnológico

Linguagem: Python 3.11

IA & NLP: OpenAI API (gpt-3.5-turbo)

Testes: Pytest, pytest-cov, pytest-mock

Qualidade de Código: Flake8 (Linting) e Mypy (Type Checking)

DevOps: GitHub Actions (Pipeline de CI/CD)




## 🚀 Começando (Instalação)
Siga estes passos para configurar e rodar o projeto localmente.

### 1. Clone o repositório
```bash
git clone [https://github.com/DevByronKing/Clinica-Saude-Viva.git](https://github.com/DevByronKing/Clinica-Saude-Viva.git)
cd Clinica-Saude-Viva ´´´´

2. Crie e ative o Ambiente Virtual:

# Crie o venv
python -m venv .venv

# Ative o venv
Windows
.\.venv\Scripts\activate

Linux/macOS
source .venv/bin/activate

3. Configure as Variáveis de Ambiente

Você precisará da sua chave da API da OpenAI.

# Copie o arquivo de exemplo
cp .env.example .env

Agora, abra o arquivo .env e adicione sua chave:

OPENAI_API_KEY=sua-chave-secreta-aqui

4. Instale as Dependências

Instale todas as dependências do requirements.txt e o projeto em modo editável (para que os import funcionem).

# 1. Instale as dependências principais da aplicação (OpenAI, etc.)
pip install -r requirements.txt

# 2. Instale as dependências de desenvolvimento (Pytest, Flake8, Mypy)
pip install pytest pytest-cov pytest-mock flake8 mypy

# 3. Instale o projeto em modo editável (para os imports funcionarem)
pip install -e .




💻 Como Usar
Com o ambiente virtual ativado e as dependências instaladas, simplesmente execute o main.py:

No Bash
python src/main.py

Você verá o menu principal:
--- Clínica SaúdeViva ---
1. Agendar consulta (Linguagem Natural)
2. Agendar consulta (Manual)
3. Listar consultas marcadas
4. Cancelar consulta
5. Sair
Escolha uma opção:




🧪 Qualidade de Código & Testes
Este projeto é totalmente testado e validado por um pipeline de CI/CD. Os testes de integração da API são feitos com mocks para evitar chamadas reais.

Executar Testes
No Bash

pytest
Relatório de Cobertura

No Bash
pytest --cov=src tests/
Linting (Flake8)

No Bash
flake8 src tests --max-line-length=88
Checagem de Tipos (Mypy)

No Bash
mypy src --ignore-missing-imports




📁 ## Estrutura do Projeto
A arquitetura do projeto foi projetada para ter uma clara separação de responsabilidades:

* `.github/workflows/`
    * `ci.yml` - Pipeline de CI/CD
* `src/`
    * `ai_services.py` - Módulo de integração com OpenAI (NLP e Geração)
    * `main.py` - Ponto de entrada da aplicação (Interface CLI)
    * `agendador.py` - Regras de negócio (validações de horário, conflitos)
    * `storage.py` - Gerenciamento da persistência (leitura/escrita do JSON)
* `testes/`
    * `test_ai_services.py`
    * `test_scheduler.py`
    * `test_storage.py`
* `.env.example` - Exemplo de variáveis de ambiente
* `.flake8` - Configuração do Linting
* `.gitignore`
* `consultas.json` - Arquivo de dados (com exemplos)
* `README.md` - Esta documentação
* `requirements.txt` - Dependências de produção
* `setup.py` - Define o projeto como um pacote Python
├── requirements.txt    # Dependências de produção
└── setup.py            # Define o projeto como um pacote Python
📄 Licença
Distribuído sob a licença MIT. Veja LICENSE para mais informações.







