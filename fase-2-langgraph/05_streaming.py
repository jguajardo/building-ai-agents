"""
FASE 2 - PASO 5: Streaming - Respuestas en Tiempo Real
=========================================================
Ver la salida del agente token por token en tiempo real.

Concepto clave:
  STREAMING permite ver los tokens del LLM a medida que se generan,
  en vez de esperar a que termine toda la respuesta.

¿Para qué sirve?
  - Mejor UX: El usuario ve progreso inmediato
  - Percepción de velocidad: Parece más rápido
  - Detección temprana de errores
  - Cancelación: Puedes parar si va mal

Tipos de streaming en LangGraph:
  1. Stream de valores: Estado completo después de cada nodo
  2. Stream de updates: Solo los cambios en cada nodo
  3. Stream de eventos: Eventos granulares (tokens, tool calls, etc.)

Ejecutar:
  uv run python fase-2-langgraph/05_streaming.py
"""

import json
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing_extensions import TypedDict

# ============================================================================
# 1. DEFINIR ESTADO Y HERRAMIENTAS
# ============================================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools = [
    {
        "name": "buscar_info",
        "description": "Busca información sobre un tema.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tema": {"type": "string", "description": "Tema a buscar"}
            },
            "required": ["tema"],
        },
    },
]


def ejecutar_tool(nombre: str, argumentos: dict) -> str:
    if nombre == "buscar_info":
        # Simular búsqueda
        tema = argumentos["tema"]
        return json.dumps({
            "info": f"Información encontrada sobre '{tema}': Es un tema interesante..."
        })
    return json.dumps({"error": "Tool no encontrada"})


# ============================================================================
# 2. NODOS
# ============================================================================

def nodo_agent(state: AgentState) -> dict:
    """Nodo del agente."""
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def nodo_action(state: AgentState) -> dict:
    """Nodo de acción."""
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        resultado = ejecutar_tool(tool_call["name"], tool_call["args"])
        tool_messages.append(
            ToolMessage(content=resultado, tool_call_id=tool_call["id"])
        )

    return {"messages": tool_messages}


def should_continue(state: AgentState) -> Literal["action", "end"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "action"
    return "end"


# ============================================================================
# 3. CONSTRUIR GRAFO
# ============================================================================

def crear_grafo():
    graph = StateGraph(AgentState)
    graph.add_node("agent", nodo_agent)
    graph.add_node("action", nodo_action)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {
        "action": "action",
        "end": END,
    })
    graph.add_edge("action", "agent")
    return graph.compile()


# ============================================================================
# 4. DEMOS DE STREAMING
# ============================================================================

def demo_stream_values():
    """
    DEMO 1: Stream de valores (estado completo después de cada nodo)
    """
    print("=" * 70)
    print("  DEMO 1: Stream de Valores (Estado Completo)")
    print("=" * 70)

    app = crear_grafo()
    estado_inicial = {
        "messages": [HumanMessage(content="Dame un dato curioso sobre Python")]
    }

    print("\n🌊 Streaming valores...")
    print("─" * 70)

    # .stream() retorna el estado después de cada nodo
    for i, chunk in enumerate(app.stream(estado_inicial), 1):
        print(f"\n📦 Chunk {i}:")
        for nodo, valor in chunk.items():
            print(f"   Nodo: {nodo}")
            if "messages" in valor:
                ultimo_msg = valor["messages"][-1]
                tipo = type(ultimo_msg).__name__
                print(f"   Tipo de mensaje: {tipo}")

                if hasattr(ultimo_msg, "content") and ultimo_msg.content:
                    preview = str(ultimo_msg.content)[:80]
                    print(f"   Contenido: {preview}...")

    print("\n💡 Cada chunk es el estado DESPUÉS de ejecutar un nodo")


def demo_stream_updates():
    """
    DEMO 2: Stream de updates (solo los cambios)
    """
    print("\n" + "=" * 70)
    print("  DEMO 2: Stream de Updates (Solo Cambios)")
    print("=" * 70)

    app = crear_grafo()
    estado_inicial = {
        "messages": [HumanMessage(content="¿Qué es un grafo de estado?")]
    }

    print("\n🌊 Streaming updates...")
    print("─" * 70)

    # mode="updates" solo retorna lo que cambió en cada nodo
    for i, chunk in enumerate(app.stream(estado_inicial, stream_mode="updates"), 1):
        print(f"\n📦 Update {i}:")
        for nodo, update in chunk.items():
            print(f"   Nodo: {nodo}")
            if "messages" in update:
                # Solo los mensajes NUEVOS agregados por este nodo
                for msg in update["messages"]:
                    tipo = type(msg).__name__
                    print(f"   Nuevo mensaje: {tipo}")

    print("\n💡 Cada update solo contiene los CAMBIOS, no el estado completo")


def demo_stream_events():
    """
    DEMO 3: Stream de eventos (granular, incluyendo tokens)
    """
    print("\n" + "=" * 70)
    print("  DEMO 3: Stream de Eventos (Máxima Granularidad)")
    print("=" * 70)

    app = crear_grafo()
    estado_inicial = {
        "messages": [HumanMessage(content="Explícame LangGraph en pocas palabras")]
    }

    print("\n🌊 Streaming eventos...")
    print("─" * 70)
    print("(Mostrando solo eventos relevantes)\n")

    # astream_events() es la forma más granular de streaming
    # Muestra TODOS los eventos internos del grafo
    evento_count = 0

    for event in app.stream(estado_inicial, stream_mode="values"):
        # En valores podemos ver el progreso nodo por nodo
        pass

    print("\n💡 stream_mode='values' es el más común y útil")
    print("   Para tokens individuales, usa .astream_events() (async)")


def demo_streaming_simple():
    """
    DEMO 4: Ejemplo simple y práctico de streaming
    """
    print("\n" + "=" * 70)
    print("  DEMO 4: Ejemplo Práctico - Chatbot con Streaming")
    print("=" * 70)

    app = crear_grafo()

    # Pregunta que genera una respuesta larga
    pregunta = "Explícame qué es LangGraph y para qué sirve."

    print(f"\n👤 Usuario: {pregunta}")
    print("🤖 Asistente: ", end="", flush=True)

    # Streaming de la respuesta final
    for chunk in app.stream({"messages": [HumanMessage(content=pregunta)]}):
        # Obtener el último mensaje de cada chunk
        for nodo, estado in chunk.items():
            if "messages" in estado:
                ultimo_msg = estado["messages"][-1]

                # Si es la respuesta final del asistente
                if isinstance(ultimo_msg, AIMessage) and ultimo_msg.content:
                    # En producción, aquí harías streaming token por token
                    # con astream_events() o similar
                    pass

    # Obtener respuesta final
    resultado_final = app.invoke({"messages": [HumanMessage(content=pregunta)]})
    respuesta = resultado_final["messages"][-1].content

    print(respuesta)

    print("\n\n💡 En una app real, usarías:")
    print("   - FastAPI con Server-Sent Events (SSE)")
    print("   - WebSockets para bidireccional")
    print("   - astream_events() para tokens individuales")


def demo_comparacion():
    """
    DEMO 5: Comparar .invoke() vs .stream()
    """
    print("\n" + "=" * 70)
    print("  DEMO 5: Comparación invoke() vs stream()")
    print("=" * 70)

    app = crear_grafo()
    pregunta = {"messages": [HumanMessage(content="¿Qué es LangChain?")]}

    # ────────────────────────────────────────────────────────────────────
    # invoke(): Espera todo el resultado
    # ────────────────────────────────────────────────────────────────────
    print("\n1️⃣ Con .invoke() (espera completa):")
    print("   [Esperando...................]")

    resultado_invoke = app.invoke(pregunta)

    print("   ✅ Resultado completo recibido")
    print(f"   Mensajes: {len(resultado_invoke['messages'])}")

    # ────────────────────────────────────────────────────────────────────
    # stream(): Ve progreso incremental
    # ────────────────────────────────────────────────────────────────────
    print("\n2️⃣ Con .stream() (progreso incremental):")

    paso = 0
    for chunk in app.stream(pregunta):
        paso += 1
        for nodo in chunk.keys():
            print(f"   ✓ Completado: {nodo} (paso {paso})")

    print("\n💡 Diferencias:")
    print("   invoke() = Bloquea hasta terminar (simple)")
    print("   stream() = Progreso incremental (mejor UX)")


# ============================================================================
# EJECUTAR DEMOS
# ============================================================================

def main():
    print("\n🎓 APRENDIENDO STREAMING EN LANGGRAPH")

    # Demo 1: Stream de valores
    demo_stream_values()

    # Demo 2: Stream de updates
    demo_stream_updates()

    # Demo 3: Stream de eventos
    demo_stream_events()

    # Demo 4: Ejemplo práctico
    demo_streaming_simple()

    # Demo 5: Comparación
    demo_comparacion()


# ============================================================================
# CONCEPTOS CLAVE APRENDIDOS
# ============================================================================
"""
1. app.stream(input)
   - Versión de streaming de .invoke()
   - Retorna un iterador de chunks
   - Cada chunk es el estado después de un nodo

2. stream_mode (modos de streaming)
   - "values" (default): Estado completo después de cada nodo
   - "updates": Solo los cambios en cada nodo
   - "debug": Info de debugging

3. Streaming en Producción
   Para streaming token-por-token real:
   - Usar .astream_events() (async)
   - Integrar con FastAPI + SSE
   - O WebSockets para bidireccional

4. Cuándo Usar Cada Modo
   - values: Ver estado completo, debugging
   - updates: Solo cambios, más eficiente
   - events: Máxima granularidad (tokens, etc.)

5. Ventajas del Streaming
   - Mejor UX: Usuario ve progreso
   - Percepción de velocidad
   - Detección temprana de errores
   - Posibilidad de cancelar

6. Ejemplo de Integración (FastAPI + SSE)

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.post("/chat")
async def chat(message: str):
    async def generate():
        for chunk in app.stream({"messages": [HumanMessage(message)]}):
            # Extraer contenido relevante del chunk
            data = extract_content(chunk)
            yield f"data: {json.dumps(data)}\\n\\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

PRÓXIMO PASO: En el archivo 06 aprenderemos SUBGRAFOS
para componer agentes complejos a partir de agentes más simples.
"""


if __name__ == "__main__":
    main()
