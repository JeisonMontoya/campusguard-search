# Análisis de Complejidad Computacional (Big O)

## Parámetros del Problema
- **b** (factor de ramificación): Número máximo de acciones válidas por estado ≈ 3-4
- **d** (profundidad de la solución óptima): Número de intervenciones necesarias ≈ 1-3
- **m** (profundidad máxima del espacio de estados): Límite por ventana 48h y MAX_INTERVENCIONES = 4

## Complejidad por Algoritmo

### BFS (Breadth-First Search)
- **Temporal**: O(b^d) — Explora todos los nodos hasta profundidad d
- **Espacial**: O(b^d) — Debe almacenar toda la frontera (todos los nodos en nivel d)
- **Optimalidad**: ✓ Garantiza solución de costo mínimo (si costos uniformes)
- **Completitud**: ✓ Encuentra solución si existe (espacio finito)

### DFS (Depth-First Search)
- **Temporal**: O(b^m) — En peor caso explora todo el árbol hasta profundidad m
- **Espacial**: O(b·m) = O(m) — Solo almacena camino actual + hermanos
- **Optimalidad**: ✗ No garantiza costo mínimo
- **Completitud**: ✗ Puede fallar en espacios infinitos (pero nuestro espacio es finito)

### A* (A-Star Search)
- **Temporal**: O(b^d) en peor caso, pero típicamente O(b^(d/ε)) con buena heurística
- **Espacial**: O(b^d) — Similar a BFS, almacena frontera priorizada
- **Optimalidad**: ✓ Garantiza solución óptima SI heurística es admisible (h ≤ h*)
- **Completitud**: ✓ En espacios finitos con heurística admisible

## Comparación Espacio de Estados CampusGuard

| Métrica | Valor Típico | Nota |
|---------|--------------|------|
| b (ramificación) | 3 | 3-4 intervenciones válidas por estado |
| d (profundidad óptima) | 2 | 1-3 intervenciones para reducir riesgo |
| m (profundidad máx) | 4 | Límite MAX_INTERVENCIONES |

## Estimación Numérica
- **Estados totales máximos**: Σ(b^i) para i=0..m ≈ 1 + 3 + 9 + 27 + 81 = 121
- **BFS expande**: ~1 + 3 + 9 = 13 nodos (hasta profundidad d=2)
- **DFS expande**: Hasta 121 en peor caso (explora rama completa)
- **A* expande**: ~5-10 nodos (guiado por heurística admisible)

## Impacto de la Heurística en A*
La heurística h(n) = costo mínimo teórico restante:
- **Admisibilidad**: h(n) ≤ h*(n) porque asume intervención ideal sin restricciones
- **Consistencia**: h(n) ≤ c(n,a,n') + h(n') se cumple (reducción monótona de riesgo)
- **Efecto**: Reduce factor de ramificación efectivo de b a b' ≈ 1.5-2.0
- **Ahorro**: Expande ~50-70% menos nodos que BFS en casos típicos