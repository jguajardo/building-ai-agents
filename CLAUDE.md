# Instrucciones para Claude Code

Este proyecto es para **aprender a construir agentes de IA** como parte de mi formación como Ingeniero de IA.

## Contexto del Proyecto

- **Objetivo:** Entender desde cero cómo funcionan los agentes de IA
- **Progresión:** SDK de Claude → LangGraph → LangChain
- **Nivel actual:** Completamos fundamentos del SDK de Claude
- **Próximo paso:** Implementar agentes con LangGraph

## Estado Actual

### ✅ Completado
- `01_basico.py` - Llamada básica a Claude API
- `02_con_tools.py` - Definición de herramientas (function calling)
- `03_agente_loop.py` - El agentic loop completo
- `04_agente_completo.py` - Agente interactivo con memoria

### 🎯 En Progreso
- Migrar a LangGraph para entender grafos de estado
- Implementar checkpointing y memoria persistente
- Agregar human-in-the-loop patterns

### 📋 Próximos Hitos
1. Crear ejemplos con LangGraph (`05_langgraph_basico.py`)
2. Refactorizar usando LangChain SDK
3. Implementar RAG con vector database
4. Construir API REST con FastAPI
5. Deploy en cloud (AWS/GCP)

## Estilo de Código

- **Lenguaje:** Python 3.13+
- **Gestor de dependencias:** uv (NO pip)
- **Formato:** Código limpio, bien comentado, educativo
- **Docstrings:** Siempre explicar QUÉ hace y POR QUÉ
- **Ejemplos:** Incluir ejemplos de uso en cada archivo
- **Progresión:** Cada archivo debe ser más complejo que el anterior

## Preferencias de Desarrollo

### Al escribir código:
- ✅ Explicaciones detalladas en comentarios
- ✅ Código didáctico (priorizar claridad sobre brevedad)
- ✅ Incluir diagramas ASCII cuando ayude
- ✅ Mostrar el "por qué" de cada decisión
- ✅ Comparar diferentes enfoques

### Al agregar dependencias:
```bash
uv add nombre-paquete
```

### Estructura de archivos nuevos:
```python
"""
TÍTULO DEL EJEMPLO
==================
Explicación breve de qué aprenderemos aquí.

Conceptos clave:
  - Concepto 1
  - Concepto 2

Antes de ejecutar:
  [instrucciones de setup si aplica]

Ejecutar:
  uv run python nombre_archivo.py
"""

# Imports
import ...

# Código bien documentado
...
```

## Aprendizaje y Documentación

- **README.md:** Mantenerlo actualizado con cada avance
- **Logging:** Usar print() detallado para ver qué hace el agente
- **Errores:** Explicarlos, no solo corregirlos
- **Comparaciones:** Si hay múltiples formas de hacer algo, mostrar las opciones

## Recursos Importantes

- Docs de Anthropic: https://docs.anthropic.com/
- LangChain: https://python.langchain.com/
- LangGraph: https://langchain-ai.github.io/langgraph/

## Objetivo Final

Construir un portfolio sólido que demuestre:
1. Entendimiento profundo de agentes de IA
2. Capacidad de usar frameworks modernos (LangChain, LangGraph)
3. Mejores prácticas de MLOps
4. Proyectos deployables en producción

---

**Nota:** Estoy aprendiendo, así que valoro explicaciones claras sobre decisiones técnicas y alternativas.
