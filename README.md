# RESTful API Producer – AWS SQS

<div align="center">
  <img src="https://img.shields.io/static/v1?label=python&message=language&color=blue&style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/static/v1?label=fastapi&message=framework&color=green&style=for-the-badge&logo=fastapi"/>
  <img src="https://img.shields.io/static/v1?label=lambda&message=runtime&color=orange&style=for-the-badge&logo=aws"/>
  <img src="https://img.shields.io/static/v1?label=boto3&message=SDK&color=yellow&style=for-the-badge"/>
  <img src="https://img.shields.io/static/v1?label=docker&message=container&color=blue&style=for-the-badge&logo=docker"/>
  <img src="https://img.shields.io/static/v1?label=openapi&message=docs&color=red&style=for-the-badge"/>
  <img src="http://img.shields.io/static/v1?label=STATUS&message=Development&color=GREEN&style=for-the-badge"/>
</div>

<div align="center">
  <img src="docs/architecture.png" alt="Arquitetura da API" width="600"/>
</div>

> Esta API RESTful tem como objetivo permitir o envio e consumo de mensagens em filas AWS SQS, oferecendo endpoints para produção, consulta de status e reprocessamento de mensagens em DLQ. A arquitetura é baseada em Lambda com FastAPI + Mangum, garantindo processamento assíncrono, idempotência e observabilidade.

---

## 📝 Visão Geral / Objetivo

* Desenvolver um **produtor de mensagens** para SQS com endpoints RESTful.
* Permitir **consulta de status** das filas e DLQ.
* Implementar **reprocessamento de mensagens DLQ** com prevenção de loops e tratamento de mensagens inválidas.
* Garantir **idempotência**, **logs detalhados**, métricas básicas e containerização via Docker.
* Fornecer documentação **OpenAPI/Swagger** completa.

---

## 🏛 Arquitetura

A solução segue a arquitetura serverless e distribuída:

* **API Gateway** → expõe endpoints da API.
* **Lambda Producer** → envia mensagens para fila SQS FIFO.
* **SQS FIFO Queue** → fila principal, com **DLQ** configurada.
* **Lambda Consumer Worker** → processa mensagens de forma assíncrona.
* **DynamoDB** → gerencia metadados das mensagens e garante idempotência.
* **CloudWatch** → logs e métricas.

---

## ⚖ Decisão de Consumo: Lambda vs ECS

| Critério                  | Lambda (Escolhido)   | ECS Fargate (Alternativa) |
| ------------------------- | -------------------- | ------------------------- |
| Complexidade de setup     | Baixa                | Média/Alta                |
| Escalabilidade            | Automática           | Manual / Configurável     |
| Custos                    | Pay-per-use          | Contêiner sempre ativo    |
| Latência de processamento | Imediata             | Variável                  |
| Retentativas / DLQ        | Configurável via SQS | Manual/Programada         |
| Observabilidade           | Integrada CloudWatch | Integrar manualmente      |

> **Justificativa:** Lambda oferece escalabilidade automática, fácil integração com SQS e menor custo operacional para este caso de uso.

---

## 📂 Estrutura de Pastas / Padrões

```
├── .github/
│   └── workflows/
│       └── ci-cd.yml                # Pipelines de CI/CD
├── app/
│   ├── controllers/
│   │   ├── messages.py              # Lógica de controllers para mensagens
│   │   └── users.py                 # Lógica de controllers para usuários
│   ├── middlewares/
│   │   └── auth.py                  # Autenticação e validação de tokens
│   ├── routes/
│   │   ├── messages.py              # Definição de rotas para mensagens
│   │   └── users.py                 # Definição de rotas para usuários
│   ├── schemas/
│   │   ├── messages.py              # Schemas Pydantic de mensagens
│   │   ├── responses.py             # Schemas de respostas gerais
│   │   ├── transactions.py          # Schemas de transações
│   │   └── users.py                 # Schemas de usuários
│   ├── security/
│   │   └── token.py                 # Geração e validação de tokens JWT
│   ├── services/
│   │   └── messages.py              # Lógica de integração com SQS
│   └── utils/
│       ├── config.py                # Configurações de ambiente
│       ├── logging.py               # Configuração de logs
│       ├── metrics.py               # Métricas customizadas
│       ├── swagger.py               # Configuração do Swagger/OpenAPI
│       └── validate.py              # Funções utilitárias de validação
│   └── main.py                      # Entrypoint FastAPI + Mangum
├── tests/                           # Testes unitários
├── .env.sample                      # Exemplo de variáveis de ambiente
├── .gitignore                       # Arquivos e pastas ignoradas no Git
├── Dockerfile                       # Dockerfile para containerização
├── README.md
├── requirements.txt                 # Dependências do projeto
└── requirements_test.txt            # Dependências para testes

```

---

## 🔌 Endpoints (OpenAPI)

* **POST /messages/send** – Envia mensagem para fila SQS.
* **GET /messages/status** – Consulta status da fila principal e DLQ.
* **POST /messages/dlq/reprocess** – Reprocessa mensagens da DLQ para a fila principal.
* **POST /users/login** – Gera token de autenticação.

Acesse a documentação interativa: [Swagger UI Localmente](http://localhost:8000/docs)
ou [Swagger UI AWS](https://fqgn7lclxb.execute-api.us-east-1.amazonaws.com/docs)

---

## 🔄 Fluxo de Processamento de Mensagens

1. Produção via POST `/messages/send`.
2. Mensagem salva em **DynamoDB** para rastreio e idempotência.
3. Lambda Worker consome mensagens da fila principal.
4. Processamento assíncrono e logging via CloudWatch.
5. Mensagens inválidas ou que excedem retentativas → DLQ.

---

## ⚠ Tratamento de Erros, Retentativas e DLQ

* Configuração de **SQS FIFO + DLQ FIFO**.
* Mensagens inválidas movidas para DLQ.
* Retentativas automáticas configuradas via SQS (maxReceiveCount).
* Prevenção de loops na reprocessamento da DLQ.

---

## ✅ Idempotência

Implementada **em dois níveis**:

- **DynamoDB**: cada mensagem possui uma chave única que garante que mensagens duplicadas não sejam processadas novamente.
- **SQS FIFO + DLQ FIFO**: utiliza o atributo `MessageDeduplicationId` para prevenir duplicações na fila, mesmo em casos de reenvio ou falhas temporárias.

Essa combinação assegura que o processamento de mensagens seja **idempotente**, evitando que mensagens duplicadas gerem efeitos colaterais indesejados e garantindo a integridade tanto do fluxo de mensagens quanto do reprocessamento da DLQ.

---

## 📊 Observabilidade

A API possui um sistema de **logs estruturados** e **métricas customizadas**, permitindo monitoramento detalhado das operações.

### Logs Detalhados

* Todos os eventos importantes são registrados via `logger` do Python.
* Os logs são estruturados em **JSON** com os seguintes campos:

  * `trace_id`: identificador único da operação, útil para rastrear o fluxo.
  * `action`: operação realizada (ex: `send_message`, `get_status`, `reprocess_dlq`, `user_login`).
  * `status`: estado da operação (`started`, `success`, `error`).
  * `details`: informações adicionais, como nome da fila, duração ou erro.
  * `timestamp`: horário UTC da execução.

**Exemplo de log:**

```json
{
  "trace_id": "51063aff-594b-41c7-9ddd-649817dfefa3",
  "action": "send_message",
  "status": "success",
  "details": {"queue_name": "main_queue", "duration": 0.124},
  "timestamp": "2025-10-05T20:26:22.883320+00:00"
}
```

### Métricas Customizadas

As métricas são enviadas para **AWS CloudWatch**, usando o namespace `API-Producer-SQS/Messages`.

Principais métricas disponíveis:

| Métrica               | Descrição                                                   |
| --------------------- | ----------------------------------------------------------- |
| `MessagesSent`        | Contagem de mensagens enviadas com sucesso para a fila SQS  |
| `MessagesReprocessed` | Quantidade de mensagens reprocessadas da DLQ                |
| `ProcessingTime`      | Tempo médio de processamento de cada operação (em segundos) |
| `Errors`              | Contagem de erros ocorridos durante operações               |
| `FailedLogins`        | Tentativas de login inválidas                               |
| `SuccessfulLogins`    | Logins autenticados com sucesso                             |


> Essa abordagem garante visibilidade completa do fluxo de mensagens, incluindo produção, consumo assíncrono via Lambda e reprocessamento da DLQ, facilitando detecção de falhas e análise de desempenho.

---

## 🔒 Segurança

* Endpoint `/users/login` gera **token JWT**.
* Token necessário em headers `Authorization` para outros endpoints.

---

## 🏡 Como Executar Localmente

**Pré-requisitos:** Python 3.11, credenciais de acesso à AWS com os recursos já criados.

### Passo a passo

* Clone o repositório:

```bash
git clone https://github.com/ViniciusGR797/producer-sqs-api.git
cd producer-sqs-api
```

* Crie e ative um ambiente virtual Python (`venv`):

```bash
python -m venv venv
```

```bash
# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

* Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

* Crie um arquivo `.env` a partir de `.env.sample`:

```bash
APP_USER_EMAIL=user@example.com
APP_USER_PASSWORD=strongpassword123
JWT_SECRET_KEY=<random_secret_key>
JWT_ACCESS_TOKEN_EXPIRES=6
REGION=us-east-1
SQS_NAME=main_queue.fifo
DLQ_NAME=dlq_queue.fifo
```

* Configure as variáveis de ambiente definindo suas credenciais AWS e outras variáveis:

```bash
export ENV=LOCAL
export AWS_ACCESS_KEY_ID="sua_access_key_id"
export AWS_SECRET_ACCESS_KEY="sua_secret_access_key"
export AWS_DEFAULT_REGION="sua_regiao"
```

> Essas variáveis permitem que a aplicação acesse os recursos AWS já existentes na sua conta.

* Executar a API:
```bash
python "app\main.py"
```

* Acessar a documentação via [Swagger UI](http://localhost:8080/docs)

* Collection do [Insomnia](http://localhost:8080/docs) para consumir os endpoints.

---

## 🧪 Testes

Todos os testes estão localizados na pasta `tests/` e pressupõem que você já tenha seguido os passos para **executar localmente** (ambiente virtual ativado, dependências instaladas e variáveis de ambiente configuradas).

Para rodar os testes sigas os passos:

* Instale as dependências de teste adicionais:

```bash
pip install -r requirements_test.txt
```

* Execute os testes unitários com `pytest`:

```bash
pytest -v
```