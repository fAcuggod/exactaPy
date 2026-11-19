"""Suite de tests unitarios de caja blanca para el TAD Matriz (TP 0)."""

import unittest
from fractions import Fraction
from definiciones import DimensionesIncompatiblesError
from matriz import Matriz


class TestMatrizCreacionEIndexacion(unittest.TestCase):
    """Tests para el Ejercicio 1: __init__, propiedades, __getitem__, fila, columna, __eq__."""

    def test_creacion_y_simplificacion_racional(self) -> None:
        m = Matriz([[1, "2/4"], ["-3", Fraction(6, 8)]])
        self.assertEqual(m.filas, 2)
        self.assertEqual(m.columnas, 2)
        self.assertEqual(m.dimension, (2, 2))
        self.assertEqual(m[0, 1], Fraction(1, 2))
        self.assertEqual(m[1, 1], Fraction(3, 4))

    def test_creacion_invalida_lanza_excepciones(self) -> None:
        with self.assertRaises(ValueError):
            Matriz([])
        with self.assertRaises(ValueError):
            Matriz([[]])

        with self.assertRaises(ValueError):
            Matriz([[1, 2], [3]])

        with self.assertRaises(TypeError):
            Matriz([[1, 0.5]])  # type: ignore[list-item]
        with self.assertRaises(TypeError):
            Matriz([[True, 1]])  # type: ignore[list-item]

    def test_indexacion_filas_columnas_y_bordes(self) -> None:
        m = Matriz([[10, 20, 30], [40, 50, 60]])
        self.assertEqual(m.fila(1), [Fraction(40), Fraction(50), Fraction(60)])
        self.assertEqual(m.columna(2), [Fraction(30), Fraction(60)])

        with self.assertRaises(IndexError):
            _ = m[-1, 0]
        with self.assertRaises(IndexError):
            _ = m[0, 3]
        with self.assertRaises(IndexError):
            m.fila(2)
        with self.assertRaises(IndexError):
            m.columna(-1)

    def test_igualdad_y_representacion(self) -> None:
        a = Matriz([[1, "1/2"], [0, 1]])
        b = Matriz([[1, "2/4"], [0, 1]])
        c = Matriz([[1, 0], [0, 1]])
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, "no soy una matriz")
        self.assertIn("1/2", repr(a))


class TestMatrizAlgebraYOperaciones(unittest.TestCase):
    """Tests para los Ejercicios 2 y 3: operadores y operaciones elementales."""

    def test_suma_resta_y_escalares(self) -> None:
        a = Matriz([[1, 2], [3, 4]])
        b = Matriz([[10, 20], [30, 40]])
        c = Matriz([[1, 3, 4], [3, 4, 9]])
        self.assertEqual(a + b, Matriz([[11, 22], [33, 44]]))
        self.assertEqual(b - a, Matriz([[9, 18], [27, 36]]))
        self.assertEqual(2 * a, Matriz([[2, 4], [6, 8]]))
        self.assertEqual(a * Fraction(1, 2), Matriz([["1/2", 1], ["3/2", 2]]))

        with self.assertRaises(DimensionesIncompatiblesError):
            _ = a + c
        with self.assertRaises(DimensionesIncompatiblesError):
            _= a - c
        with self.assertRaises(TypeError):
            _ = a * True
        with self.assertRaises(TypeError):
            _ = b * 2.0

    def test_producto_matricial_y_transpuesta(self) -> None:
        a = Matriz([[1, 2, 3], [3, 4, 1]])
        b = Matriz([[1, 2], [5, 1], [9, 0]])
        c = a @ b
        d = Matriz([[1, 0], [3, 4]])
        a_transpuesta = a.transpuesta()
        self.assertEqual(c.dimension, (2, 2))
        self.assertEqual(a_transpuesta, Matriz([[1, 3], [2, 4], [3, 1]]))
        self.assertEqual(c, Matriz([[38, 4], [32, 10]]))

        with self.assertRaises(DimensionesIncompatiblesError):
            _ = a @ d

    def test_identidad_y_operaciones_elementales(self) -> None:
        identidad_3 = Matriz([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        a = Matriz([[1, 0, 0], [0, 1, 0]])
        b = Matriz([[0, 1, 0], [1, 0, 0]])
        c = Matriz([[3, 0, 0], [0, 1, 0]])
        d = Matriz([[1, 2, 0], [0, 1, 0]])
        e = Matriz([[1, 2, 3], [0, 3, 1], [0, 0, 1]])
        g = Matriz([[1, 2, 3, 1], [0, 3, 1, 2], [0, 0, 1, 6]])
        columna = [1, 2, 6]
        self.assertEqual(identidad_3, Matriz.identidad(3))
        self.assertEqual(b, a.intercambiar_filas(0, 1))
        self.assertEqual(a.intercambiar_filas(0, 1).dimension, a.dimension)
        self.assertEqual(c, a.escalar_fila(0, 3))
        self.assertEqual(a.escalar_fila(0, 3).dimension, a.dimension)
        self.assertEqual(d, a.sumar_multiplo_fila(0, 1, 2))
        self.assertEqual(a.sumar_multiplo_fila(0, 1, 2).dimension, a.dimension)
        self.assertEqual(e.intercambiar_filas(0, 1), Matriz([[0, 3, 1], [1, 2, 3], [0, 0, 1]]))
        self.assertEqual(g, e.ampliar_columna(columna))
        with self.assertRaises(ValueError):
            _ = Matriz.identidad(0)
        with self.assertRaises(ValueError):
            _ = a.escalar_fila(0, 0)
        with self.assertRaises(ValueError):
            _ = a.sumar_multiplo_fila(0, 0, 2)
        with self.assertRaises(IndexError):
            _ = a.intercambiar_filas(3, -1)
        with self.assertRaises(IndexError):
            _ = a.escalar_fila(-1, 3)
        with self.assertRaises(IndexError):
            _ = a.sumar_multiplo_fila(0, -3, 1)
        with self.assertRaises(DimensionesIncompatiblesError):
            _ = a.ampliar_columna(columna)

    def test_to_latex(self) -> None:
        m = Matriz([[1, "3/2"], ["-1/4", -2]])
        esperado = r"\begin{pmatrix} 1 & \frac{3}{2} \\ \frac{-1}{4} & -2 \end{pmatrix}"
        self.assertEqual(m.to_latex(), esperado)

if __name__ == "__main__":
    unittest.main()
