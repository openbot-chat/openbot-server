# Openbot API Server

<p align="center">
  <img src="[logo_path]" alt="Openbot Logo" width="200"/>
</p>

<p align="center">
  <a href="[license_link]"><img src="[license_badge]" alt="License"></a>
  <a href="[build_link]"><img src="[build_badge]" alt="Build Status"></a>
  <a href="[docs_link]"><img src="[docs_badge]" alt="Documentation"></a>
</p>

OpenBot is an ​open-source AI agent development platform that combines low-code agility with professional-grade AI engineering capabilities. By integrating ​visual agent orchestration, ​multimodal model management, and ​enterprise-ready RAG pipelines.

## Features

- 🤖 Agent Discovery & Matching
- 🔌 Flexible Agent Integration
- 🔒 Multi-tenant Support with Row-Level Security
- 🗣️ Real-time Voice Interaction
- 🔄 Asynchronous Task Processing

## Quick Start

### Prerequisites

- Python 3.8+
- Poetry
- Docker (optional)

### Installation

1. Install dependencies:
```bash
poetry install
poetry shell
```

2. Run the application:
```bash
cd app
python3 main.py
```

3. Start Celery worker:
```bash
cd app
poetry run celery -A tasks.celery_worker worker -l info -Q tasks-load-datasource
```

## Development

### Database Migrations

```bash
cd app
alembic upgrade head

# Create new migration
alembic revision -m "init"
```

### Using Proxy (Optional)

Install v2ray client and enable HTTP inbounds:

```bash
export http_proxy=http://127.0.0.1:1087
export https_proxy=http://127.0.0.1:1087
python3 server.py
```

## Deployment

### Docker

Build the API server:
```bash
docker buildx build --platform linux/amd64 -t openbot-api .
```

Build the Celery worker:
```bash
docker build -f celery.Dockerfile -t openbot-celery-worker .
```

### Expose Local Server

Use localtunnel for temporary public access:
```bash
lt --port 5005 –s llm123
```

## Integration

### Slack Integration

1. Create a new Slack app at https://api.slack.com/apps
2. Configure OAuth permissions
3. Install the app to your workspace

### Wolfram Alpha Integration

- App Name: ai-plugin
- AppID: K3RPX6-E2P59EAQPA
- Usage Type: Personal/Non-commercial Only

## Technical Architecture

- Agent Discovery System
- Dynamic Agent Matching
- Efficient Agent Invocation
- Multi-tenant Data Isolation using Postgres Row Level Security
- Real-time Voice Processing with DEEPGRAM

## Development Tools

### Poetry Commands

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python -

# Common commands
poetry install        # Install all dependencies
poetry show          # List installed packages
poetry add flask     # Add new package
poetry remove flask  # Remove package
poetry shell        # Activate virtual environment
```

### Running Tests

```bash
PYTHONPATH=. poetry run pytest -s tests/test_s3.py
```

## Troubleshooting

### SSL Certificate Issues

If encountering API connection errors, install certificates:
```bash
/Applications/Python\ 3.11/Install\ Certificates.command
```

## Documentation

Detailed documentation is available at [docs_link]

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.


## Acknowledgments

- [Flowise](https://github.com/FlowiseAI/Flowise)
- [Vocode](https://github.com/vocodedev/vocode-python)
