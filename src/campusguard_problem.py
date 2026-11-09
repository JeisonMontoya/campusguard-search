"""
CampusGuard - Problema de Búsqueda para Prevención de Deserción Académica
==========================================================================

Este módulo formaliza el problema de planificación de intervenciones para un 
estudiante en riesgo como un problema de búsqueda en espacio de estados.

Autor: Jeison Montoya
Curso: Inteligencia Artificial I INF DIS (A)
Universidad Militar Nueva Granada
Fecha: 2026

Basado en: Russell, S., & Norvig, P. (2021). Artificial Intelligence: A Modern Approach (4th ed.).
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set
from enum import Enum
import copy

# Importar desde AIMA
from aima_search import Problem, Node
from aima_utils import *


# =============================================================================
# DEFINICIÓN DEL DOMINIO: TIPOS DE DATOS Y ENUMS
# =============================================================================

class NivelRiesgo(Enum):
    """Niveles de riesgo académico basados en score compuesto"""
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class TipoIntervencion(Enum):
    """Tipos de intervenciones disponibles (acciones del agente)"""
    MONITOREAR = "monitorear"
    RECOMENDAR_TUTORIA = "recomendar_tutoria"
    NOTIFICAR_BIENESTAR = "notificar_bienestar"
    REDISTRIBUIR_CARGA = "redistribuir_carga"


@dataclass
class PerfilEstudiante:
    """
    Representa el perfil académico y de riesgo de un estudiante.
    Basado en los sensores descritos en Fase 1: asistencia, calificaciones, 
    actividad LMS, historial académico, encuestas bienestar.
    """
    id_estudiante: str
    asistencia_pct: float          # Porcentaje de asistencia (0-100)
    promedio_notas: float          # Promedio ponderado (0-5.0)
    actividad_lms_pct: float       # Actividad en LMS porcentaje (0-100)
    tendencia_asistencia: float    # Cambio en asistencia últimas 2 semanas (-100 a 100)
    tendencia_notas: float         # Cambio en notas últimas 2 semanas (-5.0 a 5.0)
    semestre: int                  # Semestre actual (1-10)
    historial_desercion: bool      # Si ha estado en riesgo antes
    score_riesgo: float = field(init=False)  # Score calculado 0-100
    nivel_riesgo: NivelRiesgo = field(init=False)
    
    def __post_init__(self):
        self.score_riesgo = self._calcular_score_riesgo()
        self.nivel_riesgo = self._determinar_nivel_riesgo()
    
    def _calcular_score_riesgo(self) -> float:
        """
        Calcula score de riesgo compuesto (0-100).
        Pesos basados en literatura (Tinto 1993, modelos de retención):
        - Asistencia: 30%
        - Notas: 30%
        - Actividad LMS: 20%
        - Tendencias: 15%
        - Historial: 5%
        """
        # Normalizar cada componente a 0-100
        p_asistencia = self.asistencia_pct
        p_notas = (self.promedio_notas / 5.0) * 100
        p_lms = self.actividad_lms_pct
        
        # Tendencias: normalizar a 0-100 (negativo = peor = mayor riesgo)
        p_tend_asist = max(0, 50 - self.tendencia_asistencia * 2.5)
        p_tend_notas = max(0, 50 - self.tendencia_notas * 10)
        p_tendencias = (p_tend_asist + p_tend_notas) / 2
        
        p_historial = 100 if self.historial_desercion else 0
        
        # Score ponderado (mayor = más riesgo)
        score = (0.30 * (100 - p_asistencia) + 
                 0.30 * (100 - p_notas) + 
                 0.20 * (100 - p_lms) + 
                 0.15 * p_tendencias + 
                 0.05 * p_historial)
        
        return round(min(100, max(0, score)), 2)
    
    def _determinar_nivel_riesgo(self) -> NivelRiesgo:
        if self.score_riesgo >= 75:
            return NivelRiesgo.CRITICO
        elif self.score_riesgo >= 50:
            return NivelRiesgo.ALTO
        elif self.score_riesgo >= 25:
            return NivelRiesgo.MEDIO
        return NivelRiesgo.BAJO

    def __hash__(self):
        """Hash basado en atributos inmutables de identificación."""
        return hash((
            self.id_estudiante,
            self.asistencia_pct,
            self.promedio_notas,
            self.actividad_lms_pct,
            self.tendencia_asistencia,
            self.tendencia_notas,
            self.semestre,
            self.historial_desercion
        ))

    def __eq__(self, other):
        """Igualdad basada en todos los atributos definitorios."""
        if not isinstance(other, PerfilEstudiante):
            return False
        return (
            self.id_estudiante == other.id_estudiante and
            self.asistencia_pct == other.asistencia_pct and
            self.promedio_notas == other.promedio_notas and
            self.actividad_lms_pct == other.actividad_lms_pct and
            self.tendencia_asistencia == other.tendencia_asistencia and
            self.tendencia_notas == other.tendencia_notas and
            self.semestre == other.semestre and
            self.historial_desercion == other.historial_desercion
        )


@dataclass
class EstadoIntervencion:
    """
    Representa el estado de una intervención aplicada.
    """
    tipo: TipoIntervencion
    costo: float                    # Costo en horas-equivalentes
    efectividad: float              # Probabilidad de reducir riesgo (0-1)
    duracion_dias: int              # Días que toma implementar
    aplicada: bool = False
    dia_inicio: int = 0
    resultado: Optional[str] = None
    
    def __hash__(self):
        return hash((
            self.tipo,
            self.costo,
            self.efectividad,
            self.duracion_dias,
            self.aplicada,
            self.dia_inicio,
            self.resultado
        ))
    
    def __eq__(self, other):
        if not isinstance(other, EstadoIntervencion):
            return False
        return (
            self.tipo == other.tipo and
            self.costo == other.costo and
            self.efectividad == other.efectividad and
            self.duracion_dias == other.duracion_dias and
            self.aplicada == other.aplicada and
            self.dia_inicio == other.dia_inicio and
            self.resultado == other.resultado
        )
    
    def __lt__(self, other):
        """Para comparación en PriorityQueue (heapq)."""
        if not isinstance(other, EstadoIntervencion):
            return NotImplemented
        # Comparar por tipo (orden de enum), luego por costo
        if self.tipo != other.tipo:
            return self.tipo.value < other.tipo.value
        return self.costo < other.costo


# =============================================================================
# COSTOS Y EFECTIVIDAD DE INTERVENCIONES (Basados en literatura y Fase 1)
# =============================================================================

COSTOS_INTERVENCION = {
    TipoIntervencion.MONITOREAR: 0.5,           # 30 min revisión
    TipoIntervencion.RECOMENDAR_TUTORIA: 3.0,   # 3 horas (sesión + prep)
    TipoIntervencion.NOTIFICAR_BIENESTAR: 1.0,  # 1 hora (reporte + seguimiento)
    TipoIntervencion.REDISTRIBUIR_CARGA: 5.0,   # 5 horas (coord + aprobaciones)
}

EFECTIVIDAD_BASE = {
    TipoIntervencion.MONITOREAR: 0.05,          # 5% reducción riesgo
    TipoIntervencion.RECOMENDAR_TUTORIA: 0.25,  # 25% reducción riesgo
    TipoIntervencion.NOTIFICAR_BIENESTAR: 0.15, # 15% reducción riesgo
    TipoIntervencion.REDISTRIBUIR_CARGA: 0.35,  # 35% reducción riesgo
}

DURACION_INTERVENCION = {
    TipoIntervencion.MONITOREAR: 1,      # 1 hora
    TipoIntervencion.RECOMENDAR_TUTORIA: 8,   # 8 horas (planificar + sesión)
    TipoIntervencion.NOTIFICAR_BIENESTAR: 2,  # 2 horas (reporte + seguimiento)
    TipoIntervencion.REDISTRIBUIR_CARGA: 12,  # 12 horas (coord + aprobaciones)
}

# Umbral de éxito: riesgo ≤ 25 (nivel BAJO)
UMBRAL_EXITO = 25.0
# Ventana máxima: 48 horas (Fase 1) - ahora en horas
VENTANA_MAXIMA_HORAS = 48
# Límite de intervenciones por plan (realismo)
MAX_INTERVENCIONES = 4


# =============================================================================
# CLASE PRINCIPAL: PROBLEMA DE BÚSQUEDA CAMPUSGUARD
# =============================================================================

class CampusGuardProblem(Problem):
    """
    Formalización del problema de búsqueda para CampusGuard.
    
    ESPACIO DE ESTADOS:
    -------------------
    Un estado es una tupla: (perfil_estudiante, intervenciones_aplicadas, hora_actual)
    - perfil_estudiante: PerfilEstudiante (mutable, cambia con intervenciones)
    - intervenciones_aplicadas: Tuple[EstadoIntervencion] (historial)
    - hora_actual: int (horas transcurridas desde detección)
    
    ESTADO INICIAL:
    ---------------
    Perfil del estudiante en riesgo detectado, sin intervenciones, día 0.
    
    ACCIONES:
    ---------
    Aplicar una intervención no aplicada aún, que quepa en la ventana de 48h.
    
    MODELO DE TRANSICIÓN:
    ---------------------
    Determinista: aplicar intervención → actualizar perfil (reducir riesgo) + 
    avanzar tiempo + registrar intervención.
    
    PRUEBA DE META:
    ---------------
    Score de riesgo ≤ UMBRAL_EXITO (25) Y hora_actual ≤ VENTANA_MAXIMA_HORAS (48)
    
    FUNCIÓN DE COSTO:
    -----------------
    Suma de costos de las intervenciones aplicadas (horas-equivalentes).
    Objetivo: MINIMIZAR costo total manteniendo efectividad.
    """
    
    def __init__(self, perfil_inicial: PerfilEstudiante):
        """
        Inicializa el problema con el perfil del estudiante en riesgo.
        
        Args:
            perfil_inicial: PerfilEstudiante con score_riesgo > UMBRAL_EXITO
        """
        # Estado inicial: (perfil, tupla_vacia_intervenciones, dia_0)
        estado_inicial = (perfil_inicial, (), 0)
        super().__init__(estado_inicial, goal=None)  # goal_test personalizado
        
        self.perfil_original = perfil_inicial
        self.costo_minimo_teorico = self._calcular_costo_minimo_teorico(perfil_inicial)
    
    def _calcular_costo_minimo_teorico(self, perfil: PerfilEstudiante) -> float:
        """
        Calcula el costo mínimo teórico para reducir el riesgo al umbral.
        Usado como heurística admisible para A*.
        
        Asume la intervención más costo-efectiva (mayor reducción por costo).
        """
        riesgo_actual = perfil.score_riesgo
        riesgo_objetivo = UMBRAL_EXITO
        reduccion_necesaria = max(0, riesgo_actual - riesgo_objetivo)
        
        if reduccion_necesaria <= 0:
            return 0.0
        
        # Calcular ratio efectividad/costo para cada intervención
        ratios = {}
        for tipo in TipoIntervencion:
            if tipo == TipoIntervencion.MONITOREAR:
                continue  # Monitorear solo no resuelve
            efectividad = EFECTIVIDAD_BASE[tipo] * 100  # En puntos de score
            costo = COSTOS_INTERVENCION[tipo]
            ratios[tipo] = efectividad / costo if costo > 0 else float('inf')
        
        # Usar la mejor ratio (más reducción por unidad de costo)
        mejor_ratio = max(ratios.values())
        costo_minimo = reduccion_necesaria / mejor_ratio
        
        return round(costo_minimo, 2)
    
    # -------------------------------------------------------------------------
    # MÉTODOS REQUERIDOS POR LA CLASE PROBLEMA DE AIMA
    # -------------------------------------------------------------------------
    
    def actions(self, state) -> List[TipoIntervencion]:
        """
        Retorna las acciones válidas en el estado actual.
        
        Una acción es válida si:
        1. No se ha aplicado ya (evitar ciclos)
        2. Cabe en la ventana de 48h (día_actual + duración ≤ 2)
        3. No excede el máximo de intervenciones
        4. El estudiante sigue en riesgo (score > umbral)
        """
        perfil, intervenciones, hora_actual = state
        
        # Si ya es meta, no hay acciones
        if self.goal_test(state):
            return []
        
        # Si se pasó la ventana de 48h, no hay acciones válidas
        if hora_actual > VENTANA_MAXIMA_HORAS:
            return []
        
        # Si ya se aplicaron muchas intervenciones
        if len(intervenciones) >= MAX_INTERVENCIONES:
            return []
        
        # Tipos ya aplicados
        tipos_aplicados = {i.tipo for i in intervenciones}
        
        acciones_validas = []
        for tipo in TipoIntervencion:
            if tipo in tipos_aplicados:
                continue
            
            duracion = DURACION_INTERVENCION[tipo]
            if hora_actual + duracion <= VENTANA_MAXIMA_HORAS:
                acciones_validas.append(tipo)
        
        return acciones_validas
    
    def result(self, state, action: TipoIntervencion):
        """
        Modelo de transición: aplica la intervención y retorna nuevo estado.
        
        Determinista: dado estado y acción, el resultado es único.
        """
        perfil, intervenciones, hora_actual = state
        
        # Crear copia profunda del perfil para modificar
        nuevo_perfil = copy.deepcopy(perfil)
        
        # Calcular efecto de la intervención
        efectividad = EFECTIVIDAD_BASE[action]
        reduccion_score = efectividad * 100  # Convertir a puntos de score
        
        # Aplicar reducción (con ruido determinista basado en hash para reproducibilidad)
        # En versión determinista: reducción exacta
        nuevo_score = max(0, nuevo_perfil.score_riesgo - reduccion_score)
        nuevo_perfil.score_riesgo = round(nuevo_score, 2)
        nuevo_perfil.nivel_riesgo = nuevo_perfil._determinar_nivel_riesgo()
        
        # Registrar intervención
        nueva_intervencion = EstadoIntervencion(
            tipo=action,
            costo=COSTOS_INTERVENCION[action],
            efectividad=efectividad,
            duracion_dias=DURACION_INTERVENCION[action],
            aplicada=True,
            dia_inicio=hora_actual,
            resultado=f"Riesgo: {perfil.score_riesgo:.1f} -> {nuevo_perfil.score_riesgo:.1f}"
        )
        
        nuevas_intervenciones = intervenciones + (nueva_intervencion,)
        nueva_hora = hora_actual + DURACION_INTERVENCION[action]
        
        return (nuevo_perfil, nuevas_intervenciones, nueva_hora)
    
    def goal_test(self, state) -> bool:
        """
        Prueba de meta: ¿El estudiante salió de riesgo dentro de 48h?
        
        Criterios:
        1. Score de riesgo ≤ UMBRAL_EXITO (25 = nivel BAJO)
        2. Hora actual ≤ VENTANA_MAXIMA_HORAS (48h)
        """
        perfil, intervenciones, hora_actual = state
        
        exito_riesgo = perfil.score_riesgo <= UMBRAL_EXITO
        exito_tiempo = hora_actual <= VENTANA_MAXIMA_HORAS
        
        return exito_riesgo and exito_tiempo
    
    def path_cost(self, c: float, state1, action: TipoIntervencion, state2) -> float:
        """
        Función de costo: suma de costos de intervenciones (horas-equivalentes).
        """
        return c + COSTOS_INTERVENCION[action]
    
    def h(self, node: Node) -> float:
        """
        Heurística para A*: Costo mínimo teórico restante.
        
        ADMISIBLE: Nunca sobreestima el costo real porque:
        - Asume la intervención más costo-efectiva posible
        - No considera restricciones de tiempo (48h)
        - No considera límite de intervenciones
        - No considera que intervenciones ya aplicadas reducen efectividad marginal
        
        Por tanto: h(n) ≤ h*(n) donde h* es el costo real óptimo.
        """
        perfil, intervenciones, hora_actual = node.state
        
        # Si ya es meta, heurística = 0
        if self.goal_test(node.state):
            return 0.0
        
        # Calcular riesgo restante
        riesgo_actual = perfil.score_riesgo
        reduccion_necesaria = max(0, riesgo_actual - UMBRAL_EXITO)
        
        if reduccion_necesaria <= 0:
            return 0.0
        
        # Mejor ratio efectividad/costo entre intervenciones NO aplicadas
        tipos_aplicados = {i.tipo for i in intervenciones}
        mejor_ratio = 0.0
        
        for tipo in TipoIntervencion:
            if tipo in tipos_aplicados or tipo == TipoIntervencion.MONITOREAR:
                continue
            
            # Verificar que quepa en tiempo restante
            tiempo_restante = VENTANA_MAXIMA_HORAS - hora_actual
            if DURACION_INTERVENCION[tipo] <= tiempo_restante:
                efectividad = EFECTIVIDAD_BASE[tipo] * 100
                costo = COSTOS_INTERVENCION[tipo]
                ratio = efectividad / costo if costo > 0 else float('inf')
                mejor_ratio = max(mejor_ratio, ratio)
        
        if mejor_ratio == 0:
            # No hay intervenciones viables → heurística alta (inadmisible teóricamente 
            # pero en práctica indica estado sin solución)
            return float('inf')
        
        return round(reduccion_necesaria / mejor_ratio, 2)
    
    def __str__(self):
        return f"CampusGuardProblem(estudiante={self.perfil_original.id_estudiante}, riesgo_inicial={self.perfil_original.score_riesgo})"


# =============================================================================
# FUNCIONES AUXILIARES PARA CREAR INSTANCIAS DE PRUEBA
# =============================================================================

def crear_estudiante_riesgo_alto() -> PerfilEstudiante:
    """Crea un estudiante con riesgo ALTO (score ~60)"""
    return PerfilEstudiante(
        id_estudiante="EST-2024-001",
        asistencia_pct=65.0,
        promedio_notas=2.8,
        actividad_lms_pct=40.0,
        tendencia_asistencia=-15.0,
        tendencia_notas=-0.5,
        semestre=2,
        historial_desercion=False
    )


def crear_estudiante_riesgo_critico() -> PerfilEstudiante:
    """Crea un estudiante con riesgo CRÍTICO (score ~85)"""
    return PerfilEstudiante(
        id_estudiante="EST-2024-002",
        asistencia_pct=35.0,
        promedio_notas=1.9,
        actividad_lms_pct=15.0,
        tendencia_asistencia=-30.0,
        tendencia_notas=-1.2,
        semestre=1,
        historial_desercion=True
    )


def crear_estudiante_riesgo_medio() -> PerfilEstudiante:
    """Crea un estudiante con riesgo MEDIO (score ~35)"""
    return PerfilEstudiante(
        id_estudiante="EST-2024-003",
        asistencia_pct=80.0,
        promedio_notas=3.2,
        actividad_lms_pct=60.0,
        tendencia_asistencia=-5.0,
        tendencia_notas=-0.2,
        semestre=3,
        historial_desercion=False
    )


def crear_estudiantes_prueba() -> List[PerfilEstudiante]:
    """Crea un conjunto de estudiantes para benchmarking."""
    return [
        crear_estudiante_riesgo_medio(),      # Score ~35 - fácil
        crear_estudiante_riesgo_alto(),       # Score ~60 - medio
        crear_estudiante_riesgo_critico(),    # Score ~85 - difícil
        # Casos adicionales variando parámetros
        PerfilEstudiante("EST-2024-004", 50.0, 2.5, 30.0, -20.0, -0.8, 1, False),  # ~70
        PerfilEstudiante("EST-2024-005", 75.0, 3.0, 55.0, -10.0, -0.3, 2, True),   # ~45
        PerfilEstudiante("EST-2024-006", 45.0, 2.0, 25.0, -25.0, -1.0, 1, True),   # ~78
        PerfilEstudiante("EST-2024-007", 85.0, 3.5, 70.0, -2.0, 0.0, 3, False),    # ~20 (ya bajo)
        PerfilEstudiante("EST-2024-008", 55.0, 2.7, 45.0, -18.0, -0.6, 2, False),  # ~58
    ]


# =============================================================================
# VISUALIZACIÓN Y DEBUG
# =============================================================================

def imprimir_estado(state, titulo="ESTADO"):
    """Imprime un estado de forma legible."""
    perfil, intervenciones, hora = state
    print(f"\n{'='*60}")
    print(f"{titulo}: {perfil.id_estudiante} | Hora {hora}h | Riesgo: {perfil.score_riesgo} ({perfil.nivel_riesgo.value})")
    print(f"{'='*60}")
    print(f"  Asistencia: {perfil.asistencia_pct}% | Promedio: {perfil.promedio_notas}/5.0 | LMS: {perfil.actividad_lms_pct}%")
    print(f"  Tendencia Asist: {perfil.tendencia_asistencia:+.1f}% | Tendencia Notas: {perfil.tendencia_notas:+.1f}")
    print(f"  Historial deserción: {'Sí' if perfil.historial_desercion else 'No'}")
    
    if intervenciones:
        print(f"\n  Intervenciones aplicadas ({len(intervenciones)}):")
        costo_total = 0
        for i, interv in enumerate(intervenciones, 1):
            print(f"    {i}. {interv.tipo.value.upper()} (hora {interv.dia_inicio}h, {interv.duracion_dias}h, costo={interv.costo}h)")
            print(f"       -> {interv.resultado}")
            costo_total += interv.costo
        print(f"  COSTO TOTAL: {costo_total:.1f} horas-equivalentes")
    else:
        print("\n  Sin intervenciones aplicadas")


def imprimir_solucion(node: Node, problema: CampusGuardProblem):
    """Imprime la solución completa desde el nodo meta."""
    if node is None:
        print("NO SE ENCONTRÓ SOLUCIÓN")
        return
    
    # Reconstruir camino
    camino = []
    n = node
    while n:
        camino.append(n)
        n = n.parent
    camino.reverse()
    
    print(f"\n{'#'*70}")
    print(f"SOLUCIÓN ENCONTRADA - {problema.perfil_original.id_estudiante}")
    print(f"{'#'*70}")
    print(f"Costo total (g): {node.path_cost:.2f} horas")
    print(f"Profundidad: {node.depth} intervenciones")
    print(f"Nodos expandidos: {getattr(node, '_nodos_expandidos', 'N/A')}")
    
    for i, n in enumerate(camino):
        print(f"\n--- Paso {i} ---")
        imprimir_estado(n.state, f"PASO {i}")


if __name__ == "__main__":
    # Prueba rápida
    print("="*70)
    print("PRUEBA DEL PROBLEMA CAMPUSGUARD")
    print("="*70)
    
    estudiante = crear_estudiante_riesgo_alto()
    print(f"\nEstudiante creado: {estudiante.id_estudiante}")
    print(f"Score de riesgo: {estudiante.score_riesgo} ({estudiante.nivel_riesgo.value})")
    
    problema = CampusGuardProblem(estudiante)
    print(f"\nProblema creado: {problema}")
    print(f"Costo mínimo teórico (heurística inicial): {problema.costo_minimo_teorico}")
    
    # Probar acciones iniciales
    estado_inicial = problema.initial
    acciones = problema.actions(estado_inicial)
    print(f"\nAcciones válidas iniciales: {[a.value for a in acciones]}")
    
    # Probar transición
    if acciones:
        nuevo_estado = problema.result(estado_inicial, acciones[0])
        print(f"\nDespués de {acciones[0].value}:")
        imprimir_estado(nuevo_estado)
    
    print("\n✓ Módulo campusguard_problem.py cargado correctamente")