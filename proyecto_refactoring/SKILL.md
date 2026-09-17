# SKILLS PARA OPENCODE

## Que es un Skill?

Un skill es un conjunto de instrucciones que le dan a un agente IA como opencode
habilidades especializadas para tareas especificas.

## Estructura de un Skill

```
.opencode/skills/
  nombre-skill/
    skill.json
    instrucciones.md
```

## Los 3 Skills a Crear

### SKILL 1: Refactoring

**Proposito**: Eliminar malas practicas del codigo y mejorar su estructura.

**Archivo**: `.opencode/skills/refactoring/skill.json`

```json
{
  "name": "refactoring",
  "description": "Refactorizar codigo Python con malas practicas",
  "instructions": "instrucciones.md"
}
```

**Contenido de instrucciones.md**:

- Buscar y eliminar variables globales
- Reemplazar wildcard imports por imports especificos
- Convertir concatenacion de strings a f-strings
- Agregar type hints a funciones
- Separar responsabilidades en modulos
- Eliminar codigo duplicado
- Reemplazar bare except por excepciones especificas
- Crear dataclasses para modelos de datos
- Implementar inyeccion de dependencias

---

### SKILL 2: API Integration

**Proposito**: Conectar a APIs REST de forma robusta y mantenible.

**Archivo**: `.opencode/skills/api-integration/skill.json`

```json
{
  "name": "api-integration",
  "description": "Integrar APIs REST en Python",
  "instructions": "instrucciones.md"
}
```

**Contenido de instrucciones.md**:

- Crear clientes para cada API
- Implementar cache de respuestas
- Agregar reintentos con backoff exponencial
- Manejar rate limiting
- Validar respuestas con pydantic o dataclasses
- Logging de requests y responses
- Timeouts configurables
- Manejo de errores HTTP

---

### SKILL 3: Testing

**Proposito**: Crear tests automaticos para validar el codigo.

**Archivo**: `.opencode/skills/testing/skill.json`

```json
{
  "name": "testing",
  "description": "Crear tests con pytest",
  "instructions": "instrucciones.md"
}
```

**Contenido de instrucciones.md**:

- Estructura de tests/ con pytest
- Tests unitarios para servicios
- Mock de APIs externas con pytest-mock
- Fixtures para datos de prueba
- Parametrizacion de tests
- Coverage con pytest-cov
- Tests de integracion
- Arrange-Act-Assert pattern

---

## Como Usar los Skills

1. Crear directorio `.opencode/skills/`
2. Para cada skill, crear subdirectorio con skill.json e instrucciones.md
3. opencode cargara automaticamente los skills al iniciar
4. Usar el skill con: `/skill nombre-del-skill`

## Referencias

- Opencode docs: https://opencode.ai
- Python typing: https://docs.python.org/3/library/typing.html
- Pytest: https://docs.pytest.org/
