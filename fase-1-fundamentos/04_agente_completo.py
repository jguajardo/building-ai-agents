"""
PASO 4: Agente interactivo completo
=====================================
Un agente de terminal con:
  - System prompt configurable
  - Memoria de conversación (dentro de la sesión)
  - Múltiples herramientas
  - Loop interactivo (escribe "salir" para terminar)

Ejecutar:
  uv run python 04_agente_completo.py
"""

import json
from datetime import datetime
import anthropic

client = anthropic.Anthropic()

# --- Configuración del agente ---

SYSTEM_PROMPT = """Eres un asistente útil y amigable. Respondes en español.
Tienes acceso a herramientas que puedes usar cuando sea necesario.
Si no necesitas herramientas, responde directamente."""

MODEL = "claude-sonnet-4-5-20250929"

# --- Herramientas ---

TOOLS = [
    {
        "name": "calculadora",
        "description": "Evalúa expresiones matemáticas. Úsala para cualquier cálculo.",
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
    {
        "name": "hora_actual",
        "description": "Obtiene la fecha y hora actual.",
        "input_schema": {
            "type": "object",
            "properties": {},
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
        # En un agente real, aquí llamarías a una API como OpenWeather
        climas = {
            "madrid": "Soleado, 22°C, humedad 40%",
            "ciudad de méxico": "Nublado, 18°C, humedad 65%",
            "buenos aires": "Lluvioso, 15°C, humedad 80%",
            "bogotá": "Parcialmente nublado, 14°C, humedad 72%",
            "lima": "Nublado, 20°C, humedad 85%",
        }
        ciudad = argumentos["ciudad"].lower()
        clima = climas.get(ciudad, f"No tengo datos para {argumentos['ciudad']}")
        return json.dumps({"clima": clima})

    elif nombre == "hora_actual":
        ahora = datetime.now()
        return json.dumps({
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S"),
            "dia_semana": ahora.strftime("%A"),
        })

    return json.dumps({"error": f"Herramienta '{nombre}' no encontrada"})


def procesar_respuesta(response, messages: list) -> str:
    """
    Procesa la respuesta de Claude.
    Si hay tool_use, ejecuta las tools y hace otra llamada.
    Retorna el texto final.
    """
    # Si Claude terminó de hablar, extraer el texto
    if response.stop_reason == "end_turn":
        textos = []
        for block in response.content:
            if hasattr(block, "text"):
                textos.append(block.text)
        return "\n".join(textos)

    # Si Claude quiere usar herramientas
    if response.stop_reason == "tool_use":
        # Guardar la respuesta de Claude en el historial
        messages.append({"role": "assistant", "content": response.content})

        # Ejecutar cada herramienta solicitada
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  🔧 Usando: {block.name}({json.dumps(block.input, ensure_ascii=False)})")
                resultado = ejecutar_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": resultado,
                })

        # Enviar resultados a Claude
        messages.append({"role": "user", "content": tool_results})

        # Nueva llamada a Claude con los resultados
        nueva_respuesta = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Recursión: puede que Claude quiera usar más herramientas
        return procesar_respuesta(nueva_respuesta, messages)

    return "[Sin respuesta]"


def main():
    """Loop principal del agente interactivo."""
    print("=" * 60)
    print("  Agente con Claude SDK")
    print("  Herramientas: calculadora, clima, hora")
    print("  Escribe 'salir' para terminar")
    print("=" * 60)

    # El historial de mensajes persiste durante toda la sesión
    # Esto le da "memoria" al agente
    messages = []

    while True:
        # Leer input del usuario
        print()
        user_input = input("Tú: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ("salir", "exit", "quit"):
            print("¡Hasta luego!")
            break

        # Agregar mensaje del usuario al historial
        messages.append({"role": "user", "content": user_input})

        # Llamar a Claude con todo el historial + tools
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,  # <-- Todo el historial, esto es la "memoria"
        )

        # Procesar (puede involucrar múltiples llamadas si hay tools)
        texto_final = procesar_respuesta(response, messages)

        # Guardar la respuesta final en el historial
        messages.append({"role": "assistant", "content": texto_final})

        print(f"\nClaude: {texto_final}")


if __name__ == "__main__":
    main()
