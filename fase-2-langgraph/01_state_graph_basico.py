"""
FASE 2 - PASO 1: StateGraph Básico
===================================
Tu primer grafo de estado con LangGraph.

Concepto clave:
  Un StateGraph es un grafo dirigido donde cada NODO es una función
  que puede leer y modificar el ESTADO.

¿Por qué grafos?
  - Visualizable: Puedes ver el flujo de tu agente
  - Estructurado: Separación clara entre lógica y flujo
  - Debuggeable: Sabes exactamente en qué nodo estás
  - Componible: Puedes reutilizar nodos y subgrafos

Comparación con Fase 1:
  Fase 1: while loop manual con if/else mezclado con lógica
  Fase 2: Grafo declarativo con nodos y edges explícitos

Antes de ejecutar:
  export ANTHROPIC_API_KEY="tu-api-key"

Ejecutar:
  uv run python fase-2-langgraph/01_state_graph_basico.py
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic

# ============================================================================
# 1. DEFINIR EL ESTADO
# ============================================================================
# El estado es lo que se pasa entre nodos.
# TypedDict define la estructura del estado.

class AgentState(TypedDict):
    """
    Estado del agente. Cada nodo puede leer y modificar estos campos.

    Campos:
      - messages: Historial de mensajes (user/assistant)
      - contador: Un contador simple para demostrar que el estado persiste
    """
    messages: list[dict]
    contador: int


# ============================================================================
# 2. DEFINIR NODOS (Funciones que procesan el estado)
# ============================================================================
# Cada nodo es una función que:
#   - Recibe el estado actual
#   - Hace algo (llamar LLM, ejecutar tool, etc.)
#   - Retorna un dict con los campos a actualizar

def nodo_inicio(state: AgentState) -> dict:
    """
    Nodo de entrada: inicializa el estado.
    En un agente real, aquí podrías validar inputs, cargar contexto, etc.
    """
    print(f"📍 Nodo: INICIO")
    print(f"   Estado recibido: {state}")

    return {
        "contador": state.get("contador", 0) + 1,
        # No modificamos messages todavía
    }


def nodo_llamar_llm(state: AgentState) -> dict:
    """
    Nodo principal: llama al LLM con los mensajes actuales.
    """
    print(f"\n📍 Nodo: LLAMAR_LLM")
    print(f"   Contador: {state['contador']}")
    print(f"   Mensajes actuales: {len(state['messages'])}")

    # Crear el modelo (Claude)
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

    # Llamar al LLM
    # LangGraph trabaja con el formato de LangChain (más abstracto que el SDK puro)
    response = llm.invoke(state["messages"])

    print(f"   Respuesta del LLM: {response.content[:100]}...")

    # Retornar el nuevo mensaje en el historial
    return {
        "messages": state["messages"] + [
            {"role": "assistant", "content": response.content}
        ]
    }


def nodo_final(state: AgentState) -> dict:
    """
    Nodo de salida: muestra resultados finales.
    En un agente real, aquí podrías formatear la respuesta, guardar logs, etc.
    """
    print(f"\n📍 Nodo: FINAL")
    print(f"   Procesado {state['contador']} vez/veces")
    print(f"   Total de mensajes: {len(state['messages'])}")

    return {}  # No modificamos nada


# ============================================================================
# 3. CONSTRUIR EL GRAFO
# ============================================================================

def crear_grafo():
    """
    Construye el grafo de estado.

    Flujo:
      START → inicio → llamar_llm → final → END
    """
    # Crear el grafo con el tipo de estado
    graph = StateGraph(AgentState)

    # Agregar nodos (nombre del nodo → función)
    graph.add_node("inicio", nodo_inicio)
    graph.add_node("llamar_llm", nodo_llamar_llm)
    graph.add_node("final", nodo_final)

    # Definir edges (conexiones entre nodos)
    # Estos son "edges fijos": siempre van del nodo A al nodo B
    graph.add_edge(START, "inicio")        # Empieza en "inicio"
    graph.add_edge("inicio", "llamar_llm") # inicio → llamar_llm
    graph.add_edge("llamar_llm", "final")  # llamar_llm → final
    graph.add_edge("final", END)           # final → END (termina)

    # Compilar el grafo (lo convierte en un ejecutable)
    return graph.compile()


# ============================================================================
# 4. EJECUTAR EL GRAFO
# ============================================================================

def main():
    print("=" * 70)
    print("  StateGraph Básico - Tu Primer Grafo con LangGraph")
    print("=" * 70)

    # Crear el grafo
    app = crear_grafo()

    # Estado inicial
    estado_inicial = {
        "messages": [
            {"role": "user", "content": "Explícame en 2 líneas qué es un grafo de estado."}
        ],
        "contador": 0,
    }

    print(f"\n🚀 Ejecutando grafo con estado inicial:")
    print(f"   Mensaje del usuario: {estado_inicial['messages'][0]['content']}")

    # Ejecutar el grafo
    # .invoke() ejecuta el grafo completo de principio a fin
    resultado = app.invoke(estado_inicial)

    print("\n" + "=" * 70)
    print("✅ RESULTADO FINAL")
    print("=" * 70)
    print(f"Contador: {resultado['contador']}")
    print(f"\nConversación completa:")
    for i, msg in enumerate(resultado["messages"], 1):
        role = msg["role"].upper()
        content = msg["content"]
        print(f"\n{i}. {role}:")
        print(f"   {content}")


# ============================================================================
# CONCEPTOS CLAVE APRENDIDOS
# ============================================================================
"""
1. StateGraph(AgentState)
   - Define un grafo con un tipo de estado específico
   - El estado se pasa entre nodos automáticamente

2. Nodos (add_node)
   - Funciones que procesan el estado
   - Reciben state, retornan dict con campos a actualizar
   - LangGraph hace merge automático

3. Edges (add_edge)
   - Conexiones fijas entre nodos
   - add_edge(A, B) = "siempre ir de A a B"

4. START y END
   - START: punto de entrada del grafo
   - END: punto de salida del grafo

5. .compile() y .invoke()
   - compile(): convierte el grafo en ejecutable
   - invoke(state): ejecuta el grafo con un estado inicial

PRÓXIMO PASO: En el archivo 02 aprenderemos edges CONDICIONALES
para implementar el agentic loop con decisiones.
"""


if __name__ == "__main__":
    main()
