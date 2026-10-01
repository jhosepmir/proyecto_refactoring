---
name: testing
description: Crea y mantiene tests de Python 3.11+ con pytest priorizando calidad sobre cantidad: AAA, asserts especificos, naming diagnostico, fixtures justificadas, mocks/fakes/stubs sin sobre-mocking, parametrizacion, tests de errores y de logging, independencia, determinismo, aislamiento total de APIs externas, cobertura significativa y deteccion de regresiones. Usar para pytest, unit tests, integration tests, fixtures, mocks, cobertura.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: quality
  triggers: pytest, unit test, integration test, fixture, mock, fake, stub, parametrize, coverage, AAA, flaky
  role: specialist
  scope: quality
  related-skills: python-pro, test-master, api-integration
---
# Skill: Testing

**Proposito**: crear y mantener tests de Python 3.11+ con pytest, con enfasis en calidad, deteccion real de regresiones, independencia, determinismo, mantenibilidad y cobertura significativa.

**Alcance**: metodologia de testing propia de esta skill. Las reglas de diseno de codigo estan en la skill de refactoring y las de integraciones REST en la skill de api-integration; aqui se define **como** testear.

---

## 1. Filosofia: calidad sobre cantidad

> Un test debe detectar comportamientos incorrectos, no simplemente ejecutar codigo para aumentar coverage.

No basta con:

```python
assert result
```

cuando es posible una validacion especifica. Preferir:

```python
assert result.title == "The Matrix"
assert result.year == 1999
```

Los tests verifican **comportamiento observable**, no la implementacion interna.

Los tests son documentacion viva: deben ser claros, pequenos, especificos y faciles de mantener. Evitar fixtures o abstracciones tan complejas que oculten que se esta probando.

### Naming

El nombre explica que comportamiento se verifica:

```python
def test_movie_service_returns_invalid_response_error_when_title_is_missing():
    ...

def test_movie_1():   # evitar
    ...
```

Un buen nombre diagnostica el fallo rapidamente.

---

## 2. Estructura y organizacion

Estructura de referencia (adaptar al proyecto real; no imponer carpetas innecesarias):

```text
tests/
├── conftest.py
├── unit/
│   ├── services/
│   ├── api/
│   └── models/
└── integration/
```

- agrupar tests por componente o comportamiento;
- fixtures en `conftest.py` **solo** cuando sean realmente compartidas;
- unit e integration tests claramente diferenciados.

---

## 3. Unit tests

Aislar una unidad concreta: servicios, clientes API, models, validadores, utilidades.

- sustituir las dependencias externas de la unidad;
- no convertir un unit test en una integracion accidental;
- cubrir casos normales, casos limite y errores.

---

## 4. Integration tests

Comprobar la colaboracion real entre componentes:

```text
UI
 ↓
services
 ↓
api
```

- pueden usar sesiones HTTP scripted/fakes;
- `capsys` cuando haya que comprobar output de CLI/UI;
- **sin dependencia de Internet**;
- verifican contratos entre componentes, no repiten todos los unit tests.

---

## 5. Fixtures

Fixtures del proyecto como `fake_requests`, `clear_api_caches`, `restore_runtime_config` o datos `MOVIE_DETAILS`, `SHOW_DETAIL`, `SEARCH_RESULTS` **cuando sean necesarias**.

No convertir automaticamente todos los datos de prueba en fixtures globales. Una fixture se usa cuando aporta:

- reutilizacion;
- aislamiento;
- preparacion consistente;
- cleanup.

Evitar fixtures excesivamente complejas.

---

## 6. Independencia y estado global

Cada test debe poder ejecutarse por separado:

```bash
pytest tests/unit/services/test_movie_service.py
```

sin que importe el orden ni lo que haya dejado otro test. Los tests **no** deben depender de:

- orden de ejecucion;
- estado producido por otro test;
- variables globales modificadas por otro test;
- cache persistente;
- archivos creados por otro test;
- datos externos;
- Internet.

Si el codigo usa estado global: aislarlo con fixtures, restaurarlo tras el test y limpiar caches. Cuando el codigo se refactorice a dependency injection, adaptar los tests para depender de la inyeccion, no del estado global.

---

## 7. Aislamiento de APIs externas

Los unit tests **nunca** llaman a OMDb, TVMaze, otras APIs ni a Internet. Utilizar, segun lo apropiado:

- `monkeypatch`;
- mocks;
- fakes;
- transporte HTTP controlado.

No depender exclusivamente de parchear `requests.get` si la arquitectura tiene un cliente HTTP inyectable: la estrategia de mocking se adapta al **punto real de dependencia**.

---

## 8. Mock, Fake y Stub

| Tecnica | Cuando |
|---|---|
| **Mock** | verificar interacciones especificas cuando eso importa |
| **Fake** | implementacion simplificada pero funcional |
| **Stub** | devolver datos controlados |

No usar mocks indiscriminadamente. Preferir verificar el comportamiento sobre los detalles internos.

### No sobre-mockear

Evitar tests que solo comprueben:

```python
mock.assert_called_once_with(...)
```

sin comprobar el resultado final: un test acoplado a la implementacion sigue pasando aunque el comportamiento externo este roto. Preferir:

```text
input
 ↓
unidad
 ↓
resultado observable
```

usando mocks solo donde aporten aislamiento o verificacion util.

---

## 9. Arrange-Act-Assert y assertions especificas

```python
def test_get_movie_returns_movie(movie_service, fake_client):
    # Arrange
    fake_client.get_movie.return_value = MOVIE_DETAILS

    # Act
    result = movie_service.get_movie(1)

    # Assert
    assert result.title == "The Matrix"
    assert result.year == 1999
```

Evitar assertions debiles (`assert result`, `assert response`, `assert data`) cuando se pueda comprobar el valor esperado:

```python
assert response.status_code == 200
assert len(results) == 3
```

Para excepciones:

```python
with pytest.raises(APIError, match="timeout"):
    ...
```

comprobando tambien los atributos relevantes de la excepcion cuando corresponda.

---

## 10. Parametrizacion

```python
@pytest.mark.parametrize(
    "status_code, expected_error",
    [
        pytest.param(400, APIHTTPError, id="bad-request"),
        pytest.param(404, APIHTTPError, id="not-found"),
        pytest.param(429, APIRateLimitError, id="rate-limit"),
    ],
)
```

Util cuando existan multiples casos con la misma estructura: validacion, errores, status codes, entradas limite, formatos invalidos, casos equivalentes. Usar IDs descriptivos.

No parametrizar si reduce significativamente la legibilidad.

---

## 11. Tests de errores

Cada error importante tiene test:

```python
with pytest.raises(APITimeoutError):
    ...
```

Verificar ademas que:

- se genera la excepcion correcta;
- contiene la informacion relevante (status code, proveedor, etc.);
- no contiene secretos;
- conserva la causa original (`__cause__`) cuando corresponda.

No probar solo el mensaje si existe informacion estructurada mejor.

---

## 12. Tests de logging y seguridad

Cuando el logging es parte del contrato de seguridad, usar `caplog`:

```python
assert "secret-key" not in caplog.text
assert "apikey=***" in caplog.text
```

Comprobar que nunca aparecen API keys, tokens, Authorization, passwords ni cookies.

No acoplar el test al texto exacto de cada log cuando solo importa la propiedad de seguridad.

---

## 13. Configuracion y cache

- verificar valores por defecto, valores personalizados, restauracion tras el test y aislamiento entre tests (fixture tipo `restore_runtime_config`);
- si hay cache en memoria, aislarla entre tests (fixture tipo `clear_api_caches`) para que el estado no se comparta:

```text
test A → cache → cleanup → test B
```

- preferir dependency injection de cache cuando la arquitectura lo permita.

---

## 14. Determinismo

Los tests producen el mismo resultado repetidamente. Evitar depender innecesariamente de:

- hora actual y zona horaria;
- random y UUID;
- filesystem y red;
- estado global;
- orden de tests;
- datos externos.

Controlar esas dependencias con fixtures, `monkeypatch` o dependency injection.

### Tiempo y backoff

Los tests de retries no deben esperar de verdad:

```text
1s + 2s + 4s + 8s   # prohibido solo para verificar backoff
```

Controlar el reloj o el sleep (mock/fake) y verificar que el calculo o la secuencia de espera es correcta.

### Tests lentos

Los unit tests deben ser rapidos; los integration tests pueden serlo menos, pero sin esperas innecesarias. No introducir `sleep` real salvo que sea esencial a la prueba.

### Tests flaky

Si un test falla de forma intermitente:

1. identificar la dependencia no determinista;
2. corregir la causa;
3. no anadir retries al test;
4. no marcarlo `skip` sin investigar;
5. documentar el problema si no puede resolverse ya.

Un test flaky no es un test fiable.

---

## 15. Tests de API

Para clientes API cubrir, cuando sea aplicable:

- **Success**: `200`, datos validos, transformacion correcta.
- **Errors**: `400`, `401`, `403`, `404`, `429`, `500`, `503`.
- **Network**: timeout, connection error.
- **Retry**: retry correcto, limite de retries, exponential backoff, `Retry-After`.
- **Response validation**: JSON invalido, campos faltantes, tipos incorrectos, estructura inesperada.
- **Cache**: hit, miss, expiracion, invalidacion cuando corresponda.

---

## 16. Tests de contrato

Cuando existan interfaces entre componentes o APIs, comprobar que:

- se mantiene el formato esperado;
- existen los campos necesarios;
- los tipos son correctos;
- las capas se comunican correctamente.

Sin duplicar innecesariamente los mismos unit tests.

---

## 17. Cobertura y quality gates

```bash
pytest -q
coverage run --branch -m pytest
coverage report
```

Objetivo de referencia `>= 80%` cuando el proyecto lo establezca, con la advertencia explicita:

> 80% de cobertura no significa automaticamente que los tests sean buenos.

Coverage sirve para **encontrar codigo no probado** (ramas, errores, edge cases, excepciones), no para inflar el porcentaje: no crear tests artificiales solo para subirlo. Prestar atencion al branch coverage.

Diferenciar tres cosas que **no** son equivalentes:

| Gate | Significado |
|---|---|
| Tests pasan | el codigo cumple los assertions definidos |
| Coverage suficiente | una proporcion suficiente del codigo se ejecuto |
| Tests de calidad | los tests verifican comportamiento importante |

Respetar la configuracion de testing existente del proyecto.

---

## 18. Deteccion de regresiones

Cuando se modifique codigo existente, identificar antes del cambio:

- comportamiento actual y contratos;
- edge cases y errores esperados;
- integraciones afectadas.

Crear o reforzar tests que protejan esos comportamientos antes de dar el cambio por terminado.

---

## 19. No modificar produccion para satisfacer tests

No cambiar el comportamiento del codigo de produccion solo para que un test pase. Si necesita una modificacion para ser testeable:

- identificar la razon;
- aplicar un cambio arquitectonico razonable (p. ej. dependency injection);
- no introducir logica artificial exclusiva del test.

---

## 20. Ejecucion

```bash
pytest -q                                          # feedback rapido
pytest tests/unit/services/test_movie_service.py   # prueba concreta
coverage run --branch -m pytest                    # con cobertura
coverage report
```

---

## 21. Checklist

### Estructura

- [ ] `tests/` organizado claramente.
- [ ] Unit e integration tests diferenciados.
- [ ] Fixtures ubicadas apropiadamente.
- [ ] Tests independientes.

### Unit tests

- [ ] Servicios principales cubiertos.
- [ ] Dependencias externas aisladas.
- [ ] Sin llamadas reales a APIs.
- [ ] Assertions especificos.
- [ ] Casos normales cubiertos.
- [ ] Casos limite cubiertos.
- [ ] Errores cubiertos.

### API

- [ ] Success responses.
- [ ] HTTP errors relevantes.
- [ ] Timeout.
- [ ] Connection errors.
- [ ] `429`.
- [ ] Retry.
- [ ] Backoff.
- [ ] `Retry-After`.
- [ ] Invalid responses.
- [ ] Cache.

### Calidad

- [ ] Arrange-Act-Assert.
- [ ] Tests deterministas.
- [ ] Tests independientes.
- [ ] Sin sobre-mocking.
- [ ] Nombres descriptivos.
- [ ] Sin sleeps innecesarios.
- [ ] Sin tests flaky conocidos.

### Coverage

- [ ] `coverage run --branch -m pytest`.
- [ ] `coverage report`.
- [ ] Objetivo >= 80% cuando el proyecto lo establezca.
- [ ] Branch coverage revisado.
- [ ] Coverage no utilizado como unica metrica de calidad.

---

## 22. Informe final

Despues de crear o mejorar tests, informar:

1. Tests creados.
2. Tests modificados.
3. Funcionalidades cubiertas.
4. Casos limite cubiertos.
5. Dependencias mockeadas/fakeadas.
6. Unit tests creados.
7. Integration tests creados.
8. Coverage obtenido.
9. Branch coverage relevante.
10. Resultado de `pytest`.
11. Problemas detectados.
12. Tests pendientes o gaps de cobertura.
13. Tests potencialmente fragiles.
14. Riesgos pendientes.
