"""Suite de tests unitarios y Oráculo SymPy para el módulo algebra.py (TP 1)."""

import unittest
from fractions import Fraction
import sympy as sp  # type: ignore[import-untyped]
from exactapy_core.algebra import (
    base_imagen,
    base_nucleo,
    determinante,
    escalonar_gauss_jordan,
    inversa,
    rango,
    resolver_sistema,
)
from exactapy_core.definiciones import (
    ClasificacionSistema,
    DimensionesIncompatiblesError,
    MatrizNoCuadradaError,
    MatrizSingularError,
    Vector,
)
from exactapy_core.matriz import Matriz


def a_sympy(m: Matriz) -> sp.Matrix:
    """Convierte una Matriz exacta de ExactaPy en una Matrix simbólica de SymPy."""
    filas_sp: list[list[sp.Rational]] = []
    for i in range(m.filas):
        fila_sp: list[sp.Rational] = [
            sp.Rational(m[i, j].numerator, m[i, j].denominator)
            for j in range(m.columnas)
        ]
        filas_sp.append(fila_sp)
    return sp.Matrix(filas_sp)


def desde_sympy(sm: sp.Matrix) -> Matriz:
    """Convierte una Matrix de SymPy con entradas racionales en nuestra Matriz."""
    grilla: list[Vector] = []
    for i in range(sm.rows):
        fila: Vector = []
        for j in range(sm.cols):
            val = sp.Rational(sm[i, j])
            fila.append(Fraction(int(val.p), int(val.q)))
        grilla.append(fila)
    return Matriz(grilla)


class TestGaussJordanYSistemas(unittest.TestCase):
    """Pruebas de escalonamiento RREF y Rouché-Frobenius contrastadas con SymPy."""

    def test_rref_contra_oraculo_sympy(self) -> None:
        casos: list[Matriz] = [
            Matriz([[2, 4, -2], [4, 9, -3], [-2, -3, 7]]),
            Matriz([[0, 2, 4, 6], [1, 3, 5, 7], [2, 6, 10, 14]]),
            Matriz([[0, 0, 0], [0, 0, 0]]),
            Matriz([[1, 2], [3, 4], [5, 6]]),
        ]
        for m in casos:
            res_propio = escalonar_gauss_jordan(m)
            rref_sp, pivotes_sp = a_sympy(m).rref()

            self.assertEqual(res_propio.rref, desde_sympy(rref_sp))
            self.assertEqual(res_propio.columnas_pivote, tuple(pivotes_sp))
            self.assertEqual(rango(m), len(pivotes_sp))

    def test_sistemas_lineales_tres_clasificaciones(self) -> None:
        # (SCD)
        a_scd = Matriz([[2, 1], [1, -1]])
        b_scd = [Fraction(5), Fraction(1)]
        sol_scd = resolver_sistema(a_scd, b_scd)
        self.assertEqual(sol_scd.clasificacion, ClasificacionSistema.COMPATIBLE_DETERMINADO)
        self.assertEqual(sol_scd.solucion_particular, [Fraction(2), Fraction(1)])
        self.assertEqual(sol_scd.base_nucleo, ())

        # (SCI)
        a_sci = Matriz([[1, 2, -1], [2, 4, 1], [-1, -2, -3]])
        b_sci = [Fraction(1), Fraction(5), Fraction(-5)]
        c_sci = Matriz([[1, 2, 3], [7, 10, 3]])
        d_sci = [Fraction(1), Fraction(2)]
        sol_sci = resolver_sistema(a_sci, b_sci)
        sol_2_sci = resolver_sistema(c_sci, d_sci)
        self.assertEqual(sol_sci.clasificacion, ClasificacionSistema.COMPATIBLE_INDETERMINADO)
        self.assertEqual(sol_2_sci.clasificacion, ClasificacionSistema.COMPATIBLE_INDETERMINADO)
        self.assertEqual(sol_sci.solucion_particular, [Fraction(2), Fraction(0), Fraction(1)])
        self.assertEqual(
            sol_2_sci.solucion_particular, [Fraction(-3, 2), Fraction(5, 4), Fraction(0)])
        self.assertEqual(len(sol_sci.base_nucleo), 1)
        self.assertEqual(
            sol_2_sci.base_nucleo,
            ([Fraction(6), Fraction(-9, 2), Fraction(1)],),
        )
        # Verificamos que se cumple: para todo v en el núcleo, A * v == 0
        for v in sol_sci.base_nucleo:
            prod = a_sci @ Matriz([[x] for x in v])
            self.assertEqual(prod, Matriz([[0], [0], [0]]))

        # (SI)
        a_si = Matriz([[1, 1], [2, 2]])
        b_si = [Fraction(1), Fraction(5)]
        sol_si = resolver_sistema(a_si, b_si)
        self.assertEqual(sol_si.clasificacion, ClasificacionSistema.INCOMPATIBLE)
        self.assertIsNone(sol_si.solucion_particular)

        with self.assertRaises(DimensionesIncompatiblesError):
            resolver_sistema(a_scd, [Fraction(1), Fraction(2), Fraction(3)])


class TestDeterminanteInversaYSubespacios(unittest.TestCase):
    """Pruebas para los Ejercicios 6 y 7."""

    def test_determinante_e_inversa(self) -> None:
        casos_inversibles: list[Matriz] = [
            Matriz([[1]]),
            Matriz([[1, 2], [3, 4]]),
            Matriz([[0, 1, 2], [1, 0, 3], [4, -3, 8]])
        ]
        for m in casos_inversibles:
            sm = a_sympy(m)

            det_sp = sp.Rational(sm.det())
            self.assertEqual(determinante(m), Fraction(int(det_sp.p), int(det_sp.q)))

            inv_propia = inversa(m)
            self.assertEqual(inv_propia, desde_sympy(sm.inv()))
            self.assertEqual(m @ inv_propia, Matriz.identidad(m.filas))

        det_0: Matriz = Matriz([[1, 2, 3], [4, 5, 6], [5, 7, 9]])
        self.assertEqual(determinante(det_0), Fraction(0))
        rectangular: Matriz = Matriz([[1, 2, 3], [4, 5, 6]])
        singular: Matriz = Matriz([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        with self.assertRaises(MatrizNoCuadradaError):
            determinante(rectangular)
        with self.assertRaises(MatrizSingularError):
            inversa(singular)
        with self.assertRaises(MatrizNoCuadradaError):
            inversa(rectangular)

    def test_nucleo_e_imagen(self) -> None:
        m = Matriz([
            [1, 2, 0, 3],
            [2, 4, 1, 7],
            [-1, -2, 2, -1],
        ])
        sm = a_sympy(m)

        nuc = base_nucleo(m)
        img = base_imagen(m)

        self.assertEqual(len(nuc), len(sm.nullspace()))
        self.assertEqual(len(img), len(sm.columnspace()))
        self.assertEqual(len(nuc) + len(img), m.columnas)

        img_sympy = tuple(desde_sympy(col).columna(0) for col in sm.columnspace())
        self.assertEqual(img, img_sympy)

        for v in nuc:
            col_v = Matriz([[x] for x in v])
            self.assertEqual(m @ col_v, Matriz([[0], [0], [0]]))

if __name__ == "__main__":
    unittest.main()
