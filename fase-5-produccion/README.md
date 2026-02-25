# Fase 5: Producción - Deploy y MLOps

> **Objetivo:** Llevar agentes de IA a producción con APIs, Docker, monitoring y CI/CD.

## 🎯 Estado: PENDIENTE

---

## 🤔 ¿Qué significa "Producción"?

Un agente en desarrollo vs producción:

| Aspecto | Desarrollo | Producción |
|---------|-----------|------------|
| **Entrada** | Terminal manual | API REST |
| **Errores** | Crashes OK | Manejo robusto |
| **Performance** | No importa | Latencia, throughput |
| **Logs** | print() | Logging estructurado |
| **Secrets** | .env local | Secrets manager |
| **Deploy** | Local | Cloud (AWS/GCP) |
| **Monitoring** | Nada | Métricas, alertas |
| **Versioning** | git | Semantic versioning |

---

## 📚 Conceptos Clave

### 1. API REST con FastAPI
Exponer el agente como servicio HTTP:
```python
@app.post("/chat")
async def chat(message: str):
    response = agent.run(message)
    return {"response": response}
```

### 2. Containerización (Docker)
Empaquetar todo en una imagen:
```dockerfile
FROM python:3.11
COPY . /app
RUN uv sync
CMD ["uvicorn", "main:app"]
```

### 3. Monitoring y Observabilidad
Saber qué está pasando en producción:
- Logs estructurados
- Métricas (latencia, errores, tokens)
- Trazas (debugging)
- Alertas

### 4. CI/CD
Automatizar testing y deploy:
```
git push → tests → build → deploy → monitoring
```

---

## 📁 Archivos Planeados

### `01_fastapi_basico.py` - API simple
- Endpoint /chat
- Request/response models con Pydantic
- Manejo de errores
- CORS

### `02_fastapi_streaming.py` - Streaming de respuestas
- Server-Sent Events (SSE)
- Stream de tokens del LLM
- Mejor UX en frontend

### `03_auth_rate_limiting.py` - Seguridad
- API keys
- Rate limiting (prevenir abuso)
- User quotas
- JWT authentication

### `04_caching.py` - Optimización
- Cache de respuestas comunes
- Redis para cache distribuido
- Cache de embeddings (RAG)

### `05_logging_monitoring.py` - Observabilidad
- Logging estructurado (JSON)
- Prometheus metrics
- LangSmith tracing
- Error tracking (Sentry)

### `06_docker_deploy.py` - Containerización
- Dockerfile optimizado
- Docker Compose (app + Redis + DB)
- Health checks
- Multi-stage builds

### `07_async_processing.py` - Jobs asíncronos
- Celery para tareas largas
- Queue de trabajos
- Status endpoints
- Webhooks para resultados

### `08_testing_e2e.py` - Testing de producción
- Tests de integración
- Load testing (Locust)
- Smoke tests post-deploy

---

## 🏗️ Arquitectura de Producción

```
┌─────────────────────────────────────────────────────────┐
│                        FRONTEND                          │
│              (Web, Mobile, CLI, etc.)                    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    LOAD BALANCER                         │
│                    (nginx, ALB)                          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴─────────────┐
        ▼                          ▼
┌──────────────┐          ┌──────────────┐
│   FastAPI    │          │   FastAPI    │  (N instancias)
│   Instance   │          │   Instance   │
└───────┬──────┘          └──────┬───────┘
        │                         │
        └────────────┬────────────┘
                     ▼
        ┌────────────────────────┐
        │   Redis (Cache)        │
        └────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐         ┌──────────────┐
│  Vector DB   │         │  PostgreSQL  │
│  (Pinecone)  │         │  (user data) │
└──────────────┘         └──────────────┘
        │
        ▼
┌────────────────────────────────┐
│   LLM API (Claude, GPT)        │
└────────────────────────────────┘
        │
        ▼
┌────────────────────────────────┐
│   Monitoring (Grafana, etc.)   │
└────────────────────────────────┘
```

---

## 🚀 Stack de Deploy

### Cloud Providers

**AWS:**
- Lambda (serverless, barato)
- ECS/Fargate (containers)
- API Gateway
- RDS (PostgreSQL)
- CloudWatch (monitoring)

**Google Cloud:**
- Cloud Run (containers, fácil)
- Cloud Functions (serverless)
- Cloud SQL (PostgreSQL)
- Cloud Monitoring

**Railway/Render:**
- Más simple que AWS/GCP
- Buen tier gratis
- Deploy con git push

### Consideraciones de Costo

| Componente | Costo Aprox/mes |
|-----------|----------------|
| FastAPI en Cloud Run | $5-20 (bajo tráfico) |
| PostgreSQL (managed) | $15-30 |
| Redis (managed) | $10-20 |
| Pinecone (vector DB) | $0-70 (free tier → 1 pod) |
| LLM API calls | Variable ($50-500+) |
| Monitoring | $0-20 (tiers gratuitos) |

---

## 🔒 Seguridad Best Practices

### 1. Never Hardcode Secrets
```python
# ❌ MAL
api_key = "sk-1234567890"

# ✅ BIEN
import os
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### 2. Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.client.host)

@app.post("/chat")
@limiter.limit("10/minute")  # Max 10 requests/min
async def chat(message: str):
    ...
```

### 3. Input Validation
```python
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=5000)
    user_id: str = Field(..., regex=r"^[a-zA-Z0-9_-]+$")
```

### 4. HTTPS Only
```python
# Forzar HTTPS en producción
if not request.url.scheme == "https":
    raise HTTPException(401, "HTTPS required")
```

---

## 📊 Métricas Clave

### Application Metrics
- **Latencia**: p50, p95, p99 de respuestas
- **Throughput**: requests/segundo
- **Error rate**: % de errores
- **Uptime**: disponibilidad del servicio

### LLM Metrics
- **Tokens/request**: entrada + salida
- **Costo/request**: $$$
- **Tool calls**: frecuencia de uso
- **Cache hit rate**: % de responses cacheadas

### Business Metrics
- **Active users**: DAU, MAU
- **Queries/user**: engagement
- **Conversación duration**: sesiones largas = valor
- **User satisfaction**: ratings, feedback

---

## 🧪 Testing Strategy

### 1. Unit Tests
```python
def test_tool_calculadora():
    result = ejecutar_tool("calc", {"expr": "2+2"})
    assert result == 4
```

### 2. Integration Tests
```python
def test_agent_end_to_end():
    response = agent.run("¿Cuánto es 10*5?")
    assert "50" in response
```

### 3. Load Tests
```python
# Con Locust
from locust import HttpUser, task

class AgentUser(HttpUser):
    @task
    def chat(self):
        self.client.post("/chat", json={"message": "Hola"})
```

### 4. Smoke Tests (post-deploy)
```bash
# Verificar que el servicio está vivo
curl https://api.miagente.com/health
```

---

## 📦 Dockerfile Ejemplo

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar uv
RUN pip install uv

# Copiar dependencias
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔄 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          uv sync
          uv run pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t agente:${{ github.sha }} .

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy agente \
            --image agente:${{ github.sha }} \
            --region us-central1
```

---

## 🔗 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Twelve-Factor App](https://12factor.net/)
- [LangSmith Monitoring](https://docs.smith.langchain.com/)
- [Prometheus Metrics](https://prometheus.io/docs/introduction/overview/)

---

## 🎯 Checklist de Producción

Antes de lanzar, verifica:

- [ ] Tests automáticos (unit, integration, e2e)
- [ ] Secrets en variables de entorno (NO hardcoded)
- [ ] Rate limiting configurado
- [ ] Logging estructurado (JSON)
- [ ] Monitoring y alertas configuradas
- [ ] Health check endpoint
- [ ] Manejo de errores robusto
- [ ] Validación de inputs
- [ ] HTTPS only
- [ ] Backup de base de datos
- [ ] Documentación de API (OpenAPI/Swagger)
- [ ] Rollback strategy
- [ ] Load testing realizado
- [ ] Costos estimados y alertas de budget

---

## 💼 Portfolio-Worthy Projects

Para destacar en búsqueda de empleo:

### Proyecto 1: RAG Chatbot API
- FastAPI + LangChain + Pinecone
- Autenticación + rate limiting
- Docker + deploy en Cloud Run
- Docs en Swagger
- GitHub Actions CI/CD

### Proyecto 2: Multi-Agent System
- 3+ agentes especializados
- Comunicación inter-agente
- Dashboard de monitoreo
- Métricas en Grafana

### Proyecto 3: AI Code Reviewer
- Webhook de GitHub
- Analiza PRs con LLM
- Comenta en código
- Celery para jobs async

---

**Estado:** 📅 Planificado
**Dependencias:** Fases 1-4 completadas
**Archivos planeados:** 8+
**Tiempo estimado:** 3-4 semanas
