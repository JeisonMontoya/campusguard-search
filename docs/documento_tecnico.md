# CampusGuard: Implementación y Benchmarking de Algoritmos de Búsqueda para Prevención de Deserción Académica

**Autor:** Jeison Montoya  
**Curso:** Inteligencia Artificial I INF DIS (A)  
**Universidad:** Universidad Militar Nueva Granada  
**Docente:** Ing. Oscar Iván Varela Vélez  
**Fecha:** 9 de noviembre de 2026  

---

## Resumen

Este documento presenta la formalización e implementación computacional del agente racional **CampusGuard** (Fase 1) como un problema de búsqueda en espacio de estados. Se implementan y comparan tres algoritmos de búsqueda —BFS, DFS y A*— sobre la planificación de intervenciones para estudiantes en riesgo de deserción académica. Los resultados demuestran que A* con heurística admisible reduce el costo de la solución en un 30% promedio respecto a BFS y 44% respecto a DFS, manteniendo completitud y optimalidad.

**Palabras clave:** búsqueda en espacio de estados, BFS, DFS, A*, heurística admisible, prevención deserción académica, agente racional.

---

## 1. Introducción

La deserción académica en primer semestre alcanza el 18% en la institución (Tinto, 1993). La Fase 1 del proyecto integrador propuso **CampusGuard**, un agente racional que detecta estudiantes en riesgo en ≤48 horas y activa intervenciones autónomas: tutoría, notificación a bienestar, redistribución de carga, o monitoreo.

Esta Fase 2 avanza desde el modelado conceptual hacia la **implementación computacional**, formalizando el problema como búsqueda en espacio de estados e implementando algoritmos de búsqueda no informados (BFS, DFS) e informado (A*) con heurística admisible.

---

## 2. Abstracción del Entorno

El entorno original (Fase 1) es: parcialmente observable, estocástico, secuencial, dinámico, discreto y multiagente. Para la búsqueda algorítmica se requiere **determinismo y discretitud**:

| Propiedad Original | Abstracción para Búsqueda |
|---|---|
| Parcialmente observable | **Totalmente observable**: estado = perfil completo del estudiante |
| Estocástico | **Determinista**: intervención → reducción exacta de riesgo |
| Secuencial | **Secuencial**: acciones previas afectan estado futuro |
| Dinámico | **Estático durante planificación**: ventana de 48h fija |
| Discreto | **Discreto**: tiempo en horas, acciones finitas |
| Multiagente | **Un agente planificador**: decide secuencia para UN estudiante |

**Justificación**: La abstracción permite aplicar algoritmos clásicos de búsqueda (Russell & Norvig, 2021) manteniendo la esencia del problema: **minimizar costo de intervención** sujeto a **ventana temporal de 48h** y **reducción de riesgo ≤25**.

---

## 3. Formalización del Espacio de Estados

### 3.1 Estado
Una tupla $s = \langle P, I, h \rangle$ donde:
- $P$: `PerfilEstudiante` (asistencia, promedio, actividad LMS, tendencias, historial, score_riesgo ∈ [0,100])
- $I$: Tupla de `EstadoIntervencion` aplicadas (historial)
- $h$: Hora actual ∈ [0, 48]

### 3.2 Estado Inicial
$s_0 = \langle P_{inicial}, \langle \rangle, 0 \rangle$ donde $P_{inicial}.score\_riesgo > 25$

### 3.3 Acciones $A(s)$
Intervenciones no aplicadas que caben en tiempo restante:
- `MONITOREAR` (1h, costo 0.5h, reducción 5%)
- `RECOMENDAR_TUTORIA` (8h, costo 3.0h, reducción 25%)
- `NOTIFICAR_BIENESTAR` (2h, costo 1.0h, reducción 15%)
- `REDISTRIBUIR_CARGA` (12h, costo 5.0h, reducción 35%)

$|A(s)| \le 3$ (factor de ramificación $b \approx 3$)

### 3.4 Modelo de Transición $T(s, a) \to s'$
Determinista: $s' = \langle P', I \cup \{a\}, h + dur(a) \rangle$  
donde $P'.score\_riesgo = \max(0, P.score\_riesgo - efectividad(a) \times 100)$

### 3.5 Prueba de Meta $Goal(s)$
$$Goal(s) \iff P.score\_riesgo \le 25 \land h \le 48$$

### 3.6 Función de Costo $c(s, a, s')$
$$c(s, a, s') = costo(a) \in \{0.5, 1.0, 3.0, 5.0\} \text{ horas-equivalentes}$$
Costo de camino: $g(n) = \sum c(s_i, a_i, s_{i+1})$. **Objetivo: minimizar $g$**.

---

## 4. Implementación de Algoritmos de Búsqueda

### 4.1 Base de Código: AIMA-Python
Se utiliza `search.py` de AIMA-Python (Russell & Norvig, 2021) como base, adaptando:
- Clase `CampusGuardProblem` heredando de `Problem`
- Implementación de `actions()`, `result()`, `goal_test()`, `path_cost()`, `h()`

### 4.2 BFS (Breadth-First Search)
```python
nodo_meta = breadth_first_graph_search(problema)
```
- Explora por niveles, garantiza solución de costo mínimo (costos uniformes)
- Complejidad temporal: $O(b^d)$, espacial: $O(b^d)$

### 4.3 DFS (Depth-First Search)
```python
nodo_meta = depth_first_graph_search(problema)
```
- Explora en profundidad, usa pila implícita
- Complejidad temporal: $O(b^m)$, espacial: $O(bm) = O(m)$
- No garantiza optimalidad

### 4.4 A* (A-Star Search)
```python
nodo_meta = astar_search(problema, h=None)  # usa problema.h()
```
- Expande nodo con menor $f(n) = g(n) + h(n)$
- Complejidad temporal: $O(b^d)$ peor caso, espacial: $O(b^d)$
- **Optimalidad garantizada si $h$ es admisible**

---

## 5. Diseño de Heurística para A*

### 5.1 Heurística: Costo Mínimo Teórico Restante
$$h(n) = \frac{\max(0, riesgo\_actual(n) - 25)}{\max\limits_{a \in A_{disponible}} \frac{efectividad(a) \times 100}{costo(a)}}$$

Donde $A_{disponible}$ son intervenciones no aplicadas que caben en $48 - h$ horas.

### 5.2 Justificación de Admisibilidad
$h(n)$ es **admisible** ($h(n) \le h^*(n)$) porque:

1. **Supone intervención ideal**: Usa la mejor ratio efectividad/costo teórica
2. **Ignora restricciones temporales**: Asume que cualquier intervención cabe
3. **Ignora límite de intervenciones**: No considera $MAX\_INTERVENCIONES = 4$
4. **Determinismo optimista**: Reducción exacta sin variabilidad estocástica

Por construcción, $h(n)$ nunca sobreestima el costo real óptimo $h^*(n)$.

### 5.3 Consistencia (Monotonía)
$h$ es **consistente**: $\forall n, a, n': h(n) \le c(n,a,n') + h(n')$  
Porque la reducción de riesgo es monótona y el costo mínimo teórico restante nunca aumenta más que el costo de la acción.

---

## 6. Experimentos y Benchmark

### 6.1 Configuración Experimental
- **8 estudiantes** con perfiles variados (riesgo 27–74)
- **3 algoritmos**: BFS, DFS, A*
- **Métricas**: nodos expandidos, nodos generados, tiempo (ms), costo solución, profundidad
- **Entorno**: Python 3.14, AIMA-Python adaptado

### 6.2 Tabla de Resultados

| Estudiante | Riesgo Inicial | Algoritmo | Éxito | Nodos Exp. | Nodos Gen. | Tiempo (ms) | Costo Sol. | Prof. |
|------------|----------------|-----------|-------|------------|------------|-------------|------------|-------|
| EST-2024-003 | 33.4 (medio) | BFS | Sí | 1 | 4 | 0.14 | 3.00 | 1 |
| EST-2024-003 | 33.4 (medio) | DFS | Sí | 1 | 4 | 0.09 | 5.00 | 1 |
| EST-2024-003 | 33.4 (medio) | A* | Sí | 2 | 7 | 0.20 | **1.00** | 1 |
| EST-2024-001 | 46.4 (medio) | BFS | Sí | 1 | 4 | 0.07 | 3.00 | 1 |
| EST-2024-001 | 46.4 (medio) | DFS | Sí | 1 | 4 | 0.08 | 5.00 | 1 |
| EST-2024-001 | 46.4 (medio) | A* | Sí | 5 | 14 | 0.40 | 3.00 | 1 |
| EST-2024-002 | 74.1 (alto) | BFS | Sí | 3 | 10 | 0.20 | 8.00 | 2 |
| EST-2024-002 | 74.1 (alto) | DFS | Sí | 2 | 7 | 0.13 | 6.00 | 2 |
| EST-2024-002 | 74.1 (alto) | A* | Sí | 17 | 34 | 1.19 | **6.00** | 2 |
| EST-2024-004 | 55.9 (alto) | BFS | Sí | 1 | 4 | 0.08 | 5.00 | 1 |
| EST-2024-004 | 55.9 (alto) | DFS | Sí | 1 | 4 | 0.09 | 5.00 | 1 |
| EST-2024-004 | 55.9 (alto) | A* | Sí | 8 | 21 | 0.63 | **4.00** | 2 |
| EST-2024-005 | 43.1 (medio) | BFS | Sí | 1 | 4 | 0.07 | 3.00 | 1 |
| EST-2024-005 | 43.1 (medio) | DFS | Sí | 1 | 4 | 0.07 | 5.00 | 1 |
| EST-2024-005 | 43.1 (medio) | A* | Sí | 3 | 10 | 0.28 | **1.50** | 2 |
| EST-2024-006 | 67.4 (alto) | BFS | Sí | 3 | 10 | 0.20 | 8.00 | 2 |
| EST-2024-006 | 67.4 (alto) | DFS | Sí | 2 | 7 | 0.13 | 6.00 | 2 |
| EST-2024-006 | 67.4 (alto) | A* | Sí | 10 | 25 | 0.83 | **4.50** | 3 |
| EST-2024-007 | 27.4 (medio) | BFS | Sí | 1 | 4 | 0.07 | 0.50 | 1 |
| EST-2024-007 | 27.4 (medio) | DFS | Sí | 1 | 4 | 0.07 | 5.00 | 1 |
| EST-2024-007 | 27.4 (medio) | A* | Sí | 1 | 4 | 0.09 | 0.50 | 1 |
| EST-2024-008 | 49.6 (medio) | BFS | Sí | 1 | 4 | 0.07 | 3.00 | 1 |
| EST-2024-008 | 49.6 (medio) | DFS | Sí | 1 | 4 | 0.07 | 5.00 | 1 |
| EST-2024-008 | 49.6 (medio) | A* | Sí | 5 | 14 | 0.40 | 3.00 | 1 |

### 6.3 Resumen Comparativo (Promedios)

| Algoritmo | Tasa Éxito | Nodos Exp. Prom. | Tiempo Prom. (ms) | Costo Prom. |
|-----------|------------|------------------|-------------------|-------------|
| **BFS** | 100.0% | 1.5 | 0.11 | 4.19 |
| **DFS** | 100.0% | 1.2 | 0.09 | 5.25 |
| **A*** | 100.0% | 6.4 | 0.50 | **2.94** |

**Hallazgos clave:**
- **A* reduce costo promedio 30% vs BFS** (2.94 vs 4.19) y **44% vs DFS** (2.94 vs 5.25)
- **BFS y DFS expanden menos nodos** (1.5 y 1.2 vs 6.4) porque el espacio es pequeño ($b \approx 3, d \le 3$)
- **A* expande más nodos** que BFS/DFS en casos simples (overhead de heurística), pero encuentra soluciones de **menor costo**
- **100% tasa de éxito** en todos los algoritmos (espacio acotado y solucionable)

---

## 7. Análisis de Complejidad Computacional (Big O)

### 7.1 Parámetros del Problema
- $b$ (factor de ramificación): $\approx 3$ (3–4 intervenciones válidas por estado)
- $d$ (profundidad solución óptima): 1–3 intervenciones
- $m$ (profundidad máxima): 4 (límite `MAX_INTERVENCIONES`)

### 7.2 Complejidad por Algoritmo

| Algoritmo | Temporal | Espacial | Optimalidad | Completitud |
|-----------|----------|----------|-------------|-------------|
| **BFS** | $O(b^d)$ | $O(b^d)$ | ✓ (costos uniformes) | ✓ |
| **DFS** | $O(b^m)$ | $O(bm)$ | ✗ | ✓ (espacio finito) |
| **A*** | $O(b^d)$* | $O(b^d)$ | ✓ ($h$ admisible) | ✓ |

*Con heurística admisible, A* expande $O(b^{d/\epsilon})$ donde $\epsilon$ depende de la calidad de $h$.

### 7.3 Estimación Numérica CampusGuard
- **Estados totales máximos**: $\sum_{i=0}^{4} b^i \approx 1 + 3 + 9 + 27 + 81 = 121$
- **BFS expande**: $\approx 1 + 3 + 9 = 13$ nodos (hasta $d=2$)
- **DFS expande**: Hasta 121 en peor caso
- **A* expande**: 5–17 nodos (guiado por $h$)

---

## 8. Evaluación de la Heurística en A*

### 8.1 Impacto en Rendimiento

| Métrica | BFS (sin heurística) | A* (con $h$) | Mejora |
|---------|---------------------|--------------|--------|
| Costo solución promedio | 4.19 | **2.94** | **30% menor** |
| Nodos expandidos (alto riesgo) | 3 | 10–17 | Más expansión |
| Optimalidad garantizada | Solo costos uniformes | ✓ Siempre | **Teórica** |

### 8.2 Análisis de Sensibilidad
La calidad de $h$ depende de:
1. **Precisión de `EFECTIVIDAD_BASE`**: Valores de literatura vs realidad institucional
2. **Granularidad de intervenciones**: Más tipos → mejor ratio máximo
3. **Ventana temporal**: 48h restringe opciones, $h$ menos informativa

En casos límite (riesgo CRÍTICO, ventana agotada), $h(n) \to \infty$ indicando correctamente ausencia de solución viable.

### 8.3 Conclusión Heurística
La heurística **costo mínimo teórico** es **admisible y consistente**, garantizando optimalidad en A*. Aunque expande más nodos que BFS/DFS en este espacio pequeño, **reduce el costo de la solución en 30–44%**, validando su uso en contextos donde el costo de intervención (horas tutoría, carga bienestar) es crítico.

---

## 9. Repositorio y Código

**Repositorio GitHub:** `https://github.com/jeisonmontoya/campusguard-search`  
**Estructura:**
```
campusguard-search/
├── src/
│   ├── aima_search.py      # AIMA search algorithms (adaptado)
│   ├── aima_utils.py       # Utilidades AIMA (sin numpy)
│   ├── campusguard_problem.py  # Formalización del problema
│   └── search_runner.py    # Benchmarking y métricas
├── benchmark/
│   ├── resultados.json     # Datos crudos
│   ├── tabla_benchmark.md  # Tabla para documento
│   ├── analisis_complejidad.md
│   └── evaluacion_heuristica.md
└── docs/
    └── documento_tecnico.pdf
```

**Ejecución:**
```bash
cd src && python search_runner.py
```

---

## 10. Conclusiones

1. **Formalización exitosa**: El problema CampusGuard se modela como espacio de estados determinista y discreto con $b \approx 3, d \le 3$.

2. **Implementación funcional**: BFS, DFS y A* ejecutan correctamente sobre AIMA-Python adaptado, con métricas cuantitativas.

3. **A* supera en costo**: Reduce costo promedio 30% vs BFS y 44% vs DFS gracias a heurística admisible.

4. **Heurística validada**: Costo mínimo teórico es admisible ($h \le h^*$) y consistente, garantizando optimalidad.

5. **Escalabilidad**: En espacios mayores (múltiples estudiantes, más intervenciones), la ventaja de A* crecería exponencialmente.

---

## Referencias

Barocas, S., Hardt, M., & Narayanan, A. (2023). *Fairness and machine learning: Limitations and opportunities*. MIT Press.

Congreso de la República de Colombia. (2012). *Ley Estatutaria 1581 de 2012, por la cual se dictan disposiciones generales para la protección de datos personales*.

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4th ed.). Pearson.

Simon, H. A. (1955). A behavioral model of rational choice. *The Quarterly Journal of Economics, 69*(1), 99–118. https://doi.org/10.2307/1884852

Tinto, V. (1993). *Leaving college: Rethinking the causes and cures of student attrition* (2nd ed.). University of Chicago Press.

---

*Documento generado automáticamente desde benchmark experimental. Código disponible en repositorio GitHub.*