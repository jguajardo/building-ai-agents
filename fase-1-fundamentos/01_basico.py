"""
PASO 1: Llamada básica a Claude
================================
Esto es lo más simple que puedes hacer con el SDK.
Envías un mensaje, Claude responde. Sin herramientas, sin agentes.

Antes de ejecutar:
  export ANTHROPIC_API_KEY="tu-api-key"

Ejecutar:
  uv run python 01_basico.py
"""

import anthropic

# 1. Crear el cliente (usa ANTHROPIC_API_KEY del entorno automáticamente)
client = anthropic.Anthropic()

# 2. Enviar un mensaje a Claude
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",  # El modelo a usar
    max_tokens=1024,                      # Límite de tokens en la respuesta
    messages=[
        # Cada mensaje tiene un "role" (user/assistant) y "content"
        {"role": "user", "content": "Explícame qué es un agente de IA en 3 líneas."}
    ],
)

# 3. La respuesta viene en response.content, que es una lista de bloques
#    Para texto simple, el primer bloque es de tipo TextBlock
print(response.content[0].text)

# 4. Información útil de la respuesta:
print(f"\n--- Metadata ---")
print(f"Modelo usado: {response.model}")
print(f"Razón de parada: {response.stop_reason}")  # "end_turn" = terminó normalmente
print(f"Tokens entrada: {response.usage.input_tokens}")
print(f"Tokens salida: {response.usage.output_tokens}")
