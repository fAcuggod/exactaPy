"""Módulo TP 0: Implementación del TAD Matriz sobre el cuerpo de los racionales (Q)."""

from __future__ import annotations
from fractions import Fraction
from definiciones import (
    DimensionesIncompatiblesError,
    EntradaEscalar,
    Escalar,
    GrillaEntrada,
    Vector,
)


class Matriz:
    """Representa una matriz inmutable de m x n sobre el cuerpo racional Q.

    Invariante de Representación:
        - _filas > 0 y _columnas > 0.
        - len(_celdas) == _filas.
        - Para toda fila r en _celdas: len(r) == _columnas.
        - Todos los elementos almacenados en _celdas son instancias de Fraction.
    """

    # Declaración de tipos de los atributos privados para mypy --strict
    _celdas: tuple[tuple[Escalar, ...], ...]
    _filas: int
    _columnas: int

    def __init__(self, grilla: GrillaEntrada) -> None:
        """Construye una Matriz validando la grilla y convirtiendo a Fraction.

        PRE: True (valida internamente y lanza ValueError/TypeError si no cumple).

        Args:
            grilla: Lista de listas con enteros, strings fraccionarios o Fractions.

        Raises:
            ValueError: Si la grilla está vacía, alguna fila está vacía, o las
                filas tienen distinta longitud.
            TypeError: Si algún elemento es de tipo float (prohibido por exactitud).
        """
        if len(grilla) == 0 or len(grilla[0]) == 0:
            raise ValueError("La matriz no puede ser vacía.")

        ancho_esperado: int = len(grilla[0])
        for fila in grilla:
            if len(fila) != ancho_esperado:
                raise ValueError("Todas las filas deben tener la misma longitud.")

        filas_convertidas: list[tuple[Escalar, ...]] = []
        for i in range(len(grilla)):
            fila_actual: list[Escalar] = []
            for j in range(len(grilla[0])):
                valor: EntradaEscalar = grilla[i][j]
                if isinstance(valor, (float, bool)):
                    raise TypeError("No se permiten floats ni booleanos.")
                fila_actual.append(Fraction(valor))
            filas_convertidas.append(tuple(fila_actual))

        self._celdas = tuple(filas_convertidas)
        self._filas = len(grilla)
        self._columnas = ancho_esperado

    @property
    def filas(self) -> int:
        """Devuelve la cantidad de filas de la matriz (solo lectura)."""
        return self._filas

    @property
    def columnas(self) -> int:
        """Devuelve la cantidad de columnas de la matriz (solo lectura)."""
        return self._columnas

    @property
    def dimension(self) -> tuple[int, int]:
        """Devuelve una tupla (filas, columnas) con el tamaño de la matriz."""
        return (self._filas, self._columnas)

    def __getitem__(self, indices: tuple[int, int]) -> Escalar:
        """Permite indexar la matriz usando A[i, j] con índices de 0 a m-1, n-1.

        PRE: True (valida rangos y lanza IndexError si están fuera de rango).

        Args:
            indices: Tupla (i, j) con la fila y columna deseadas.

        Returns:
            El escalar (Fraction) almacenado en la posición (i, j).

        Raises:
            IndexError: Si i o j están fuera de los rangos [0, filas) o [0, columnas).
        """
        # Desempaquetamos la tupla de índices en dos variables enteras:
        i, j = indices

        if 0 <= i < self._filas and 0 <= j < self._columnas:
            return self._celdas[i][j]
        raise IndexError("Índice fuera de rango.")

    def fila(self, i: int) -> Vector:
        """Devuelve una copia de la fila i-ésima como lista de Escalares.

        Args:
            i: Índice de la fila (0 <= i < filas).

        Raises:
            IndexError: Si el índice de fila está fuera de rango.
        """
        if 0 <= i < self._filas:
            return list(self._celdas[i])
        raise IndexError("Índice de fila fuera de rango.")

    def columna(self, j: int) -> Vector:
        """Devuelve una copia de la columna j-ésima como lista de Escalares.

        Args:
            j: Índice de la columna (0 <= j < columnas).

        Raises:
            IndexError: Si el índice de columna está fuera de rango.
        """
        if 0 <= j < self._columnas:
            col: list[Escalar] = []
            for i in range(self._filas):
                col.append(self._celdas[i][j])
            return col
        raise IndexError("Índice de columna fuera de rango.")

    def __eq__(self, otro: object) -> bool:
        """Compara si dos matrices son matemáticamente iguales celda por celda."""
        # En mypy --strict, __eq__ debe aceptar 'object' porque alguien podría comparar A == "hola".
        if not isinstance(otro, Matriz):
            return False

        return self._celdas == otro._celdas

    def __repr__(self) -> str:
        """Devuelve una representación legible de la matriz para la consola."""
        lineas: list[str] = []
        for fila in self._celdas:
            elementos_str: list[str] = [str(elem) for elem in fila]
            lineas.append("[" + ", ".join(elementos_str) + "]")
        return "Matriz([\n  " + ",\n  ".join(lineas) + "\n])"
