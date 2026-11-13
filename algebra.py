"""Módulo TP 1: Algoritmos de Álgebra Lineal exacta y resolución de sistemas."""

from __future__ import annotations
from collections.abc import Sequence
from fractions import Fraction
from definiciones import (
    ClasificacionSistema,
    DimensionesIncompatiblesError,
    EntradaEscalar,
    Escalar,
    OperacionElemental,
    ResultadoEscalonamiento,
    SolucionSistema,
    TipoOperacionElemental,
    Vector,
)
from matriz import Matriz


def escalonar_gauss_jordan(a: Matriz) -> ResultadoEscalonamiento:
    """Calcula la Forma Escalonada Reducida por Filas (RREF) registrando cada paso.

    PRE: True (toda instancia de Matriz cumple el invariante de representación).

    Args:
        a: Matriz de entrada de m x n sobre Q.

    Returns:
        ResultadoEscalonamiento con la matriz RREF, tupla de pasos elementales,
        índices de las columnas pivote y cantidad de intercambios de filas.
    """
    actual: Matriz = a
    pasos: list[OperacionElemental] = []
    columnas_pivote: list[int] = []
    intercambios: int = 0
    fila_pivote: int = 0

    for col in range(actual.columnas):
        if fila_pivote >= actual.filas:
            break

        fila_candidata: int | None = None
        for r in range(fila_pivote, actual.filas):
            if actual[r, col] != Fraction(0):
                fila_candidata = r
                break

        if fila_candidata is None:
            continue

        columnas_pivote.append(col)

        if fila_candidata != fila_pivote:
            actual = actual.intercambiar_filas(fila_pivote, fila_candidata)
            intercambios += 1
            pasos.append(OperacionElemental(
                        tipo=TipoOperacionElemental.INTERCAMBIO,
                        fila_destino=fila_pivote,
                        descripcion=f"F{fila_pivote + 1} <-> F{fila_candidata + 1}",
                        fila_origen=fila_candidata))

        valor_pivote = actual[fila_pivote, col]
        if valor_pivote != 1:
            factor_escala: Escalar = Fraction(1) / valor_pivote
            actual = actual.escalar_fila(fila_pivote, factor_escala)
            pasos.append(OperacionElemental(
                        tipo=TipoOperacionElemental.ESCALADO,
                        fila_destino=fila_pivote,
                        descripcion=f"F{fila_pivote + 1} -> {factor_escala} * F{fila_pivote + 1}",
                        factor= factor_escala))

        for i in range(actual.filas):
            if i != fila_pivote and actual[i, col] != Fraction(0):
                factor_elim: Escalar = -actual[i, col]
                actual = actual.sumar_multiplo_fila(i, fila_pivote, factor_elim)
                pasos.append(OperacionElemental(
                        tipo=TipoOperacionElemental.ELIMINACION,
                        fila_destino=i,
                        descripcion=f"F{i + 1} -> F{i + 1} + {factor_elim} * F{fila_pivote + 1}",
                        fila_origen=fila_pivote,
                        factor=factor_elim))
        fila_pivote += 1

    return ResultadoEscalonamiento(
        rref=actual,
        pasos=tuple(pasos),
        columnas_pivote=tuple(columnas_pivote),
        intercambios_realizados=intercambios,
    )

def rango(a: Matriz) -> int:
    """Calcula el rango de la matriz A (cantidad de columnas pivote en su RREF)."""
    # TODO 4: Escalonar 'a' y devolver la cantidad de columnas pivote.
    pass


def resolver_sistema(a: Matriz, b: Sequence[EntradaEscalar]) -> SolucionSistema:
    """Clasifica y resuelve el sistema lineal Ax = b usando Gauss-Jordan y Rouché-Frobenius.

    Raises:
        DimensionesIncompatiblesError: Si len(b) != a.filas.
    """
    # 1. Construimos la matriz ampliada (A | b) y la escalonamos
    #    (ampliar_columna ya lanza DimensionesIncompatiblesError si len(b) != a.filas)
    ampliada: Matriz = a.ampliar_columna(b)
    esc: ResultadoEscalonamiento = escalonar_gauss_jordan(ampliada)

    n_incognitas: int = a.columnas
    pivotes_a: list[int] = [c for c in esc.columnas_pivote if c < n_incognitas]
    rango_a: int = len(pivotes_a)
    rango_amp: int = len(esc.columnas_pivote)

    # TODO 5 (Sistema Incompatible):
    # Si rango_a < rango_amp:
    #   Devolver SolucionSistema con clasificacion=ClasificacionSistema.INCOMPATIBLE,
    #   rango_a=rango_a, rango_ampliada=rango_amp, solucion_particular=None,
    #   base_nucleo=(), pasos_gauss=esc.pasos.

    # TODO 6 (Solución particular para sistemas compatibles):
    # Crear sol_particular: Vector = [Fraction(0) for _ in range(n_incognitas)]
    # Recorrer con 'for fila_idx, col_piv in enumerate(pivotes_a):'
    #   Asignar sol_particular[col_piv] = esc.rref[fila_idx, n_incognitas]

    # TODO 7 (Base del núcleo / variables libres):
    # Una columna 'c' (entre 0 y n_incognitas - 1) es libre si 'c not in pivotes_a'.
    # Por cada 'col_libre' libre:
    #   - Crear vec_gen: Vector = [Fraction(0) for _ in range(n_incognitas)]
    #   - Poner vec_gen[col_libre] = Fraction(1)
    #   - Para cada 'fila_idx, col_piv in enumerate(pivotes_a)':
    #       vec_gen[col_piv] = -esc.rref[fila_idx, col_libre]
    #   - Guardar vec_gen en una lista 'generadores_nucleo'.

    # TODO 8:
    # Determinar si es COMPATIBLE_DETERMINADO (si rango_a == n_incognitas)
    # o COMPATIBLE_INDETERMINADO (si rango_a < n_incognitas), y devolver SolucionSistema.
    pass
