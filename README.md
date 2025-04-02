# Openbot API Server

<p align="center">
  <img src="/images/logo.png" alt="Openbot Logo" width="200"/>
</p>

<p align="center">
  <a href="https://github.com/openbot-chat/openbot-server/graphs/commit-activity"  target="_blank">
        <img alt="Commits last month" src="https://img.shields.io/github/commit-activity/m/openbot-chat/openbot-server?labelColor=%20%2332b583&color=%20%2312b76a"></a>
  <a href="https://github.com/openbot-chat/openbot-server/" target="_blank">
        <img alt="Issues closed" src="https://img.shields.io/github/issues-search?query=repo%3Aopenbot-chat%2Fopenbot-server%20is%3Aclosed&label=issues%20closed&labelColor=%20%237d89b0&color=%20%235d6b98"></a>
  <a href="https://github.com/openbot-chat/openbot-server/discussions/" target="_blank">
        <img alt="Discussion posts" src="https://img.shields.io/github/discussions/openbot-chat/openbot-server?labelColor=%20%239b8afb&color=%20%237a5af8"></a>
</p>

OpenBot is an ​open-source AI agent development platform that combines low-code agility with professional-grade AI engineering capabilities. By integrating ​visual agent orchestration, ​multimodal model management, and ​enterprise-ready RAG pipelines.

## Features
**1. LLM-Modal Management**
- Native support for **GPT, Claude, Llama3, Grok, DeepSeek**, and private model deployment via kubernetes clusters or HuggingFace.
- Automated **RAG pipeline** integrating PDF/HTML crawling, vectorization, and incremental updates.

**2. Multi-Modal Capabilities**
- **Digital Human**
  - **Avatar Engine**
  - **Video Synthesis**
- **Audio Intelligence**
  - **Voice Cloning**
  - **Sound Effects**
- **Image Understanding & Creation**

**3. Enterprise-Grade Observability**
- Real-time monitoring of model latency (avg. <200ms), token consumption analytics, and error tracking.
- **A/B testing dashboard** for performance benchmarking across agent versions.

**4. Multi-Channel Publishing**
- ​**Embedded Web Integration**
  - Support seamless embedding via `<iframe>` or custom Web Components for third-party platforms (e.g., Shopify stores, CMS systems).
  - Provide API endpoints for dynamic content injection (e.g., real-time chat widgets for customer service).

- ​**Standalone H5/Web Applications**
  - Generate white-label web apps with custom domains and branding, optimized for mobile-first experiences.
  - Integrated with Volcano Engine's CDN for global acceleration (latency <50ms in Tier-1 cities).

- ​**Chatbot Ecosystem Integration**
  - Telegram, Discord, X, Slack, WeChat, Lark, Dingtalk, Google Talk, etc.

**5. Visual Agent Orchestration**
- **Drag-and-drop workflow designer** with 200+ prebuilt templates for rapid agent creation.[TODO]



## Channel Supported
| Platform       | Implementation Features                          |  |  
|----------------|---------------------------------------------------|-----------|  
| ​**Telegram Bot** | - Instant deployment via BotFather API<br>- Support inline keyboards & payment integration |
| ​**Discord Bot**  | - Slash command customization<br>- Role-based access control for enterprise servers         |
| ​**WeChat Bot**   | - Official Account API integration<br>- Mini-program interoperability with OpenBot workflows |
| ​**Twitter/X**    | - Auto-post AI-generated threads<br>- Direct Message-based agent interaction                 |
| ​**WhatsApp**     | - Twilio API bridge for business verification<br>- Multi-language template messaging        |
| ​**DingTalk**   | - Enterprise-level API integration for workflow automation<br>- Support OA message templates and approval process triggers |
| ​**Lark**       | - Interactive card message builder with OpenBot data binding<br>- Real-time collaboration space integration |


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





## Contributing


## Community & contact

- [Github Discussion](https://github.com/openbot-chat/openbot-server/discussions). Best for: sharing feedback and asking questions.
- [GitHub Issues](https://github.com/openbot-chat/openbot-server/issues). Best for: bugs you encounter using Openbot, and feature proposals. See our [Contribution Guide](https://github.com/openbot-chat/openbot-server/blob/main/CONTRIBUTING.md).
- [Discord](https://discord.gg/FngNHpbcY7). Best for: sharing your applications and hanging out with the community.
- [X(Twitter)](https://twitter.com/fair3_official). Best for: sharing your applications and hanging out with the **Fair community**.


**Contributors**

<a href="https://github.com/openbot-chat/openbot-server/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=openbot-chat/openbot-server" />
</a>


<br/>
<br/>

**Community**

This project has been integrated into the **FAIR³ Community's Open Source Ecosystem Initiative**

<p align="center">
  <img src="/images/fair3.jpg" alt="FAIR³" width="300"/>
</p>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.
