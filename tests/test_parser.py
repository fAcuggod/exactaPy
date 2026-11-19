"""Tests unitarios para el parser seguro de expresiones simbólicas."""

import math
import unittest

from exactapy_core.parser import parsear_expresion


class TestParserExpresiones(unittest.TestCase):
    def test_polinomio_y_producto_implicito(self) -> None:
        expr = parsear_expresion("x^3 - 3x + 2")
        self.assertAlmostEqual(expr.evaluar(2.0), 4.0)
        self.assertAlmostEqual(expr.derivar().evaluar(2.0), 9.0)

    def test_precedencia_signo_unario_y_potencia(self) -> None:
        # -x^2 debe ser -(x^2) = -9 en x=3, no (-3)^2 = 9
        expr = parsear_expresion("-x^2 + x^(-1)")
        self.assertAlmostEqual(expr.evaluar(2.0), -3.5)

    def test_funciones_trascendentes_y_euler(self) -> None:
        self.assertAlmostEqual(parsear_expresion("sin(pi/2) + cos(0)").evaluar(0.0), 2.0)
        self.assertAlmostEqual(parsear_expresion("sen(x)").evaluar(math.pi / 2), 1.0)
        self.assertAlmostEqual(parsear_expresion("e^(2x)").evaluar(1.0), math.exp(2.0))
        self.assertAlmostEqual(parsear_expresion("ln(e) + sqrt(9)").evaluar(0.0), 4.0)
        self.assertAlmostEqual(parsear_expresion("2(x + 1)**2 / 4").evaluar(1.0), 2.0)

    def test_errores_de_sintaxis_y_seguridad(self) -> None:
        invalidas = [
            "",
            "   ",
            "x + ",
            "(x + 1",
            "x + 1)",
            "3..5 + x",
            "sin x",
            "__import__('os')",
            "x^x",
            "x @ 2",
        ]
        for formula in invalidas:
            with self.assertRaises(ValueError, msg=f"Debería fallar: {formula}"):
                parsear_expresion(formula)


if __name__ == "__main__":
    unittest.main()
