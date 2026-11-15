"""Módulo TP 2: Métodos numéricos de análisis matemático I y funciones de orden superior."""

from __future__ import annotations
from definiciones import (
    DerivadaNulaError,
    FuncionReal,
    HipotesisDeBolzanoError,
    PasoIteracion,
    ResultadoRaiz,
)


def derivada_numerica(f: FuncionReal, h: float = 1e-7) -> FuncionReal:
    """Construye y devuelve una clausura que aproxima f'(x) por diferencia centrada.

    Raises:
        ValueError: Si h <= 0.
    """
    if h <= 0:
        raise ValueError("*h* debe ser mayor estricto que cero.")

    def f_derivada(x: float) -> float:
        return (f(x + h) - f(x - h)) / (2*h)

    return f_derivada

def biseccion_bolzano(
    f: FuncionReal,
    a: float,
    b: float,
    tol: float = 1e-7,
    max_iter: int = 100,
) -> ResultadoRaiz:
    """Aproxima una raíz de f en [a, b] mediante el método de bisección (Bolzano).

    Raises:
        ValueError: Si a >= b, tol <= 0 o max_iter <= 0.
        HipotesisDeBolzanoError: Si f(a) y f(b) tienen el mismo signo y no son raíces.
    """
    if a >= b or tol <= 0 or max_iter <= 0:
        raise ValueError("*a* debe ser menor estricto que *b*, *tol* > 0 y *max_iter* > 0")

    imagen_a: float = f(a)
    imagen_b: float = f(b)
    if imagen_a * imagen_b > 0:
        raise HipotesisDeBolzanoError("No se cumple la hipótesis de bolzano.")

    if imagen_a == 0:
        return ResultadoRaiz(raiz_aproximada=a,
                             iteraciones_realizadas=0,
                             convergio=True,
                             historial_iteraciones=())

    if imagen_b == 0:
        return ResultadoRaiz(raiz_aproximada=b,
                             iteraciones_realizadas=0,
                             convergio=True,
                             historial_iteraciones=())

    iteraciones: list[PasoIteracion] = []
    for i in range(max_iter):
        punto_medio: float = (a+b)/2
        imagen_m: float = f(punto_medio)
        error: float = (b-a)/2
        iteracion_actual: PasoIteracion = PasoIteracion(i+1, punto_medio, imagen_m, error)
        iteraciones.append(iteracion_actual)
        if abs(imagen_m) <= tol or error <= tol:
            return ResultadoRaiz(raiz_aproximada=punto_medio,
                                 iteraciones_realizadas=i+1,
                                 convergio=True,
                                 historial_iteraciones=tuple(iteraciones))
        if imagen_a * imagen_m < 0:
            b = punto_medio
        else:
            a = punto_medio
            imagen_a = imagen_m

    return ResultadoRaiz(raiz_aproximada=(a+b)/2,
                        iteraciones_realizadas=max_iter,
                        convergio=False,
                        historial_iteraciones=tuple(iteraciones))

def newton_raphson(
    f: FuncionReal,
    x0: float,
    tol: float = 1e-7,
    max_iter: int = 100,
    df: FuncionReal | None = None,
) -> ResultadoRaiz:
    """Aproxima una raíz de f partiendo de x0 mediante el método de Newton-Raphson.

    Raises:
        ValueError: Si tol <= 0 o max_iter <= 0.
        DerivadaNulaError: Si en algún paso |f'(x_k)| < 1e-12.
    """
    if tol <= 0 or max_iter <= 0:
        raise ValueError("*tol* debe ser mayor estricto que cero y *max_iter* tambien.")

    if df is None:
        df = derivada_numerica(f)

    imagen_x0 = f(x0)
    if abs(imagen_x0) <= tol:
        return ResultadoRaiz(raiz_aproximada=x0,
                             iteraciones_realizadas=0,
                             convergio=True,
                             historial_iteraciones=())

    iteraciones: list[PasoIteracion] = []
    for i in range(max_iter):
        imagen_derivada_x0: float = df(x0)
        if abs(imagen_derivada_x0) < 1e-12:
            raise DerivadaNulaError("La derivada de *f* se anula en *x0*.")

        nuevo_punto: float = x0 - (imagen_x0 / imagen_derivada_x0)
        imagen_nuevo_punto: float = f(nuevo_punto)
        error: float = abs(nuevo_punto - x0)
        iteracion_actual: PasoIteracion = PasoIteracion(i+1, nuevo_punto, imagen_nuevo_punto, error)
        iteraciones.append(iteracion_actual)
        if abs(imagen_nuevo_punto) <= tol or error <= tol:
            return ResultadoRaiz(raiz_aproximada=nuevo_punto,
                                 iteraciones_realizadas=i+1,
                                 convergio=True,
                                 historial_iteraciones=tuple(iteraciones))
        x0 = nuevo_punto
        imagen_x0 = imagen_nuevo_punto

    return ResultadoRaiz(raiz_aproximada=x0,
                        iteraciones_realizadas=max_iter,
                        convergio=False,
                        historial_iteraciones=tuple(iteraciones))

def integrar_trapecios(f: FuncionReal, a: float, b: float, n: int = 100) -> float:
    """Aproxima la integral definida de f en [a, b] con n trapecios compuestos.

    Raises:
        ValueError: Si a >= b o n <= 0.
    """
    if a >= b or n <= 0:
        raise ValueError("*a* debe ser estrictamente menor que b y *n* > 0.")

    h: float = (b-a)/n
    resultado_acumulado: float = (f(a)+f(b))/2
    for k in range(1, n):
        resultado_acumulado += f(a+(k*h))
    return resultado_acumulado * h

def integrar_simpson(f: FuncionReal, a: float, b: float, n: int = 100) -> float:
    """Aproxima la integral definida de f en [a, b] mediante la regla de Simpson 1/3.

    Raises:
        ValueError: Si a >= b, n <= 0 o n es impar.
    """
    if a >=b or n <= 0 or n % 2 != 0:
        raise ValueError("*n* debe ser par mayor que 0 y *a* < *b*")

    h: float = (b-a)/n
    resultado_acumulado: float = f(a) + f(b)
    for k in range(1, n):
        if k % 2 != 0:
            resultado_acumulado += f(a+k*h) * 4
        else: # k es par
            resultado_acumulado += f(a+k*h) * 2
    return resultado_acumulado * (h/3)
