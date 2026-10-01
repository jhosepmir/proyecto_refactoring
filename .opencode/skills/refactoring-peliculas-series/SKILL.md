---
name: refactoring-peliculas-series
description: Refactoriza codigo Python 3.11+ eliminando malas practicas sin cambiar su comportamiento: estado global mutable, wildcard imports, concatenacion de strings, falta de type hints, duplicacion, bare except, clases de datos y dependencias ocultas. Exige analisis previo, validacion con tests, evitar over-refactoring e informe obligatorio. Usar para refactor, limpieza de codigo, deuda tecnica, malas practicas, Python.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: quality
  triggers: refactor, refactoring, malas practicas, code smell, deuda tecnica, clean code, Python
  role: specialist
  scope: quality
  related-skills: python-pro, code-reviewer, api-integration
---
# Skill: Refactoring

**Proposito**: mejorar la estructura y el diseño del codigo Python eliminando malas practicas, **sin modificar su comportamiento funcional**.

**Alcance**: codigo Python 3.11+ (proyecto actual: 3.12). La metodologia completa de testing pertenece a la skill `testing`; aqui solo se exige identificar y ejecutar los tests relevantes.

---

## 0. Principio fundamental: preservar el comportamiento

Un refactoring mejora la estructura del codigo **sin cambiar lo que el codigo hace**. Se debe preservar:

- logica de negocio;
- contratos publicos (firmas, parametros, valores de retorno que consumen otros modulos);
- APIs y formatos de respuesta;
- comportamiento observable (salidas, mensajes, efectos secundarios relevantes);
- funcionalidades existentes.

Si un cambio funcional fuera realmente necesario, debe identificarse **explicitamente** como tal en el informe y separarse del refactoring. Nunca disfrazar un cambio de comportamiento de refactorizacion.

---

## 1. Analisis antes de modificar (obligatorio)

Antes de editar codigo, analizar:

1. estructura del proyecto;
2. dependencias entre modulos;
3. modulos afectados por el cambio;
4. interfaces publicas (exports, firmas, contratos);
5. logica de negocio;
6. tests existentes que cubren el area;
7. posibles efectos secundarios;
8. duplicacion existente;
9. acoplamiento;
10. riesgos del refactoring.

Entender primero el codigo, modificar despues. No realizar una reescritura masiva sin justificacion.

---

## 2. Reglas de refactoring

### 2.1 Variables globales

Buscar y eliminar **estado global mutable** cuando sea apropiado. Distinguir siempre:

| Tipo | Ejemplo | Accion |
|---|---|---|
| Estado global mutable | `dict`/`list` global modificado en runtime | encapsular en clase/servicio o inyectar |
| Constantes inmutables | `MAX_RETRIES = 3` | conservar; no es mala practica |
| Configuracion | modulo `config.py` | conservar como configuracion; inyectarla donde se consuma |
| Dependencias externas | cliente HTTP, conexion a BD | inyectar por constructor; no crearlas ni importarlas como globals |

No tratar toda variable global como mala practica: el problema es el **estado mutable compartido** que dificulta razonamiento y testing.

Cuando corresponda: encapsular el estado, moverlo a servicios o clases, o aplicar inyeccion de dependencias (ver 2.9).

### 2.2 Wildcard imports

Eliminar `from module import *` y reemplazarlos por imports explicitos:

```python
from services.movie_service import buscar_pelicula, obtener_detalles
```

El refactoring **no debe introducir dependencias circulares** (A importa B y B importa A). Si aparece un ciclo, resolverlo reorganizando responsabilidades, no con imports diferidos ad-hoc.

### 2.3 Strings

Preferir f-strings para interpolacion:

```python
message = f"Movie: {movie.title}"
```

No convertir mecanicamente todos los `+`. Distinguir:

- **interpolacion de strings** → convertir a f-string;
- **concatenacion deliberada** (constantes unidas, mensajes largos partidos en lineas) → conservar si es mas legible;
- **operaciones donde `+` tenga otro significado** (listas, numeros, objetos con `__add__` propio) → no tocar.

### 2.4 Type hints (Python 3.11+)

- agregar type hints a funciones y metodos **nuevos o modificados**;
- agregar type hints a atributos **nuevos o modificados**;
- utilizar tipos especificos (`list[str]`, `dict[str, int]`, `Movie | None`) en lugar de genericos cuando exista uno mas preciso;
- evitar `Any` cuando pueda utilizarse un tipo mas preciso; si es imprescindible, documentar el motivo.

```python
def get_movie(movie_id: int) -> Movie:
    ...
```

No es obligatorio tipar el codigo que no se toca: la regla aplica al codigo nuevo o modificado.

### 2.5 Separacion de responsabilidades

Promover una separacion clara entre responsabilidades reales. Estructura de referencia (**no obligatoria**):

```text
api/
models/
services/
ui/
exceptions/
utils/
```

- no imponer esta estructura literalmente en todos los proyectos;
- no crear modulos artificialmente pequenos;
- no mover codigo solamente para "cumplir una arquitectura";
- toda separacion debe estar justificada por responsabilidades reales, con una razon de ser clara para cada modulo resultante.

### 2.6 Codigo duplicado

Detectar y eliminar duplicacion real: funciones, validaciones, constantes, transformaciones, manejo de errores y logica repetida. Extraer codigo comun cuando exista una responsabilidad genuinamente compartida.

Evitar abstracciones prematuras: dos apariciones de un fragmento corto no justifican por si solas una jerarquia de clases. Preferir extraer una funcion pequena antes que construir una abstraccion general.

### 2.7 Excepciones

Eliminar los `except:` (bare except) y usar excepciones especificas:

```python
except SomeError as exc:
    raise DomainError(...) from exc
```

- capturar solo lo que puede fallar realmente en esa operacion;
- no utilizar `except Exception:` como sustituto generico: se tolera unicamente en la ultima capa de proteccion de la aplicacion (entrada principal), donde debe loguear el error sin exponer trazas al usuario;
- conservar la causa original con `raise ... from exc`;
- se pueden crear jerarquias de excepciones cuando mejoren la arquitectura (p. ej. una base `ApplicationError` con especializaciones por dominio).

### 2.8 Dataclasses

Cuando existan clases que representen principalmente datos, evaluar el uso de `@dataclass`:

```python
@dataclass
class Movie:
    id: int
    title: str
    year: int
```

Aplicar el mismo criterio a modelos como `Series`.

**No convertir automaticamente todas las clases en dataclasses.** No utilizarlas cuando la clase tenga comportamiento complejo, invariantes que deban mantenerse, lifecycle propio o una arquitectura que no lo justifica.

### 2.9 Inyeccion de dependencias

Promover la inyeccion de dependencias para: clientes HTTP, bases de datos, configuracion, servicios externos, APIs, filesystem y cualquier otro recurso externo. Evitar dependencias ocultas en variables globales.

```python
class MovieService:
    def __init__(
        self,
        client: MovieClient,
        config: Config,
    ) -> None:
        self.client = client
        self.config = config
```

Objetivo: desacoplamiento, testabilidad, mantenibilidad y sustitucion de implementaciones.

---

## 3. Evitar over-refactoring

Prohibido, salvo justificacion explicita en el informe:

- reescrituras innecesarias;
- cambios masivos de una sola vez;
- abstracciones prematuras;
- creacion excesiva de clases;
- creacion excesiva de modulos;
- cambios de nombres publicos sin necesidad;
- cambios arquitectonicos sin justificacion;
- modificaciones no relacionadas con el objetivo de la tarea.

Preferir siempre:

```text
cambio pequeno
→ verificar
→ siguiente cambio
→ verificar
```

ante una reescritura completa. Si el objetivo se alcanza con un cambio local, no reestructurar el modulo entero.

---

## 4. Validacion mediante tests

1. identificar los tests relevantes al area modificada;
2. ejecutarlos **antes y despues** del cambio cuando sea posible;
3. todo cambio critico debe tener una forma razonable de validacion (tests, ejecucion manual del flujo, comparacion de salida);
4. si los tests existentes son insuficientes para cubrir el cambio, señalarlo explicitamente en el informe;
5. el refactoring **no** se considera completamente validado solo porque `pytest` termine correctamente si los tests relevantes son inexistentes o claramente insuficientes.

La metodologia especializada de testing (cobertura, fixtures, mocks, parametrizacion) permanece en la skill `testing`; no duplicar aqui.

### Herramientas de calidad

Cuando esten configuradas en el proyecto, considerar:

```bash
pytest
ruff check .
mypy .
```

- no instalar ni configurar automaticamente estas herramientas si no existen;
- no modificar la configuracion del proyecto solamente para satisfacer esta skill;
- si alguna herramienta no esta disponible, indicarlo en el resultado.

---

## 5. Checklist final

### Codigo

- [ ] Sin variables globales mutables injustificadas.
- [ ] Sin `from x import *`.
- [ ] Sin concatenaciones innecesarias de strings mediante `+`.
- [ ] Type hints en funciones y metodos modificados.
- [ ] Type hints en atributos modificados.
- [ ] Sin `bare except`.
- [ ] Excepciones especificas.
- [ ] Sin duplicacion evidente.
- [ ] Responsabilidades correctamente separadas.
- [ ] Dataclasses utilizadas cuando corresponda.
- [ ] Dependencias inyectadas cuando corresponda.
- [ ] No se introdujeron dependencias circulares.

### Comportamiento

- [ ] No se modifico accidentalmente la logica de negocio.
- [ ] No se eliminaron funcionalidades.
- [ ] No se rompieron interfaces publicas.
- [ ] No se modificaron contratos sin justificacion.

### Validacion

- [ ] Tests relevantes identificados.
- [ ] Tests ejecutados.
- [ ] Resultado de los tests verificado.
- [ ] Ruff ejecutado si esta configurado.
- [ ] Mypy ejecutado si esta configurado.
- [ ] Problemas pendientes documentados.

---

## 6. Informe obligatorio

Al terminar un refactoring, el agente debe informar:

### Problemas encontrados
Que malas practicas fueron detectadas.

### Cambios realizados
Que modificaciones concretas fueron realizadas.

### Archivos modificados
Lista de archivos afectados.

### Arquitectura
Que responsabilidades fueron separadas o desacopladas.

### Dependencias
Que dependencias fueron introducidas, eliminadas o inyectadas.

### Validacion
Que tests y herramientas fueron ejecutados y cual fue su resultado.

### Riesgos
Que problemas o riesgos permanecen.

### Checklist
Que elementos quedaron cumplidos y cuales no, explicando el motivo.
