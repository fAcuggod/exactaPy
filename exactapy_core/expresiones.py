"""Módulo TP 3: Cálculo simbólico, árboles de expresión y polinomio de taylor."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from exactapy_core.definiciones import PuntoCritico, ReporteFuncion, TipoExtremo
from exactapy_core.analisis_num import biseccion_bolzano, integrar_simpson

def _asegurar_expresion(valor: Expresion | float | int) -> Expresion:
    """Convierte números reales/enteros en nodos constante automáticamente."""
    if isinstance(valor, Expresion):
        return valor
    if isinstance(valor, (int, float)):
        return Constante(float(valor))
    raise TypeError(f"No se puede convertir {type(valor)} a expresion.")


class Expresion(ABC):
    """Clase base abstracta para el árbol de sintaxis abstracta (AST) simbólico."""

    @abstractmethod
    def to_latex(self) -> str:
        """Devuelve la expresión formateada en código LaTeX."""

    @abstractmethod
    def evaluar(self, valor_x: float) -> float:
        """Evalúa numéricamente la expresión reemplazando la variable por valor_x."""

    @abstractmethod
    def derivar(self) -> Expresion:
        """Construye y devuelve el árbol de la derivada simbólica exacta."""

    @abstractmethod
    def simplificar(self) -> Expresion:
        """Devuelve una nueva expresión algebraicamente simplificada."""

    @abstractmethod
    def __str__(self) -> str:
        """Representación legible en notación infija/prefija."""


    def __add__(self, otro: Expresion | float | int) -> Expresion:
        return Suma(self, _asegurar_expresion(otro))

    def __radd__(self, otro: Expresion | float | int) -> Expresion:
        return Suma(_asegurar_expresion(otro), self)

    def __sub__(self, otro: Expresion | float | int) -> Expresion:
        return Suma(self, Producto(Constante(-1.0), _asegurar_expresion(otro)))

    def __rsub__(self, otro: Expresion | float | int) -> Expresion:
        return Suma(_asegurar_expresion(otro), Producto(Constante(-1.0), self))

    def __mul__(self, otro: Expresion | float | int) -> Expresion:
        return Producto(self, _asegurar_expresion(otro))

    def __rmul__(self, otro: Expresion | float | int) -> Expresion:
        return Producto(_asegurar_expresion(otro), self)

    def __truediv__(self, otro: Expresion | float | int) -> Expresion:
        return Cociente(self, _asegurar_expresion(otro))

    def __rtruediv__(self, otro: Expresion | float | int) -> Expresion:
        return Cociente(_asegurar_expresion(otro), self)

    def __pow__(self, exponente: float | int) -> Expresion:
        return Potencia(self, float(exponente))

    def __neg__(self) -> Expresion:
        return Producto(Constante(-1.0), self)

@dataclass(frozen=True)
class Constante(Expresion):
    """Representa una constante real c."""

    valor: float

    def to_latex(self) -> str:
        return str(self)

    def evaluar(self, valor_x: float) -> float:
        return self.valor

    def derivar(self) -> Expresion:
        return Constante(0.0)

    def simplificar(self) -> Expresion:
        return self

    def __str__(self) -> str:
        if self.valor.is_integer():
            return str(int(self.valor))
        return str(self.valor)


@dataclass(frozen=True)
class Variable(Expresion):
    """Representa la variable simbólica independiente (por defecto 'x')."""

    nombre: str = "x"

    def to_latex(self) -> str:
        return self.nombre

    def evaluar(self, valor_x: float) -> float:
        return valor_x

    def derivar(self) -> Expresion:
        return Constante(1.0)

    def simplificar(self) -> Expresion:
        return self

    def __str__(self) -> str:
        return self.nombre


@dataclass(frozen=True)
class Suma(Expresion):
    """Representa la suma simbólica (izq + der)."""

    izq: Expresion
    der: Expresion

    def to_latex(self) -> str:
        return f"{self.izq.to_latex()} + {self.der.to_latex()}"

    def evaluar(self, valor_x: float) -> float:
        return self.izq.evaluar(valor_x) + self.der.evaluar(valor_x)

    def derivar(self) -> Expresion:
        return self.izq.derivar() + self.der.derivar()

    def simplificar(self) -> Expresion:
        izq_simp: Expresion = self.izq.simplificar()
        der_simp: Expresion = self.der.simplificar()

        if isinstance(izq_simp, Constante) and isinstance(der_simp, Constante):
            return Constante(izq_simp.valor + der_simp.valor)

        if izq_simp == Constante(0):
            return der_simp

        if der_simp == Constante(0):
            return izq_simp

        return Suma(izq_simp, der_simp)

    def __str__(self) -> str:
        return f"({self.izq} + {self.der})"


@dataclass(frozen=True)
class Producto(Expresion):
    """Representa el producto simbólico (izq * der)."""

    izq: Expresion
    der: Expresion

    def to_latex(self) -> str:
        return f"{self.izq.to_latex()} \\cdot {self.der.to_latex()}"

    def evaluar(self, valor_x: float) -> float:
        return self.izq.evaluar(valor_x) * self.der.evaluar(valor_x)

    def derivar(self) -> Expresion:
        return self.izq.derivar() * self.der + self.izq * self.der.derivar()

    def simplificar(self) -> Expresion:
        izq_simp: Expresion = self.izq.simplificar()
        der_simp: Expresion = self.der.simplificar()

        if isinstance(izq_simp, Constante) and isinstance(der_simp, Constante):
            return Constante(izq_simp.valor * der_simp.valor)

        if izq_simp == Constante(0.0) or der_simp == Constante(0.0):
            return Constante(0.0)

        if izq_simp == Constante(1.0):
            return der_simp

        if der_simp == Constante(1.0):
            return izq_simp

        return Producto(izq_simp, der_simp)

    def __str__(self) -> str:
        return f"({self.izq} * {self.der})"


@dataclass(frozen=True)
class Cociente(Expresion):
    """Representa el cociente simbólico (num / den)."""

    num: Expresion
    den: Expresion

    def to_latex(self) -> str:
        return f"\\frac{{{self.num.to_latex()}}}{{{self.den.to_latex()}}}"

    def evaluar(self, valor_x: float) -> float:
        den_val: float = self.den.evaluar(valor_x)
        if den_val == 0.0:
            raise ZeroDivisionError("No se puede dividir por cero.")
        return self.num.evaluar(valor_x) / self.den.evaluar(valor_x)

    def derivar(self) -> Expresion:
        return (self.num.derivar() * self.den - self.num * self.den.derivar()) / self.den ** 2

    def simplificar(self) -> Expresion:
        num_simp: Expresion = self.num.simplificar()
        den_simp: Expresion = self.den.simplificar()

        if den_simp == Constante(0.0):
            raise ZeroDivisionError("No se puede dividir por cero.")

        if isinstance(num_simp, Constante) and isinstance(den_simp, Constante):
            return Constante(num_simp.valor / den_simp.valor)

        if num_simp == Constante(0.0):
            return Constante(0.0)

        if den_simp == Constante(1.0):
            return num_simp

        return Cociente(num_simp, den_simp)

    def __str__(self) -> str:
        return f"({self.num} / {self.den})"


@dataclass(frozen=True)
class Potencia(Expresion):
    """Representa una potencia con exponente real fijo (base ^ exp)."""

    base: Expresion
    exp: float

    def to_latex(self) -> str:
        exp_str = str(int(self.exp)) if self.exp.is_integer() else str(self.exp)
        return f"{{{self.base.to_latex()}}}^{{{exp_str}}}"

    def evaluar(self, valor_x: float) -> float:
        base_val: float = self.base.evaluar(valor_x)
        return float(base_val ** self.exp)

    def derivar(self) -> Expresion:
        if self.exp == 0.0:
            return Constante(0.0)

        return self.exp * (self.base ** (self.exp - 1)) * self.base.derivar()

    def simplificar(self) -> Expresion:
        base_simp: Expresion = self.base.simplificar()
        if self.exp == 0.0:
            return Constante(1.0)

        if self.exp == 1.0:
            return base_simp

        if isinstance(base_simp, Constante):
            return Constante(float(base_simp.valor ** self.exp))

        return Potencia(base_simp, self.exp)

    def __str__(self) -> str:
        exp_str = str(int(self.exp)) if float(self.exp).is_integer() else str(self.exp)
        return f"({self.base} ^ {exp_str})"


@dataclass(frozen=True)
class Seno(Expresion):
    """Representa sin(arg)."""

    arg: Expresion

    def to_latex(self) -> str:
        return f"\\sin\\left({self.arg.to_latex()}\\right)"

    def evaluar(self, valor_x: float) -> float:
        arg_val: float = self.arg.evaluar(valor_x)
        return math.sin(arg_val)

    def derivar(self) -> Expresion:
        return Coseno(self.arg) * self.arg.derivar()

    def simplificar(self) -> Expresion:
        arg_simp: Expresion = self.arg.simplificar()
        if isinstance(arg_simp, Constante):
            return Constante(math.sin(arg_simp.valor))
        return Seno(arg_simp)

    def __str__(self) -> str:
        return f"sin({self.arg})"


@dataclass(frozen=True)
class Coseno(Expresion):
    """Representa cos(arg)."""

    arg: Expresion

    def to_latex(self) -> str:
        return f"\\cos\\left({self.arg.to_latex()}\\right)"

    def evaluar(self, valor_x: float) -> float:
        arg_val: float = self.arg.evaluar(valor_x)
        return math.cos(arg_val)

    def derivar(self) -> Expresion:
        return (Constante(-1.0) * Seno(self.arg)) * self.arg.derivar()

    def simplificar(self) -> Expresion:
        arg_simp: Expresion = self.arg.simplificar()
        if isinstance(arg_simp, Constante):
            return Constante(math.cos(arg_simp.valor))
        return Coseno(arg_simp)

    def __str__(self) -> str:
        return f"cos({self.arg})"


@dataclass(frozen=True)
class Exponencial(Expresion):
    """Representa exp(arg) = e^(arg)."""

    arg: Expresion

    def to_latex(self) -> str:
        return f"\\exp\\left({self.arg.to_latex()}\\right)"

    def evaluar(self, valor_x: float) -> float:
        arg_val: float = self.arg.evaluar(valor_x)
        return math.exp(arg_val)

    def derivar(self) -> Expresion:
        return Exponencial(self.arg) * self.arg.derivar()

    def simplificar(self) -> Expresion:
        arg_simp: Expresion = self.arg.simplificar()
        if isinstance(arg_simp, Constante):
            return Constante(math.exp(arg_simp.valor))
        return Exponencial(arg_simp)

    def __str__(self) -> str:
        return f"exp({self.arg})"


@dataclass(frozen=True)
class Logaritmo(Expresion):
    """Representa ln(arg)."""

    arg: Expresion

    def to_latex(self) -> str:
        return f"\\ln\\left({self.arg.to_latex()}\\right)"

    def evaluar(self, valor_x: float) -> float:
        arg_val: float = self.arg.evaluar(valor_x)
        if arg_val <= 0:
            raise ValueError("El dominio de ln son los x en R > 0.")
        return math.log(arg_val)

    def derivar(self) -> Expresion:
        return self.arg.derivar() / self.arg

    def simplificar(self) -> Expresion:
        arg_simp: Expresion = self.arg.simplificar()
        if isinstance(arg_simp, Constante):
            if arg_simp.valor <= 0:
                raise ValueError("El dominio de ln son los x en R > 0.")
            return Constante(math.log(arg_simp.valor))
        return Logaritmo(arg_simp)

    def __str__(self) -> str:
        return f"ln({self.arg})"


def polinomio_taylor(expr: Expresion, x0: float, orden: int) -> Expresion:
    """Construye el Polinomio de Taylor de orden n centrado en x0 como una Expresion.

    Raises:
        ValueError: Si orden < 0.
    """
    if orden < 0:
        raise ValueError("Se necesita al menos *orden* 0.")

    derivada_actual: Expresion = expr
    polinomio: Expresion = Constante(0.0)
    for k in range(orden+1):
        coef: float = derivada_actual.evaluar(x0) / math.factorial(k)
        termino_kesimo: Expresion = Constante(coef) * Potencia(Variable("x") - Constante(x0), float(k))
        polinomio = polinomio + termino_kesimo
        if k < orden:
            derivada_actual = derivada_actual.derivar().simplificar()
    return polinomio.simplificar()

def _buscar_ceros_en_intervalo(
    expr: Expresion,
    a: float,
    b: float,
    subintervalos: int,
    tol: float,
) -> list[float]:
    """Busca todas las raíces aproximadas de expr en [a, b] subdividiendo el intervalo."""
    h: float = (b-a)/subintervalos
    raices: list[float] = []
    for i in range(subintervalos):
        x_izq: float = a + i * h
        x_der: float = a + (i + 1) * h
        f_izq: float = expr.evaluar(x_izq)
        f_der: float = expr.evaluar(x_der)
        candidato: float | None = None
        if abs(f_izq) <= tol:
            candidato = x_izq

        elif f_izq * f_der < 0:
            candidato = biseccion_bolzano(expr.evaluar, x_izq, x_der, tol).raiz_aproximada

        if candidato is not None and (not raices or abs(candidato - raices[-1]) > 1e-4):
            raices.append(candidato)

    if abs(expr.evaluar(b)) <= tol and (not raices or abs(b - raices[-1]) > 1e-4):
        raices.append(b)

    return raices

def analizar_funcion_en_intervalo(
    expr: Expresion,
    a: float,
    b: float,
    subintervalos: int = 50,
    tol: float = 1e-6,
) -> ReporteFuncion:
    """Realiza el estudio completo de expr en [a, b]: derivadas, raíces, extremos e integral.

    Raises:
        ValueError: Si a >= b, subintervalos <= 0 o tol <= 0.
    """
    if a >= b or subintervalos <= 0 or tol <= 0:
        raise ValueError(
            "*a* debe ser menor estricto que *b*, *subintervalos* > 0 y *tol* > 0.")

    df: Expresion = expr.derivar().simplificar()
    ddf: Expresion = df.derivar().simplificar()
    raices: list[float] = _buscar_ceros_en_intervalo(expr, a, b, subintervalos, tol)
    puntos_criticos: list[float] = _buscar_ceros_en_intervalo(df, a, b, subintervalos, tol)
    info_x_criticos: list[PuntoCritico] = []

    for x_critico in puntos_criticos:
        val_f: float = expr.evaluar(x_critico)
        val_ddf: float = ddf.evaluar(x_critico)

        if val_ddf > tol:
            clasif: TipoExtremo = TipoExtremo.MINIMO_LOCAL

        elif val_ddf < -tol:
            clasif = TipoExtremo.MAXIMO_LOCAL

        else:
            clasif = TipoExtremo.PUNTO_INFLEXION_O_DEGENERADO

        info_x_criticos.append(
            PuntoCritico(
                x=x_critico,
                valor_f=val_f,
                segunda_derivada=val_ddf,
                clasificacion=clasif
            )
        )

    integral: float = integrar_simpson(expr.evaluar, a, b)

    return ReporteFuncion(
        derivada_primera=str(df),
        derivada_segunda=str(ddf),
        raices_aproximadas=tuple(raices),
        puntos_criticos=tuple(info_x_criticos),
        integral_definida=integral
    )
