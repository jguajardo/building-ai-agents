"""
PASO 3: El Agentic Loop (el corazón de un agente)
===================================================
Este es EL concepto más importante. Un agente es simplemente un LOOP:

  1. Usuario envía mensaje
  2. Claude responde (puede ser texto O tool_use)
  3. Si es tool_use → ejecutas la tool → envías el resultado → vuelve a paso 2
  4. Si es texto (end_turn) → muestras la respuesta → fin

          ┌─────────────────────────────────┐
          │         Usuario pregunta         │
          └──────────────┬──────────────────┘
                         │
                         ▼
          ┌─────────────────────────────────┐
          │    Claude procesa el mensaje     │◄──────┐
          └──────────────┬──────────────────┘       │
                         │                           │
                    ¿tool_use?                       │
                   /          \                      │
                 Sí            No                    │
                 │              │                    │
                 ▼              ▼                    │
          ┌────────────┐ ┌──────────┐               │
          │ Ejecutar   │ │ Mostrar  │               │
          │ herramienta│ │ respuesta│               │
          └─────┬──────┘ └──────────┘               │
                │                                    │
                │  Enviar resultado                  │
                └────────────────────────────────────┘

Ejecutar:
  uv run python 03_agente_loop.py
"""

import json
import anthropic

client = anthropic.Anthropic()

# --- Herramientas: definición + implementación ---

tools = [
    {
        "name": "calculadora",
        "description": "Realiza operaciones matemáticas.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operacion": {
                    "type": "string",
                    "description": "Expresión matemática a evaluar, ej: '2 + 2'"
                }
            },
            "required": ["operacion"],
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
    """Ejecuta una herramienta y devuelve el resultado como string."""
    if nombre == "calculadora":
        try:
            # En producción NUNCA uses eval() - aquí es solo para aprender
            resultado = eval(argumentos["operacion"])
            return json.dumps({"resultado": resultado})
        except Exception as e:
            return json.dumps({"error": str(e)})

    elif nombre == "obtener_clima":
        # Simulamos una API de clima (en un agente real, llamarías a una API)
        climas = {
            "madrid": "Soleado, 22°C",
            "ciudad de méxico": "Nublado, 18°C",
            "buenos aires": "Lluvioso, 15°C",
        }
        ciudad = argumentos["ciudad"].lower()
        clima = climas.get(ciudad, f"No tengo datos para {argumentos['ciudad']}")
        return json.dumps({"clima": clima})

    return json.dumps({"error": f"Herramienta '{nombre}' no encontrada"})


# --- El Agentic Loop ---

def ejecutar_agente(pregunta: str):
    """Ejecuta el loop completo del agente para una pregunta."""
    print(f"\n{'='*60}")
    print(f"Usuario: {pregunta}")
    print(f"{'='*60}")

    messages = [{"role": "user", "content": pregunta}]

    # El loop: seguimos mientras Claude quiera usar herramientas
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        # Caso 1: Claude terminó de responder (no necesita más tools)
        if response.stop_reason == "end_turn":
            # Extraer el texto final
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nClaude: {block.text}")
            break

        # Caso 2: Claude quiere usar una herramienta
        if response.stop_reason == "tool_use":
            # Agregar la respuesta de Claude al historial
            messages.append({"role": "assistant", "content": response.content})

            # Procesar cada tool_use en la respuesta
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n  [Tool] {block.name}({json.dumps(block.input, ensure_ascii=False)})")

                    # Ejecutar la herramienta
                    resultado = ejecutar_tool(block.name, block.input)
                    print(f"  [Resultado] {resultado}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,  # Vincular con el tool_use original
                        "content": resultado,
                    })

            # Enviar los resultados de vuelta a Claude
            messages.append({"role": "user", "content": tool_results})
            # El loop continúa: Claude procesará los resultados


# --- Probar el agente ---

# Pregunta simple (sin tools)
ejecutar_agente("¿Qué es Python?")

# Pregunta que necesita la calculadora
ejecutar_agente("¿Cuánto es 1547 multiplicado por 38?")

# Pregunta que necesita el clima
ejecutar_agente("¿Qué clima hace en Madrid?")

# Pregunta que necesita AMBAS tools
ejecutar_agente("¿Cuánto es 100 * 22? Y dime qué clima hace en Buenos Aires.")
