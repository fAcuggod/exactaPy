"""Suite de tests unitarios y de caja blanca para expresiones.py (TP 3)."""

import math
import unittest

from exactapy_core.definiciones import ReporteFuncion, TipoExtremo
from exactapy_core.expresiones import (
    Cociente,
    Constante,
    Coseno,
    Exponencial,
    Expresion,
    Logaritmo,
    Potencia,
    Producto,
    Seno,
    Suma,
    Variable,
    analizar_funcion_en_intervalo,
    polinomio_taylor,
    _asegurar_expresion,
    _buscar_ceros_en_intervalo,
)

class TestEvaluarNodos(unittest.TestCase):

    def test_evaluar_nodos_basicos(self) -> None:
        x = Variable("x")
        expr: Expresion = _asegurar_expresion(6.0)
        expr_2: Expresion = x ** 2 - 2 * x
        expr_3: Expresion = 5 * x
        self.assertEqual(isinstance(expr, Constante), True)
        self.assertEqual(isinstance(_asegurar_expresion(expr_2), Expresion), True)

        with self.assertRaises(TypeError):
            _asegurar_expresion(str(x + 3))

        self.assertEqual(x.derivar(), Constante(1.0))
        self.assertEqual(x.simplificar(), x)
        self.assertEqual(
            Suma(x.evaluar(Constante(1.0)), Constante(2.0)).simplificar(),
            Constante(3.0)
            )
        self.assertEqual(
            Suma(x.evaluar(Constante(10.0)), Constante(0.0)).simplificar(),
            Constante(10.0)
        )
        self.assertEqual(
            Suma(
                Constante(6.0), Producto(Constante(-1.0), x.evaluar(Constante(1.0)))).simplificar(),
            Constante(5.0)
        )
        self.assertEqual(
            Producto(x.evaluar(Constante(5.0)), x.evaluar(Constante(0.0))).simplificar(),
            Constante(0.0)
            )
        self.assertEqual(
            Suma(expr_2.evaluar(0.0), expr_2.evaluar(1.0)),
            Suma(0.0, -1.0)
        )
        self.assertEqual(
            Suma(expr_3.derivar().simplificar(), expr_3.derivar().simplificar()),
            Suma(Constante(5.0), Constante(5.0))
        )
        self.assertEqual(
            Suma(Variable('x'), Constante(2.0)).derivar(),
            Suma(Constante(1.0), Constante(0.0))
        )
        self.assertEqual(
            Suma(Constante(0.0), Variable('x')).simplificar(),
            Variable('x')
        )
        self.assertEqual(
            Suma(Variable('x'), Constante(0.0)).simplificar(),
            Variable('x')
        )
        self.assertEqual(
            Suma(Variable('x'), Constante(2.0)).simplificar(),
            Suma(Variable('x'), Constante(2.0))
        )
        self.assertEqual(
            Producto(Producto(Variable('x'), Constante(1.0)),
                     Producto(Constante(1.0), Variable('x'))).simplificar(),
            Producto(Variable('x'), Variable('x'))
        )
        self.assertEqual(
            str(Producto((Constante(4.0)), Constante(1.0))),
            "(4 * 1)"
        )

        c: Constante = Constante(5.0)
        c_decimal: Constante = Constante(2.5)
        self.assertEqual(c.evaluar(99.0), 5.0)
        self.assertEqual(c.derivar(), Constante(0.0))
        self.assertEqual(str(c_decimal), "2.5")

    def test_cociente_completo(self) -> None:
        x = Variable("x")

        self.assertAlmostEqual(Cociente(x, Constante(2.0)).evaluar(6.0), 3.0)
        with self.assertRaises(ZeroDivisionError):
            Cociente(x, Constante(0.0)).evaluar(2.0)

        self.assertAlmostEqual(Cociente(x, x + Constante(1.0)).derivar().evaluar(1.0), 0.25)

        with self.assertRaises(ZeroDivisionError):
            Cociente(x, Constante(0.0)).simplificar()
        self.assertEqual(Cociente(Constante(6.0), Constante(2.0)).simplificar(), Constante(3.0))
        self.assertEqual(Cociente(Constante(0.0), x).simplificar(), Constante(0.0))
        self.assertEqual(Cociente(x, Constante(1.0)).simplificar(), x)
        self.assertEqual(
            Cociente(x, x + Constante(2.0)).simplificar(), Cociente(x, x + Constante(2.0)))

        self.assertEqual(str(Cociente(x, Constante(2.0))), "(x / 2)")

    def test_potencia_completa(self) -> None:
        x = Variable("x")

        self.assertAlmostEqual(Potencia(x, 3.0).evaluar(2.0), 8.0)

        self.assertEqual(Potencia(x, 0.0).derivar(), Constante(0.0))
        self.assertAlmostEqual(Potencia(x, 3.0).derivar().evaluar(2.0), 12.0)

        self.assertEqual(Potencia(x, 0.0).simplificar(), Constante(1.0))
        self.assertEqual(Potencia(x, 1.0).simplificar(), x)
        self.assertEqual(Potencia(Constante(3.0), 2.0).simplificar(), Constante(9.0))
        self.assertEqual(Potencia(x, 2.0).simplificar(), Potencia(x, 2.0))

        self.assertEqual(str(Potencia(x, 2.0)), "(x ^ 2)")
        self.assertEqual(str(Potencia(x, 0.5)), "(x ^ 0.5)")

    def test_evaluar_nodos_trascendentes(self) -> None:
        x = Variable("x")
        arg: Expresion = x
        arg_2: Expresion = (2 / 4) * x
        arg_3: Expresion = (0 / x) * 1
        arg_4: Expresion = 2 * x

        self.assertAlmostEqual(Seno(arg).evaluar(math.pi), 0.0, places=7)
        self.assertAlmostEqual(Seno(arg).derivar().evaluar(math.pi), -1.0)
        self.assertEqual(Seno(arg_2).simplificar(), Seno((1 / 2) * x))
        self.assertEqual(Seno(arg_3).simplificar(), Constante(math.sin(0.0)))
        self.assertEqual(str(Seno(arg)), "sin(x)")

        self.assertAlmostEqual(Coseno(arg).derivar().evaluar(math.pi), 0.0, places=7)
        self.assertEqual(Coseno(arg_2).simplificar(), Coseno((1 / 2) * x))
        self.assertEqual(Coseno(arg_3).simplificar(), Constante(math.cos(0.0)))
        self.assertEqual(str(Coseno(arg)), "cos(x)")

        self.assertEqual(Exponencial(arg).evaluar(0.0), 1.0)
        self.assertEqual(Exponencial(arg).derivar().simplificar(), Exponencial(arg))
        self.assertEqual(
            Exponencial((3 / x).evaluar(Constante(1.0))).simplificar(),
            Constante(math.exp(3.0))
            )
        self.assertEqual(str(Exponencial(arg)), "exp(x)")

        self.assertEqual(Logaritmo(arg).evaluar(1.0), 0.0)
        with self.assertRaises(ValueError):
            Logaritmo(arg).evaluar(0.0)
        self.assertEqual(
            Logaritmo(arg_4).derivar().simplificar(),
            Cociente(Constante(2.0), Producto(Constante(2.0), x))
            )
        self.assertEqual(Logaritmo(Constante(1.0)).simplificar(), Constante(0.0))
        with self.assertRaises(ValueError):
            Logaritmo(Constante(-1.0)).simplificar()
        self.assertEqual(Logaritmo(x).simplificar(), Logaritmo(x))
        self.assertEqual(str(Logaritmo(arg)),"ln(x)")

    def test_sobrecarga_operadores_y_radd_rmul_rsub_rtruediv(self) -> None:
        x = Variable("x")
        self.assertEqual(6.0 + Constante(5.0), Suma(Constante(6.0), Constante(5.0)))
        self.assertEqual(4.0 - x, Suma(Constante(4.0), Producto(Constante(-1.0), x)))
        self.assertEqual(x * 2, Producto(x, Constante(2)))
        self.assertEqual(-x / 1, Cociente(Producto(Constante(-1.0), x), Constante(1.0)))
        self.assertEqual(1 / x, Cociente(Constante(1.0), x))

    def test_to_latex_todas_las_expresiones(self) -> None:
        x = Variable("x")

        self.assertEqual(Constante(3.0).to_latex(), "3")
        self.assertEqual(Constante(2.5).to_latex(), "2.5")
        self.assertEqual(x.to_latex(), "x")

        self.assertEqual(Suma(x, Constante(2.0)).to_latex(), "x + 2")
        self.assertEqual(Producto(Constante(3.0), x).to_latex(), r"3 \cdot x")
        self.assertEqual(
            Cociente(x, Suma(x, Constante(1.0))).to_latex(),
            r"\frac{x}{x + 1}",
        )
        self.assertEqual(Potencia(x, 2.0).to_latex(), r"{x}^{2}")
        self.assertEqual(Potencia(x, 0.5).to_latex(), r"{x}^{0.5}")

        self.assertEqual(Seno(x).to_latex(), r"\sin\left(x\right)")
        self.assertEqual(Coseno(x).to_latex(), r"\cos\left(x\right)")
        self.assertEqual(Exponencial(x).to_latex(), r"\exp\left(x\right)")
        self.assertEqual(Logaritmo(x).to_latex(), r"\ln\left(x\right)")

class TestPolinomioDeTaylor(unittest.TestCase):

    def test_orden_menor_que_cero(self):
        with self.assertRaises(ValueError):
            polinomio_taylor(lambda x: 2 * x, 1.0, -3)

    def test_taylor_orden_3(self):        
        x = Variable("x")
        expr: Expresion = 2 * (x ** 3)
        expr_taylor: Expresion = polinomio_taylor(expr, 0, 3)
        self.assertEqual(expr_taylor, expr)


class TestAnalizarFuncionEnIntervalo(unittest.TestCase):

    def test_raices_sin_intervalo_cerrado(self):
        x: Variable = Variable('x')
        raices: list[float] = _buscar_ceros_en_intervalo(
            Seno(x), -1.0, 6.5, 100, 1e-7
        )
        raices_cheq: list[float] = [0, math.pi, 2 * math.pi]

        for i in range(len(raices_cheq)):
            self.assertAlmostEqual(raices[i], raices_cheq[i], places=6)

    def test_raices_exactas_en_nodos_y_extremo_derecho(self) -> None:
        x: Variable = Variable("x")
        expr: Expresion = (x ** 2) - Constante(1.0)
        raices: list[float] = _buscar_ceros_en_intervalo(
            expr, -1.0, 1.0, 10, 1e-7
        )
        self.assertEqual(len(raices), 2)
        self.assertAlmostEqual(raices[0], -1.0, places=7)
        self.assertAlmostEqual(raices[1], 1.0, places=7)

    def test_analizar_funcion_en_intervalo_completo(self) -> None:
        x: Variable = Variable("x")
        expr: Expresion = (x ** 5) - (Constante(5.0) / Constante(3.0)) * (x ** 3)

        reporte: ReporteFuncion = analizar_funcion_en_intervalo(
            expr, a=-2.0, b=2.0, subintervalos=40, tol=1e-7
        )
        self.assertEqual(len(reporte.puntos_criticos), 3)
        self.assertAlmostEqual(reporte.puntos_criticos[0].x, -1.0, places=6)
        self.assertEqual(
            reporte.puntos_criticos[0].clasificacion,
            TipoExtremo.MAXIMO_LOCAL,
        )
        self.assertAlmostEqual(reporte.puntos_criticos[1].x, 0.0, places=6)
        self.assertEqual(
            reporte.puntos_criticos[1].clasificacion,
            TipoExtremo.PUNTO_INFLEXION_O_DEGENERADO,
        )
        self.assertAlmostEqual(reporte.puntos_criticos[2].x, 1.0, places=6)
        self.assertEqual(
            reporte.puntos_criticos[2].clasificacion,
            TipoExtremo.MINIMO_LOCAL,
        )

    def test_analizar_funcion__value_error(self) -> None:
        x: Variable = Variable("x")
        with self.assertRaises(ValueError):
            analizar_funcion_en_intervalo(x, a=2.0, b=1.0)
        with self.assertRaises(ValueError):
            analizar_funcion_en_intervalo(x, a=0, b=1, tol=-1)
        with self.assertRaises(ValueError):
            analizar_funcion_en_intervalo(x, a=0, b=1, subintervalos=-1)
