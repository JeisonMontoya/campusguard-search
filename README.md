# CampusGuard: Búsqueda para Prevención de Deserción Académica

Implementación y benchmarking de algoritmos de búsqueda (BFS, DFS, A*) para el agente racional CampusGuard (Fase 1).

## Descripción

Este proyecto formaliza el problema de planificación de intervenciones para estudiantes en riesgo de deserción académica como un **problema de búsqueda en espacio de estados** determinista y discreto, e implementa tres algoritmos de búsqueda:

- **BFS** (Breadth-First Search) - Búsqueda en amplitud
- **DFS** (Depth-First Search) - Búsqueda en profundidad  
- **A*** (A-Star Search) - Búsqueda informada con heurística admisible

## Estructura del Proyecto

```
campusguard-search/
├── src/
│   ├── aima_search.py          # Algoritmos de búsqueda (AIMA-Python adaptado)
│   ├── aima_utils.py           # Utilidades (sin dependencias externas)
│   ├── campusguard_problem.py  # Formalización del problema
│   └── search_runner.py        # Benchmarking y métricas
├── benchmark/
│   ├── resultados.json         # Datos crudos del benchmark
│   ├── tabla_benchmark.md      # Tabla para documento técnico
│   ├── analisis_complejidad.md # Análisis Big O
│   └── evaluacion_heuristica.md
├── docs/
│   ├── documento_tecnico.md    # Documento técnico en Markdown
│   ├── documento_tecnico.pdf   # Documento técnico en PDF (APA 7ma ed.)
│   └── md_to_pdf.py            # Conversor Markdown a PDF
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.8+
- fpdf2 (para generar PDF): `pip install fpdf2`

## Ejecución

```bash
cd src
python search_runner.py
```

Esto ejecutará el benchmark completo y generará:
- Tabla comparativa en consola
- `benchmark/resultados.json` - Datos completos
- `benchmark/tabla_benchmark.md` - Tabla Markdown
- `benchmark/analisis_complejidad.md` - Análisis Big O
- `benchmark/evaluacion_heuristica.md` - Evaluación heurística

## Resultados Principales

| Algoritmo | Tasa Éxito | Nodos Exp. Prom. | Tiempo Prom. (ms) | Costo Prom. |
|-----------|------------|------------------|-------------------|-------------|
| **BFS** | 100% | 1.5 | 0.11 | 4.19 |
| **DFS** | 100% | 1.2 | 0.09 | 5.25 |
| **A*** | 100% | 6.4 | 0.50 | **2.94** |

**Conclusión**: A* con heurística admisible reduce el costo de solución en **30% vs BFS** y **44% vs DFS**, garantizando optimalidad.

## Formalización del Problema

- **Estado**: `(PerfilEstudiante, Intervenciones[], hora_actual)`
- **Estado inicial**: Perfil en riesgo, sin intervenciones, hora 0
- **Acciones**: 4 intervenciones (monitorear, tutoría, bienestar, redistribuir)
- **Transición**: Determinista - reduce score_riesgo, avanza tiempo
- **Meta**: score_riesgo ≤ 25 Y hora ≤ 48
- **Costo**: Horas-equivalentes de intervención

## Heurística A* (Admisible)

**Costo Mínimo Teórico Restante**:
```
h(n) = (riesgo_actual - 25) / max_ratio_efectividad_costo
```

Es **admisible** porque asume intervención ideal sin restricciones temporales ni límite de intervenciones.

## Documento Técnico

Ver `docs/documento_tecnico.pdf` (formato APA 7ma edición, máx. 5 páginas).

## Referencias

- Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
- Tinto, V. (1993). *Leaving College: Rethinking the Causes and Cures of Student Attrition*. University of Chicago Press.
- Código base: AIMA-Python (https://github.com/aimacode/aima-python)

## Autor

**Jeison Montoya**  
Inteligencia Artificial I INF DIS (A)  
Universidad Militar Nueva Granada  
2026