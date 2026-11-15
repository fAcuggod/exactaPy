"""Módulo TP 0: Implementación del TAD matriz sobre el cuerpo de los racionales (Q)."""

from __future__ import annotations
from collections.abc import Sequence
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

    def __add__(self, otra: Matriz) -> Matriz:
        """Suma dos matrices de iguales dimensiones (A + B).

        Raises:
            DimensionesIncompatiblesError: Si self y otra tienen distinta dimensión.
        """
        if self.dimension != otra.dimension:
            raise DimensionesIncompatiblesError(
                "No se pueden sumar matrices de dimensión incompatible.")

        grilla_nueva: list[Vector] = []
        for i in range(self._filas):
            fila_resultado: Vector = []
            for j in range(self._columnas):
                fila_resultado.append(self[i, j] + otra[i, j])
            grilla_nueva.append(fila_resultado)

        return Matriz(grilla_nueva)

    def __sub__(self, otra: Matriz) -> Matriz:
        """Resta dos matrices de iguales dimensiones (A - B).

        Raises:
            DimensionesIncompatiblesError: Si self y otra tienen distinta dimensión.
        """
        if self.dimension != otra.dimension:
            raise DimensionesIncompatiblesError(
                "No se pueden restar matrices de dimensión incompatible.")

        return self + (Fraction(-1) * otra)

    def __mul__(self, escalar: int | Escalar) -> Matriz:
        """Multiplica la matriz por un escalar a derecha (A * k)."""
        if isinstance(escalar, bool) or not isinstance(escalar, (int, Fraction)):
            raise TypeError("El escalar debe ser un entero o Fraction.")
        factor: Escalar = Fraction(escalar)
        grilla_nueva: list[Vector] = []
        for i in range(self._filas):
            fila_resultado: Vector = []
            for j in range(self._columnas):
                fila_resultado.append(factor * self[i, j])
            grilla_nueva.append(fila_resultado)

        return Matriz(grilla_nueva)

    def __rmul__(self, escalar: int | Escalar) -> Matriz:
        """Multiplica un escalar por la matriz a izquierda (k * A)."""
        return self.__mul__(escalar)

    def __matmul__(self, otra: Matriz) -> Matriz:
        """Realiza el producto matricial (A @ B).

        Raises:
            DimensionesIncompatiblesError: Si self.columnas != otra.filas.
        """
        if self._columnas != otra._filas:
            raise DimensionesIncompatiblesError(
                "Las columnas de la primera matriz deben coincidir con las filas de la segunda."
            )

        grilla__nueva: list[Vector] = []
        for i in range(self._filas):
            fila_resultado: Vector = []
            for j in range(otra._columnas):
                fila_i: Vector = self.fila(i)
                col_j: Vector = otra.columna(j)
                suma_acumulada: Escalar = Fraction(0)
                for elem_a, elem_b in zip(fila_i, col_j):
                    suma_acumulada += elem_a * elem_b
                fila_resultado.append(suma_acumulada)
            grilla__nueva.append(fila_resultado)

        return Matriz(grilla__nueva)

    def transpuesta(self) -> Matriz:
        """Devuelve la matriz transpuesta A^T (intercambiando filas por columnas)."""
        grilla_nueva: list[Vector] = []
        for j in range(self._columnas):
            grilla_nueva.append(self.columna(j))

        return Matriz(grilla_nueva)

    @classmethod
    def identidad(cls, n: int) -> Matriz:
        """Construye y devuelve la matriz identidad I_n de dimensión n x n.

        Args:
            n: Dimensión de la matriz cuadrada (n >= 1).

        Raises:
            ValueError: Si n < 1.
        """
        if n < 1:
            raise ValueError("La dimensión n debe ser >= 1")

        grilla_nueva: list[Vector] = []
        for i in range(n):
            fila_actual: Vector = []
            for j in range(n):
                if i == j:
                    fila_actual.append(Fraction(1))
                else:
                    fila_actual.append(Fraction(0))
            grilla_nueva.append(fila_actual)
        return cls(grilla_nueva)

    def intercambiar_filas(self, f1: int, f2: int) -> Matriz:
        """Devuelve una nueva Matriz con las filas f1 y f2 intercambiadas (F_f1 <-> F_f2).

        Raises:
            IndexError: Si f1 o f2 están fuera de [0, filas).
        """
        if not (0 <= f1 < self.filas and 0 <= f2 < self.filas):
            raise IndexError("Asegúrate que f1 y f2 sean filas válidas.")

        grilla_nueva: list[Vector] = []
        for i in range(self._filas):
            if i == f1:
                grilla_nueva.append(self.fila(f2))
            elif i == f2:
                grilla_nueva.append(self.fila(f1))
            else:
                grilla_nueva.append(self.fila(i))
        return Matriz(grilla_nueva)

    def escalar_fila(self, fila: int, k: int | Escalar) -> Matriz:
        """Devuelve una nueva Matriz multiplicando la fila f por el escalar no nulo k.

        Raises:
            IndexError: Si f está fuera de [0, filas).
            ValueError: Si k == 0 (en Gauss-Jordan no es válido escalar fila por 0).
        """
        factor: Escalar = Fraction(k)
        if not 0 <= fila < self.filas:
            raise IndexError("*fila* no es una fila válida.")

        if k == 0:
            raise ValueError("No es válido escalar *fila* por 0.")

        grilla_nueva: list[Vector] = []
        for i in range(self._filas):
            if i == fila:
                fila_escalada: Vector = []
                for j in range(self._columnas):
                    valor: Escalar = factor * self[i, j]
                    fila_escalada.append(valor)
                grilla_nueva.append(fila_escalada)
            else:
                grilla_nueva.append(self.fila(i))

        return Matriz(grilla_nueva)

    def sumar_multiplo_fila(
        self, f_destino: int, f_origen: int, k: int | Escalar
    ) -> Matriz:
        """Devuelve una nueva Matriz aplicando F_destino <- F_destino + k * F_origen.

        Raises:
            IndexError: Si f_destino o f_origen están fuera de [0, filas).
            ValueError: Si f_destino == f_origen.
        """
        factor: Escalar = Fraction(k)
        if not (0 <= f_destino < self.filas and 0 <= f_origen < self.filas):
            raise IndexError("Las filas deben estar en rango.")

        if f_destino == f_origen:
            raise ValueError("*fila_destino* es igual a *fila_origen.")

        grilla_nueva: list[Vector] = []
        for i in range(self._filas):
            if i == f_destino:
                fila_combinada: Vector = []
                for j in range(self._columnas):
                    valor: Escalar = self[f_destino, j] + factor * self[f_origen, j]
                    fila_combinada.append(valor)
                grilla_nueva.append(fila_combinada)
            else:
                grilla_nueva.append(self.fila(i))

        return Matriz(grilla_nueva)

    def ampliar_columna(self, b: Sequence[EntradaEscalar]) -> Matriz:
        """Devuelve la matriz ampliada (A | b) agregando el vector b como última columna.

        Raises:
            DimensionesIncompatiblesError: Si len(b) != self.filas.
        """
        if len(b) != self._filas:
            raise DimensionesIncompatiblesError(
                "La longitud del vector columna debe coincidir con las filas de la matriz."
            )
        grilla_nueva: list[list[EntradaEscalar]] = []
        for i in range(self._filas):
            fila_ampliada: list[EntradaEscalar] = list(self._celdas[i])
            fila_ampliada.append(b[i])
            grilla_nueva.append(fila_ampliada)
        return Matriz(grilla_nueva)
