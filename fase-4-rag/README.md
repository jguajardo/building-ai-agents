# Fase 4: RAG - Retrieval Augmented Generation

> **Objetivo:** Conectar agentes con bases de conocimiento usando embeddings y vector databases.

## 🎯 Estado: PENDIENTE

---

## 🤔 ¿Qué es RAG?

**Problema:** Los LLMs tienen conocimiento limitado (fecha de corte, datos privados, etc.)

**Solución RAG:**
1. Guarda documentos en una base de datos vectorial
2. Cuando llega una pregunta, busca documentos relevantes
3. Pasa los documentos al LLM como contexto
4. El LLM responde basándose en esos documentos

```
Pregunta Usuario
      ↓
Convertir a embedding (vector)
      ↓
Buscar docs similares en vector DB
      ↓
Pasar docs + pregunta al LLM
      ↓
Respuesta basada en tus datos
```

---

## 📚 Conceptos Clave

### 1. Embeddings
Convertir texto a vectores (arrays de números):
```python
"hola mundo" → [0.23, -0.45, 0.12, ..., 0.89]  # 1536 dimensiones
```

Textos similares → vectores similares

### 2. Vector Databases
Bases de datos optimizadas para buscar vectores similares:
- Pinecone (managed)
- ChromaDB (local)
- Weaviate (self-hosted)
- pgvector (PostgreSQL)

### 3. Chunking
Dividir documentos grandes en pedazos pequeños:
```
Documento de 10,000 palabras
  → 50 chunks de ~200 palabras
  → 50 embeddings
```

### 4. Similarity Search
Buscar los chunks más relevantes:
```python
query = "¿Cómo funciona el motor?"
results = vector_db.similarity_search(query, k=5)  # Top 5 chunks
```

---

## 📁 Archivos Planeados

### `01_embeddings_basico.py` - Entendiendo embeddings
- Crear embeddings con OpenAI/Anthropic
- Calcular similitud coseno
- Ver que textos similares → embeddings similares

### `02_chromadb_local.py` - Vector DB local
- Setup ChromaDB
- Insertar documentos
- Similarity search básico

### `03_document_loaders.py` - Cargar documentos
- Cargar PDFs, TXT, markdown
- Chunking strategies
- Metadata en chunks

### `04_rag_simple.py` - RAG básico
- Pipeline completo: load → chunk → embed → store
- Query → retrieve → LLM
- Responder sobre tus documentos

### `05_rag_con_agente.py` - Agente + RAG
- Agente que decide cuándo usar RAG
- Tool "buscar_documentos"
- Combinar RAG con otras herramientas

### `06_rag_avanzado.py` - Técnicas avanzadas
- Re-ranking de resultados
- Hybrid search (keyword + semantic)
- Parent document retrieval
- Multi-query retrieval

---

## 🗺️ Arquitectura RAG Típica

```
┌──────────────────────────────────────────────────────────┐
│                    INDEXING (una vez)                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Documentos  →  Chunking  →  Embeddings  →  Vector DB    │
│                                                           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                  RETRIEVAL (cada query)                   │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Pregunta  →  Embedding  →  Search Vector DB  →  Top K   │
│                                                           │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   GENERATION (cada query)                 │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Pregunta + Docs Retrieved  →  LLM  →  Respuesta         │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 🎓 Chunking Strategies

### 1. Fixed Size
Dividir cada N caracteres:
```python
chunk_size = 500
overlap = 50  # Overlap para no perder contexto
```

### 2. Semantic
Dividir por significado (párrafos, secciones):
```python
# Por párrafos
chunks = doc.split("\n\n")
```

### 3. Recursive
LangChain tiene RecursiveCharacterTextSplitter:
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

---

## 📊 Embeddings: Opciones

| Provider | Model | Dimensiones | Costo |
|----------|-------|-------------|-------|
| OpenAI | text-embedding-3-small | 1536 | $0.02/1M tokens |
| OpenAI | text-embedding-3-large | 3072 | $0.13/1M tokens |
| Anthropic | (usa Voyage AI) | 1024 | $0.10/1M tokens |
| Cohere | embed-english-v3.0 | 1024 | Gratis tier |
| Local | sentence-transformers | 384-768 | Gratis |

---

## 🗄️ Vector Databases: Comparación

### ChromaDB (recomendado para empezar)
- ✅ Fácil setup (pip install)
- ✅ Corre localmente
- ✅ Perfecto para desarrollo
- ❌ No escalable para producción grande

### Pinecone
- ✅ Managed, fácil de usar
- ✅ Escalable
- ✅ Buen tier gratis
- ❌ Vendor lock-in

### Weaviate
- ✅ Open source
- ✅ Muy completo
- ✅ Auto-vectorization
- ❌ Más complejo de configurar

### pgvector (PostgreSQL)
- ✅ Aprovecha Postgres existente
- ✅ SQL + vector search
- ✅ Open source
- ❌ Performance menor que DBs especializadas

---

## 📦 Dependencias

```bash
# Embeddings
uv add openai  # Para embeddings de OpenAI

# Vector DB
uv add chromadb  # O pinecone-client, weaviate-client

# Document loaders
uv add pypdf  # PDFs
uv add beautifulsoup4  # HTML
uv add python-docx  # Word docs

# Text splitting
uv add langchain-text-splitters
```

---

## 🎯 Casos de Uso RAG

1. **Chatbot de documentación**
   - Carga tus docs
   - Usuarios hacen preguntas
   - Respuestas precisas basadas en docs

2. **Asistente de soporte**
   - Base de conocimiento de tickets
   - FAQs
   - Respuestas automáticas

3. **Análisis de documentos legales/financieros**
   - Contratos, reportes
   - Extracción de información
   - Compliance checking

4. **Research assistant**
   - Papers científicos
   - Notas personales
   - Second brain

---

## 🔗 Recursos

- [RAG Guide - LangChain](https://python.langchain.com/docs/tutorials/rag/)
- [Vector Databases](https://www.pinecone.io/learn/vector-database/)
- [Chunking Strategies](https://www.pinecone.io/learn/chunking-strategies/)
- [ChromaDB Docs](https://docs.trychroma.com/)

---

## ➡️ Próximo Paso

**Fase 5: Producción** - Deploy de agentes con FastAPI, Docker, monitoring, y CI/CD.

---

**Estado:** 📅 Planificado
**Dependencias:** Fase 1 ✅, Fase 2-3 (pendientes)
**Archivos planeados:** 6
