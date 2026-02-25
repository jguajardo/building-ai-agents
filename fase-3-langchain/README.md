# Fase 3: LangChain SDK - Orquestación de LLMs

> **Objetivo:** Migrar a LangChain para mayor flexibilidad, interoperabilidad y acceso al ecosistema completo.

## 🎯 Estado: PENDIENTE

---

## 🤔 ¿Por qué LangChain?

Hasta ahora usamos el SDK de Anthropic directamente. LangChain agrega:

- ✅ **Cambiar de LLM fácilmente** (Claude ↔ GPT ↔ Gemini)
- ✅ **100+ integraciones** (APIs, bases de datos, servicios)
- ✅ **Chains y LCEL** (LangChain Expression Language)
- ✅ **Document loaders** para RAG
- ✅ **Vector stores** integrados
- ✅ **Callbacks y monitoring** built-in
- ✅ **Comunidad y ejemplos** gigantes

---

## 📚 Conceptos Clave

### 1. Chat Models
Wrapper unificado para diferentes LLMs:

```python
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# Mismo interface, diferentes modelos
claude = ChatAnthropic(model="claude-sonnet-4-5")
gpt = ChatOpenAI(model="gpt-4")
```

### 2. LCEL (LangChain Expression Language)
Composición de componentes con `|`:

```python
chain = prompt | model | output_parser
result = chain.invoke({"input": "..."})
```

### 3. Tools
Herramientas con decorador simple:

```python
from langchain.tools import tool

@tool
def buscar_web(query: str) -> str:
    """Busca información en la web."""
    return resultado
```

### 4. Agents
Agentes pre-construidos:

```python
from langchain.agents import create_tool_calling_agent

agent = create_tool_calling_agent(llm, tools, prompt)
```

### 5. Runnables
Todo es un Runnable (invoke, stream, batch):

```python
result = chain.invoke(input)
for chunk in chain.stream(input):
    print(chunk)
results = chain.batch([input1, input2])
```

---

## 📁 Archivos Planeados

### `01_chat_models.py` - Modelos de chat
- ChatAnthropic vs ChatOpenAI
- Mismo código, diferentes modelos
- Comparar respuestas

### `02_prompts_templates.py` - Templates de prompts
- ChatPromptTemplate
- Variables en prompts
- Few-shot examples
- System messages

### `03_lcel_chains.py` - Composición con LCEL
- Chains simples con `|`
- Output parsers
- RunnablePassthrough
- Debugging chains

### `04_tools_langchain.py` - Herramientas
- Decorator @tool
- Bind tools a modelos
- Tool calling con LangChain

### `05_agents_prebuilt.py` - Agentes pre-construidos
- create_tool_calling_agent
- AgentExecutor
- Comparar con nuestra implementación

### `06_callbacks_monitoring.py` - Observabilidad
- Callbacks para logging
- Tracking de tokens
- Latencia y costos
- LangSmith integration

---

## 🗺️ Migración: Anthropic SDK → LangChain

### Antes (SDK Anthropic)
```python
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": "Hola"}]
)
```

### Después (LangChain)
```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-5")
response = llm.invoke("Hola")
```

### Ventaja
Ahora puedes cambiar a GPT con solo cambiar una línea:
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
# ¡El resto del código es igual!
```

---

## 📦 Dependencias

```bash
# LangChain core
uv add langchain langchain-core

# Integraciones de LLMs
uv add langchain-anthropic langchain-openai

# Para RAG (más adelante)
uv add langchain-community

# Monitoring (opcional)
uv add langsmith
```

---

## 🎓 Diferencias Clave

| Aspecto | Anthropic SDK | LangChain |
|---------|--------------|-----------|
| **Flexibilidad** | Solo Claude | Cualquier LLM |
| **Boilerplate** | Poco | Más |
| **Integraciones** | Manual | 100+ built-in |
| **Comunidad** | Pequeña | Enorme |
| **Performance** | Más rápido | Overhead mínimo |
| **Complejidad** | Simple | Más conceptos |

---

## 🔗 Recursos

- [LangChain Docs](https://python.langchain.com/)
- [LCEL Guide](https://python.langchain.com/docs/concepts/lcel/)
- [Chat Models](https://python.langchain.com/docs/integrations/chat/)
- [Tools](https://python.langchain.com/docs/how_to/custom_tools/)

---

## ➡️ Próximo Paso

**Fase 4: RAG (Retrieval Augmented Generation)** - Conectaremos los agentes con bases de conocimiento usando vector databases.

---

**Estado:** 📅 Planificado
**Dependencias:** Fase 1 ✅, Fase 2 (en progreso)
**Archivos planeados:** 6
