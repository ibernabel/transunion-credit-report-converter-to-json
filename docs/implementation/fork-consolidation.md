# Implementation Plan: Fork Consolidation

## Project: TransUnion PDF to JSON Parser

## Phase: Fork Consolidation & Production Readiness

## Author: Antigravity (Architect Mode)

## Date: 2026-01-29

## Status: PENDING APPROVAL

---

## 1. Objective

Consolidate valuable components from the abandoned fork (`credit_report_to_json`) into the original continued project (`transonion-pdf-to-json`) to achieve production readiness while preserving the superior parsing engine and modern stack of the original.

### Success Criteria

- [ ] Docker configuration ready for production deployment
- [ ] Comprehensive VPS deployment documentation
- [ ] Structured logging and monitoring system
- [ ] Automated backup and maintenance utilities
- [ ] Extended test suite with fixtures
- [ ] Complete project documentation (README, CONTRIBUTING, LICENSE)
- [ ] All existing functionality preserved and tests passing

---

## 2. Scope Analysis

### 2.1 Components to Port from Fork

| Component          | Source Path                                                  | Target Path                                                   | Priority |
| ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------- | -------- |
| Dockerfile         | `credit_report_to_json/Dockerfile`                           | `transonion-pdf-to-json/Dockerfile`                           | HIGH     |
| docker-compose.yml | `credit_report_to_json/docker-compose.yml`                   | `transonion-pdf-to-json/docker-compose.yml`                   | HIGH     |
| VPS Setup Guide    | `credit_report_to_json/docs/vps_setup.md`                    | `transonion-pdf-to-json/docs/deployment/vps_setup.md`         | HIGH     |
| Logging Middleware | `credit_report_to_json/app/middleware/logging_middleware.py` | `transonion-pdf-to-json/src/middleware/logging_middleware.py` | MEDIUM   |
| Logging Config     | `credit_report_to_json/app/utils/logging_config.py`          | `transonion-pdf-to-json/src/utils/logging_config.py`          | MEDIUM   |
| Backup Utility     | `credit_report_to_json/app/utils/backup.py`                  | `transonion-pdf-to-json/src/utils/backup.py`                  | MEDIUM   |
| Maintenance Script | `credit_report_to_json/app/maintenance.py`                   | `transonion-pdf-to-json/src/maintenance.py`                   | MEDIUM   |
| Test Fixtures      | `credit_report_to_json/tests/conftest.py`                    | `transonion-pdf-to-json/tests/conftest.py`                    | MEDIUM   |
| CONTRIBUTING.md    | `credit_report_to_json/CONTRIBUTING.md`                      | `transonion-pdf-to-json/CONTRIBUTING.md`                      | LOW      |
| LICENSE            | `credit_report_to_json/LICENSE`                              | `transonion-pdf-to-json/LICENSE`                              | LOW      |

### 2.2 Components to Create/Expand

| Component      | Description                             | Priority |
| -------------- | --------------------------------------- | -------- |
| README.md      | Comprehensive project documentation     | HIGH     |
| docs/README.md | Documentation index                     | MEDIUM   |
| pyproject.toml | Add new dependencies (logging, psutil)  | HIGH     |
| src/main.py    | Integrate middleware and startup events | MEDIUM   |

### 2.3 Components to Keep As-Is (Original is Superior)

- `src/parser/engine.py` - Superior multi-currency parsing
- `src/models/report.py` - Detailed Pydantic V2 models
- `src/scrubber/service.py` - PII scrubbing service
- `src/api/routes.py` - Clean API routing
- `frontend/` - Complete React UI

---

## 3. Technical Specifications

### 3.1 Directory Structure (Target State)

```
transonion-pdf-to-json/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── report.py
│   ├── parser/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── scrubber/
│   │   ├── __init__.py
│   │   └── service.py
│   ├── middleware/                    # NEW - From Fork
│   │   ├── __init__.py
│   │   └── logging_middleware.py
│   ├── utils/                         # NEW - From Fork
│   │   ├── __init__.py
│   │   ├── logging_config.py
│   │   └── backup.py
│   ├── main.py                        # UPDATED
│   └── maintenance.py                 # NEW - From Fork
├── frontend/                          # Existing React UI
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # NEW - From Fork
│   ├── test_core.py
│   ├── test_robustness.py
│   ├── test_api.py                    # NEW - Adapted from Fork
│   └── test_files/                    # NEW - Test fixtures
│       └── sample_report.pdf
├── docs/
│   ├── README.md                      # NEW - Documentation index
│   ├── planning/
│   │   └── architecture.md            # NEW
│   ├── implementation/
│   │   └── fork-consolidation.md      # THIS FILE
│   └── deployment/
│       └── vps_setup.md               # NEW - From Fork
├── Dockerfile                         # NEW - From Fork (updated)
├── docker-compose.yml                 # NEW - From Fork (updated)
├── docker-compose.prod.yml            # NEW - Production config
├── pyproject.toml                     # UPDATED
├── README.md                          # UPDATED - Comprehensive
├── CONTRIBUTING.md                    # NEW - From Fork
├── LICENSE                            # NEW - Apache-2.0
└── .gitignore                         # UPDATED
```

### 3.2 Dockerfile Specifications (Updated for Python 3.12)

```dockerfile
# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libmupdf-dev \
    swig \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Runtime stage
FROM python:3.12-slim

# Create non-root user for security
RUN useradd -m -r -u 1000 appuser && \
    apt-get update && apt-get install -y \
    libmupdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Create necessary directories
RUN mkdir -p logs backups temp_uploads && \
    chown -R appuser:appuser /app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/v1/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3.3 Updated pyproject.toml

```toml
[project]
name = "transunion-pdf-to-json"
version = "1.0.0"
description = "Production-ready FastAPI service to parse TransUnion Credit Reports (PDF) into structured JSON with PII scrubbing"
authors = [
    {name = "Idequel Bernabel"}
]
license = {text = "Apache-2.0"}
readme = "README.md"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.22.0",
    "pydantic[email]>=2.0.0",
    "pymupdf>=1.22.0",
    "unidecode>=1.3.6",
    "python-multipart>=0.0.6",
    # New dependencies for logging/monitoring (from fork)
    "python-json-logger>=2.0.7",
    "psutil>=5.9.0",
    "schedule>=1.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.1",
    "httpx>=0.24.1",
    "mypy>=1.4.1",
    "black>=23.7.0",
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "W"]

[tool.black]
line-length = 100
```

### 3.4 Logging Configuration Adaptation

The logging configuration from the fork needs adaptation to match the new import paths:

```python
# src/utils/logging_config.py
import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger

# Log directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# API Logger
api_logger = logging.getLogger("api")
api_logger.setLevel(logging.INFO)

# JSON formatter for structured logs
json_formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)

# File handler
file_handler = logging.FileHandler(LOG_DIR / "api.log")
file_handler.setFormatter(json_formatter)
api_logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(json_formatter)
api_logger.addHandler(console_handler)
```

### 3.5 Main Application Updates

```python
# src/main.py - Updated with middleware integration
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import router
from src.middleware.logging_middleware import logging_middleware, start_metrics_logging
from src.utils.logging_config import api_logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    api_logger.info("Application starting up")
    start_metrics_logging()
    yield
    # Shutdown
    api_logger.info("Application shutting down")

app = FastAPI(
    title="TransUnion PDF to JSON API",
    description="Production-ready API to parse TransUnion Credit Reports into structured JSON with PII scrubbing.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)
app.middleware("http")(logging_middleware)

@app.get("/")
async def root():
    return {
        "message": "Welcome to TransUnion PDF to JSON API",
        "docs": "/docs",
        "health": "/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 4. Implementation Tasks

### Phase 1: Infrastructure Setup (Priority: HIGH)

- [ ] **Task 1.1**: Create directory structure

  ```bash
  mkdir -p src/middleware src/utils docs/deployment docs/planning
  touch src/middleware/__init__.py src/utils/__init__.py
  ```

- [ ] **Task 1.2**: Create Dockerfile (updated for Python 3.12)
  - Adapt from fork's Dockerfile
  - Update base image to `python:3.12-slim`
  - Update paths for `src/` structure
  - Ensure `pyproject.toml` based installation

- [ ] **Task 1.3**: Create docker-compose.yml (development)
  - Adapt from fork
  - Mount volumes for hot-reload
  - Set DEBUG=1

- [ ] **Task 1.4**: Create docker-compose.prod.yml (production)
  - Remove volume mounts
  - Set proper worker count
  - Add resource limits

- [ ] **Task 1.5**: Update pyproject.toml
  - Add new dependencies: `python-json-logger`, `psutil`, `schedule`
  - Add `ruff` for linting
  - Update version to 1.0.0

### Phase 2: Logging & Monitoring (Priority: MEDIUM)

- [ ] **Task 2.1**: Port logging configuration
  - Copy and adapt `logging_config.py`
  - Update import paths for `src/` structure
  - Ensure log directory creation

- [ ] **Task 2.2**: Port logging middleware
  - Copy and adapt `logging_middleware.py`
  - Add request timing
  - Add metrics collection startup

- [ ] **Task 2.3**: Update `src/main.py`
  - Add lifespan context manager
  - Integrate logging middleware
  - Add startup/shutdown logging

- [ ] **Task 2.4**: Port backup utility
  - Copy and adapt `backup.py`
  - Update paths for project structure

- [ ] **Task 2.5**: Port maintenance script
  - Copy and adapt `maintenance.py`
  - Integrate with backup utility

### Phase 3: Documentation (Priority: MEDIUM-HIGH)

- [ ] **Task 3.1**: Port and update VPS setup guide
  - Copy `vps_setup.md` to `docs/deployment/`
  - Update paths and references
  - Update for Python 3.12

- [ ] **Task 3.2**: Create comprehensive README.md
  - Project description
  - Features list
  - Installation (local + Docker)
  - API usage with examples
  - Environment variables reference
  - Development guide

- [ ] **Task 3.3**: Port CONTRIBUTING.md
  - Update for `pyproject.toml` workflow
  - Add code style guidelines (ruff, black)

- [ ] **Task 3.4**: Add LICENSE file
  - Apache-2.0 license

- [ ] **Task 3.5**: Create docs/README.md
  - Documentation index
  - Navigation guide

### Phase 4: Testing Enhancements (Priority: MEDIUM)

- [ ] **Task 4.1**: Create test fixtures
  - Port `conftest.py` from fork
  - Adapt for project structure
  - Create `tests/test_files/` directory

- [ ] **Task 4.2**: Adapt API tests
  - Port `test_api.py` patterns from fork
  - Update for current endpoints
  - Add file upload tests

- [ ] **Task 4.3**: Run full test suite
  ```bash
  pytest -v --tb=short
  ```

### Phase 5: Cleanup & Verification (Priority: HIGH)

- [ ] **Task 5.1**: Update .gitignore
  - Add `logs/`, `backups/`, `temp_uploads/`
  - Ensure `myenv/` is ignored

- [ ] **Task 5.2**: Build and test Docker image

  ```bash
  docker build -t transunion-parser:1.0.0 .
  docker run -p 8000:8000 transunion-parser:1.0.0
  ```

- [ ] **Task 5.3**: Test API endpoints

  ```bash
  curl http://localhost:8000/v1/health
  curl -X POST -F "file=@test.pdf" http://localhost:8000/v1/parse
  ```

- [ ] **Task 5.4**: Verify PII scrubbing works

- [ ] **Task 5.5**: Cleanup old files
  - Remove old `implementation_plan.md` from root (or move to docs)
  - Remove `walkthrough.md` from root (or move to docs)
  - Consider archiving `legacy_backup/`

---

## 5. Dependencies & Risks

### 5.1 New Dependencies

| Package            | Version | Purpose                       |
| ------------------ | ------- | ----------------------------- |
| python-json-logger | >=2.0.7 | Structured JSON logging       |
| psutil             | >=5.9.0 | System metrics collection     |
| schedule           | >=1.2.0 | Task scheduling (maintenance) |
| ruff               | >=0.1.0 | Fast Python linter (dev)      |

### 5.2 Risks & Mitigations

| Risk                                    | Impact | Mitigation                         |
| --------------------------------------- | ------ | ---------------------------------- |
| Import path changes break existing code | HIGH   | Run tests after each change        |
| Docker image size increase              | LOW    | Multi-stage build already in place |
| Logging adds latency                    | LOW    | Use async logging, monitor impact  |
| psutil system calls fail in container   | MEDIUM | Add try/except fallbacks           |

---

## 6. Verification Checklist

### Functional Verification

- [ ] PDF upload and parsing works
- [ ] PII scrubbing applied correctly
- [ ] Health endpoint responds
- [ ] Swagger docs load at `/docs`
- [ ] Frontend builds and connects to API

### Docker Verification

- [ ] Image builds successfully
- [ ] Container starts without errors
- [ ] Health check passes
- [ ] Logs are written correctly
- [ ] Non-root user is active

### Documentation Verification

- [ ] README renders correctly on GitHub
- [ ] All code examples work
- [ ] VPS guide is accurate for new structure
- [ ] CONTRIBUTING guide is accurate

---

## 7. Estimated Effort

| Phase                           | Tasks  | Estimated Time |
| ------------------------------- | ------ | -------------- |
| Phase 1: Infrastructure         | 5      | 2-3 hours      |
| Phase 2: Logging & Monitoring   | 5      | 2-3 hours      |
| Phase 3: Documentation          | 5      | 2-3 hours      |
| Phase 4: Testing                | 3      | 1-2 hours      |
| Phase 5: Cleanup & Verification | 5      | 1-2 hours      |
| **Total**                       | **23** | **8-13 hours** |

---

## 8. Post-Implementation

### What to do with the Fork

After consolidation is complete:

1. **Archive option**: Keep `credit_report_to_json/` as reference
2. **Delete option**: Remove fork directory entirely
3. **Document**: Note in commit message that fork was consolidated

### Commit Message Template

```
feat: consolidate fork components for production readiness

- Add Docker configuration (Dockerfile, docker-compose.yml)
- Implement structured logging with JSON formatter
- Add system metrics monitoring and backup utilities
- Port VPS deployment documentation
- Expand README with comprehensive usage guide
- Add CONTRIBUTING.md and Apache-2.0 LICENSE
- Enhance test suite with fixtures and API tests

Consolidates valuable components from credit_report_to_json fork
while preserving superior parsing engine and Pydantic V2 models.
```

---

## Approval

**Architect Review**: Pending  
**Developer Review**: Pending  
**Security Review**: Pending

---

_This implementation plan follows the ASD Framework guidelines and prioritizes SOLID, KISS, and DRY principles._
