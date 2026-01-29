# TransUnion PDF to JSON API

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

Production-ready FastAPI service that converts **TransUnion Credit Reports** (PDF format) into structured JSON data with automatic **PII scrubbing** for data privacy.

---

## ✨ Features

- ✅ **PDF Parsing** - Extract data from TransUnion credit report PDFs
- ✅ **Structured Output** - Validated JSON with Pydantic models
- ✅ **PII Scrubbing** - Automatic masking of sensitive personal information
- ✅ **Multi-currency Support** - Handles DOP and USD accounts
- ✅ **Structured Logging** - JSON-formatted logs for easy parsing
- ✅ **System Monitoring** - Built-in CPU, memory, and disk usage tracking
- ✅ **Automated Backups** - Daily backups with 7-day retention
- ✅ **Docker Ready** - Production-ready containers with health checks
- ✅ **Interactive API Docs** - Auto-generated Swagger/ReDoc documentation
- ✅ **Frontend UI** - Modern React interface for upload and visualization

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
  - [Local Development](#local-development)
  - [Docker](#docker)
- [Usage](#-usage)
  - [API Endpoints](#api-endpoints)
  - [Python Examples](#python-examples)
  - [cURL Examples](#curl-examples)
- [API Documentation](#-api-documentation)
- [Configuration](#%EF%B8%8F-configuration)
- [Deployment](#-deployment)
- [Monitoring](#-monitoring)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/your-username/transunion-pdf-to-json.git
cd transunion-pdf-to-json

# Start with Docker Compose
docker compose up

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Local Development

```bash
# Clone repository
git clone https://github.com/your-username/transunion-pdf-to-json.git
cd transunion-pdf-to-json

# Install dependencies (Python 3.12+ required)
pip install -e .

# Start development server
uvicorn src.main:app --reload

# API available at http://localhost:8000
```

---

## 📦 Installation

### Prerequisites

- **Python 3.12+** (or Docker)
- **System Dependencies**: `libmupdf-dev`, `swig` (for PDF processing)

### Local Development

#### 1. System Dependencies (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-dev build-essential libmupdf-dev swig
```

#### 2. Python Environment

```bash
# Create virtual environment
python3.12 -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install package in editable mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

#### 3. Run the Application

```bash
# Development server with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
# Build image
docker build -t transunion-parser:1.0.0 .

# Run container
docker run -d -p 8000:8000 transunion-parser:1.0.0

# Or use Docker Compose
docker compose up -d               # Development
docker compose -f docker-compose.prod.yml up -d  # Production
```

---

## 💻 Usage

### API Endpoints

| Endpoint     | Method | Description                        |
| ------------ | ------ | ---------------------------------- |
| `/`          | GET    | API information and navigation     |
| `/v1/health` | GET    | Health check endpoint              |
| `/v1/parse`  | POST   | Upload PDF and get structured JSON |
| `/docs`      | GET    | Interactive Swagger documentation  |
| `/redoc`     | GET    | ReDoc API documentation            |

### Python Examples

```python
import requests

# Parse credit report
with open('credit_report.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/v1/parse',
        files={'file': f}
    )

# Get parsed data
data = response.json()

# Access structured data
print(f"Score: {data['score']['score']}")
print(f"Name: {data['personal_data']['first_names']}")
print(f"Accounts: {len(data['details_open_accounts'])}")
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/v1/health

# Upload and parse PDF
curl -X POST "http://localhost:8000/v1/parse" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@credit_report.pdf"

# Pretty print JSON response
curl -X POST "http://localhost:8000/v1/parse" \
  -F "file=@credit_report.pdf" | jq '.'
```

---

## 📚 API Documentation

### Interactive Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Response Structure

```json
{
  "inquirer": {
    "subscriber": "BANCO EJEMPLO",
    "user": "Usuario123",
    "consultation_date": "2024-01-29",
    "consultation_time": "10:30 AM"
  },
  "personal_data": {
    "identification": "001-******* -7",
    "first_names": "Jo****",
    "last_names": "Do**",
    "birth_date": "1990-01-01",
    "age": 34
  },
  "score": {
    "score": 750,
    "factors": ["Payment history", "Credit utilization"]
  },
  "summary_open_accounts": [],
  "details_open_accounts": []
}
```

**Note**: PII is automatically scrubbed in responses.

---

## ⚙️ Configuration

### Environment Variables

| Variable                | Description                       | Default |
| ----------------------- | --------------------------------- | ------- |
| `DEBUG`                 | Enable debug mode                 | `0`     |
| `MAX_WORKERS`           | Number of Uvicorn workers         | `4`     |
| `LOG_LEVEL`             | Logging level (info/debug/error)  | `info`  |
| `MAX_LOG_SIZE_MB`       | Max log file size before rotation | `100`   |
| `BACKUP_RETENTION_DAYS` | Days to keep backups              | `7`     |

### Docker Compose Configuration

Create a `.env` file in the project root:

```env
DEBUG=0
MAX_WORKERS=4
LOG_LEVEL=info
```

---

## 🌐 Deployment

### VPS Deployment

See the comprehensive [VPS Setup Guide](docs/deployment/vps_setup.md) for detailed instructions on:

- Server hardening and security
- Docker installation
- SSL/TLS setup with Certbot
- Nginx reverse proxy configuration
- Monitoring and maintenance

### Quick Deployment

```bash
# On your VPS
git clone https://github.com/your-username/transunion-pdf-to-json.git
cd transunion-pdf-to-json

# Build and start
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
```

---

## 📊 Monitoring

### Logs

The application uses structured JSON logging:

```bash
# View API logs
tail -f logs/api.log

# View system metrics
tail -f logs/monitoring.log

# Parse JSON logs (requires jq)
tail -f logs/api.log | jq '.'
```

### System Metrics

Automatically logged every 60 seconds:

- CPU usage percentage
- Memory utilization
- Disk usage
- Request/response timing

### Health Check

```bash
# Check application health
curl http://localhost:8000/v1/health

# Expected: {"status": "healthy"}
```

---

## 🛠️ Development

### Setup Development Environment

```bash
# Clone and install
git clone https://github.com/your-username/transunion-pdf-to-json.git
cd transunion-pdf-to-json
pip install -e ".[dev]"

# Run tests
pytest -v

# Run with code coverage
pytest --cov=src --cov-report=html

# Lint code
ruff check src/
black --check src/

# Format code
black src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v --tb=short

# Run with coverage
pytest --cov=src
```

### Code Quality

```bash
# Type checking with mypy
mypy src/

# Linting with ruff
ruff check src/

# Code formatting with black
black src/
```

---

## 📁 Project Structure

```
transunion-pdf-to-json/
├── src/
│   ├── api/                    # API routes and endpoints
│   │   └── routes.py
│   ├── models/                 # Pydantic data models
│   │   └── report.py
│   ├── parser/                 # PDF parsing engine
│   │   └── engine.py
│   ├── scrubber/               # PII scrubbing service
│   │   └── service.py
│   ├── middleware/             # Request/response middleware
│   │   └── logging_middleware.py
│   ├── utils/                  # Utilities (logging, backup)
│   │   ├── logging_config.py
│   │   └── backup.py
│   ├── main.py                 # Application entry point
│   └── maintenance.py          # Maintenance scheduler
├── frontend/                   # React UI (Vite + shadcn/ui)
├── tests/                      # Test suite
├── docs/                       # Documentation
│   ├── deployment/             # Deployment guides
│   └── implementation/         # Technical documentation
├── logs/                       # Application logs (gitignored)
├── backups/                    # Automated backups (gitignored)
├── Dockerfile                  # Production Docker image
├── docker-compose.yml          # Development compose
├── docker-compose.prod.yml     # Production compose
├── pyproject.toml              # Python package configuration
└── README.md                   # This file
```

---

## 🗺️ Roadmap

We're continuously improving the TransUnion parser with new features and enhancements!

### Upcoming Features

**Phase 2 (v1.1.0) - CI/CD & Quality** 🟡

- GitHub Actions CI/CD pipeline
- Automated testing and deployment
- 90%+ code coverage
- Enhanced test suite

**Phase 3 (v1.2.0) - Authentication & Security** 🔴

- API key authentication
- Rate limiting
- OAuth2 support (optional)
- Enhanced security features

**Phase 4 (v2.0.0) - Data Persistence** 🔴

- PostgreSQL database integration
- Store and manage parsed reports
- Full-text search
- Analytics dashboard

**Phase 5 (v2.1.0) - Monitoring** 🔴

- Grafana dashboards
- Prometheus metrics
- APM integration
- Advanced alerting

### Future Considerations

- Machine learning for improved parsing
- Multi-bureau support (Equifax, Experian)
- Batch processing capabilities
- GraphQL API

See the full [ROADMAP.md](ROADMAP.md) for detailed plans, timelines, and technical specifications.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass (`pytest`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- PDF processing powered by [PyMuPDF](https://pymupdf.readthedocs.io/)
- Data validation with [Pydantic](https://pydantic-docs.helpmanual.io/)
- Frontend built with [Vite](https://vitejs.dev/) and [shadcn/ui](https://ui.shadcn.com/)

---

## 📞 Support

If you encounter issues:

1. Check the [documentation](docs/)
2. Review existing [GitHub Issues](https://github.com/your-username/transunion-pdf-to-json/issues)
3. Create a new issue with details

---

**Made with ❤️ by Idequel Bernabel**
