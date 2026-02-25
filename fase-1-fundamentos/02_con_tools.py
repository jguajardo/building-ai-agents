"""
PASO 2: Definir herramientas (Tools)
=====================================
Aquí le damos "superpoderes" a Claude: herramientas que puede decidir usar.

Claude NO ejecuta las herramientas. Solo DECIDE cuál usar y con qué parámetros.
Tú ejecutas la herramienta y le devuelves el resultado.

Concepto clave:
  - Tú defines las herramientas con un JSON Schema
  - Claude analiza el mensaje del usuario
  - Si necesita una herramienta, responde con stop_reason="tool_use"
  - En vez de texto, te da el nombre de la tool y los argumentos

Ejecutar:
  uv run python 02_con_tools.py
"""

import anthropic

client = anthropic.Anthropic()

# 1. Definir las herramientas disponibles
#    Cada herramienta tiene: name, description, input_schema (JSON Schema)
tools = [
    {
        "name": "calculadora",
        "description": "Realiza operaciones matemáticas. Usa esta herramienta cuando el usuario pida cálculos.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operacion": {
                    "type": "string",
                    "description": "La operación matemática a evaluar, ej: '2 + 2', '100 * 3.14'"
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
                    "description": "Nombre de la ciudad, ej: 'Madrid', 'Ciudad de México'"
                }
            },
            "required": ["ciudad"],
        },
    },
]

# 2. Enviar un mensaje que REQUIERE usar una herramienta
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=tools,  # <-- Le pasamos las herramientas disponibles
    messages=[
        {"role": "user", "content": "¿Cuánto es 1547 * 38?"}
    ],
)

# 3. Observar la respuesta
print(f"Stop reason: {response.stop_reason}")
# Será "tool_use" en vez de "end_turn"

print(f"\nBloques en la respuesta:")
for block in response.content:
    print(f"  Tipo: {block.type}")
    if block.type == "tool_use":
        print(f"  Tool: {block.name}")
        print(f"  Input: {block.input}")
        print(f"  ID: {block.id}")  # Necesitarás este ID para devolver el resultado
    elif block.type == "text":
        print(f"  Texto: {block.text}")

# NOTA: Claude NO ejecutó la calculadora. Solo dijo:
# "Quiero usar 'calculadora' con operacion='1547 * 38'"
# En el paso 3 aprenderás a ejecutar la tool y devolver el resultado.
