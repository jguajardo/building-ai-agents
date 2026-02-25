# Proyecto: Agente Básico de IA

> **Objetivo:** Aprender a construir agentes de IA desde cero, entendiendo los fundamentos y progresando hacia frameworks avanzados. Proyecto de aprendizaje para convertirse en Ingeniero de IA.

---

## 📂 Estructura del Proyecto

El proyecto está organizado en **fases incrementales** para mantener el historial completo de aprendizaje:

```
agente-basico/
├── fase-1-fundamentos/     ✅ COMPLETADO
│   ├── README.md           → Guía de la fase
│   ├── 01_basico.py
│   ├── 02_con_tools.py
│   ├── 03_agente_loop.py
│   └── 04_agente_completo.py
│
├── fase-2-langgraph/       🎯 EN PROGRESO
│   └── README.md           → Qué aprenderemos
│
├── fase-3-langchain/       📅 PRÓXIMAMENTE
│   └── README.md
│
├── fase-4-rag/             📅 PRÓXIMAMENTE
│   └── README.md
│
├── fase-5-produccion/      📅 PRÓXIMAMENTE
│   └── README.md
│
├── README.md               ← Estás aquí (guía general)
├── CLAUDE.md               ← Instrucciones para Claude Code
├── pyproject.toml
└── .gitignore
```

**Cada fase tiene:**
- ✅ Su propio README con conceptos y recursos
- 📝 Ejemplos progresivos (01_, 02_, 03_...)
- 🎓 Lecciones aprendidas documentadas
- 🔗 Enlaces a documentación oficial

---

## 📋 Estado del Proyecto

| Fase | Estado | Archivos | Conceptos Clave |
|------|--------|----------|-----------------|
| **1. Fundamentos** | ✅ Completado | 4 | SDK Claude, Tools, Agentic Loop |
| **2. LangGraph** | 🎯 En progreso | 0/6 | StateGraph, Checkpointing, Grafos |
| **3. LangChain** | 📅 Pendiente | 0/6 | LCEL, Chains, Interoperabilidad |
| **4. RAG** | 📅 Pendiente | 0/6 | Embeddings, Vector DB, Retrieval |
| **5. Producción** | 📅 Pendiente | 0/8 | FastAPI, Docker, Deploy, MLOps |

### 🎯 Próximo Milestone
**Fase 2: LangGraph** - Construir agentes con grafos de estado para mejor control y visualización.

---

## 🚀 Inicio Rápido

### Setup Inicial
```bash
# Clonar o crear el proyecto
cd agente-basico

# Instalar dependencias
uv sync

# Configurar API key
export ANTHROPIC_API_KEY="tu-api-key"
```

### Ejecutar Fase 1 (Fundamentos)
```bash
uv run python fase-1-fundamentos/01_basico.py
uv run python fase-1-fundamentos/02_con_tools.py
uv run python fase-1-fundamentos/03_agente_loop.py
uv run python fase-1-fundamentos/04_agente_completo.py
```

### Ver Guía de Cada Fase
```bash
# Leer la guía completa de la fase actual
cat fase-1-fundamentos/README.md
cat fase-2-langgraph/README.md
# etc...
```

---

## 📚 Conceptos Aprendidos

### 1. Fundamentos de Agentes de IA

#### ¿Qué es un Agente?
Un agente de IA es un sistema que puede:
- **Percibir**: Recibir información del entorno (mensajes del usuario, APIs, bases de datos)
- **Razonar**: Usar un LLM para decidir qué hacer
- **Actuar**: Ejecutar acciones (llamar herramientas, APIs, escribir código)
- **Aprender**: Mantener contexto y memoria de interacciones previas

#### El Agentic Loop
```
┌─────────────────────────────────┐
│      Usuario pregunta           │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   LLM procesa el mensaje         │◄──────┐
└──────────────┬──────────────────┘       │
               │                           │
          ¿Necesita tool?                  │
           /          \                    │
         Sí            No                  │
         │              │                  │
         ▼              ▼                  │
  ┌────────────┐ ┌──────────┐             │
  │ Ejecutar   │ │ Responder│             │
  │ herramienta│ │ al usuario│            │
  └─────┬──────┘ └──────────┘             │
        │                                  │
        │  Devolver resultado              │
        └──────────────────────────────────┘
```

### 2. Tool Calling (Function Calling)

Las herramientas le dan "superpoderes" al LLM:
- El LLM **NO ejecuta** las herramientas, solo **decide** cuándo y cómo usarlas
- Defines herramientas con JSON Schema
- El LLM responde con `tool_use` cuando necesita una herramienta
- Ejecutas la herramienta y devuelves el resultado
- El LLM procesa el resultado y continúa

**Ejemplo de definición de herramienta:**
```python
{
    "name": "buscar_web",
    "description": "Busca información en internet",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Término de búsqueda"
            }
        },
        "required": ["query"]
    }
}
```

### 3. Memoria y Contexto

Un agente mantiene memoria pasando **todo el historial de mensajes** en cada llamada:
```python
messages = [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte?"},
    {"role": "user", "content": "¿Recuerdas lo que dijimos antes?"},
    # ^ Claude puede "recordar" porque tiene todo el historial
]
```

Tipos de memoria:
- **Memoria de corto plazo**: Contexto de la conversación actual
- **Memoria de largo plazo**: Base de datos, vector stores, archivos
- **Memoria de trabajo**: Estado temporal del agente

---

## 🛠️ Stack Tecnológico para Ingeniero de IA

### 🔤 Lenguajes de Programación

| Lenguaje | Uso | Prioridad |
|----------|-----|-----------|
| **Python** | LLM apps, ML, data science | 🔴 CRÍTICO |
| **JavaScript/TypeScript** | Apps web, serverless | 🟡 IMPORTANTE |
| **SQL** | Bases de datos, análisis de datos | 🟡 IMPORTANTE |
| **Go** | Servicios de alto rendimiento | 🟢 OPCIONAL |

### 🤖 Frameworks de LLM

#### Nivel 1: SDKs Nativos
- **Anthropic SDK** (Claude) ✅ - *Ya dominado*
- **OpenAI SDK** (GPT, o1)
- **Google AI SDK** (Gemini)
- **Mistral SDK**

#### Nivel 2: Orquestación
- **LangChain** 🎯 - *Próximo objetivo*
  - Chains, Agents, LCEL
  - Integraciones con 100+ servicios
  - RAG, document loaders
- **LangGraph** 🎯 - *Próximo objetivo*
  - Agentes con grafos de estado
  - Control fino sobre el flujo
  - Checkpointing, human-in-the-loop

#### Nivel 3: Frameworks Especializados
- **LlamaIndex** - RAG y document indexing
- **Haystack** - Pipelines de NLP
- **AutoGen** - Multi-agent systems
- **CrewAI** - Agentes colaborativos

### 🗄️ Bases de Datos y Storage

#### Vector Databases (para RAG)
- **Pinecone** - Managed, fácil de usar
- **Weaviate** - Open source, escalable
- **ChromaDB** - Lightweight, ideal para desarrollo
- **Qdrant** - Rust, muy rápido
- **pgvector** - Extensión de PostgreSQL

#### Bases de Datos Tradicionales
- **PostgreSQL** - Relacional, robusta
- **MongoDB** - NoSQL, documentos
- **Redis** - Cache, colas, pub/sub
- **SQLite** - Desarrollo local

### 🔧 Herramientas de Desarrollo

#### Testing
- **pytest** - Testing framework
- **unittest** - Librería estándar
- **responses** - Mock HTTP requests
- **pytest-asyncio** - Testing async

#### CI/CD
- **GitHub Actions** - CI/CD integrado con GitHub
- **GitLab CI** - CI/CD de GitLab
- **CircleCI** - CI/CD como servicio

#### Gestión de Dependencias
- **uv** ✅ - *Usando actualmente* (más rápido que pip)
- **poetry** - Gestión de dependencias y empaquetado
- **pip-tools** - pip + requirements.txt mejorado

### ☁️ MLOps y Deployment

#### Plataformas de Deploy
- **AWS**
  - Lambda (serverless)
  - ECS/EKS (containers)
  - SageMaker (ML)
  - Bedrock (LLMs managed)
- **Google Cloud**
  - Cloud Run (containers)
  - Vertex AI (ML)
  - Cloud Functions (serverless)
- **Azure**
  - Functions (serverless)
  - AKS (Kubernetes)
  - OpenAI Service

#### Containerización
- **Docker** - Contenedores
- **Docker Compose** - Multi-container
- **Kubernetes** - Orquestación (avanzado)

#### Monitoreo y Observabilidad
- **LangSmith** - Debug LangChain apps
- **Weights & Biases** - Experimentos ML
- **Prometheus + Grafana** - Métricas
- **Sentry** - Error tracking
- **DataDog** - APM full-stack

### 📊 MLOps: Ciclo de Vida Completo

```
1. Experimentación          2. Training               3. Deployment
   ├─ Jupyter Notebooks        ├─ Scripts Python         ├─ FastAPI/Flask
   ├─ Data exploration         ├─ Training loops         ├─ Docker
   └─ Prototipos               ├─ Hyperparameter tuning  └─ Cloud providers
                               └─ Model versioning

4. Monitoreo                5. Reentrenamiento        6. Governance
   ├─ Métricas de uso          ├─ Detección de drift     ├─ Model registry
   ├─ Performance              ├─ Pipelines automáticos  ├─ Versionado
   └─ Alertas                  └─ A/B testing            └─ Compliance
```

#### Herramientas MLOps
- **MLflow** - Tracking, projects, models
- **DVC** - Version control para datos
- **Kubeflow** - ML en Kubernetes
- **Feast** - Feature store
- **Great Expectations** - Data quality

### 🎨 Interfaces y Aplicaciones

#### Web Frameworks
- **FastAPI** - APIs REST modernas, async
- **Flask** - Lightweight, flexible
- **Streamlit** - Dashboards rápidos
- **Gradio** - Demos de ML

#### Frontend (opcional pero útil)
- **React** + **Next.js** - Apps web modernas
- **Vue.js** - Alternativa a React
- **Tailwind CSS** - Estilos rápidos

### 🔐 Seguridad y Autenticación

- **OAuth 2.0** - Estándar de autenticación
- **JWT** - Tokens de autenticación
- **Auth0** - Servicio de autenticación managed
- **Secrets management**: AWS Secrets Manager, HashiCorp Vault

---

## 📖 Estándares y Mejores Prácticas

### 1. Estructura de Proyectos

```
proyecto/
├── src/
│   ├── __init__.py
│   ├── agents/          # Lógica de agentes
│   ├── tools/           # Herramientas/funciones
│   ├── prompts/         # Prompts reutilizables
│   ├── utils/           # Utilidades
│   └── config.py        # Configuración
├── tests/               # Tests unitarios
├── data/                # Datos de entrenamiento/ejemplo
├── notebooks/           # Jupyter notebooks
├── docs/                # Documentación
├── .env.example         # Variables de entorno (ejemplo)
├── .gitignore
├── pyproject.toml       # Dependencias (uv/poetry)
├── Dockerfile
└── README.md
```

### 2. Prompt Engineering

#### Técnicas esenciales:
- **System Prompts**: Define el rol y comportamiento del agente
- **Few-shot learning**: Ejemplos en el prompt
- **Chain-of-Thought (CoT)**: "Piensa paso a paso"
- **ReAct**: Reasoning + Acting (alternando razonamiento y acciones)
- **Tree of Thoughts**: Explorar múltiples razonamientos

#### Mejores prácticas:
- Sé específico y claro
- Da ejemplos
- Define el formato de salida esperado
- Usa delimitadores (```, ---, etc.)
- Itera y mejora basándote en resultados

### 3. Manejo de Errores y Reintentos

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def llamar_llm(mensaje):
    # Tu código aquí
    pass
```

### 4. Logging y Debugging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Agente iniciado")
logger.error("Error al procesar", exc_info=True)
```

### 5. Testing de LLMs

```python
import pytest

def test_herramienta_calculadora():
    resultado = ejecutar_tool("calculadora", {"expresion": "2 + 2"})
    assert resultado == {"resultado": 4}

# Testing con mocks
from unittest.mock import patch

@patch('anthropic.Anthropic.messages.create')
def test_agente_responde(mock_create):
    mock_create.return_value = MockResponse(...)
    respuesta = agente.procesar("Hola")
    assert "hola" in respuesta.lower()
```

---

## 🎓 Roadmap de Aprendizaje

### Fase 1: Fundamentos (1-2 meses) ✅
- [x] Python intermedio-avanzado
- [x] SDKs nativos de LLMs (Claude, OpenAI)
- [x] Tool calling / function calling
- [x] Agentic loop
- [x] Prompt engineering básico

### Fase 2: Frameworks (2-3 meses) 🎯
- [ ] LangGraph (control fino de agentes)
- [ ] LangChain (orquestación)
- [ ] Vector databases
- [ ] RAG (Retrieval Augmented Generation)
- [ ] Streaming de respuestas

### Fase 3: Aplicaciones (2-3 meses)
- [ ] FastAPI para APIs de LLM
- [ ] Autenticación y seguridad
- [ ] Rate limiting y caching
- [ ] Monitoreo con LangSmith
- [ ] Deploy en cloud (AWS/GCP)

### Fase 4: MLOps (2-3 meses)
- [ ] Docker y containerización
- [ ] CI/CD para ML
- [ ] Monitoring y observability
- [ ] A/B testing de prompts
- [ ] Model versioning

### Fase 5: Especialización (Continuo)
- [ ] Multi-agent systems
- [ ] Fine-tuning de modelos
- [ ] Edge cases y robustez
- [ ] Costos y optimización
- [ ] Evaluación de agentes

---

## 🔗 Recursos de Aprendizaje

### Documentación Oficial
- [Anthropic Claude Docs](https://docs.anthropic.com/)
- [OpenAI Platform Docs](https://platform.openai.com/docs)
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)

### Cursos Recomendados
- **DeepLearning.AI**
  - Generative AI with LLMs
  - LangChain courses
  - Building Systems with ChatGPT API
- **Fast.ai** - Practical Deep Learning
- **Full Stack Deep Learning** - MLOps completo

### Libros
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "Machine Learning Engineering" - Andriy Burkov
- "Building LLM Apps" - Valentina Alto

### Comunidades
- Discord de LangChain
- r/LangChain (Reddit)
- r/MachineLearning
- Hugging Face forums
- Twitter: #AIEngineering

---

## 💼 Preparación para Búsqueda de Empleo

### Portfolio Sugerido

1. **Proyecto RAG Completo**
   - Vector database
   - Document chunking strategies
   - API REST
   - Deploy en cloud

2. **Multi-Agent System**
   - 3+ agentes especializados
   - Comunicación entre agentes
   - Orquestación con LangGraph

3. **Chatbot de Producción**
   - FastAPI + LangChain
   - Autenticación
   - Rate limiting
   - Logging y monitoring
   - Docker + CI/CD

4. **Fine-tuned Model**
   - Dataset curado
   - Fine-tuning process
   - Evaluación de métricas
   - Comparación con base model

### Skills Técnicos Clave para CV

**Nivel Experto:**
- Python, LangChain, LangGraph
- Tool calling, Agentic systems
- Prompt engineering
- FastAPI, REST APIs

**Nivel Intermedio:**
- Docker, CI/CD
- Vector databases
- PostgreSQL/MongoDB
- AWS/GCP básico

**Nivel Básico:**
- Fine-tuning
- Kubernetes
- React (frontend)
- MLflow, MLOps

### Tipos de Roles

1. **LLM Engineer / AI Engineer**
   - Construir aplicaciones con LLMs
   - Integrar modelos en productos
   - Focus: aplicaciones prácticas

2. **ML Engineer**
   - Training, fine-tuning, deployment
   - Pipelines de ML
   - Focus: infraestructura ML

3. **AI Solutions Architect**
   - Diseñar arquitecturas complejas
   - Multi-agent systems
   - Focus: diseño de sistemas

4. **Prompt Engineer**
   - Optimización de prompts
   - Evaluación de outputs
   - Focus: calidad de respuestas

---

## 🚧 Próximos TODOs

### Inmediato (Esta Semana)
- [ ] Crear `05_langgraph_basico.py` - Primer ejemplo con LangGraph
- [ ] Implementar StateGraph con 3 nodos
- [ ] Agregar checkpointing para memoria persistente
- [ ] Documentar diferencias entre SDK puro vs LangGraph

### Corto Plazo (2-3 Semanas)
- [ ] Crear `06_langgraph_avanzado.py` - Human-in-the-loop
- [ ] Implementar herramientas más complejas (web search, code execution)
- [ ] Agregar tests unitarios con pytest
- [ ] Migrar a LangChain SDK

### Medio Plazo (1-2 Meses)
- [ ] Proyecto RAG completo con vector database
- [ ] API con FastAPI + LangChain
- [ ] Docker + deploy en cloud
- [ ] Documentación completa de arquitectura

---

## 📝 Notas de Desarrollo

### Aprendizajes Clave
- **Tool calling es el corazón de los agentes**: Sin herramientas, un LLM es solo un chatbot.
- **El agentic loop es simple pero poderoso**: La complejidad viene de las herramientas y el razonamiento, no del loop.
- **Memoria = contexto**: Los LLMs no tienen memoria real, simulamos memoria pasando el historial.
- **Start simple, iterate**: Es mejor un agente simple que funciona que uno complejo que no.

### Errores Comunes Evitados
- ❌ Usar `eval()` en producción (inseguro)
- ❌ No manejar rate limits de APIs
- ❌ No validar inputs de usuario
- ❌ No tener timeouts en tool calls
- ❌ Hardcodear API keys (usar variables de entorno)

---

## 📞 Contacto y Colaboración

Este es un proyecto de aprendizaje abierto. Si tienes sugerencias, correcciones o quieres colaborar:

- Issues y PRs son bienvenidos
- Comparte tus propios proyectos de agentes
- Conectemos en LinkedIn/Twitter

---

## 📄 Licencia

MIT License - Siéntete libre de usar este código para aprender y construir.

---

**Última actualización:** 2026-02-25
**Versión:** 0.1.0
**Autor:** Jorge Guajardo (aprendiz de Ingeniero de IA)

---

> "El mejor momento para empezar fue ayer. El segundo mejor momento es ahora." 🚀
