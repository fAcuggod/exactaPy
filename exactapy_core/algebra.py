"""Módulo TP 1: Algoritmos de álgebra lineal exacta y resolución de sistemas."""

from __future__ import annotations
from collections.abc import Sequence
from fractions import Fraction
from exactapy_core.definiciones import (
    ClasificacionSistema,
    EntradaEscalar,
    Escalar,
    OperacionElemental,
    ResultadoEscalonamiento,
    SolucionSistema,
    TipoOperacionElemental,
    Vector,
    MatrizNoCuadradaError,
    MatrizSingularError
)
from exactapy_core.matriz import Matriz


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
    return len(escalonar_gauss_jordan(a).columnas_pivote)

def resolver_sistema(a: Matriz, b: Sequence[EntradaEscalar]) -> SolucionSistema:
    """Clasifica y resuelve el sistema lineal Ax = b usando Gauss-Jordan y Rouché-Frobenius.

    Raises:
        DimensionesIncompatiblesError: Si len(b) != a.filas.
    """
    ampliada: Matriz = a.ampliar_columna(b)
    esc: ResultadoEscalonamiento = escalonar_gauss_jordan(ampliada)

    n_incognitas: int = a.columnas
    pivotes_a: list[int] = [c for c in esc.columnas_pivote if c < n_incognitas]
    rango_a: int = len(pivotes_a)
    rango_amp: int = len(esc.columnas_pivote)

    if rango_a < rango_amp:
        return SolucionSistema(clasificacion=ClasificacionSistema.INCOMPATIBLE,
                               rango_a=rango_a,
                               rango_ampliada=rango_amp,
                               solucion_particular=None,
                               base_nucleo=(),
                               pasos_gauss=esc.pasos)

    sol_particular: Vector = [Fraction(0) for _ in range(n_incognitas)]
    for fila_idx, col_piv in enumerate(pivotes_a):
        sol_particular[col_piv] = esc.rref[fila_idx, n_incognitas]

    generadores_nucleo: list[Vector] = []
    for c in range(n_incognitas):
        if c not in pivotes_a:
            vec_gen: Vector = [Fraction(0)] * n_incognitas
            vec_gen[c] = Fraction(1)
            for fila_idx, col_piv in enumerate(pivotes_a):
                vec_gen[col_piv] = -esc.rref[fila_idx, c]
            generadores_nucleo.append(vec_gen)

    if rango_a == n_incognitas:
        return SolucionSistema(clasificacion=ClasificacionSistema.COMPATIBLE_DETERMINADO,
                               rango_a=n_incognitas,
                               rango_ampliada=rango_amp,
                               solucion_particular=sol_particular,
                               base_nucleo=(),
                               pasos_gauss=esc.pasos)

    return SolucionSistema(clasificacion=ClasificacionSistema.COMPATIBLE_INDETERMINADO,
                               rango_a=rango_a,
                               rango_ampliada=rango_amp,
                               solucion_particular=sol_particular,
                               base_nucleo=tuple(generadores_nucleo),
                               pasos_gauss=esc.pasos)

def determinante(a: Matriz) -> Escalar:
    """Calcula el determinante de una matriz cuadrada A sobre Q.

    PRE: True (valida internamente que sea cuadrada).

    Raises:
        MatrizNoCuadradaError: Si a.filas != a.columnas.
    """
    if a.filas != a.columnas:
        raise MatrizNoCuadradaError("La matriz *a* no es cuadrada.")

    esc: ResultadoEscalonamiento = escalonar_gauss_jordan(a)

    if len(esc.columnas_pivote) < a.filas:
        return Fraction(0)

    intercambios_totales: Escalar = Fraction(-1) ** esc.intercambios_realizados
    prod_factores: Escalar = Fraction(1)
    for paso in esc.pasos:
        if paso.tipo == TipoOperacionElemental.ESCALADO and paso.factor is not None:
            prod_factores *= paso.factor
    return intercambios_totales / prod_factores

def inversa(a: Matriz) -> Matriz:
    """Calcula la matriz inversa A^(-1) mediante Gauss-Jordan sobre (A | I_n).

    PRE: True (valida que sea cuadrada e inversible).

    Raises:
        MatrizNoCuadradaError: Si a.filas != a.columnas.
        MatrizSingularError: Si det(A) == 0 (rango(A) < n).
    """
    if a.filas != a.columnas:
        raise MatrizNoCuadradaError("La matriz *a* no es cuadrada.")

    ampliada: Matriz = a
    ident: Matriz = Matriz.identidad(a.filas)
    for j in range(ident.columnas):
        ampliada = ampliada.ampliar_columna(ident.columna(j))

    esc: ResultadoEscalonamiento = escalonar_gauss_jordan(ampliada)
    pivotes_en_a: list[int] = [c for c in esc.columnas_pivote if c < a.columnas]
    if len(pivotes_en_a) < a.filas:
        raise MatrizSingularError("La matriz *a* no es invertible.")

    inversa_a: list[Vector] = []
    for i in range(ampliada.filas):
        fila_actual: Vector = []
        for j in range(a.columnas, ampliada.columnas):
            fila_actual.append(esc.rref[i, j])
        inversa_a.append(fila_actual)

    return Matriz(inversa_a)

def base_nucleo(a: Matriz) -> tuple[Vector, ...]:
    """Devuelve una base del subespacio Núcleo Nu(A) = {x in Q^n : A*x = 0}."""
    vec_nulo: Vector = [Fraction(0)] * a.filas
    sist: SolucionSistema = resolver_sistema(a, vec_nulo)
    return sist.base_nucleo


def base_imagen(a: Matriz) -> tuple[Vector, ...]:
    """Devuelve una base del subespacio Imagen Im(A) (espacio columna de A)."""
    base: list[Vector] = []
    esc: ResultadoEscalonamiento = escalonar_gauss_jordan(a)

    for col in esc.columnas_pivote:
        base.append(a.columna(col))
    return tuple(base)
