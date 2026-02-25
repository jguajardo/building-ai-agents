# Fase 1: Fundamentos del SDK de Claude

> **Objetivo:** Entender los conceptos básicos de agentes de IA usando el SDK nativo de Anthropic.

## ✅ Estado: COMPLETADO

---

## 🎯 Conceptos Aprendidos

### 1. Llamada Básica a un LLM
- Crear cliente de Anthropic
- Enviar mensajes y recibir respuestas
- Estructura de mensajes (role: user/assistant)
- Metadata de la respuesta (tokens, stop_reason)

### 2. Tool Calling (Function Calling)
- Definir herramientas con JSON Schema
- El LLM decide cuándo usar herramientas
- Diferencia entre `tool_use` y `end_turn`
- Estructura de tool_result

### 3. El Agentic Loop
- El corazón de cualquier agente de IA
- Loop: mensaje → razonamiento → tool_use? → ejecutar → repetir
- Manejo de múltiples herramientas en una sola respuesta
- Recursión hasta que el LLM termine (`end_turn`)

### 4. Memoria y Conversación
- Memoria = historial completo de mensajes
- Persistir contexto entre turnos
- Sistema de prompt para definir comportamiento
- Loop interactivo con entrada del usuario

---

## 📁 Archivos

### `01_basico.py` - Primera llamada a Claude
```bash
uv run python fase-1-fundamentos/01_basico.py
```

**Qué hace:**
- Llamada más simple posible al API
- Envía un mensaje, recibe una respuesta
- Muestra metadata (tokens, modelo, etc.)

**Conceptos:**
- Cliente de Anthropic
- Estructura de mensajes
- Content blocks (TextBlock)
- Stop reason

---

### `02_con_tools.py` - Definiendo herramientas
```bash
uv run python fase-1-fundamentos/02_con_tools.py
```

**Qué hace:**
- Define herramientas (calculadora, clima)
- Claude decide usar una herramienta
- Muestra cómo se ve un `tool_use` response

**Conceptos:**
- JSON Schema para herramientas
- `stop_reason = "tool_use"`
- ToolUseBlock (name, input, id)
- **Importante:** Claude NO ejecuta la tool, solo decide usarla

---

### `03_agente_loop.py` - El Agentic Loop
```bash
uv run python fase-1-fundamentos/03_agente_loop.py
```

**Qué hace:**
- Implementa el loop completo
- Ejecuta herramientas y devuelve resultados
- Continúa hasta que Claude termine
- Incluye diagrama ASCII del flujo

**Conceptos:**
- Loop while con stop_reason
- tool_result structure
- Vincular tool_result con tool_use_id
- Múltiples herramientas en una respuesta
- Recursión del loop

**Diagrama del loop:**
```
┌─────────────────────────────────┐
│      Usuario pregunta           │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Claude procesa el mensaje      │◄──────┐
└──────────────┬──────────────────┘       │
               │                           │
          ¿tool_use?                       │
           /          \                    │
         Sí            No                  │
         │              │                  │
         ▼              ▼                  │
  ┌────────────┐ ┌──────────┐             │
  │ Ejecutar   │ │ Responder│             │
  │ herramienta│ │ al usuario│            │
  └─────┬──────┘ └──────────┘             │
        │                                  │
        │  Enviar resultado                │
        └──────────────────────────────────┘
```

---

### `04_agente_completo.py` - Agente Interactivo
```bash
uv run python fase-1-fundamentos/04_agente_completo.py
```

**Qué hace:**
- Agente completo con loop interactivo de terminal
- Mantiene historial de conversación (memoria)
- System prompt configurable
- Múltiples herramientas (calculadora, clima, hora)
- Escribe "salir" para terminar

**Conceptos:**
- System prompt para definir personalidad/comportamiento
- Memoria mediante historial completo de mensajes
- Input loop del usuario
- Manejo de múltiples tools en secuencia
- Función recursiva para procesar respuestas

---

## 🎓 Lecciones Clave

### 1. Los LLMs NO ejecutan código
El LLM solo **decide** qué herramienta usar y con qué parámetros.
**Tú** ejecutas la herramienta y devuelves el resultado.

### 2. El Agentic Loop es simple pero poderoso
```python
while True:
    response = llm.call(messages)
    if response.stop_reason == "end_turn":
        break
    # Ejecutar tools
    # Agregar resultados a messages
    # Continuar loop
```

### 3. Memoria = Historial
Los LLMs no tienen memoria real. Simulamos memoria pasando todo el historial de mensajes en cada llamada.

### 4. System Prompt es crítico
Define el comportamiento, personalidad y capacidades del agente.

---

## 🚀 Cómo Ejecutar Todo

```bash
# Asegúrate de tener la API key configurada
export ANTHROPIC_API_KEY="tu-api-key"

# Ejecutar cada ejemplo
uv run python fase-1-fundamentos/01_basico.py
uv run python fase-1-fundamentos/02_con_tools.py
uv run python fase-1-fundamentos/03_agente_loop.py
uv run python fase-1-fundamentos/04_agente_completo.py
```

---

## 🔗 Recursos

- [Anthropic API Docs](https://docs.anthropic.com/)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Prompt Engineering](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering)

---

## ➡️ Próximo Paso

**Fase 2: LangGraph** - Aprenderemos a construir agentes más estructurados usando grafos de estado, con checkpointing, human-in-the-loop y mejor control del flujo.

---

**Completado:** 2026-02-25
**Tiempo invertido:** ~1-2 horas
**Archivos:** 4
**Líneas de código:** ~300
