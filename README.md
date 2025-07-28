# Stock AI Agent SaaS

A comprehensive SaaS platform that leverages AI agents to assist with stock trading decisions by monitoring news feeds and analyzing stock data. The platform helps users set trading limits and provides stock summaries including PE ratios and market sentiment analysis.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Stock AI Agent SaaS is a modern monorepo project designed to provide intelligent stock trading assistance through AI-powered analysis. The platform combines real-time news monitoring, sentiment analysis, and automated trading recommendations to help users make informed investment decisions.

## 🛠 Tech Stack

### Frontend
- **Framework:** Next.js (React)
- **Styling:** TailwindCSS (planned)
- **State Management:** Redux Toolkit (planned)

### Backend
- **API Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **Caching:** Redis
- **Task Queue:** Celery (planned)

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Orchestration:** Kubernetes (planned)
- **Cloud Platform:** Azure Cloud (future deployment)
- **CI/CD:** GitHub Actions (planned)

### AI/ML Stack
- **News Processing:** RSS feed aggregation
- **Sentiment Analysis:** NLP models
- **Market Analysis:** Custom AI algorithms

## ✨ Key Features

- **Smart Alerts:** Set up stock alerts with custom keywords and criteria
- **News Aggregation:** AI agent pulls news from multiple sources via RSS feeds
- **Sentiment Analysis:** Analyze news sentiment based on configured keywords
- **Stock Insights:** Comprehensive stock summaries including PE ratios and sentiment scores
- **Notification System:** Multi-channel alerts (LINE Notify, Email - planned)
- **Cloud Deployment:** Azure Cloud support for scalable infrastructure
- **Real-time Monitoring:** Live stock data and news feed monitoring

## 📁 Project Structure

This is a monorepo containing multiple services and applications:

```
stock-ai-agent-saas/
├── apps/
│   ├── frontend/          # Next.js web application
│   ├── api/              # FastAPI backend service
│   └── ai-agent/         # AI processing service
├── packages/
│   ├── shared/           # Shared utilities and types
│   ├── database/         # Database schemas and migrations
│   └── config/           # Configuration management
├── infrastructure/
│   ├── docker/           # Docker configurations
│   ├── kubernetes/       # K8s deployment manifests
│   └── azure/            # Azure infrastructure as code
├── docs/                 # Documentation
├── scripts/              # Build and deployment scripts
└── tests/                # End-to-end tests
```

*Note: Project structure will be implemented as development progresses.*

## 🚀 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python (v3.9 or higher)
- Docker and Docker Compose
- PostgreSQL (v13 or higher)
- Redis (v6 or higher)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jin-tech/stock-ai-agent-saas.git
   cd stock-ai-agent-saas
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Install dependencies**
   ```bash
   # Install frontend dependencies
   npm install

   # Install backend dependencies
   pip install -r requirements.txt
   ```

4. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Run database migrations**
   ```bash
   # This will be implemented with the backend service
   python manage.py migrate
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 💻 Development

### Local Development Setup

1. **Frontend Development**
   ```bash
   cd apps/frontend
   npm run dev
   ```

2. **Backend Development**
   ```bash
   cd apps/api
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **AI Agent Service**
   ```bash
   cd apps/ai-agent
   python main.py
   ```

### Code Quality

- **Linting:** ESLint for JavaScript/TypeScript, Black for Python
- **Type Checking:** TypeScript for frontend, mypy for Python
- **Testing:** Jest for frontend, pytest for backend
- **Pre-commit Hooks:** Husky for automated code quality checks

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/stockai
REDIS_URL=redis://localhost:6379

# API Keys
STOCK_API_KEY=your_stock_api_key
NEWS_API_KEY=your_news_api_key

# Authentication
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256

# External Services
LINE_NOTIFY_TOKEN=your_line_notify_token
SMTP_HOST=your_smtp_host
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

## 🚀 Deployment

### Azure Cloud Deployment

The platform is designed to be deployed on Azure Cloud with the following services:

- **Azure Container Instances** or **Azure Kubernetes Service** for application hosting
- **Azure Database for PostgreSQL** for data storage
- **Azure Cache for Redis** for caching and session management
- **Azure Functions** for serverless AI processing tasks
- **Azure Event Grid** for event-driven architecture

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or build individual services
docker build -t stock-ai-frontend ./apps/frontend
docker build -t stock-ai-api ./apps/api
docker build -t stock-ai-agent ./apps/ai-agent
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/kubernetes/
```

## 🤝 Contributing

We welcome contributions to the Stock AI Agent SaaS project! Please follow these guidelines:

### Development Process

1. **Fork the repository** and create a feature branch
2. **Follow coding standards** and write tests for new features
3. **Run tests** and ensure all checks pass
4. **Submit a pull request** with a clear description of changes

### Coding Standards

- Follow conventional commit messages
- Use TypeScript for frontend development
- Follow PEP 8 for Python code
- Write comprehensive tests for new features
- Update documentation for API changes

### Issue Reporting

- Use GitHub Issues for bug reports and feature requests
- Provide detailed reproduction steps for bugs
- Include environment information and logs when relevant

## 📋 Roadmap

- [ ] **Phase 1:** Core infrastructure setup and basic UI
- [ ] **Phase 2:** AI agent implementation and news processing
- [ ] **Phase 3:** Trading integration and alert system
- [ ] **Phase 4:** Advanced analytics and reporting
- [ ] **Phase 5:** Mobile app development
- [ ] **Phase 6:** Enterprise features and scaling

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](docs/)
- [API Documentation](http://localhost:8000/docs) (when running locally)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## 📧 Support

For support and questions:

- Create an issue on GitHub
- Contact the development team
- Check the documentation for common questions

---

**Built with ❤️ by the Jin-Tech team**