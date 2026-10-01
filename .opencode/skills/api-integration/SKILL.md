---
name: api-integration
description: Integra APIs REST en Python 3.11+ con clientes robustos y testeables: HTTP transversal compartido, inyeccion de dependencias, configuracion centralizada, timeouts, retries con backoff exponencial, rate limiting con Retry-After, cache, validacion de respuestas, jerarquia de excepciones, logging seguro con redaccion de secretos y tests sin Internet. Usar para integracion API, cliente REST, HTTP, proveedores externos.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: integration
  triggers: API integration, REST client, HTTP client, retries, backoff, rate limit, cache, secretos
  role: specialist
  scope: integration
  related-skills: python-pro, api-designer, testing
---
# Skill: API Integration

**Proposito**: integrar APIs REST en Python 3.11+ con codigo robusto, seguro, testeable y mantenible.

**Alcance**: vale para cualquier proveedor REST. OMDb y TVMaze se usan unicamente como ejemplos; no son requisitos arquitectonicos. La metodologia general de testing pertenece a la skill `testing`; aqui solo se definen los requisitos de testeo de integraciones API.

---

## 1. Arquitectura de clientes

Un cliente por proveedor cuando existan multiples APIs:

```text
api/
├── omdb.py
├── tvmaze.py
└── http_client.py
```

Cada cliente de proveedor contiene principalmente:

- construccion de requests;
- parametros propios del proveedor;
- autenticacion especifica;
- transformacion y validacion de respuestas;
- errores especificos del proveedor.

El codigo HTTP transversal vive en una capa comun (`http_client`) cuando corresponda. **No duplicar** en cada cliente: timeout, retries, backoff, manejo de HTTP, rate limiting, logging ni transporte HTTP.

### HTTP client compartido

Centraliza solo responsabilidades transversales:

- ejecucion HTTP;
- timeout;
- retries y backoff;
- manejo de conexiones y status codes;
- rate limiting;
- logging seguro.

Los clientes especificos agregan unicamente comportamiento propio del proveedor. Evitar un `http_client` excesivamente inteligente que termine conteniendo logica de negocio de OMDb, TVMaze u otros proveedores.

---

## 2. Dependency Injection

Los clientes API no deben depender de globals:

```python
class OmdbClient:
    def __init__(
        self,
        http_client: HttpClient,
        config: ApiConfig,
    ) -> None:
        self.http_client = http_client
        self.config = config
```

Esto permite: tests, mocks, sustitucion del transporte HTTP y configuracion por entorno.

Evitar dependencias globales ocultas como:

```python
API_KEY = ...
client = requests.Session()
```

Lo mismo aplica a cache, rate limiter y logger: inyectarlos, no importarlos desde un modulo con estado.

---

## 3. Configuracion

Centralizar la configuracion relacionada con APIs, no dispersarla por el codigo:

- base URL;
- timeout;
- max retries;
- backoff;
- API keys;
- rate limits;
- cache TTL;
- headers.

Preferir el mecanismo de configuracion ya existente en el proyecto (variables de entorno, modulo `config`, archivos de configuracion). No introducir un sistema de configuracion nuevo si el actual funciona.

**Nunca almacenar secretos directamente en el codigo fuente.**

---

## 4. Secretos y autenticacion

Proteger: API keys, tokens, Authorization headers, cookies, credenciales y URLs que contengan secretos.

Nunca registrar una URL con credenciales:

```python
logger.debug("GET %s", url_with_api_key)   # prohibido
```

Aplicar una estrategia de sanitizacion/redaccion **antes** de escribir en logs:

```text
apikey=***
Authorization=***
token=***
```

La redaccion debe cubrir los secretos cuando aparezcan en:

- query parameters;
- headers;
- mensajes de error;
- excepciones;
- URLs;
- payloads.

Lo mismo vale para los mensajes de las excepciones: nunca exponer secretos ahi.

---

## 5. Timeouts

Toda llamada HTTP debe tener timeout explicito y configurable; no depender del timeout por defecto de la libreria.

Distinguir, cuando corresponda:

- connect timeout;
- read timeout;
- total/request timeout.

Traducir el timeout a una excepcion de dominio, conservando la causa original:

```python
raise APITimeoutError(...) from exc
```

---

## 6. Retries y exponential backoff

Reintentar solo errores razonablemente recuperables:

- `429`;
- `5xx`;
- errores temporales de conexion;
- timeouts.

**No** reintentar indiscriminadamente `400`, `401`, `403`, `404`, salvo comportamiento especifico documentado del proveedor.

Requisitos:

- numero maximo de retries configurable (sin loops infinitos de retry);
- backoff exponencial configurable;
- jitter cuando corresponda para evitar retry storms.

### Idempotencia

Considerar la idempotencia antes de aplicar retries:

```text
GET, HEAD, OPTIONS   → reintentar suele ser seguro
POST, PUT, PATCH, DELETE → depende de la semantica del endpoint
```

No asumir que cualquier request puede repetirse sin consecuencias.

---

## 7. Rate limiting

Manejar explicitamente `429 Too Many Requests`:

1. detectar `429`;
2. leer `Retry-After` (respetarlo cuando sea valido);
3. calcular el tiempo de espera;
4. esperar;
5. reintentar solo si queda presupuesto de retries.

Si el proveedor usa headers especificos de rate limit, adaptarlos en el cliente correspondiente. No asumir que todos los proveedores implementan el mismo mecanismo.

---

## 8. Cache

El cache evita requests repetitivos; la implementacion inicial puede ser en memoria, con limitaciones conocidas:

- TTL;
- tamano maximo;
- invalidacion;
- claves deterministicas;
- respuestas negativas;
- concurrencia.

No asumir que un `dict` global es suficiente para todos los escenarios. Cuando lo sea:

```text
dict + TTL
```

cuando no lo sea, considerar una abstraccion:

```text
Cache
├── InMemoryCache
└── RedisCache
```

El cache debe poder sustituirse mediante dependency injection. No introducir Redis u otro backend si el proyecto no lo necesita (ver seccion 15).

---

## 9. Validacion de respuestas

Un HTTP `200` no garantiza que los datos sean correctos. Validar:

- estructura;
- campos requeridos;
- tipos;
- valores importantes;
- formato esperado;
- errores funcionales devueltos dentro de HTTP 200.

Usar dataclasses, validadores o el mecanismo de validacion ya usado en el proyecto. Si la respuesta no cumple el contrato:

```text
InvalidResponseError
```

o una excepcion derivada apropiada. Distinguir tres casos:

```text
error HTTP          → fallo de transporte/servidor
respuesta invalida  → 200 pero el cuerpo no cumple el contrato
error funcional     → el proveedor reporta un fallo dentro de una respuesta HTTP valida
```

---

## 10. Jerarquia de excepciones

Jerarquia coherente (nombres adaptados al proyecto; no es obligatoria esta exacta):

```text
APIError
├── APITimeoutError
├── APIConnectionError
├── APIRateLimitError
├── APIHTTPError
├── InvalidResponseError
├── OMDBError
└── TVMazeError
```

Cada excepcion debe conservar informacion util cuando corresponda:

- status code;
- proveedor;
- endpoint;
- causa original (`raise ... from exc`);
- informacion de retries.

Sin secretos en los mensajes de error.

---

## 11. HTTP status codes

Usar `raise_for_status()` o mecanismo equivalente y mapear a excepciones de dominio:

```text
4xx → errores del request / autorizacion / recurso
5xx → errores temporales del proveedor
429 → rate limiting
```

No convertir todos los status codes en el mismo error: conservar el `status_code` cuando sea util.

---

## 12. Logging y observabilidad

Logging estructurado y seguro. Puede incluir:

- metodo HTTP;
- host;
- endpoint sanitizado;
- status code;
- duracion;
- numero de retry;
- proveedor;
- tipo de error.

No registrar: API keys, tokens, Authorization headers, passwords, cookies ni otros secretos (ver seccion 4). No registrar response bodies completos automaticamente: pueden contener datos sensibles o ser demasiado grandes.

Niveles:

```text
DEBUG   → detalle tecnico (endpoint sanitizado, duracion)
INFO    → operaciones significativas
WARNING → reintentos, rate limit, respuestas inesperadas
ERROR   → fallos tras agotar retries o errores no recuperables
```

El logging no debe modificar el comportamiento de la integracion.

---

## 13. Paginacion

Cuando la API soporte paginacion, considerar:

- page/offset o cursor;
- limites maximos;
- terminacion clara;
- errores intermedios.

Evitar cargar cantidades potencialmente ilimitadas en memoria: preferir iteradores/generadores o paginacion controlada.

---

## 14. Proteccion de recursos (response size)

No asumir que una respuesta HTTP tiene un tamano razonable. Cuando la libreria o la arquitectura lo permitan, limitar:

- tamano de respuesta;
- cantidad de paginas;
- numero de retries;
- tiempo total de operacion.

Evitar que una API defectuosa provoque consumo ilimitado de memoria o CPU.

---

## 15. Evitar over-engineering

No implementar automaticamente:

- Redis;
- circuit breakers;
- colas;
- async;
- sistemas de cache complejos;
- abstracciones excesivas;

si el proyecto no las necesita. La arquitectura debe ser proporcional al problema: preferir la solucion mas sencilla que cumpla robustez y mantenibilidad.

### Concurrencia

Si la integracion usa concurrencia o async:

- no compartir estado mutable sin proteccion;
- reutilizar correctamente los clientes HTTP (una conexion por request es innecesaria);
- respetar rate limits;
- evitar cientos de requests simultaneos.

No introducir async solo por moda: la arquitectura debe corresponder al modelo de ejecucion existente.

---

## 16. Compatibilidad con proveedores

Los clientes de proveedor encapsulan sus diferencias: autenticacion, parametros, formatos de respuesta, errores, paginacion y rate limits.

El resto de la aplicacion no deberia conocer detalles innecesarios de OMDb, TVMaze ni de otros proveedores concretos.

---

## 17. Testing de integraciones API

Las integraciones deben ser testeables **sin APIs externas reales**. Los tests unitarios deben simular, como minimo:

- respuesta exitosa;
- timeout;
- connection error;
- `400`, `401`, `403`, `404`;
- `429`;
- `500`, `503`;
- respuesta invalida;
- retries y exponential backoff;
- `Retry-After`;
- cache hit / cache miss / expiracion;
- sanitizacion de logs con API keys ocultas.

### Unit tests vs integration tests

**Unit tests**: sin Internet, sin APIs externas, sin credenciales reales, sin depender de la disponibilidad del proveedor; usar mocks/fakes o un transporte HTTP controlado.

**Integration tests** (si existen): claramente identificados, ejecucion controlada (por ejemplo con marca o variable de entorno), sin exponer secretos y sin ser necesarios para la suite unitaria normal.

Verificar comportamiento real, no solo que un log contiene un mensaje. La metodologia general de tests (fixtures, cobertura, AAA) esta en la skill `testing`.

---

## 18. Checklist

### Arquitectura

- [ ] Cliente separado por proveedor cuando corresponde.
- [ ] Transporte HTTP comun sin duplicacion innecesaria.
- [ ] Sin logica especifica de proveedores dentro del cliente HTTP generico.
- [ ] Dependencias inyectables.
- [ ] Configuracion centralizada.

### Robustez

- [ ] Timeout explicito y configurable.
- [ ] Retries configurables.
- [ ] Exponential backoff.
- [ ] Jitter cuando sea apropiado.
- [ ] `429` manejado correctamente.
- [ ] `Retry-After` respetado.
- [ ] No se reintentan indiscriminadamente errores no recuperables.
- [ ] Idempotencia considerada.
- [ ] Paginacion controlada cuando corresponda.

### Errores

- [ ] Jerarquia `APIError`.
- [ ] Errores HTTP mapeados.
- [ ] Timeout diferenciado.
- [ ] Connection errors diferenciados.
- [ ] Rate limit diferenciado.
- [ ] Respuestas invalidas detectadas.
- [ ] Causa original preservada cuando corresponda.

### Seguridad

- [ ] Secretos fuera del codigo.
- [ ] API keys protegidas.
- [ ] Authorization headers nunca aparecen en logs.
- [ ] Query parameters sensibles sanitizados.
- [ ] Errores sin secretos.
- [ ] Response bodies sensibles no registrados indiscriminadamente.

### Cache

- [ ] Cache implementada cuando aporta valor.
- [ ] TTL definido cuando corresponda.
- [ ] Cache key deterministica.
- [ ] Cache testeada.
- [ ] Sin estado global mutable injustificado.

### Testing

- [ ] Unit tests sin llamadas reales a Internet.
- [ ] Success response cubierta.
- [ ] Timeout cubierto.
- [ ] Connection error cubierto.
- [ ] `4xx` cubiertos cuando sean relevantes.
- [ ] `429` cubierto.
- [ ] `5xx` cubiertos.
- [ ] Retry cubierto.
- [ ] Backoff cubierto.
- [ ] `Retry-After` cubierto.
- [ ] Cache hit/miss cubierto.
- [ ] Respuesta invalida cubierta.
- [ ] Sanitizacion de secretos en logs cubierta.

---

## 19. Informe final

Despues de implementar una integracion API, informar:

1. Proveedores integrados.
2. Clientes creados/modificados.
3. Endpoints utilizados.
4. Configuracion utilizada.
5. Estrategia de timeout.
6. Estrategia de retry/backoff.
7. Estrategia de rate limiting.
8. Estrategia de cache.
9. Validacion de respuestas.
10. Jerarquia de excepciones.
11. Estrategia de logging.
12. Proteccion de secretos.
13. Tests realizados.
14. Resultado de los tests.
15. Riesgos o limitaciones pendientes.
