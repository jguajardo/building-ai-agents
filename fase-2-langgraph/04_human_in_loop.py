"""
FASE 2 - PASO 4: Human-in-the-Loop - Aprobación Humana
========================================================
Pausar el agente para obtener aprobación del usuario.

Concepto clave:
  INTERRUPT permite pausar el grafo antes/después de un nodo
  y esperar input del usuario antes de continuar.

¿Para qué sirve?
  - Aprobar acciones críticas (ej: enviar email, hacer compra)
  - Revisar respuestas antes de enviarlas al usuario
  - Editar el estado antes de continuar
  - Intervención humana en decisiones importantes

Comparación:
  Sin interrupts: El agente corre de principio a fin automáticamente
  Con interrupts: Se pausa y espera aprobación/edición del humano

Ejecutar:
  uv run python fase-2-langgraph/04_human_in_loop.py
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
# 1. DEFINIR ESTADO Y HERRAMIENTAS
# ============================================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# Herramienta "peligrosa" que requiere aprobación
tools = [
    {
        "name": "enviar_email",
        "description": "Envía un email. REQUIERE APROBACIÓN HUMANA.",
        "input_schema": {
            "type": "object",
            "properties": {
                "destinatario": {"type": "string", "description": "Email del destinatario"},
                "asunto": {"type": "string", "description": "Asunto del email"},
                "cuerpo": {"type": "string", "description": "Contenido del email"},
            },
            "required": ["destinatario", "asunto", "cuerpo"],
        },
    },
    {
        "name": "calculadora",
        "description": "Realiza cálculos matemáticos simples.",
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
    """Ejecuta herramientas (simuladas)."""
    if nombre == "calculadora":
        try:
            resultado = eval(argumentos["expresion"])
            return json.dumps({"resultado": resultado})
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif nombre == "enviar_email":
        # En un sistema real, aquí enviarías el email
        return json.dumps({
            "status": "enviado",
            "mensaje": f"Email enviado a {argumentos['destinatario']}"
        })

    return json.dumps({"error": f"Tool '{nombre}' no encontrada"})


# ============================================================================
# 2. NODOS
# ============================================================================

def nodo_agent(state: AgentState) -> dict:
    """Nodo del agente: decide qué hacer."""
    print(f"\n📍 Nodo: AGENT")

    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])

    if response.tool_calls:
        print(f"   🔧 Claude quiere usar: {[tc['name'] for tc in response.tool_calls]}")
    else:
        print(f"   💬 Claude respondió sin usar tools")

    return {"messages": [response]}


def nodo_action(state: AgentState) -> dict:
    """Nodo de acción: ejecuta herramientas."""
    print(f"\n📍 Nodo: ACTION")

    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.tool_calls:
        nombre = tool_call["name"]
        args = tool_call["args"]

        print(f"   🔧 Ejecutando: {nombre}")
        print(f"      Args: {args}")

        resultado = ejecutar_tool(nombre, args)
        tool_messages.append(
            ToolMessage(content=resultado, tool_call_id=tool_call["id"])
        )

    return {"messages": tool_messages}


def should_continue(state: AgentState) -> Literal["action", "end"]:
    """Decide si continuar o terminar."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "action"
    return "end"


# ============================================================================
# 3. CONSTRUIR GRAFO CON INTERRUPT
# ============================================================================

def crear_grafo_con_interrupt():
    """
    Crea un grafo que se interrumpe ANTES del nodo 'action'.

    Esto permite revisar qué herramientas va a ejecutar el agente
    antes de que las ejecute.
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

    memory = MemorySaver()

    # ¡LA MAGIA!
    # interrupt_before=["action"] pausa el grafo ANTES de ejecutar "action"
    # También existe interrupt_after=["nodo"] para pausar DESPUÉS
    return graph.compile(
        checkpointer=memory,
        interrupt_before=["action"]  # <-- Pausar antes de action
    )


# ============================================================================
# 4. DEMOSTRACIÓN DE HUMAN-IN-THE-LOOP
# ============================================================================

def demo_interrupt_basic():
    """
    Demo básica: El grafo se pausa antes de ejecutar herramientas.
    """
    print("=" * 70)
    print("  DEMO 1: Interrupción Básica")
    print("=" * 70)

    app = crear_grafo_con_interrupt()
    config = {"configurable": {"thread_id": "demo-1"}}

    # ────────────────────────────────────────────────────────────────────
    # Primera invocación: Se pausará antes de 'action'
    # ────────────────────────────────────────────────────────────────────
    print("\n🚀 Paso 1: Invocar el agente")
    print("─" * 70)

    estado_inicial = {
        "messages": [HumanMessage(content="Calcula 100 + 200")]
    }

    resultado = app.invoke(estado_inicial, config)

    print("\n⏸️  EL GRAFO SE PAUSÓ")
    print("─" * 70)

    # Verificar el estado
    state = app.get_state(config)
    print(f"   Siguiente nodo a ejecutar: {state.next}")
    print(f"   El agente quiere ejecutar: {state.values['messages'][-1].tool_calls[0]['name']}")

    print("\n💡 El grafo está esperando tu aprobación para continuar.")

    # ────────────────────────────────────────────────────────────────────
    # Segunda invocación: Continuar desde donde se pausó
    # ────────────────────────────────────────────────────────────────────
    print("\n✅ Paso 2: Aprobar y continuar")
    print("─" * 70)

    # Para continuar, simplemente invocamos de nuevo con None
    resultado_final = app.invoke(None, config)

    print(f"\n📨 Respuesta final:")
    print(f"   {resultado_final['messages'][-1].content}")


def demo_aprobar_o_rechazar():
    """
    Demo avanzada: Aprobar, rechazar o modificar la acción.
    """
    print("\n" + "=" * 70)
    print("  DEMO 2: Aprobar, Rechazar o Modificar")
    print("=" * 70)

    app = crear_grafo_con_interrupt()
    config = {"configurable": {"thread_id": "demo-2"}}

    # ────────────────────────────────────────────────────────────────────
    # Invocar: Agente quiere enviar un email (acción crítica)
    # ────────────────────────────────────────────────────────────────────
    print("\n🚀 El agente quiere enviar un email")
    print("─" * 70)

    estado_inicial = {
        "messages": [
            HumanMessage(
                content="Envía un email a juan@example.com con asunto 'Reunión' "
                        "y cuerpo 'Confirma tu asistencia a la reunión de mañana.'"
            )
        ]
    }

    app.invoke(estado_inicial, config)

    # Ver qué quiere hacer
    state = app.get_state(config)
    tool_call = state.values['messages'][-1].tool_calls[0]

    print(f"\n⚠️  ACCIÓN CRÍTICA DETECTADA:")
    print(f"   Tool: {tool_call['name']}")
    print(f"   Args: {json.dumps(tool_call['args'], indent=4, ensure_ascii=False)}")

    # ────────────────────────────────────────────────────────────────────
    # Opción 1: APROBAR (simplemente continuar)
    # ────────────────────────────────────────────────────────────────────
    print("\n✅ Aprobando la acción...")
    resultado = app.invoke(None, config)
    print(f"   {resultado['messages'][-1].content}")

    print("\n💡 En un sistema real, aquí podrías:")
    print("   - Aprobar: app.invoke(None, config)")
    print("   - Rechazar: app.update_state(config, {...}) con mensaje de rechazo")
    print("   - Modificar: app.update_state(config, {...}) con args editados")


def demo_update_state():
    """
    Demo de modificar el estado durante la interrupción.
    """
    print("\n" + "=" * 70)
    print("  DEMO 3: Modificar Estado Durante Interrupción")
    print("=" * 70)

    app = crear_grafo_con_interrupt()
    config = {"configurable": {"thread_id": "demo-3"}}

    # Invocar
    app.invoke(
        {"messages": [HumanMessage(content="Calcula 50 * 2")]},
        config
    )

    print("\n⏸️  Grafo pausado. Vamos a MODIFICAR el estado.")

    # Obtener estado actual
    state = app.get_state(config)
    print(f"\n📊 Tool call original:")
    print(f"   {state.values['messages'][-1].tool_calls[0]}")

    # Modificar el estado (cambiar la expresión)
    print(f"\n🔧 Modificando la expresión de '50 * 2' a '50 * 3'...")

    # Crear nuevo mensaje modificado
    mensaje_original = state.values['messages'][-1]
    mensaje_modificado = AIMessage(
        content=mensaje_original.content,
        tool_calls=[{
            **mensaje_original.tool_calls[0],
            "args": {"expresion": "50 * 3"}  # Modificamos aquí
        }]
    )

    # Actualizar el estado
    app.update_state(
        config,
        {"messages": [mensaje_modificado]},
        as_node="agent"  # Actualizamos como si viniéramos del nodo "agent"
    )

    print(f"   ✅ Estado actualizado")

    # Continuar con el estado modificado
    resultado = app.invoke(None, config)

    print(f"\n📨 Resultado (con expresión modificada):")
    print(f"   {resultado['messages'][-1].content}")
    print(f"\n💡 Calculó 50 * 3 = 150 en vez de 50 * 2 = 100")


# ============================================================================
# EJECUTAR DEMOS
# ============================================================================

def main():
    print("\n🎓 APRENDIENDO HUMAN-IN-THE-LOOP EN LANGGRAPH")

    # Demo 1: Interrupción básica
    demo_interrupt_basic()

    # Demo 2: Aprobar o rechazar
    demo_aprobar_o_rechazar()

    # Demo 3: Modificar estado
    demo_update_state()


# ============================================================================
# CONCEPTOS CLAVE APRENDIDOS
# ============================================================================
"""
1. interrupt_before=["nodo"]
   - Pausa el grafo ANTES de ejecutar ese nodo
   - El grafo retorna control al código
   - Estado queda guardado en el checkpoint

2. interrupt_after=["nodo"]
   - Pausa el grafo DESPUÉS de ejecutar ese nodo
   - Útil para revisar resultados antes de continuar

3. .get_state(config)
   - Ver el estado actual durante la interrupción
   - state.next muestra qué nodo se ejecutará después
   - state.values tiene el estado completo

4. app.invoke(None, config)
   - Continuar desde donde se pausó
   - None = no agregar nuevo input, solo continuar
   - Ejecuta el siguiente nodo (el que estaba en state.next)

5. app.update_state(config, values, as_node="...")
   - Modificar el estado durante la interrupción
   - values: dict con campos a actualizar
   - as_node: simula que la actualización viene de ese nodo

6. Casos de Uso Reales
   - Aprobar envío de emails/mensajes
   - Confirmar compras o transacciones
   - Revisar código generado antes de ejecutar
   - Editar respuestas del LLM antes de enviar al usuario
   - Intervención humana en decisiones críticas

FLUJO CON INTERRUPT:
  1. app.invoke(input, config) → Se ejecuta hasta el interrupt
  2. app.get_state(config) → Revisar qué quiere hacer
  3. Decidir: aprobar, rechazar o modificar
  4. app.invoke(None, config) → Continuar (si aprobaste)
     O app.update_state(...) → Modificar (si rechazaste/editaste)

PRÓXIMO PASO: En el archivo 05 aprenderemos STREAMING
para ver respuestas del LLM en tiempo real (token by token).
"""


if __name__ == "__main__":
    main()
