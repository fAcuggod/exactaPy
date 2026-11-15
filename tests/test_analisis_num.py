"""Suite de tests unitarios para analisis_num.py (TP 2)."""
import unittest
import math
from definiciones import(
    HipotesisDeBolzanoError,
    DerivadaNulaError,
    FuncionReal,
    ResultadoRaiz,
)
from analisis_num import(
    derivada_numerica,
    biseccion_bolzano,
    newton_raphson,
    integrar_trapecios,
    integrar_simpson,
)

class TestDerivadasNumericas(unittest.TestCase):

    def test_h_menor_que_cero(self) -> None:
        f: FuncionReal = lambda x: x**2
        with self.assertRaises(ValueError):
            derivada_numerica(f, 0)

    def test_h_valido(self) -> None:
        df = derivada_numerica(math.cos)
        for x in (0.0, math.pi / 2, (3*math.pi) / 2, math.pi / 6):
            self.assertAlmostEqual(df(x), -math.sin(x), places=7)


class TestBiseccionBolzano(unittest.TestCase):

    def test_value_error(self):
        f: FuncionReal = lambda x: 2*x
        with self.assertRaises(ValueError):
            biseccion_bolzano(f, 5.0, 4.0)
        with self.assertRaises(ValueError):
            biseccion_bolzano(f, 2.0, 3.0, -1.0)
        with self.assertRaises(ValueError):
            biseccion_bolzano(f, 2.0, 3.0, 1e-7, -1.0)

    def test_raices(self):
        raiz: ResultadoRaiz = biseccion_bolzano(math.sin, math.pi - 1, math.pi + 1)
        raiz_1_iteracion: ResultadoRaiz = biseccion_bolzano(
            math.sin, math.pi - 1, math.pi + 3,1e-7, 1)
        raiz_2: ResultadoRaiz = biseccion_bolzano(lambda x: x - 3.0, 3.0, 4.0)
        raiz_3: ResultadoRaiz = biseccion_bolzano(lambda x: x - 4.0, 1.0, 4.0)
        raiz_4: ResultadoRaiz = biseccion_bolzano(math.sin, math.pi + 1, 2 * math.pi + 2)
        self.assertAlmostEqual(raiz.raiz_aproximada, math.pi, places=7)
        self.assertEqual(raiz_1_iteracion.convergio, False)
        self.assertAlmostEqual(raiz_2.raiz_aproximada, 3.0)
        self.assertEqual(raiz_3.raiz_aproximada, 4.0)
        self.assertAlmostEqual(raiz_4.raiz_aproximada, 2 * math.pi, places=7)
        with self.assertRaises(HipotesisDeBolzanoError):
            biseccion_bolzano(math.sin, math.pi - 1, 2 * math.pi + 1)


class TestNewtonRaphson(unittest.TestCase):

    def test_value_error(self):
        f: FuncionReal = lambda x: 5*x
        with self.assertRaises(ValueError):
            newton_raphson(f, 2.0, -1.0)
        with self.assertRaises(ValueError):
            newton_raphson(f, 2.0, 1e-7, -1)

    def test_sin_df(self):
        f: FuncionReal = lambda x: 5*x - 2
        raiz: ResultadoRaiz = newton_raphson(f, 1)
        raiz_2: ResultadoRaiz = newton_raphson(f, 0.4)
        self.assertAlmostEqual(raiz.raiz_aproximada, 0.4, places=7)
        self.assertAlmostEqual(raiz_2.raiz_aproximada, 0.4, places=7)

    def test_derivada_nula(self):
        f: FuncionReal = lambda x: 2*(x**2) + 2
        with self.assertRaises(DerivadaNulaError):
            newton_raphson(f, 0)

    def test_1_iteracion_con_df(self):
        f: FuncionReal = lambda x: 2*(x**5) + 1
        df: FuncionReal = derivada_numerica(f)
        raiz: ResultadoRaiz = newton_raphson(f, 1.0, 1e-7, 1, df)
        self.assertAlmostEqual(raiz.raiz_aproximada, 0.7, places=7)


class TestIntegrarTrapecios(unittest.TestCase):

    def test_value_error(self):
        with self.assertRaises(ValueError):
            integrar_trapecios(math.sin, 0.0, -math.pi)
            integrar_trapecios(math.cos, 0.0, 1.0, -1)

    def test_es_integrable(self):
        integral: float = integrar_trapecios(math.sin, 0.0, math.pi)
        self.assertAlmostEqual(integral, 2.0, places=3)


class TestIntegrarSimpson(unittest.TestCase):

    def test_value_error(self):
        with self.assertRaises(ValueError):
            integrar_simpson(math.sin, math.pi, 1.0)
        with self.assertRaises(ValueError):
            integrar_simpson(math.sin, 0.0, 1.0, -1)
        with self.assertRaises(ValueError):
            integrar_simpson(math.sin, 1.0, 3.0, 3)

    def test_es_integrable(self):
        integral: float = integrar_simpson(lambda x: x**2, 0.0, 2.0)
        self.assertAlmostEqual(integral, 2.6666666666, places=7)

if __name__ == "__main__":
    unittest.main()
