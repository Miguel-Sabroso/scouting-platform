# CLAUDE.md — scouting-platform

Plataforma de datos de fútbol con dos productos encima:
1. **Buscador de jugadores**: encuentra jugadores parecidos a uno dado o que cumplan un perfil, con filtros de posición, edad, valor de mercado y liga.
2. **Simulador de liga**: simula el resto de temporada (Monte Carlo) y mide el impacto de escenarios como la lesión de un jugador clave.

Es un proyecto personal para aprender y para explicarlo en vídeos (TikTok/YouTube). **Entender cada pieza es tan importante como que funcione.**

## Cómo quiero que trabajes conmigo

- **Plan antes que código.** Ante una tarea no trivial, propón primero el enfoque, los archivos que vas a tocar y por qué. No implementes hasta que lo apruebe.
- **Explica el porqué.** En cada decisión de diseño, explica qué alternativas había y por qué eliges esa. Si introduces un concepto nuevo (estadístico, de ML o de arquitectura), explícalo brevemente con un ejemplo de fútbol.
- **Pasos pequeños.** Un cambio acotado cada vez, que se pueda revisar en un diff.
- **Piezas clave = modo tutor.** En el modelo de partido (Poisson/Dixon-Coles), el RAPM, la búsqueda por similitud y el Monte Carlo, **no escribas la implementación completa salvo que te lo pida**: guíame, revisa mi código y señala errores. En lo repetitivo (scrapers, endpoints, configuración, tests, frontend) puedes implementar directamente.
- **Sé crítico.** Si una idea mía es mala o sobreingenierizada, dímelo y explica por qué.
- **Nunca inventes datos ni APIs.** Si no sabes qué devuelve una fuente o una librería, compruébalo o dilo.

## Arquitectura

Monolito modular en un monorepo. Los módulos se comunican por interfaces claras para poder extraerlos más adelante si hace falta. Nada de microservicios por ahora.

```
scouting-platform/
├── data_platform/   # adaptadores por fuente, ingesta raw, normalización, resolución de entidades
├── features/        # métricas por 90', percentiles por posición, ajuste por liga, vectores
├── scouting/        # búsqueda por similitud (pgvector) + capa LLM
├── simulation/      # modelo de partido, impacto por jugador (RAPM), Monte Carlo, escenarios
├── api/             # FastAPI: api/ → services/ → repositories/ → domain/
├── web/             # Next.js
└── infra/           # docker-compose, CI
```

Flujo de datos: fuentes (Understat, Transfermarkt, StatsBomb Open Data) → ingesta con adaptadores → raw en Parquet (inmutable) → limpieza + resolución de entidades → PostgreSQL (+ pgvector) → buscador y simulador → API → web.

### Principios
- **Patrón adaptador para fuentes:** cada fuente implementa la interfaz `Source`. Cambiar o añadir una fuente no toca el resto del sistema.
- **Raw inmutable:** lo descargado se guarda tal cual. Toda transformación se puede repetir sin volver a descargar.
- **Pasos idempotentes:** ejecutar dos veces da el mismo resultado (upserts, nada de duplicados).
- **IDs canónicos:** todo jugador, equipo y partido se referencia por nuestro ID, nunca por el de una fuente. El mapeo vive en `player_id_map`.
- **El LLM nunca toca los números:** solo traduce texto a una consulta estructurada (validada con Pydantic) y redacta explicaciones a partir de datos reales.
- **Medir antes de complicar:** un parámetro nuevo del simulador entra solo si mejora el backtest (RPS, log loss). Una pieza de infraestructura entra solo si resuelve un problema real.
- **Sin fuga de datos:** en el backtesting, cada predicción usa solo los datos disponibles en ese momento.

## Stack y convenciones

- **Idioma:** código, identificadores, docstrings, comentarios y mensajes de commit en inglés. CLAUDE.md, documentación de diseño y conversación en español. Las etiquetas visibles en la web (posiciones, roles) pueden ir en español mediante un catálogo.
- Python 3.12+, dependencias con `uv`.
- Calidad: `ruff` (lint + formato), `mypy` en modo estricto, `pytest`. Todo pasa por `pre-commit` y por CI (GitHub Actions).
- Tipado en todas las funciones públicas; modelos de dominio con dataclasses o Pydantic.
- Configuración con `pydantic-settings` y variables de entorno. **Nunca** credenciales en el código; `.env` en `.gitignore`.
- Base de datos: PostgreSQL + pgvector en Docker; migraciones con Alembic.
- Datos analíticos: Polars o pandas; almacenamiento raw en Parquet.
- Scraping responsable: pausas entre peticiones, caché local, reintentos con backoff y respeto a las condiciones de uso de cada fuente.
- Tests: unitarios para la lógica (sin BD) y tests de calidad de datos en cada carga.
- Commits pequeños y descriptivos; una rama por paso del plan.

## Comandos

```bash
docker compose up -d        # levanta PostgreSQL + pgvector
uv sync                     # instala dependencias
uv run pre-commit install   # engancha los hooks a git (una vez por clon)
uv run pre-commit run --all-files   # pasa todos los hooks a mano
uv run pytest               # tests
uv run ruff check . && uv run mypy .
```
(Actualizar esta sección según se añadan comandos.)

## Plan por fases

0. **Entorno:** monorepo, herramientas, Docker, CI.
1. **Plataforma de datos mínima:** una liga, 2-3 temporadas, resolución de entidades.
2. **Simulador v1:** Poisson + Dixon-Coles con xG, decaimiento temporal, backtesting walk-forward, Monte Carlo con incertidumbre de parámetros.
3. **Buscador MVP:** features, pgvector, perfiles de rol, API, web, UMAP precalculado.
4. **Capa LLM:** lenguaje natural → consulta estructurada + explicaciones.
5. **Simulador v2:** RAPM con prior, profundidad de plantilla, escenarios de lesión con números aleatorios comunes.
6. **Escalado:** solo según aparezcan problemas reales.

No se pasa de fase hasta cumplir su criterio de terminado y que yo pueda explicar cada concepto con mis palabras.

## Estado actual

- Fase actual: **0**
- Siguiente paso: crear el monorepo y la configuración base.
- Decisiones pendientes: liga inicial (LaLiga o Segunda).
