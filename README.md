# CampusGuard - Búsqueda para Prevención de Deserción

Implementación y benchmarking de BFS, DFS y A* para el agente CampusGuard (Fase 1 del proyecto integrador).

## Descripción

Formaliza la planificación de intervenciones para estudiantes en riesgo como un problema de búsqueda en espacio de estados determinista y discreto. Implementa tres algoritmos:

- **BFS** - Búsqueda en amplitud
- **DFS** - Búsqueda en profundidad  
- **A*** - Búsqueda informada con heurística admisible

## Estructura

```
campusguard-search/
├── src/
│   ├── aima_search.py          # Algoritmos base (AIMA adaptado)
│   ├── aima_utils.py           # Utilidades sin numpy
│   ├── campusguard_problem.py  # Definición del problema
│   └── search_runner.py        # Benchmarking y métricas
├── benchmark/
│   ├── resultados.json         # Datos crudos
│   ├── tabla_benchmark.md      # Tabla para el informe
│   ├── analisis_complejidad.md # Big O
│   └── evaluacion_heuristica.md
├── docs/
│   ├── documento_tecnico.md    # Informe en Markdown
│   ├── documento_tecnico.pdf   # Informe PDF (APA 7ma)
│   └── md_to_pdf.py            # Conversor
├── .gitignore
└── README.md
```

## Requisitos

- Python 3.8+
- `pip install fpdf2`

## Ejecución

```bash
cd src
python search_runner.py
```

Genera: tabla en consola, `benchmark/resultados.json`, `benchmark/tabla_benchmark.md`, `benchmark/analisis_complejidad.md`, `benchmark/evaluacion_heuristica.md`.

## Resultados (promedios 8 estudiantes)

| Algoritmo | Éxito | Nodos exp. | Tiempo (ms) | **Costo** |
|-----------|-------|------------|-------------|-----------|
| **BFS** | 100% | 1.5 | 0.11 | 4.19 |
| **DFS** | 100% | 1.2 | 0.09 | 5.25 |
| **A*** | 100% | 6.4 | 0.50 | **2.94** |

A* reduce costo **30% vs BFS** y **44% vs DFS** con heurística admisible.

## Formalización rápida

- **Estado**: `(PerfilEstudiante, Intervenciones[], hora_actual)`
- **Inicial**: Perfil en riesgo, sin intervenciones, hora 0
- **Acciones**: 4 intervenciones (monitorear, tutoría, bienestar, redistribuir)
- **Transición**: Determinista - reduce score_riesgo, avanza tiempo
- **Meta**: score_riesgo ≤ 25 Y hora ≤ 48
- **Costo**: Horas-equivalentes de intervención

## Heurística A*

**Costo Mínimo Teórico Restante**:
```
h(n) = (riesgo_actual - 25) / max_ratio_efectividad_costo
```
Admisible: asume intervención ideal sin restricciones temporales ni límite de intervenciones.

## Informe técnico

Ver `docs/documento_tecnico.pdf` (APA 7ma, máx. 5 páginas).

## Referencias

- Russell & Norvig (2021). *AI: A Modern Approach* (4ta ed.). Pearson.
- Tinto (1993). *Leaving College*. U. Chicago Press.
- Base: AIMA-Python (github.com/aimacode/aima-python)

---

**Jeison Montoya**  
Inteligencia Artificial I INF DIS (A)  
Universidad Militar Nueva Granada  
2026