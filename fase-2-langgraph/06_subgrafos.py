"""
FASE 2 - PASO 6: Subgrafos - Composición de Agentes
=====================================================
Crear agentes complejos componiendo agentes más simples.

Concepto clave:
  Un SUBGRAFO es un grafo dentro de otro grafo.
  Permite modularidad y reutilización de componentes.

¿Para qué sirve?
  - Multi-agent systems: Especialistas trabajando juntos
  - Modularidad: Divide y vencerás
  - Reutilización: Un subgrafo puede usarse en múltiples lugares
  - Abstracción: Oculta complejidad interna

Ejemplo real:
  Agente principal → Subagente de investigación
                  → Subagente de escritura
                  → Subagente de revisión

Ejecutar:
  uv run python fase-2-langgraph/06_subgrafos.py
"""

import json
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing_extensions import TypedDict

# ============================================================================
# 1. DEFINIR ESTADOS
# ============================================================================

class ResearchState(TypedDict):
    """Estado del subgrafo de investigación."""
    messages: Annotated[list, add_messages]
    query: str
    results: str


class WriterState(TypedDict):
    """Estado del subgrafo de escritura."""
    messages: Annotated[list, add_messages]
    topic: str
    draft: str


class MainState(TypedDict):
    """Estado del grafo principal."""
    messages: Annotated[list, add_messages]
    topic: str
    research_results: str
    final_article: str


# ============================================================================
# 2. SUBGRAFO 1: RESEARCH AGENT (Investigador)
# ============================================================================

def research_gather(state: ResearchState) -> dict:
    """Simula búsqueda de información."""
    print(f"\n🔍 Investigando sobre: {state['query']}")

    # En un agente real, aquí llamarías APIs de búsqueda (Tavily, Serper, etc.)
    resultados_simulados = f"""
    Información encontrada sobre '{state['query']}':
    - Es un framework de orquestación de agentes
    - Desarrollado por LangChain
    - Usa grafos de estado para estructurar agentes
    - Permite checkpointing, human-in-the-loop y más
    """

    return {"results": resultados_simulados}


def research_analyze(state: ResearchState) -> dict:
    """Analiza y resume los resultados de investigación."""
    print(f"📊 Analizando resultados...")

    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

    messages = [
        SystemMessage(content="Eres un investigador experto. Resume la información de forma concisa."),
        HumanMessage(content=f"Resume estos hallazgos:\n{state['results']}")
    ]

    response = llm.invoke(messages)

    print(f"   ✅ Análisis completado")

    return {
        "results": state['results'] + f"\n\nRESUMEN: {response.content}",
        "messages": [response]
    }


def crear_research_agent():
    """Crea el subgrafo de investigación."""
    graph = StateGraph(ResearchState)

    graph.add_node("gather", research_gather)
    graph.add_node("analyze", research_analyze)

    graph.add_edge(START, "gather")
    graph.add_edge("gather", "analyze")
    graph.add_edge("analyze", END)

    return graph.compile()


# ============================================================================
# 3. SUBGRAFO 2: WRITER AGENT (Escritor)
# ============================================================================

def writer_draft(state: WriterState) -> dict:
    """Escribe un borrador."""
    print(f"\n✍️  Escribiendo borrador sobre: {state['topic']}")

    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

    messages = [
        SystemMessage(content="Eres un escritor técnico experto."),
        HumanMessage(content=f"Escribe un artículo breve sobre: {state['topic']}")
    ]

    response = llm.invoke(messages)

    print(f"   ✅ Borrador creado")

    return {
        "draft": response.content,
        "messages": [response]
    }


def writer_polish(state: WriterState) -> dict:
    """Mejora el borrador."""
    print(f"✨ Puliendo el borrador...")

    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

    messages = [
        SystemMessage(content="Eres un editor experto. Mejora el texto haciéndolo más claro y conciso."),
        HumanMessage(content=f"Mejora este texto:\n\n{state['draft']}")
    ]

    response = llm.invoke(messages)

    print(f"   ✅ Artículo pulido")

    return {
        "draft": response.content,
        "messages": state["messages"] + [response]
    }


def crear_writer_agent():
    """Crea el subgrafo de escritura."""
    graph = StateGraph(WriterState)

    graph.add_node("draft", writer_draft)
    graph.add_node("polish", writer_polish)

    graph.add_edge(START, "draft")
    graph.add_edge("draft", "polish")
    graph.add_edge("polish", END)

    return graph.compile()


# ============================================================================
# 4. GRAFO PRINCIPAL: ORCHESTRATOR
# ============================================================================

def main_start(state: MainState) -> dict:
    """Nodo inicial: Define la tarea."""
    print(f"\n{'='*70}")
    print(f"🎯 INICIANDO PIPELINE DE ARTÍCULO")
    print(f"   Tema: {state['topic']}")
    print(f"{'='*70}")
    return {}


def main_research(state: MainState) -> dict:
    """Delega al subgrafo de investigación."""
    print(f"\n📚 FASE 1: INVESTIGACIÓN")
    print(f"{'─'*70}")

    # Crear el subagente de investigación
    research_agent = crear_research_agent()

    # Invocar el subagente con su propio estado
    research_input = {
        "query": state["topic"],
        "results": "",
        "messages": []
    }

    resultado = research_agent.invoke(research_input)

    # Extraer los resultados
    return {"research_results": resultado["results"]}


def main_write(state: MainState) -> dict:
    """Delega al subgrafo de escritura."""
    print(f"\n📝 FASE 2: ESCRITURA")
    print(f"{'─'*70}")

    # Crear el subagente de escritura
    writer_agent = crear_writer_agent()

    # Preparar contexto para el escritor
    topic_with_context = f"{state['topic']}\n\nInvestigación:\n{state['research_results']}"

    writer_input = {
        "topic": topic_with_context,
        "draft": "",
        "messages": []
    }

    resultado = writer_agent.invoke(writer_input)

    return {"final_article": resultado["draft"]}


def main_finish(state: MainState) -> dict:
    """Nodo final: Muestra resultados."""
    print(f"\n{'='*70}")
    print(f"✅ PIPELINE COMPLETADO")
    print(f"{'='*70}")

    print(f"\n📄 ARTÍCULO FINAL:")
    print(f"{'─'*70}")
    print(state["final_article"])

    return {}


def crear_main_graph():
    """Crea el grafo principal que orquesta los subgrafos."""
    graph = StateGraph(MainState)

    # Nodos del orquestador
    graph.add_node("start", main_start)
    graph.add_node("research", main_research)  # Llama al subgrafo de investigación
    graph.add_node("write", main_write)        # Llama al subgrafo de escritura
    graph.add_node("finish", main_finish)

    # Flujo lineal
    graph.add_edge(START, "start")
    graph.add_edge("start", "research")
    graph.add_edge("research", "write")
    graph.add_edge("write", "finish")
    graph.add_edge("finish", END)

    return graph.compile()


# ============================================================================
# 5. DEMOSTRACIÓN
# ============================================================================

def demo_subgrafos():
    """
    Demo: Sistema multi-agente con subgrafos.

    Flujo:
      Main Graph
        ├─> Research Agent (subgrafo)
        │     ├─> gather
        │     └─> analyze
        │
        └─> Writer Agent (subgrafo)
              ├─> draft
              └─> polish
    """
    print("\n🎓 DEMO: SISTEMA MULTI-AGENTE CON SUBGRAFOS")

    # Crear el grafo principal
    app = crear_main_graph()

    # Estado inicial
    estado_inicial = {
        "messages": [],
        "topic": "LangGraph",
        "research_results": "",
        "final_article": ""
    }

    # Ejecutar el pipeline completo
    app.invoke(estado_inicial)


def demo_conceptos():
    """Explica los conceptos clave."""
    print("\n" + "="*70)
    print("💡 CONCEPTOS CLAVE")
    print("="*70)

    print("""
1. MODULARIDAD
   - Cada subgrafo es independiente y reutilizable
   - El research_agent puede usarse en otros grafos
   - El writer_agent también

2. SEPARACIÓN DE CONCERNS
   - Research Agent: Solo investiga
   - Writer Agent: Solo escribe
   - Main Graph: Solo orquesta

3. ESTADO INDEPENDIENTE
   - Cada subgrafo tiene su propio tipo de estado
   - ResearchState ≠ WriterState ≠ MainState
   - El grafo principal hace "traducción" entre estados

4. COMPOSICIÓN
   - Grafos pequeños y simples → Grafo complejo
   - Fácil de debuggear (un subgrafo a la vez)
   - Fácil de testear (cada subgrafo por separado)

5. ESCALABILIDAD
   - Agregar más subgrafos es fácil
   - Ej: ReviewAgent, FactCheckAgent, SEOAgent, etc.

CASOS DE USO REALES:
   - Content generation pipeline (research → write → edit → SEO)
   - Customer support (classifier → specialist agents → summarizer)
   - Code generation (planner → coder → tester → reviewer)
   - Data analysis (collector → processor → analyzer → reporter)

PRÓXIMOS PASOS:
   ✅ Completaste Fase 2: LangGraph
   ➡️  Siguiente: Fase 3: LangChain SDK (migración)
    """)


# ============================================================================
# EJECUTAR
# ============================================================================

def main():
    # Demo de subgrafos
    demo_subgrafos()

    # Explicación de conceptos
    demo_conceptos()


# ============================================================================
# RESUMEN FINAL DE FASE 2
# ============================================================================
"""
🎉 ¡FELICITACIONES! Completaste la Fase 2: LangGraph

LO QUE APRENDISTE:
──────────────────

Archivo 01: StateGraph Básico
  ✓ Grafos de estado
  ✓ Nodos como funciones
  ✓ Edges fijos
  ✓ START y END

Archivo 02: Agente con Tools
  ✓ Conditional edges
  ✓ Agentic loop en grafo
  ✓ Tool calling
  ✓ add_messages reducer

Archivo 03: Checkpointing
  ✓ Memoria persistente
  ✓ thread_id para conversaciones
  ✓ MemorySaver
  ✓ get_state()

Archivo 04: Human-in-the-Loop
  ✓ interrupt_before/after
  ✓ Aprobar/rechazar acciones
  ✓ update_state()
  ✓ Intervención humana

Archivo 05: Streaming
  ✓ Respuestas en tiempo real
  ✓ stream_mode: values, updates
  ✓ Mejor UX
  ✓ Progreso incremental

Archivo 06: Subgrafos
  ✓ Composición de agentes
  ✓ Multi-agent systems
  ✓ Modularidad
  ✓ Reutilización

DIFERENCIA CLAVE vs FASE 1:
───────────────────────────

Fase 1 (SDK puro):
  - While loops manuales
  - Lógica mezclada
  - Difícil de debuggear
  - No hay estructura visual

Fase 2 (LangGraph):
  - Grafos declarativos
  - Separación de concerns
  - Visualizable y debuggeable
  - Checkpointing, streaming, etc.

CUÁNDO USAR LANGGRAPH:
──────────────────────

✅ Usa LangGraph cuando:
  - Agentes complejos con múltiples pasos
  - Necesitas memoria persistente
  - Human-in-the-loop
  - Multi-agent systems
  - Producción

❌ No necesitas LangGraph cuando:
  - Prototipo rápido
  - Agente muy simple (1-2 tools)
  - No necesitas checkpointing
  - Solo estás experimentando

PRÓXIMA FASE:
─────────────

Fase 3: LangChain SDK
  - Migrar a LangChain para mayor interoperabilidad
  - LCEL (LangChain Expression Language)
  - Cambiar de LLM fácilmente
  - 100+ integraciones

¡Excelente progreso! 🚀
"""


if __name__ == "__main__":
    main()
