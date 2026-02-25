"""
FASE 2 - PASO 3: Checkpointing - Memoria Persistente
=====================================================
Guardar el estado del agente entre sesiones.

Concepto clave:
  CHECKPOINTING permite pausar y resumir conversaciones.
  El estado se guarda automáticamente después de cada nodo.

¿Para qué sirve?
  - Memoria entre sesiones (cerrar y reabrir la app)
  - Múltiples conversaciones simultáneas (threads)
  - Time-travel debugging (ver estados pasados)
  - Rollback a estados anteriores

Comparación:
  Sin checkpointing: Memoria solo durante la ejecución
  Con checkpointing: Memoria persiste en base de datos/memoria

Ejecutar:
  uv run python fase-2-langgraph/03_checkpointing.py
"""

import json
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing_extensions import TypedDict

# ============================================================================
# 1. DEFINIR ESTADO Y HERRAMIENTAS (igual que archivo 02)
# ============================================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools = [
    {
        "name": "calculadora",
        "description": "Realiza operaciones matemáticas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expresion": {"type": "string", "description": "Expresión matemática"}
            },
            "required": ["expresion"],
        },
    },
]


def ejecutar_tool(nombre: str, argumentos: dict) -> str:
    if nombre == "calculadora":
        try:
            resultado = eval(argumentos["expresion"])
            return json.dumps({"resultado": resultado})
        except Exception as e:
            return json.dumps({"error": str(e)})
    return json.dumps({"error": f"Tool '{nombre}' no encontrada"})


# ============================================================================
# 2. NODOS (igual que archivo 02)
# ============================================================================

def nodo_agent(state: AgentState) -> dict:
    print(f"\n📍 Nodo: AGENT")
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])

    if response.tool_calls:
        print(f"   🔧 Claude quiere usar {len(response.tool_calls)} tool(s)")
    else:
        print(f"   💬 Claude respondió sin usar tools")

    return {"messages": [response]}


def nodo_action(state: AgentState) -> dict:
    print(f"\n📍 Nodo: ACTION")
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        print(f"   🔧 Ejecutando: {tool_call['name']}")
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
# 3. CONSTRUIR GRAFO CON CHECKPOINTING
# ============================================================================

def crear_grafo_con_checkpointing():
    """
    Crea un grafo con checkpointing habilitado.

    LA DIFERENCIA CLAVE: .compile(checkpointer=memory)
    """
    graph = StateGraph(AgentState)

    graph.add_node("agent", nodo_agent)
    graph.add_node("action", nodo_action)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {
        "action": "action",
        "end": END,
    })
    graph.add_edge("action", "agent")

    # ¡AQUÍ ESTÁ LA MAGIA!
    # MemorySaver guarda el estado en memoria (RAM)
    # En producción usarías SqliteSaver, PostgresSaver, etc.
    memory = MemorySaver()

    # Compilar CON checkpointer
    return graph.compile(checkpointer=memory)


# ============================================================================
# 4. DEMOSTRACIÓN DE CHECKPOINTING
# ============================================================================

def demo_conversacion_continua():
    """
    Demuestra cómo mantener una conversación a través de múltiples llamadas.
    """
    print("=" * 70)
    print("  DEMO 1: Conversación Continua")
    print("=" * 70)

    app = crear_grafo_con_checkpointing()

    # Configuración con thread_id
    # El thread_id identifica una conversación específica
    config = {"configurable": {"thread_id": "conversacion-1"}}

    # ────────────────────────────────────────────────────────────────────
    # TURNO 1: Primera pregunta
    # ────────────────────────────────────────────────────────────────────
    print("\n🎬 TURNO 1: Primera pregunta")
    print("─" * 70)

    estado_1 = {"messages": [HumanMessage(content="¿Cuánto es 100 + 50?")]}
    resultado_1 = app.invoke(estado_1, config)

    print("\n📨 Respuesta:")
    print(f"   {resultado_1['messages'][-1].content}")

    # ────────────────────────────────────────────────────────────────────
    # TURNO 2: Pregunta de seguimiento (sin repetir el contexto)
    # ────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("🎬 TURNO 2: Pregunta de seguimiento")
    print("─" * 70)
    print("Nota: NO pasamos el historial anterior, el checkpointer lo maneja")

    # Solo pasamos el NUEVO mensaje
    estado_2 = {"messages": [HumanMessage(content="Multiplica eso por 3")]}
    resultado_2 = app.invoke(estado_2, config)

    print("\n📨 Respuesta:")
    print(f"   {resultado_2['messages'][-1].content}")

    print("\n💡 ¡Claude recordó el resultado anterior (150) sin que se lo pasáramos!")

    # ────────────────────────────────────────────────────────────────────
    # Verificar el estado guardado
    # ────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("📦 Estado guardado en memoria:")
    print("─" * 70)
    print(f"   Total de mensajes en el thread: {len(resultado_2['messages'])}")
    print(f"   Thread ID: {config['configurable']['thread_id']}")


def demo_multiples_conversaciones():
    """
    Demuestra múltiples conversaciones independientes (threads).
    """
    print("\n" + "=" * 70)
    print("  DEMO 2: Múltiples Conversaciones Simultáneas")
    print("=" * 70)

    app = crear_grafo_con_checkpointing()

    # ────────────────────────────────────────────────────────────────────
    # Thread 1: Usuario A
    # ────────────────────────────────────────────────────────────────────
    print("\n👤 USUARIO A (thread-A)")
    print("─" * 70)
    config_a = {"configurable": {"thread_id": "thread-A"}}

    app.invoke(
        {"messages": [HumanMessage(content="Hola, soy el usuario A. ¿Cuánto es 10 + 20?")]},
        config_a
    )
    print("   ✅ Usuario A hizo su pregunta")

    # ────────────────────────────────────────────────────────────────────
    # Thread 2: Usuario B (conversación independiente)
    # ────────────────────────────────────────────────────────────────────
    print("\n👤 USUARIO B (thread-B)")
    print("─" * 70)
    config_b = {"configurable": {"thread_id": "thread-B"}}

    app.invoke(
        {"messages": [HumanMessage(content="Hola, soy el usuario B. ¿Cuánto es 5 * 8?")]},
        config_b
    )
    print("   ✅ Usuario B hizo su pregunta")

    # ────────────────────────────────────────────────────────────────────
    # Usuario A continúa su conversación
    # ────────────────────────────────────────────────────────────────────
    print("\n👤 USUARIO A (continuación)")
    print("─" * 70)
    resultado_a = app.invoke(
        {"messages": [HumanMessage(content="Multiplica ese resultado por 2")]},
        config_a
    )
    print(f"   💬 {resultado_a['messages'][-1].content}")
    print("   ✅ Usuario A obtuvo: 30 * 2 = 60 (recordó su conversación)")

    # ────────────────────────────────────────────────────────────────────
    # Usuario B continúa su conversación
    # ────────────────────────────────────────────────────────────────────
    print("\n👤 USUARIO B (continuación)")
    print("─" * 70)
    resultado_b = app.invoke(
        {"messages": [HumanMessage(content="Suma 10 a eso")]},
        config_b
    )
    print(f"   💬 {resultado_b['messages'][-1].content}")
    print("   ✅ Usuario B obtuvo: 40 + 10 = 50 (recordó su conversación)")

    print("\n💡 Cada thread mantiene su propia conversación independiente!")


def demo_get_state():
    """
    Demuestra cómo acceder al estado guardado.
    """
    print("\n" + "=" * 70)
    print("  DEMO 3: Acceder al Estado Guardado")
    print("=" * 70)

    app = crear_grafo_con_checkpointing()
    config = {"configurable": {"thread_id": "demo-state"}}

    # Crear conversación
    app.invoke(
        {"messages": [HumanMessage(content="Calcula 7 * 9")]},
        config
    )

    # Obtener el estado actual
    state = app.get_state(config)

    print("\n📊 Información del estado:")
    print(f"   Total de mensajes: {len(state.values['messages'])}")
    print(f"   Siguiente nodo a ejecutar: {state.next}")
    print(f"   Config: {state.config}")

    print("\n📨 Mensajes en el estado:")
    for i, msg in enumerate(state.values['messages'], 1):
        tipo = type(msg).__name__
        preview = str(msg.content)[:60] if hasattr(msg, 'content') else str(msg)[:60]
        print(f"   {i}. {tipo}: {preview}...")


# ============================================================================
# EJECUTAR DEMOS
# ============================================================================

def main():
    print("\n🎓 APRENDIENDO CHECKPOINTING EN LANGGRAPH")

    # Demo 1: Conversación continua
    demo_conversacion_continua()

    # Demo 2: Múltiples conversaciones
    demo_multiples_conversaciones()

    # Demo 3: Acceder al estado
    demo_get_state()


# ============================================================================
# CONCEPTOS CLAVE APRENDIDOS
# ============================================================================
"""
1. MemorySaver
   - Checkpointer que guarda en memoria (RAM)
   - En producción: SqliteSaver, PostgresSaver, RedisSaver
   - Automático: guarda después de cada nodo

2. thread_id
   - Identifica una conversación específica
   - Cada thread tiene su propio estado independiente
   - Permite múltiples conversaciones simultáneas

3. .compile(checkpointer=memory)
   - Habilita el checkpointing en el grafo
   - Sin esto, el estado solo vive durante .invoke()

4. config = {"configurable": {"thread_id": "..."}}
   - Se pasa a .invoke() para especificar el thread
   - Mismo thread_id = misma conversación
   - Diferente thread_id = conversación nueva

5. .get_state(config)
   - Obtiene el estado actual de un thread
   - Útil para debugging y monitoring
   - Puedes ver qué nodo se ejecutará después

6. Memoria Persistente
   - El estado persiste entre llamadas a .invoke()
   - No necesitas pasar el historial completo cada vez
   - El checkpointer lo maneja automáticamente

CASOS DE USO:
  - Chatbots con memoria entre sesiones
  - Múltiples usuarios simultáneos
  - Debugging (ver estado en cada paso)
  - Rollback (volver a estados anteriores)
  - A/B testing (comparar diferentes paths)

PRÓXIMO PASO: En el archivo 04 aprenderemos HUMAN-IN-THE-LOOP
para pausar el agente y pedir aprobación del usuario.
"""


if __name__ == "__main__":
    main()
