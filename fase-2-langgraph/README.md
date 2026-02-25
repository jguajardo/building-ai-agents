# Fase 2: LangGraph - Agentes con Grafos de Estado

> **Objetivo:** Construir agentes más estructurados y controlables usando grafos de estado con LangGraph.

## 🎯 Estado: EN PROGRESO

---

## 🤔 ¿Por qué LangGraph?

El SDK puro de Claude es genial para empezar, pero tiene limitaciones:
- ❌ Difícil de visualizar el flujo del agente
- ❌ La lógica de control está mezclada con la lógica de negocio
- ❌ Complicado agregar persistencia/memoria
- ❌ Hard de debuggear agentes complejos
- ❌ No hay forma estándar de hacer human-in-the-loop

**LangGraph soluciona esto con:**
- ✅ Grafos visualizables (nodos + edges)
- ✅ Separación clara de estados y transiciones
- ✅ Checkpointing automático (memoria persistente)
- ✅ Human-in-the-loop built-in
- ✅ Mejor debugging y observabilidad

---

## 📚 Conceptos Clave de LangGraph

### 1. StateGraph
Un grafo dirigido donde cada nodo puede modificar el estado.

```python
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    messages: list[dict]
    next_action: str

graph = StateGraph(AgentState)
```

### 2. Nodos
Funciones que procesan y modifican el estado.

```python
def llamar_modelo(state: AgentState):
    # Procesar estado
    return {"messages": [...], "next_action": "tool"}
```

### 3. Edges
Conexiones entre nodos. Pueden ser:
- **Condicionales**: Deciden qué nodo ejecutar basándose en el estado
- **Fijos**: Siempre van al mismo nodo

```python
graph.add_conditional_edges(
    "agent",
    should_continue,  # Función que decide el siguiente nodo
    {"continue": "action", "end": END}
)
```

### 4. Checkpointing
Guarda el estado en cada paso para:
- Pausar y resumir
- Time-travel debugging
- Memoria persistente entre sesiones

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = graph.compile(checkpointer=memory)
```

---

## 📁 Archivos Planeados

### `01_state_graph_basico.py` - Primer grafo de estado
**Conceptos:**
- Definir StateGraph
- Crear nodos simples
- Conectar con edges fijos
- Compilar y ejecutar

### `02_agente_con_tools.py` - Loop agnético en grafo
**Conceptos:**
- Nodo de "agent" (llamar LLM)
- Nodo de "action" (ejecutar tools)
- Conditional edges (agent → action o agent → end)
- Replicar el agentic loop en grafo

### `03_checkpointing.py` - Memoria persistente
**Conceptos:**
- MemorySaver para persistencia
- thread_id para separar conversaciones
- Pausar y resumir ejecución
- Ver historial de estados

### `04_human_in_loop.py` - Aprobación humana
**Conceptos:**
- Interrupt before/after nodes
- Esperar input del usuario
- Modificar estado antes de continuar
- Casos de uso: aprobación de acciones críticas

### `05_streaming.py` - Respuestas en tiempo real
**Conceptos:**
- Stream de tokens
- Stream de eventos del grafo
- Mostrar progreso al usuario
- Mejor UX

### `06_subgrafos.py` - Composición de agentes
**Conceptos:**
- Un grafo dentro de otro grafo
- Agentes especializados
- Modularidad y reutilización

---

## 🗺️ Comparación: SDK vs LangGraph

### Mismo agente, dos enfoques:

#### SDK Puro (Fase 1)
```python
while True:
    response = client.messages.create(...)
    if response.stop_reason == "end_turn":
        break
    # Ejecutar tools
    # Agregar a messages
```

**Pros:** Simple, directo, sin dependencias extras
**Contras:** Lógica mezclada, difícil de escalar

#### LangGraph (Fase 2)
```python
graph = StateGraph(AgentState)
graph.add_node("agent", llamar_modelo)
graph.add_node("action", ejecutar_tools)
graph.add_conditional_edges("agent", should_continue)
graph.set_entry_point("agent")
```

**Pros:** Estructurado, visualizable, escalable
**Contras:** Más boilerplate, curva de aprendizaje

---

## 🎓 Cuándo Usar Cada Uno

### Usa SDK Puro cuando:
- Prototipando rápidamente
- Agente simple con 1-3 herramientas
- No necesitas persistencia
- No necesitas debugging avanzado

### Usa LangGraph cuando:
- Agente complejo con múltiples pasos
- Necesitas visualizar el flujo
- Requieres persistencia/checkpointing
- Human-in-the-loop
- Multi-agent systems
- Producción

---

## 📦 Dependencias

```bash
# Instalar LangGraph y dependencias
uv add langgraph langchain-core langchain-anthropic

# Opcional: visualización de grafos
uv add pygraphviz
```

---

## 🚀 Cómo Ejecutar (cuando estén listos)

```bash
export ANTHROPIC_API_KEY="tu-api-key"

uv run python fase-2-langgraph/01_state_graph_basico.py
uv run python fase-2-langgraph/02_agente_con_tools.py
uv run python fase-2-langgraph/03_checkpointing.py
uv run python fase-2-langgraph/04_human_in_loop.py
uv run python fase-2-langgraph/05_streaming.py
uv run python fase-2-langgraph/06_subgrafos.py
```

---

## 🔗 Recursos

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
- [StateGraph API](https://langchain-ai.github.io/langgraph/reference/graphs/)
- [Checkpointing Guide](https://langchain-ai.github.io/langgraph/how-tos/persistence/)

---

## ➡️ Próximo Paso

**Fase 3: LangChain SDK** - Migraremos a usar LangChain para mayor interoperabilidad, más integraciones y poder cambiar de LLM fácilmente.

---

**Iniciado:** 2026-02-25
**Estado:** 🏗️ En construcción
**Archivos planeados:** 6
