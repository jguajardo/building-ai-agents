# SupportGPT - Especificaciones Técnicas Completas

> **Documento de Especificaciones para Desarrollo desde Cero**
> **Versión:** 1.0
> **Fecha:** 2026-02-25
> **Propósito:** Documento completo para iniciar proyecto con Claude Code

---

## 📋 ÍNDICE

1. [Visión General](#visión-general)
2. [Arquitectura Completa (5 Fases)](#arquitectura-completa)
3. [Stack Tecnológico Detallado](#stack-tecnológico)
4. [Funcionalidades Completas](#funcionalidades-completas)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Modelos de Datos](#modelos-de-datos)
7. [APIs y Endpoints](#apis-y-endpoints)
8. [GUI en Python](#gui-en-python)
9. [Seguridad y Compliance](#seguridad-y-compliance)
10. [Monitoreo y Observabilidad](#monitoreo-y-observabilidad)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Roadmap de Implementación](#roadmap)

---

## 🎯 VISIÓN GENERAL

### Problema que Resuelve
Automatizar 70-80% de tickets de soporte técnico usando IA, reduciendo costos y tiempo de respuesta de horas a segundos.

### Propuesta de Valor
- **Para clientes:** Respuestas instantáneas 24/7 basadas en documentación oficial
- **Para empresas:** Reducir carga de equipo de soporte en 70%+
- **Para agentes:** Enfocarse en casos complejos, no repetitivos

### Métricas de Éxito
- 70%+ de tickets auto-resueltos
- <5 segundos tiempo de respuesta
- 90%+ de accuracy en respuestas
- 4.5/5 satisfacción de usuario

---

## 🏗️ ARQUITECTURA COMPLETA (5 FASES)

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA 5: MLOPS                             │
│  FastAPI + Docker + Railway + Monitoring + CI/CD             │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    CAPA 4: RAG                               │
│  ChromaDB + Embeddings + Semantic Search                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                 CAPA 3: LANGGRAPH                            │
│  State Management + Routing + Human-in-Loop                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                 CAPA 2: LANGCHAIN                            │
│  Tools + Prompts + Memory + LLM Integration                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                 CAPA 1: LLM (CLAUDE)                         │
│              Inteligencia Base                               │
└─────────────────────────────────────────────────────────────┘
```

### Fase 1: LLM Base (Claude Sonnet 4.5)

**Responsabilidad:** Inteligencia y generación de respuestas

**Componentes:**
- Cliente de Anthropic para Claude
- Prompt engineering templates
- Response generation
- Context understanding

**Por qué Claude:**
- Mejor seguimiento de instrucciones
- 200k context window (docs grandes)
- Tool calling nativo
- Español + inglés fluido

---

### Fase 2: LangChain (Orquestación)

**Responsabilidad:** Conectar LLM con herramientas y gestionar flujos

**Componentes:**

1. **Chat Models**
   ```python
   from langchain_anthropic import ChatAnthropic

   llm = ChatAnthropic(
       model="claude-sonnet-4-5-20250929",
       temperature=0.3,  # Más determinístico para soporte
       max_tokens=4096
   )
   ```

2. **Prompt Templates**
   ```python
   SUPPORT_PROMPT = ChatPromptTemplate.from_messages([
       ("system", """Eres un agente de soporte técnico experto.

       REGLAS ESTRICTAS:
       - Solo responde basándote en la documentación proporcionada
       - Si no sabes algo, di "No tengo esa información" y escala a humano
       - Sé conciso pero completo
       - Usa formato markdown para mejor legibilidad
       - Incluye links a documentación relevante

       Documentación disponible:
       {context}

       Historial de conversación:
       {history}
       """),
       ("human", "{question}")
   ])
   ```

3. **Memory**
   - ConversationBufferMemory para sesión actual
   - ConversationSummaryMemory para historial largo

4. **Tools**
   - `search_docs`: Búsqueda en knowledge base
   - `create_ticket`: Crear ticket para escalamiento
   - `get_user_info`: Obtener contexto del usuario
   - `check_system_status`: Ver estado de servicios

---

### Fase 3: LangGraph (Control de Flujo)

**Responsabilidad:** Orquestar el proceso completo con decisiones inteligentes

**Grafo de Estados:**

```
                    START
                      ↓
              ┌───────────────┐
              │   Classify    │ ← Clasificar tipo de consulta
              └───────┬───────┘
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
    ┌──────────┐            ┌──────────┐
    │ Technical│            │ Billing/ │
    │          │            │ General  │
    └────┬─────┘            └────┬─────┘
         │                       │
         ↓                       ↓
    ┌──────────┐            ┌──────────┐
    │  Search  │            │  Search  │
    │  RAG     │            │  RAG     │
    └────┬─────┘            └────┬─────┘
         │                       │
         ↓                       ↓
    ┌──────────┐            ┌──────────┐
    │ Generate │            │ Generate │
    │ Response │            │ Response │
    └────┬─────┘            └────┬─────┘
         │                       │
         └───────────┬───────────┘
                     ↓
            ┌────────────────┐
            │  Confidence?   │
            └────┬───────┬───┘
                 │       │
            High │       │ Low
                 ↓       ↓
            ┌────────┐  ┌────────┐
            │  Send  │  │ Human  │
            │Response│  │ Review │
            └────────┘  └────────┘
                 │           │
                 └─────┬─────┘
                       ↓
                     END
```

**Código de Estado:**

```python
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

class SupportState(TypedDict):
    messages: Annotated[list, add_messages]
    query_type: str  # "technical", "billing", "general"
    context: str  # Documentos relevantes encontrados
    confidence: float  # 0.0 - 1.0
    escalate: bool  # True si necesita humano
    ticket_id: str | None
    user_id: str
    session_id: str

# Nodos del grafo
def classify_query(state: SupportState) -> dict:
    """Clasifica el tipo de consulta."""
    # Usar LLM para clasificar
    pass

def search_knowledge_base(state: SupportState) -> dict:
    """Busca en RAG."""
    # Búsqueda semántica
    pass

def generate_response(state: SupportState) -> dict:
    """Genera respuesta con LLM."""
    # Usar LLM + context
    pass

def evaluate_confidence(state: SupportState) -> dict:
    """Evalúa confianza de la respuesta."""
    # Calcular confidence score
    pass

def should_escalate(state: SupportState) -> Literal["human", "send"]:
    """Decide si escalar a humano."""
    if state["confidence"] < 0.7 or state["escalate"]:
        return "human"
    return "send"

# Construcción del grafo
graph = StateGraph(SupportState)
graph.add_node("classify", classify_query)
graph.add_node("search", search_knowledge_base)
graph.add_node("generate", generate_response)
graph.add_node("evaluate", evaluate_confidence)
graph.add_node("human_review", human_review_node)

graph.add_edge(START, "classify")
graph.add_edge("classify", "search")
graph.add_edge("search", "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges(
    "evaluate",
    should_escalate,
    {"human": "human_review", "send": END}
)
```

**Checkpointing:**
```python
from langgraph.checkpoint.postgres import PostgresSaver

# Memoria persistente
checkpointer = PostgresSaver(
    connection_string="postgresql://..."
)

app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]  # Pausar antes de revisión humana
)
```

---

### Fase 4: RAG (Retrieval Augmented Generation)

**Responsabilidad:** Conocimiento especializado basado en documentación

**Componentes Detallados:**

#### 4.1 Document Processing Pipeline

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    MarkdownLoader,
    WebBaseLoader
)

class DocumentProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def load_documents(self, source_path: str):
        """Carga docs de múltiples formatos."""
        if source_path.endswith('.pdf'):
            loader = PyPDFLoader(source_path)
        elif source_path.endswith('.md'):
            loader = MarkdownLoader(source_path)
        elif source_path.startswith('http'):
            loader = WebBaseLoader(source_path)
        else:
            loader = TextLoader(source_path)

        docs = loader.load()
        return self.splitter.split_documents(docs)

    def add_metadata(self, docs):
        """Agrega metadata importante."""
        for doc in docs:
            doc.metadata.update({
                'source_type': 'documentation',
                'indexed_at': datetime.now().isoformat(),
                'language': detect_language(doc.page_content),
                'category': classify_doc_category(doc.page_content)
            })
        return docs
```

#### 4.2 Vector Store (ChromaDB)

```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class KnowledgeBase:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"  # Costo-efectivo
        )

        self.vectorstore = Chroma(
            collection_name="support_docs",
            embedding_function=self.embeddings,
            persist_directory="./chroma_db",
            collection_metadata={"hnsw:space": "cosine"}
        )

    def index_documents(self, docs: list):
        """Indexa documentos en vector DB."""
        self.vectorstore.add_documents(docs)
        self.vectorstore.persist()

    def search(self, query: str, k: int = 5, filter: dict = None):
        """Búsqueda semántica."""
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query,
            k=k,
            filter=filter
        )
        return results

    def hybrid_search(self, query: str, k: int = 5):
        """Combina búsqueda semántica + keyword."""
        # Semantic search
        semantic_results = self.search(query, k=k)

        # Keyword search (BM25)
        keyword_results = self.vectorstore.max_marginal_relevance_search(
            query, k=k
        )

        # Combine and re-rank
        return self.rerank(semantic_results + keyword_results)
```

#### 4.3 Embeddings Strategy

**Modelo:** `text-embedding-3-small` (OpenAI)
- Dimensiones: 1536
- Costo: $0.02 / 1M tokens
- Performance: Excelente para soporte

**Alternativa (local):** `all-MiniLM-L6-v2`
- Gratis
- 384 dimensiones
- Para testing/desarrollo

#### 4.4 Retrieval Strategy

**Multi-Query Retrieval:**
```python
def multi_query_retrieval(query: str):
    """Genera múltiples variaciones de la query."""
    llm = ChatAnthropic(...)

    # Generar variaciones
    variations = llm.invoke(f"""Genera 3 variaciones de esta pregunta:
    {query}

    Variaciones:""")

    # Buscar con cada variación
    all_results = []
    for variation in variations:
        results = kb.search(variation, k=3)
        all_results.extend(results)

    # Deduplicar y rerank
    return deduplicate_and_rerank(all_results)
```

**Parent Document Retrieval:**
- Indexa chunks pequeños para mejor recall
- Retorna documento completo para mejor context

---

### Fase 5: MLOps (Producción)

**Responsabilidad:** Sistema robusto, escalable y observable en producción

#### 5.1 API REST (FastAPI)

```python
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import asyncio

app = FastAPI(
    title="SupportGPT API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Models
class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: str | None = None
    context: dict | None = None

class ChatResponse(BaseModel):
    message: str
    confidence: float
    sources: list[str]
    escalated: bool
    session_id: str
    ticket_id: str | None = None

# Auth
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica API key."""
    token = credentials.credentials
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return get_user_from_token(token)

# Endpoints
@app.post("/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user = Depends(verify_token),
    background_tasks: BackgroundTasks
):
    """Endpoint principal de chat."""
    try:
        # Invoke agent
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config={"configurable": {"thread_id": request.session_id}}
        )

        # Log async
        background_tasks.add_task(log_interaction, request, response)

        return ChatResponse(**response)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")

@app.post("/v1/knowledge-base/upload")
async def upload_docs(
    files: list[UploadFile],
    user = Depends(verify_token)
):
    """Upload documentos a la knowledge base."""
    # Procesar y indexar
    pass

@app.get("/v1/analytics")
async def get_analytics(
    start_date: str,
    end_date: str,
    user = Depends(verify_token)
):
    """Obtener analytics del chatbot."""
    # Retornar métricas
    pass

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
```

#### 5.2 Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/v1/chat")
@limiter.limit("100/minute")  # 100 requests por minuto
async def chat(request: Request, ...):
    pass
```

#### 5.3 Caching

```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def cache_response(ttl=3600):
    """Decorator para cachear respuestas."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args))}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute
            result = await func(*args, **kwargs)

            # Cache result
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            return result
        return wrapper
    return decorator

@cache_response(ttl=1800)  # 30 minutos
async def search_knowledge_base(query: str):
    """Búsqueda cacheada."""
    pass
```

#### 5.4 Monitoring (Prometheus + Grafana)

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
chat_requests_total = Counter(
    'supportgpt_chat_requests_total',
    'Total de requests de chat',
    ['status', 'user_tier']
)

chat_duration_seconds = Histogram(
    'supportgpt_chat_duration_seconds',
    'Duración de requests de chat'
)

confidence_score = Histogram(
    'supportgpt_confidence_score',
    'Confidence score de respuestas'
)

escalations_total = Counter(
    'supportgpt_escalations_total',
    'Total de escalamientos a humanos'
)

active_sessions = Gauge(
    'supportgpt_active_sessions',
    'Sesiones activas'
)

@app.post("/v1/chat")
async def chat(request: ChatRequest, ...):
    start_time = time.time()

    try:
        response = await agent.invoke(...)

        # Record metrics
        chat_requests_total.labels(status='success', user_tier=user.tier).inc()
        confidence_score.observe(response.confidence)

        if response.escalated:
            escalations_total.inc()

        return response

    except Exception as e:
        chat_requests_total.labels(status='error', user_tier=user.tier).inc()
        raise

    finally:
        duration = time.time() - start_time
        chat_duration_seconds.observe(duration)
```

#### 5.5 Logging Estructurado

```python
import structlog
from pythonjsonlogger import jsonlogger

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info(
    "chat_request_processed",
    user_id=request.user_id,
    session_id=request.session_id,
    query_length=len(request.message),
    confidence=response.confidence,
    escalated=response.escalated,
    duration_ms=duration * 1000
)
```

---

## 🛠️ STACK TECNOLÓGICO DETALLADO

### Core Stack

| Componente | Tecnología | Versión | Justificación |
|------------|------------|---------|---------------|
| **LLM** | Claude Sonnet 4.5 | Latest | Mejor para soporte, 200k context |
| **Framework AI** | LangChain | 1.x | Estándar de industria |
| **Orchestration** | LangGraph | 1.x | Control fino de agentes |
| **Vector DB** | ChromaDB | Latest | Fácil, local-first |
| **Embeddings** | OpenAI text-embedding-3-small | Latest | Costo-efectivo |
| **API Framework** | FastAPI | 0.115+ | Async, rápido, docs automáticas |
| **GUI** | Gradio | 5.x | Mejor para AI/ML apps |
| **Database** | PostgreSQL | 16+ | Checkpointing + analytics |
| **Cache** | Redis | 7+ | Rate limiting + caching |
| **Monitoring** | Prometheus + Grafana | Latest | Estándar observability |

### Python Dependencies

```toml
[project]
name = "supportgpt"
version = "1.0.0"
description = "AI-powered support chatbot with RAG"
requires-python = ">=3.11"
dependencies = [
    # Core AI
    "anthropic>=0.83.0",
    "langchain>=1.2.0",
    "langchain-anthropic>=1.3.0",
    "langchain-core>=1.2.0",
    "langchain-openai>=1.1.0",  # Para embeddings
    "langgraph>=1.0.0",
    "langgraph-checkpoint>=4.0.0",

    # RAG
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",

    # Document Processing
    "pypdf>=4.0.0",
    "python-docx>=1.1.0",
    "beautifulsoup4>=4.12.0",
    "markdown>=3.5.0",

    # API
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.31.0",
    "pydantic>=2.9.0",
    "python-multipart>=0.0.9",

    # Auth & Security
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-dotenv>=1.0.0",

    # Database
    "psycopg2-binary>=2.9.9",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",

    # Caching
    "redis>=5.0.0",
    "hiredis>=2.3.0",

    # Monitoring
    "prometheus-client>=0.20.0",
    "python-json-logger>=2.0.7",
    "structlog>=24.1.0",

    # Rate Limiting
    "slowapi>=0.1.9",

    # GUI
    "gradio>=5.0.0",

    # Utils
    "httpx>=0.27.0",
    "tenacity>=8.2.3",
    "pydantic-settings>=2.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]
```

---

## ⚙️ FUNCIONALIDADES COMPLETAS

### Funcionalidades Core (MVP)

#### F1: Chat Inteligente con RAG
**Descripción:** Usuario hace pregunta, bot responde basándose en documentación

**User Story:**
```
Como usuario de soporte
Quiero hacer una pregunta sobre el producto
Para recibir respuesta instantánea basada en documentación oficial
```

**Acceptance Criteria:**
- ✅ Respuesta en <5 segundos
- ✅ Cita fuentes de documentación
- ✅ Formato markdown legible
- ✅ Maneja typos y preguntas mal formuladas
- ✅ Soporta español e inglés

**Flujo Técnico:**
1. Usuario envía mensaje
2. Clasificar tipo de query
3. Buscar en knowledge base (top 5 docs)
4. LLM genera respuesta con context
5. Evaluar confidence
6. Si confidence >0.7 → Enviar respuesta
7. Si confidence <0.7 → Escalar a humano

---

#### F2: Knowledge Base Management
**Descripción:** Admin puede cargar, editar y gestionar documentos

**Features:**
- Upload múltiples formatos (PDF, MD, TXT, DOCX, HTML)
- Auto-parsing y chunking
- Preview de documentos indexados
- Edición en vivo
- Versionado de documentos
- Búsqueda y filtrado
- Estadísticas de uso por documento

**GUI:**
```
┌─────────────────────────────────────────────────┐
│  Knowledge Base Manager                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  📁 Upload Documents                            │
│  [Drag & Drop Area or Click to Browse]          │
│                                                 │
│  📚 Current Documents (127)                     │
│  ┌─────────────────────────────────────────┐   │
│  │ FAQ.md              Updated: 2h ago     │   │
│  │ User Manual.pdf     Updated: 1d ago     │   │
│  │ API Docs.md         Updated: 3d ago     │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  🔍 [Search documents...]                       │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

#### F3: Conversación Multi-turn con Memoria
**Descripción:** Bot mantiene contexto de la conversación

**Example:**
```
User: "¿Cómo reseteo mi contraseña?"
Bot: "Para resetear tu contraseña, ve a Settings > Security > Reset Password"

User: "¿Y si no recibo el email?"
Bot: [ENTIENDE QUE SE REFIERE AL EMAIL DE RESET]
     "Si no recibes el email de reseteo, verifica tu carpeta de spam..."
```

**Implementación:**
- ConversationBufferMemory para últimos 10 mensajes
- ConversationSummaryMemory para historial completo
- Resumen automático cada 20 mensajes

---

#### F4: Escalamiento a Humano (Human-in-the-Loop)
**Descripción:** Cuando el bot no puede resolver, escala a agente humano

**Triggers de Escalamiento:**
- Confidence <0.7
- Usuario pide "hablar con humano"
- Query clasificada como "crítica" o "legal"
- 3+ mensajes sin resolver el problema

**Flujo:**
1. Bot detecta necesidad de escalamiento
2. Crea ticket con contexto completo
3. Notifica agente humano (email + dashboard)
4. Agente puede ver toda la conversación
5. Agente responde, bot relay la respuesta
6. Agente puede cerrar ticket

**Dashboard para Agentes:**
```
┌─────────────────────────────────────────────────┐
│  Open Tickets (3)                               │
├─────────────────────────────────────────────────┤
│                                                 │
│  🔴 URGENT - Ticket #1234                       │
│     User: john@example.com                      │
│     Issue: Billing problem                      │
│     Messages: 4                                 │
│     [View Conversation] [Take Ticket]           │
│                                                 │
│  🟡 Ticket #1235                                │
│     User: jane@example.com                      │
│     Issue: Cannot login                         │
│     [View] [Take]                               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

#### F5: Multi-idioma (Español + Inglés)
**Descripción:** Detecta idioma y responde en el mismo

**Implementación:**
```python
from langdetect import detect

def detect_and_respond(message: str):
    language = detect(message)

    if language == 'es':
        system_prompt = SPANISH_PROMPT
    else:
        system_prompt = ENGLISH_PROMPT

    # Procesar con prompt correcto
    ...
```

---

### Funcionalidades Avanzadas (Post-MVP)

#### F6: Analytics Dashboard
**Métricas:**
- Total queries / día
- % auto-resueltos vs escalados
- Tiempo promedio de respuesta
- Confidence score promedio
- Top 10 preguntas
- Documentos más usados
- Satisfacción de usuario

**Visualización:**
```
┌─────────────────────────────────────────────────┐
│  Analytics Dashboard                            │
├─────────────────────────────────────────────────┤
│                                                 │
│  📊 Today's Overview                            │
│  ┌──────────┬──────────┬──────────┬──────────┐ │
│  │  1,247   │   987    │   260    │  4.2s    │ │
│  │  Queries │  Auto    │  Escalated│ Avg Time│ │
│  └──────────┴──────────┴──────────┴──────────┘ │
│                                                 │
│  📈 Queries Over Time (7 days)                  │
│  [Line Chart]                                   │
│                                                 │
│  🔝 Top Questions                               │
│  1. How to reset password? (143)               │
│  2. Billing question (98)                      │
│  3. Cannot login (76)                          │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

#### F7: Feedback Loop
**Descripción:** Usuario califica respuestas, sistema mejora

**Flow:**
```
Bot: "Aquí está tu respuesta... [respuesta]"

     👍 Útil    👎 No útil

Si 👎:
  → "¿Qué faltó?" [texto libre]
  → Guardar feedback
  → Escalar a humano si es crítico
```

**Uso del Feedback:**
- Identificar gaps en documentación
- Reentrenar modelos de clasificación
- Priorizar qué docs actualizar
- Mejorar prompts

---

#### F8: Integraciones Externas

**Slack Integration:**
```python
@app.post("/webhooks/slack")
async def slack_webhook(request: Request):
    """Responde en Slack."""
    data = await request.json()

    # Procesar mensaje de Slack
    response = await agent.invoke(...)

    # Responder en Slack
    await slack_client.chat_postMessage(
        channel=data['channel'],
        text=response.message
    )
```

**Email Integration:**
- Monitorear inbox de soporte
- Convertir email a ticket
- Responder automáticamente si puede
- Escalar a humano si no puede

**WhatsApp/Discord/Telegram:**
- Webhooks similares
- Mismo agente, diferentes canales

---

#### F9: Sugerencias Proactivas
**Descripción:** Mientras usuario escribe, mostrar sugerencias

```
User typing: "How to rese..."

Sugerencias:
  💡 How to reset password?
  💡 How to reset 2FA?
  💡 How to reset API keys?
```

**Implementación:**
- Embeddings de preguntas comunes
- Búsqueda en tiempo real mientras escribe
- Top 3 sugerencias

---

#### F10: A/B Testing de Prompts
**Descripción:** Probar diferentes prompts para mejorar respuestas

**Features:**
- Definir variantes de prompts
- Asignar aleatoriamente a usuarios
- Medir performance (confidence, feedback)
- Auto-seleccionar el mejor

```python
prompt_variants = {
    'A': "Eres un asistente de soporte...",
    'B': "Eres un experto técnico...",
    'C': "Eres un amigo ayudando..."
}

# Asignar variante
variant = get_variant_for_user(user_id)
prompt = prompt_variants[variant]

# Log resultado
log_ab_test(variant, confidence, feedback)
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
supportgpt/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                 # CI/CD pipeline
│       └── deploy.yml             # Auto-deploy
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── agent.py               # Main agent logic (LangGraph)
│   │   ├── prompts.py             # Prompt templates
│   │   └── config.py              # Configuration
│   │
│   ├── rag/                       # RAG components
│   │   ├── __init__.py
│   │   ├── document_processor.py  # Process docs
│   │   ├── embeddings.py          # Embedding logic
│   │   ├── vector_store.py        # ChromaDB wrapper
│   │   └── retrieval.py           # Retrieval strategies
│   │
│   ├── api/                       # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # Chat endpoints
│   │   │   ├── knowledge_base.py  # KB management
│   │   │   ├── analytics.py       # Analytics endpoints
│   │   │   └── webhooks.py        # External integrations
│   │   ├── models.py              # Pydantic models
│   │   ├── auth.py                # Authentication
│   │   └── middleware.py          # Custom middleware
│   │
│   ├── gui/                       # Gradio GUI
│   │   ├── __init__.py
│   │   ├── app.py                 # Main Gradio app
│   │   ├── components/
│   │   │   ├── chat_interface.py
│   │   │   ├── kb_manager.py
│   │   │   ├── analytics_panel.py
│   │   │   └── settings.py
│   │   └── themes.py              # Custom Gradio themes
│   │
│   ├── db/                        # Database
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── session.py             # DB session management
│   │   └── migrations/            # Alembic migrations
│   │
│   ├── monitoring/                # Observability
│   │   ├── __init__.py
│   │   ├── metrics.py             # Prometheus metrics
│   │   ├── logging.py             # Structured logging
│   │   └── tracing.py             # Distributed tracing
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── cache.py               # Redis caching
│       ├── rate_limit.py          # Rate limiting
│       └── validators.py          # Input validation
│
├── tests/                         # Tests
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agent.py
│   │   ├── test_rag.py
│   │   └── test_api.py
│   ├── integration/
│   │   ├── test_e2e.py
│   │   └── test_workflows.py
│   └── fixtures/
│       └── sample_docs/
│
├── docs/                          # Documentation
│   ├── architecture.md
│   ├── api_reference.md
│   ├── deployment.md
│   └── user_guide.md
│
├── scripts/                       # Utility scripts
│   ├── setup_db.py
│   ├── index_documents.py
│   └── run_tests.sh
│
├── docker/
│   ├── Dockerfile                 # Main dockerfile
│   ├── Dockerfile.dev             # Development dockerfile
│   └── docker-compose.yml         # Services composition
│
├── data/                          # Data files
│   ├── documents/                 # Sample documents
│   ├── vector_db/                 # ChromaDB persistence
│   └── logs/                      # Log files
│
├── .env.example                   # Example environment variables
├── .gitignore
├── pyproject.toml                 # Python dependencies
├── README.md
└── Makefile                       # Common commands
```

---

## 🗄️ MODELOS DE DATOS

### PostgreSQL Schema

```sql
-- Users (clientes del servicio)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255),
    api_key VARCHAR(64) UNIQUE NOT NULL,
    tier VARCHAR(20) DEFAULT 'starter',  -- starter, growth, scale
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Knowledge Base Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    source_type VARCHAR(50),  -- pdf, markdown, web, etc
    source_url VARCHAR(1000),
    metadata JSONB,
    indexed_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

    -- Full-text search index
    content_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX idx_documents_vector ON documents USING GIN(content_vector);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    end_user_id VARCHAR(255),  -- ID del usuario final que chatea
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    message_count INT DEFAULT 0,
    escalated BOOLEAN DEFAULT FALSE,
    avg_confidence FLOAT
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id),
    role VARCHAR(20) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    confidence FLOAT,
    sources JSONB,  -- Array de document IDs usados
    created_at TIMESTAMP DEFAULT NOW(),

    -- Metadata
    token_count INT,
    latency_ms INT
);

-- Escalations (tickets)
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id),
    reason VARCHAR(500),
    status VARCHAR(20) DEFAULT 'open',  -- open, in_progress, resolved, closed
    assigned_to VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution TEXT
);

-- Feedback
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics Events
CREATE TABLE analytics_events (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    event_type VARCHAR(100) NOT NULL,  -- query, escalation, feedback, etc
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analytics_created_at ON analytics_events(created_at);
CREATE INDEX idx_analytics_user_id ON analytics_events(user_id);

-- API Usage Tracking
CREATE TABLE api_usage (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    endpoint VARCHAR(255),
    status_code INT,
    latency_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- A/B Test Experiments
CREATE TABLE ab_experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    variants JSONB NOT NULL,  -- {A: {...}, B: {...}}
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ab_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES ab_experiments(id),
    user_id UUID REFERENCES users(id),
    variant VARCHAR(10),
    assigned_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ab_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID REFERENCES ab_experiments(id),
    variant VARCHAR(10),
    confidence FLOAT,
    feedback_rating INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### ChromaDB Collections

```python
# Collection metadata
collection_metadata = {
    "hnsw:space": "cosine",  # Distance metric
    "hnsw:construction_ef": 200,
    "hnsw:M": 16
}

# Document metadata example
document_metadata = {
    "doc_id": "uuid",
    "title": "How to Reset Password",
    "source": "faq.md",
    "category": "authentication",
    "language": "en",
    "indexed_at": "2026-02-25T10:00:00Z",
    "updated_at": "2026-02-25T10:00:00Z",
    "user_id": "uuid",
    "chunk_index": 0,
    "total_chunks": 5
}
```

---

## 🔌 APIs Y ENDPOINTS

### API v1 Endpoints

#### Authentication
```
POST /v1/auth/register       # Register new user
POST /v1/auth/login          # Login
POST /v1/auth/refresh        # Refresh token
POST /v1/auth/api-key        # Generate API key
```

#### Chat
```
POST /v1/chat                # Send message
GET  /v1/chat/sessions       # List sessions
GET  /v1/chat/sessions/{id}  # Get session details
DELETE /v1/chat/sessions/{id}# Delete session
POST /v1/chat/feedback       # Submit feedback
```

#### Knowledge Base
```
POST /v1/kb/upload           # Upload documents
GET  /v1/kb/documents        # List documents
GET  /v1/kb/documents/{id}   # Get document
PUT  /v1/kb/documents/{id}   # Update document
DELETE /v1/kb/documents/{id} # Delete document
POST /v1/kb/search           # Search knowledge base
POST /v1/kb/reindex          # Reindex all documents
```

#### Escalations
```
GET  /v1/escalations         # List open tickets
GET  /v1/escalations/{id}    # Get ticket details
PUT  /v1/escalations/{id}    # Update ticket
POST /v1/escalations/{id}/resolve  # Resolve ticket
```

#### Analytics
```
GET  /v1/analytics/overview  # Dashboard overview
GET  /v1/analytics/queries   # Query statistics
GET  /v1/analytics/documents # Document usage
GET  /v1/analytics/export    # Export data (CSV)
```

#### Webhooks
```
POST /webhooks/slack         # Slack integration
POST /webhooks/discord       # Discord integration
POST /webhooks/teams         # MS Teams integration
```

#### Health & Monitoring
```
GET  /health                 # Health check
GET  /metrics                # Prometheus metrics
GET  /version                # Version info
```

### API Request/Response Examples

#### Chat Request
```json
POST /v1/chat

{
  "message": "How do I reset my password?",
  "user_id": "user_123",
  "session_id": "session_abc",  // optional, creates new if not provided
  "context": {  // optional
    "user_tier": "premium",
    "previous_tickets": 3
  }
}
```

#### Chat Response
```json
{
  "message": "To reset your password:\n\n1. Go to Settings\n2. Click Security\n3. Click 'Reset Password'\n4. Check your email for the reset link\n\n[Learn more](https://docs.example.com/reset-password)",
  "confidence": 0.92,
  "sources": [
    {
      "title": "Password Reset Guide",
      "url": "https://docs.example.com/reset-password",
      "relevance": 0.95
    }
  ],
  "escalated": false,
  "session_id": "session_abc",
  "ticket_id": null,
  "metadata": {
    "tokens_used": 245,
    "latency_ms": 1250,
    "model": "claude-sonnet-4-5"
  }
}
```

#### Upload Document
```json
POST /v1/kb/upload

Content-Type: multipart/form-data

{
  "file": [binary],
  "metadata": {
    "category": "authentication",
    "language": "en",
    "tags": ["password", "security"]
  }
}
```

---

## 🎨 GUI EN PYTHON (GRADIO)

### Por Qué Gradio

Basándome en la investigación:
- **Rápido de desarrollar** - ML/AI apps en minutos
- **Nativo para AI** - Diseñado específicamente para demos de ML
- **Deployment fácil** - `gr.launch(share=True)` y listo
- **Componentes ricos** - Chatbot, file upload, plots integrados

**Alternativa:** Streamlit es mejor para dashboards complejos, pero Gradio es superior para chatbots.

### Aplicación Gradio Completa

```python
import gradio as gr
from typing import List, Tuple
import asyncio

# ============================================================================
# COMPONENTES
# ============================================================================

def create_chat_interface():
    """Interfaz principal de chat."""

    def respond(message, history):
        """Handle chat message."""
        # Call agent
        response = agent.invoke({
            "messages": [{"role": "user", "content": message}]
        })

        return response["message"]

    chatbot = gr.Chatbot(
        label="SupportGPT",
        height=600,
        bubble_full_width=False,
        avatar_images=("user.png", "bot.png")
    )

    chat_interface = gr.ChatInterface(
        fn=respond,
        chatbot=chatbot,
        textbox=gr.Textbox(
            placeholder="Ask a question...",
            container=False,
            scale=7
        ),
        submit_btn="Send",
        retry_btn="🔄 Retry",
        undo_btn="↩️ Undo",
        clear_btn="🗑️ Clear",
        examples=[
            "How do I reset my password?",
            "What are your pricing plans?",
            "I can't login to my account"
        ]
    )

    return chat_interface


def create_kb_manager():
    """Knowledge base management interface."""

    def upload_documents(files):
        """Handle document upload."""
        results = []
        for file in files:
            try:
                # Process document
                processor.process_document(file.name)
                results.append(f"✅ {file.name} uploaded successfully")
            except Exception as e:
                results.append(f"❌ {file.name} failed: {str(e)}")

        return "\n".join(results)

    def list_documents():
        """List all documents."""
        docs = kb.list_documents()

        # Format as markdown table
        table = "| Title | Type | Updated | Chunks |\n"
        table += "|-------|------|---------|--------|\n"
        for doc in docs:
            table += f"| {doc.title} | {doc.type} | {doc.updated} | {doc.chunks} |\n"

        return table

    with gr.Blocks() as kb_interface:
        gr.Markdown("# 📚 Knowledge Base Manager")

        with gr.Tab("Upload Documents"):
            file_input = gr.File(
                label="Upload Documents",
                file_count="multiple",
                file_types=[".pdf", ".md", ".txt", ".docx"]
            )
            upload_btn = gr.Button("Upload", variant="primary")
            upload_output = gr.Textbox(label="Upload Results", lines=5)

            upload_btn.click(
                fn=upload_documents,
                inputs=[file_input],
                outputs=[upload_output]
            )

        with gr.Tab("Current Documents"):
            refresh_btn = gr.Button("Refresh")
            docs_table = gr.Markdown()

            refresh_btn.click(
                fn=list_documents,
                inputs=[],
                outputs=[docs_table]
            )

            # Load on startup
            kb_interface.load(
                fn=list_documents,
                inputs=[],
                outputs=[docs_table]
            )

    return kb_interface


def create_analytics_dashboard():
    """Analytics and metrics dashboard."""
    import plotly.graph_objects as go

    def get_metrics():
        """Get current metrics."""
        metrics = analytics.get_today_metrics()

        return (
            f"**{metrics['total_queries']:,}**",
            f"**{metrics['auto_resolved']:,}** ({metrics['auto_resolve_rate']:.1f}%)",
            f"**{metrics['escalated']:,}** ({metrics['escalation_rate']:.1f}%)",
            f"**{metrics['avg_response_time']:.2f}s**"
        )

    def get_chart_data():
        """Get chart data."""
        data = analytics.get_7day_data()

        # Create plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['queries'],
            name='Total Queries',
            line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=data['dates'],
            y=data['auto_resolved'],
            name='Auto-Resolved',
            line=dict(color='green')
        ))

        fig.update_layout(
            title="Queries Over Time (7 Days)",
            xaxis_title="Date",
            yaxis_title="Count",
            hovermode='x unified'
        )

        return fig

    with gr.Blocks() as analytics_interface:
        gr.Markdown("# 📊 Analytics Dashboard")

        with gr.Row():
            metric1 = gr.Markdown("Loading...")
            metric2 = gr.Markdown("Loading...")
            metric3 = gr.Markdown("Loading...")
            metric4 = gr.Markdown("Loading...")

        gr.Markdown("## Queries Over Time")
        chart = gr.Plot()

        refresh_btn = gr.Button("Refresh Data")

        def update_dashboard():
            metrics = get_metrics()
            chart_data = get_chart_data()
            return (*metrics, chart_data)

        refresh_btn.click(
            fn=update_dashboard,
            inputs=[],
            outputs=[metric1, metric2, metric3, metric4, chart]
        )

        # Auto-refresh every 30 seconds
        analytics_interface.load(
            fn=update_dashboard,
            inputs=[],
            outputs=[metric1, metric2, metric3, metric4, chart]
        )

    return analytics_interface


def create_settings_panel():
    """Settings and configuration."""

    def save_settings(api_key, model, temperature, max_tokens):
        """Save configuration."""
        config.update({
            'anthropic_api_key': api_key,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens
        })
        return "✅ Settings saved successfully"

    with gr.Blocks() as settings_interface:
        gr.Markdown("# ⚙️ Settings")

        api_key = gr.Textbox(
            label="Anthropic API Key",
            type="password",
            value=config.get('anthropic_api_key', '')
        )

        model = gr.Dropdown(
            label="Model",
            choices=[
                "claude-sonnet-4-5-20250929",
                "claude-opus-4-6-20250929",
                "claude-haiku-4-5-20251001"
            ],
            value=config.get('model', 'claude-sonnet-4-5-20250929')
        )

        temperature = gr.Slider(
            label="Temperature",
            minimum=0,
            maximum=1,
            step=0.1,
            value=config.get('temperature', 0.3)
        )

        max_tokens = gr.Slider(
            label="Max Tokens",
            minimum=256,
            maximum=8192,
            step=256,
            value=config.get('max_tokens', 4096)
        )

        save_btn = gr.Button("Save Settings", variant="primary")
        status = gr.Textbox(label="Status")

        save_btn.click(
            fn=save_settings,
            inputs=[api_key, model, temperature, max_tokens],
            outputs=[status]
        )

    return settings_interface


# ============================================================================
# MAIN APP
# ============================================================================

def create_app():
    """Create main Gradio application."""

    # Custom CSS
    custom_css = """
    .gradio-container {
        font-family: 'Inter', sans-serif;
    }
    .chat-message {
        border-radius: 8px;
        padding: 12px;
    }
    """

    # Custom theme
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="slate"
    )

    with gr.Blocks(
        title="SupportGPT",
        theme=theme,
        css=custom_css
    ) as app:

        gr.Markdown(
            """
            # 🤖 SupportGPT
            ### AI-Powered Support Chatbot with RAG
            """
        )

        with gr.Tabs():
            with gr.Tab("💬 Chat"):
                create_chat_interface()

            with gr.Tab("📚 Knowledge Base"):
                create_kb_manager()

            with gr.Tab("📊 Analytics"):
                create_analytics_dashboard()

            with gr.Tab("⚙️ Settings"):
                create_settings_panel()

        gr.Markdown(
            """
            ---
            Built with ❤️ using LangChain + LangGraph + Claude
            """
        )

    return app


# ============================================================================
# LAUNCH
# ============================================================================

if __name__ == "__main__":
    app = create_app()

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set True for public link
        show_error=True,
        show_api=True  # Auto-generate API docs
    )
```

---

## 🔒 SEGURIDAD Y COMPLIANCE

### Mejores Prácticas de Seguridad (Basado en investigación 2026)

#### 1. Autenticación y Autorización

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token generation
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 2. Input Validation y Sanitization

```python
from pydantic import BaseModel, Field, validator
import bleach

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=5000, min_length=1)
    user_id: str = Field(..., regex=r'^[a-zA-Z0-9_-]+$')

    @validator('message')
    def sanitize_message(cls, v):
        # Remove HTML/scripts
        return bleach.clean(v, strip=True)

    @validator('message')
    def detect_injection(cls, v):
        # Detect prompt injection attempts
        dangerous_patterns = [
            'ignore previous instructions',
            'system:',
            'override',
            'jailbreak'
        ]
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError("Potential injection detected")
        return v
```

#### 3. Data Privacy (GDPR/CCPA Compliance)

```python
class PrivacyManager:
    """Manage user data privacy."""

    @staticmethod
    def anonymize_pii(text: str) -> str:
        """Remove PII from text."""
        import re

        # Email
        text = re.sub(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            '[EMAIL]',
            text
        )

        # Phone
        text = re.sub(
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            '[PHONE]',
            text
        )

        # SSN
        text = re.sub(
            r'\b\d{3}-\d{2}-\d{4}\b',
            '[SSN]',
            text
        )

        return text

    @staticmethod
    def delete_user_data(user_id: str):
        """GDPR right to be forgotten."""
        # Delete from all tables
        db.query(Messages).filter(Messages.user_id == user_id).delete()
        db.query(ChatSessions).filter(ChatSessions.user_id == user_id).delete()
        # ... delete from all tables
        db.commit()
```

#### 4. Audit Logging

```python
class AuditLogger:
    """Security audit logging."""

    @staticmethod
    def log_access(
        user_id: str,
        action: str,
        resource: str,
        result: str
    ):
        """Log security-relevant events."""
        logger.info(
            "security_audit",
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            timestamp=datetime.utcnow().isoformat(),
            ip_address=request.client.host
        )
```

#### 5. RAG Security (Basado en investigación)

```python
class SecureRAG:
    """Secure RAG with access controls."""

    def retrieve_with_acl(
        self,
        query: str,
        user_id: str,
        user_permissions: list[str]
    ):
        """Retrieve only documents user has access to."""

        # Filter by user permissions
        filter_dict = {
            "$or": [
                {"public": True},
                {"allowed_users": {"$contains": user_id}},
                {"required_permission": {"$in": user_permissions}}
            ]
        }

        results = self.vectorstore.similarity_search(
            query,
            k=5,
            filter=filter_dict
        )

        # Audit log
        AuditLogger.log_access(
            user_id=user_id,
            action="document_retrieval",
            resource=f"query:{query}",
            result=f"retrieved:{len(results)}"
        )

        return results
```

#### 6. LLM Output Guardrails

```python
class OutputGuardrails:
    """Ensure LLM outputs are safe."""

    @staticmethod
    def check_output(text: str) -> tuple[bool, str]:
        """Check if output is safe to send."""

        # Check for hallucinated information
        if not has_citations(text):
            return False, "No sources cited"

        # Check for inappropriate content
        if contains_inappropriate_content(text):
            return False, "Inappropriate content detected"

        # Check for PII leakage
        if contains_pii(text):
            return False, "PII detected in output"

        return True, "OK"
```

---

## 📈 MONITOREO Y OBSERVABILIDAD

### Métricas Críticas (Prometheus)

```python
# Define metrics
from prometheus_client import Counter, Histogram, Gauge, Summary

# Request metrics
requests_total = Counter(
    'supportgpt_requests_total',
    'Total requests',
    ['endpoint', 'method', 'status']
)

request_duration = Histogram(
    'supportgpt_request_duration_seconds',
    'Request duration',
    ['endpoint']
)

# LLM metrics
llm_calls_total = Counter(
    'supportgpt_llm_calls_total',
    'Total LLM API calls',
    ['model', 'status']
)

llm_tokens_used = Counter(
    'supportgpt_llm_tokens_total',
    'Total tokens used',
    ['model', 'type']  # type: input, output
)

llm_latency = Histogram(
    'supportgpt_llm_latency_seconds',
    'LLM API latency'
)

# RAG metrics
rag_retrievals = Counter(
    'supportgpt_rag_retrievals_total',
    'Total RAG retrievals'
)

rag_relevance_score = Histogram(
    'supportgpt_rag_relevance_score',
    'RAG relevance scores'
)

# Business metrics
queries_auto_resolved = Counter(
    'supportgpt_queries_auto_resolved_total',
    'Queries resolved without escalation'
)

queries_escalated = Counter(
    'supportgpt_queries_escalated_total',
    'Queries escalated to human',
    ['reason']
)

user_satisfaction = Histogram(
    'supportgpt_user_satisfaction',
    'User satisfaction ratings'
)

# System metrics
active_sessions = Gauge(
    'supportgpt_active_sessions',
    'Number of active chat sessions'
)

database_connections = Gauge(
    'supportgpt_database_connections',
    'Active database connections'
)
```

### Grafana Dashboards

**Dashboard 1: Overview**
```yaml
panels:
  - title: "Request Rate"
    query: rate(supportgpt_requests_total[5m])

  - title: "Error Rate"
    query: rate(supportgpt_requests_total{status=~"5.."}[5m])

  - title: "Latency (p95)"
    query: histogram_quantile(0.95, supportgpt_request_duration_seconds)

  - title: "Auto-Resolution Rate"
    query: |
      supportgpt_queries_auto_resolved_total /
      (supportgpt_queries_auto_resolved_total + supportgpt_queries_escalated_total)
```

**Dashboard 2: LLM Performance**
```yaml
panels:
  - title: "LLM Calls/min"
    query: rate(supportgpt_llm_calls_total[1m])

  - title: "Token Usage"
    query: rate(supportgpt_llm_tokens_total[5m])

  - title: "LLM Latency"
    query: histogram_quantile(0.95, supportgpt_llm_latency_seconds)

  - title: "LLM Cost Estimate"
    query: |
      (rate(supportgpt_llm_tokens_total{type="input"}[1h]) * 0.003 / 1000) +
      (rate(supportgpt_llm_tokens_total{type="output"}[1h]) * 0.015 / 1000)
```

### Alerting Rules

```yaml
groups:
  - name: supportgpt_alerts
    interval: 1m
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(supportgpt_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"

      # Slow responses
      - alert: SlowResponses
        expr: histogram_quantile(0.95, supportgpt_request_duration_seconds) > 10
        for: 5m
        annotations:
          summary: "95th percentile latency > 10s"

      # High escalation rate
      - alert: HighEscalationRate
        expr: |
          rate(supportgpt_queries_escalated_total[1h]) /
          rate(supportgpt_requests_total[1h]) > 0.4
        for: 30m
        annotations:
          summary: "Escalation rate > 40%"

      # Database connection pool exhausted
      - alert: DatabaseConnectionPoolExhausted
        expr: supportgpt_database_connections > 45
        for: 5m
        annotations:
          summary: "Database connection pool nearly exhausted"
```

---

## 🧪 TESTING

### Test Strategy

```
Unit Tests (70%)
  ├── Test individual functions
  ├── Mock external dependencies
  └── Fast execution (<1s each)

Integration Tests (20%)
  ├── Test component interactions
  ├── Real database (test instance)
  └── Medium execution (<10s each)

E2E Tests (10%)
  ├── Test complete workflows
  ├── Real services
  └── Slow execution (<60s each)
```

### Unit Tests Example

```python
# tests/unit/test_rag.py
import pytest
from src.rag.retrieval import KnowledgeBase
from unittest.mock import Mock, patch

@pytest.fixture
def mock_vectorstore():
    """Mock vector store."""
    with patch('src.rag.retrieval.Chroma') as mock:
        yield mock

def test_search_knowledge_base(mock_vectorstore):
    """Test semantic search."""
    # Arrange
    kb = KnowledgeBase()
    mock_vectorstore.return_value.similarity_search.return_value = [
        Mock(page_content="How to reset password", metadata={"source": "faq.md"})
    ]

    # Act
    results = kb.search("reset password", k=5)

    # Assert
    assert len(results) > 0
    assert "password" in results[0].page_content.lower()

def test_search_with_filters():
    """Test search with metadata filters."""
    kb = KnowledgeBase()

    results = kb.search(
        "billing question",
        k=5,
        filter={"category": "billing"}
    )

    assert all(r.metadata.get("category") == "billing" for r in results)
```

### Integration Tests

```python
# tests/integration/test_agent.py
import pytest
from src.core.agent import SupportAgent
from src.db.session import get_test_db

@pytest.fixture
def test_db():
    """Test database fixture."""
    db = get_test_db()
    yield db
    db.rollback()

@pytest.mark.asyncio
async def test_complete_workflow(test_db):
    """Test complete chat workflow."""
    agent = SupportAgent()

    # User asks question
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "How do I reset my password?"}]
    })

    # Assert
    assert response["confidence"] > 0.7
    assert "password" in response["message"].lower()
    assert len(response["sources"]) > 0
    assert not response["escalated"]

@pytest.mark.asyncio
async def test_escalation_workflow(test_db):
    """Test that unknown queries escalate."""
    agent = SupportAgent()

    # User asks something not in knowledge base
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "What is the meaning of life?"}]
    })

    # Assert
    assert response["escalated"] == True
    assert response["ticket_id"] is not None
```

### E2E Tests

```python
# tests/e2e/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_chat_endpoint_e2e():
    """Test complete chat flow via API."""
    # Get API key
    response = client.post("/v1/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    token = response.json()["access_token"]

    # Send chat message
    response = client.post(
        "/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "How do I reset my password?",
            "user_id": "test_user"
        }
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["confidence"] > 0.5

def test_upload_and_query_e2e():
    """Test uploading doc and querying it."""
    token = get_test_token()

    # Upload document
    with open("tests/fixtures/faq.md", "rb") as f:
        response = client.post(
            "/v1/kb/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": f}
        )
    assert response.status_code == 200

    # Wait for indexing
    import time
    time.sleep(2)

    # Query
    response = client.post(
        "/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Question from the FAQ", "user_id": "test"}
    )

    # Should find it
    data = response.json()
    assert len(data["sources"]) > 0
```

### Performance Tests (Locust)

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class SupportGPTUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login once."""
        response = self.client.post("/v1/auth/login", json={
            "email": "load_test@example.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def chat_common_question(self):
        """Simulate common questions (70% of traffic)."""
        self.client.post(
            "/v1/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "message": "How do I reset my password?",
                "user_id": f"user_{self.user_id}"
            }
        )

    @task(1)
    def chat_complex_question(self):
        """Simulate complex questions (30% of traffic)."""
        self.client.post(
            "/v1/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "message": "Can you explain the difference between X and Y?",
                "user_id": f"user_{self.user_id}"
            }
        )
```

Run: `locust -f tests/performance/locustfile.py --host=http://localhost:8000`

---

## 🚀 DEPLOYMENT

### Docker Setup

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports
EXPOSE 8000 7860

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Local Development)

```yaml
# docker/docker-compose.yml
version: '3.8'

services:
  # Main application
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
      - "7860:7860"
    environment:
      - DATABASE_URL=postgresql://supportgpt:password@postgres:5432/supportgpt
      - REDIS_URL=redis://redis:6379/0
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ../src:/app/src
      - chroma_data:/app/data/vector_db
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # PostgreSQL
  postgres:
    image: postgres:16
    environment:
      - POSTGRES_USER=supportgpt
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=supportgpt
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  chroma_data:
  prometheus_data:
  grafana_data:
```

### Railway Deployment

```toml
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "docker/Dockerfile"

[deploy]
startCommand = "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[deploy.environmentVariables]]
name = "DATABASE_URL"
value = "${{Postgres.DATABASE_URL}}"

[[deploy.environmentVariables]]
name = "REDIS_URL"
value = "${{Redis.REDIS_URL}}"
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run linters
        run: |
          uv run ruff check src/
          uv run black --check src/

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: |
          uv run pytest tests/ -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t supportgpt:${{ github.sha }} -f docker/Dockerfile .

      - name: Push to Registry
        run: |
          # Push to your container registry
          echo "Pushing image..."

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Deploy to Railway
        run: |
          # Deploy using Railway CLI or API
          echo "Deploying..."
```

---

## 📅 ROADMAP DE IMPLEMENTACIÓN

### Semana 1: Setup + Core RAG

**Días 1-2: Proyecto Base**
- [ ] Crear estructura de carpetas
- [ ] Setup pyproject.toml con todas las dependencias
- [ ] Configurar variables de entorno
- [ ] Setup PostgreSQL + Redis con Docker Compose
- [ ] Crear modelos de base de datos (SQLAlchemy)
- [ ] Setup logging estructurado

**Días 3-4: Document Processing + RAG**
- [ ] Implementar `DocumentProcessor`
- [ ] Setup ChromaDB
- [ ] Implementar embeddings (OpenAI)
- [ ] Crear pipeline de indexación
- [ ] Implementar semantic search
- [ ] Tests unitarios de RAG

**Días 5-7: Retrieval Strategies**
- [ ] Multi-query retrieval
- [ ] Hybrid search (semantic + keyword)
- [ ] Re-ranking
- [ ] Tests de retrieval quality

---

### Semana 2: Agent + LangGraph

**Días 1-3: LangChain Base**
- [ ] Setup ChatAnthropic
- [ ] Crear prompt templates
- [ ] Implementar memory (ConversationBuffer)
- [ ] Crear tools básicas (search_docs, create_ticket)
- [ ] Tests de LangChain components

**Días 4-7: LangGraph Workflow**
- [ ] Definir `SupportState`
- [ ] Implementar nodos (classify, search, generate, evaluate)
- [ ] Implementar conditional edges
- [ ] Setup checkpointing con PostgreSQL
- [ ] Implementar human-in-the-loop
- [ ] Tests end-to-end del agent

---

### Semana 3: API + GUI

**Días 1-3: FastAPI**
- [ ] Setup FastAPI app
- [ ] Implementar endpoints (/chat, /kb, /analytics)
- [ ] Implementar autenticación (JWT)
- [ ] Implementar rate limiting
- [ ] Implementar caching (Redis)
- [ ] API tests

**Días 4-7: Gradio GUI**
- [ ] Create chat interface
- [ ] Create KB manager
- [ ] Create analytics dashboard
- [ ] Create settings panel
- [ ] Connect GUI to FastAPI
- [ ] UI/UX tests

---

### Semana 4: MLOps + Production

**Días 1-2: Monitoring**
- [ ] Setup Prometheus metrics
- [ ] Setup Grafana dashboards
- [ ] Implement structured logging
- [ ] Setup alerting rules

**Días 3-4: Security**
- [ ] Implement input validation
- [ ] Add PII detection
- [ ] Setup audit logging
- [ ] Security testing

**Días 5-7: Deployment**
- [ ] Create Dockerfile optimizado
- [ ] Setup CI/CD pipeline
- [ ] Deploy to Railway
- [ ] Performance testing
- [ ] Documentation final

---

## 🎯 MÉTRICAS DE ÉXITO

### KPIs Técnicos

| Métrica | Target | Medición |
|---------|--------|----------|
| **Latencia p95** | <5s | Prometheus |
| **Uptime** | >99.5% | Health checks |
| **Error rate** | <1% | Logs + metrics |
| **Test coverage** | >80% | pytest-cov |

### KPIs de Producto

| Métrica | Target | Medición |
|---------|--------|----------|
| **Auto-resolution rate** | >70% | Analytics |
| **Confidence score** | >0.8 | Agent output |
| **User satisfaction** | >4.5/5 | Feedback |
| **Time to first response** | <3s | Latency metrics |

### KPIs de Negocio

| Métrica | Target | Medición |
|---------|--------|----------|
| **Tickets reducidos** | 70% | Comparar antes/después |
| **Cost savings** | $2k+/mes | vs humano |
| **Customer satisfaction** | +20% | Surveys |

---

## 📚 REFERENCIAS Y RECURSOS

### Documentación Oficial

- [Anthropic Claude API](https://docs.anthropic.com/)
- [LangChain Python](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [Gradio Docs](https://www.gradio.app/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)

### Mejores Prácticas (Investigación 2026)

- [Chatbot Architecture Best Practices](https://research.aimultiple.com/chatbot-architecture/)
- [Production RAG Systems Guide](https://brlikhon.engineer/blog/building-production-rag-systems-in-2026-complete-architecture-guide)
- [RAG Security Best Practices](https://aws.amazon.com/blogs/security/hardening-the-rag-chatbot-architecture-powered-by-amazon-bedrock-blueprint-for-secure-design-and-anti-pattern-migration/)
- [AI Chatbot Best Practices 2026](https://gettalkative.com/info/chatbot-best-practices)
- [Gradio vs Streamlit Comparison](https://www.squadbase.dev/en/blog/streamlit-vs-gradio-in-2025-a-framework-comparison-for-ai-apps)

---

## ✅ CHECKLIST FINAL

Antes de considerar el proyecto completo:

### Funcionalidad
- [ ] Chat responde correctamente
- [ ] RAG busca docs relevantes
- [ ] Escalamiento funciona
- [ ] Multi-idioma funciona
- [ ] GUI completa y usable

### Calidad
- [ ] Tests >80% coverage
- [ ] No errores en linters
- [ ] Documentación completa
- [ ] Code review aprobado

### Performance
- [ ] Latencia <5s
- [ ] Maneja 100 concurrent users
- [ ] No memory leaks
- [ ] Costos optimizados

### Seguridad
- [ ] Auth implementado
- [ ] Input validation completa
- [ ] PII protection
- [ ] Audit logging funciona

### Deployment
- [ ] Docker funciona
- [ ] CI/CD configurado
- [ ] Monitoring activo
- [ ] Alertas configuradas

---

## 🎬 CONCLUSIÓN

Este documento contiene **TODAS** las especificaciones necesarias para construir SupportGPT desde cero. Incluye:

✅ Arquitectura completa de 5 fases
✅ Stack tecnológico justificado
✅ Funcionalidades detalladas
✅ Código de ejemplo
✅ Estructura del proyecto
✅ Modelos de datos
✅ APIs completas
✅ GUI en Python (Gradio)
✅ Seguridad y compliance
✅ Monitoring
✅ Testing
✅ Deployment
✅ Roadmap de 4 semanas

**Próximo paso:** Iniciar nueva sesión de Claude Code con este documento y comenzar la implementación.

---

**Documento creado:** 2026-02-25
**Versión:** 1.0
**Estado:** Listo para implementación ✅
**Investigación:** Basado en mejores prácticas 2026

---

**Sources:**
- [Chatbot Architecture 2026](https://research.aimultiple.com/chatbot-architecture/)
- [Production RAG Systems](https://brlikhon.engineer/blog/building-production-rag-systems-in-2026-complete-architecture-guide)
- [RAG Security Guide](https://aws.amazon.com/blogs/security/hardening-the-rag-chatbot-architecture-powered-by-amazon-bedrock-blueprint-for-secure-design-and-anti-pattern-migration/)
- [Chatbot Best Practices](https://gettalkative.com/info/chatbot-best-practices)
- [Gradio Framework Guide](https://www.squadbase.dev/en/blog/streamlit-vs-gradio-in-2025-a-framework-comparison-for-ai-apps)
