"""
FASE 2 - PASO 2: Agente con Tools y Conditional Edges
=======================================================
El Agentic Loop en LangGraph: Edges Condicionales

Concepto clave:
  Los CONDITIONAL EDGES permiten que el grafo tome decisiones:
    - Si Claude quiere usar una tool → ir a "action"
    - Si Claude terminó → ir a END

Esto replica el agentic loop de Fase 1, pero de forma estructurada.

Comparación:
  Fase 1: while True con if/else manualmente
  Fase 2: Grafo con edges condicionales que manejan el loop automáticamente

Diagrama del flujo:
                    ┌─────────────┐
                    │    START    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
              ┌─────│    agent    │
              │     └──────┬──────┘
              │            │
              │      ¿tool_use?
              │       /        \
              │     NO         SÍ
              │     │           │
              │     ▼           ▼
              │  ┌─────┐   ┌─────────┐
              │  │ END │   │ action  │
              │  └─────┘   └────┬────┘
              │                  │
              └──────────────────┘
                    (loop)

Ejecutar:
  uv run python fase-2-langgraph/02_agente_con_tools.py
"""

import json
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing_extensions import TypedDict

# ============================================================================
# 1. DEFINIR EL ESTADO
# ============================================================================

class AgentState(TypedDict):
    """
    Estado del agente con tools.

    Campos:
      - messages: Historial completo de la conversación
                  Incluye: HumanMessage, AIMessage, ToolMessage

    IMPORTANTE: Usamos Annotated[list, add_messages]
      add_messages es un "reducer" que sabe cómo hacer merge de mensajes.
      Hace append automáticamente cuando retornamos {"messages": [nuevo_msg]}
    """
    messages: Annotated[list, add_messages]


# ============================================================================
# 2. DEFINIR HERRAMIENTAS
# ============================================================================

# Definición de tools (igual que Fase 1, pero formato LangChain)
tools = [
    {
        "name": "calculadora",
        "description": "Realiza operaciones matemáticas. Usa esto para cualquier cálculo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expresion": {
                    "type": "string",
                    "description": "Expresión matemática, ej: '(100 + 50) * 0.16'"
                }
            },
            "required": ["expresion"],
        },
    },
    {
        "name": "obtener_clima",
        "description": "Obtiene el clima actual de una ciudad.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ciudad": {
                    "type": "string",
                    "description": "Nombre de la ciudad"
                }
            },
            "required": ["ciudad"],
        },
    },
]


def ejecutar_tool(nombre: str, argumentos: dict) -> str:
    """Ejecuta una herramienta y retorna el resultado."""
    if nombre == "calculadora":
        try:
            resultado = eval(argumentos["expresion"])
            return json.dumps({"resultado": resultado})
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif nombre == "obtener_clima":
        climas = {
            "madrid": "Soleado, 22°C, humedad 40%",
            "ciudad de méxico": "Nublado, 18°C, humedad 65%",
            "buenos aires": "Lluvioso, 15°C, humedad 80%",
        }
        ciudad = argumentos["ciudad"].lower()
        clima = climas.get(ciudad, f"No tengo datos para {argumentos['ciudad']}")
        return json.dumps({"clima": clima})

    return json.dumps({"error": f"Herramienta '{nombre}' no encontrada"})


# ============================================================================
# 3. DEFINIR NODOS
# ============================================================================

def nodo_agent(state: AgentState) -> dict:
    """
    Nodo principal: Llama al LLM para decidir qué hacer.

    El LLM puede:
      1. Responder directamente (sin tools)
      2. Decidir usar una o más tools
    """
    print(f"\n📍 Nodo: AGENT")
    print(f"   Mensajes actuales: {len(state['messages'])}")

    # Crear modelo y vincular las herramientas
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
    llm_with_tools = llm.bind_tools(tools)

    # Llamar al LLM con el historial completo
    response = llm_with_tools.invoke(state["messages"])

    print(f"   Tipo de respuesta: {type(response).__name__}")

    # Verificar si hay tool calls
    if response.tool_calls:
        print(f"   🔧 Claude quiere usar {len(response.tool_calls)} tool(s)")
        for tc in response.tool_calls:
            print(f"      - {tc['name']}({tc['args']})")
    else:
        print(f"   💬 Claude respondió sin usar tools")

    # Agregar la respuesta de Claude al historial
    return {"messages": [response]}


def nodo_action(state: AgentState) -> dict:
    """
    Nodo de acción: Ejecuta las herramientas solicitadas.

    Toma los tool_calls del último mensaje y ejecuta cada uno.
    """
    print(f"\n📍 Nodo: ACTION")

    # Obtener el último mensaje (debería ser de Claude con tool_calls)
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls

    print(f"   Ejecutando {len(tool_calls)} herramienta(s)...")

    # Ejecutar cada tool y crear ToolMessages
    tool_messages = []
    for tool_call in tool_calls:
        nombre = tool_call["name"]
        args = tool_call["args"]

        print(f"   🔧 Ejecutando: {nombre}({args})")

        # Ejecutar la herramienta
        resultado = ejecutar_tool(nombre, args)

        print(f"      → Resultado: {resultado[:80]}...")

        # Crear ToolMessage (formato LangChain)
        tool_messages.append(
            ToolMessage(
                content=resultado,
                tool_call_id=tool_call["id"],
            )
        )

    # Retornar los resultados de las tools
    return {"messages": tool_messages}


# ============================================================================
# 4. FUNCIÓN DE DECISIÓN (para conditional edges)
# ============================================================================

def should_continue(state: AgentState) -> Literal["action", "end"]:
    """
    Decide el siguiente paso basándose en el último mensaje.

    Returns:
      - "action": Si Claude quiere usar tools → ir a nodo "action"
      - "end": Si Claude terminó → ir a END
    """
    last_message = state["messages"][-1]

    # Si el último mensaje tiene tool_calls, continuar a action
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"\n🔀 Decisión: Ir a ACTION (hay {len(last_message.tool_calls)} tool call(s))")
        return "action"
    else:
        print(f"\n🔀 Decisión: Ir a END (no hay tool calls)")
        return "end"


# ============================================================================
# 5. CONSTRUIR EL GRAFO
# ============================================================================

def crear_grafo():
    """
    Construye el grafo del agente con conditional edges.

    Flujo:
      START → agent → [decision] → action (si hay tools) → agent (loop)
                                 → END (si terminó)
    """
    graph = StateGraph(AgentState)

    # Agregar nodos
    graph.add_node("agent", nodo_agent)
    graph.add_node("action", nodo_action)

    # Edge fijo: empezar en "agent"
    graph.add_edge(START, "agent")

    # CONDITIONAL EDGE: La magia del agentic loop
    # Después de "agent", decidir a dónde ir
    graph.add_conditional_edges(
        "agent",           # Desde este nodo
        should_continue,   # Función que decide
        {
            "action": "action",  # Si retorna "action" → ir a nodo "action"
            "end": END,          # Si retorna "end" → terminar
        },
    )

    # Edge fijo: después de ejecutar tools, volver a "agent"
    # Esto crea el LOOP: agent → action → agent → action → ...
    graph.add_edge("action", "agent")

    return graph.compile()


# ============================================================================
# 6. EJECUTAR EL AGENTE
# ============================================================================

def main():
    print("=" * 70)
    print("  Agente con Tools y Conditional Edges")
    print("=" * 70)

    # Crear el grafo
    app = crear_grafo()

    # Estado inicial con una pregunta que requiere herramientas
    estado_inicial = {
        "messages": [
            HumanMessage(content="¿Cuánto es 1547 * 38? Y dime el clima en Madrid.")
        ]
    }

    print(f"\n🚀 Pregunta: {estado_inicial['messages'][0].content}")
    print(f"\n{'─' * 70}")

    # Ejecutar el grafo
    # El grafo hará el loop automáticamente hasta que Claude termine
    resultado = app.invoke(estado_inicial)

    # Mostrar resultado final
    print(f"\n{'=' * 70}")
    print("✅ CONVERSACIÓN COMPLETA")
    print("=" * 70)

    for i, msg in enumerate(resultado["messages"], 1):
        if isinstance(msg, HumanMessage):
            print(f"\n{i}. 👤 USER:")
            print(f"   {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"\n{i}. 🤖 ASSISTANT:")
            if msg.content:
                print(f"   {msg.content}")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"   [Solicitó {len(msg.tool_calls)} tool(s)]")
        elif isinstance(msg, ToolMessage):
            print(f"\n{i}. 🔧 TOOL RESULT:")
            print(f"   {msg.content[:100]}...")


# ============================================================================
# CONCEPTOS CLAVE APRENDIDOS
# ============================================================================
"""
1. Conditional Edges (add_conditional_edges)
   - Permiten que el grafo tome decisiones
   - Función de decisión retorna el nombre del siguiente nodo
   - Mapeo de retornos → nodos destino

2. Tool Binding (llm.bind_tools)
   - Vincula herramientas al modelo
   - El LLM puede decidir usarlas automáticamente
   - LangChain maneja el formato internamente

3. Tool Messages
   - ToolMessage: resultado de ejecutar una herramienta
   - Incluye tool_call_id para vincular con el tool_call original

4. El Agentic Loop en Grafo
   - agent → [decisión] → action → agent (loop)
   - Se repite automáticamente hasta que Claude termine
   - No necesitas while True, el grafo lo maneja

5. Estado como Historial
   - messages acumula todo: HumanMessage, AIMessage, ToolMessage
   - El LLM ve todo el contexto en cada iteración
   - El grafo hace merge automático de estados

VENTAJA vs Fase 1:
  - Más estructurado y visualizable
  - Lógica de control separada de lógica de negocio
  - Fácil agregar más nodos (ej: validación, logging)
  - Debugging más simple

PRÓXIMO PASO: En el archivo 03 aprenderemos CHECKPOINTING
para memoria persistente entre sesiones.
"""


if __name__ == "__main__":
    main()
