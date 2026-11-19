"""Definiciones de tipos, estructuras de datos inmutables y excepciones de ExactaPy"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import TypeAlias, TYPE_CHECKING
from collections.abc import Sequence, Callable

### 1. ALIAS DE TIPOS

Escalar: TypeAlias = Fraction

EntradaEscalar: TypeAlias = int | str | Fraction

# Un Vector es una lista de escalares.
Vector: TypeAlias = list[Escalar]

GrillaEntrada: TypeAlias = Sequence[Sequence[EntradaEscalar]]

FuncionReal: TypeAlias = Callable[[float], float]

### 2. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS

class ExactaPyError(Exception):
    """Excepción base para todos los errores matemáticos del motor ExactaPy."""


class DimensionesIncompatiblesError(ExactaPyError):
    """Se lanza cuando las dimensiones de dos matrices impiden operar entre sí."""


class MatrizNoCuadradaError(ExactaPyError):
    """Se lanza al solicitar determinante o inversa de una matriz rectangular."""


class MatrizSingularError(ExactaPyError):
    """Se lanza al intentar invertir una matriz con determinante nulo (no inversible)."""


class HipotesisDeBolzanoError(ValueError):
    """Se lanza cuando el intervalo [a, b] no cumple las hipótesis de Bolzano."""


class DerivadaNulaError(ArithmeticError):
    """Se lanza cuando la derivada en Newton-Raphson es nula o casi nula."""

### 3. ENUMERADOS

class TipoOperacionElemental(Enum):
    """Tipos de operaciones elementales por fila en el método de Gauss-Jordan."""

    INTERCAMBIO = "Intercambio de filas (Fi <-> Fj)"
    ESCALADO = "Multiplicación de fila por escalar no nulo (Fi <- k * Fi)"
    ELIMINACION = "Suma de múltiplo de otra fila (Fi <- Fi + k * Fj)"


class ClasificacionSistema(Enum):
    """Clasificación de un sistema lineal Ax = b según Rouché-Frobenius."""

    COMPATIBLE_DETERMINADO = "Sistema Compatible Determinado (SCD)"
    COMPATIBLE_INDETERMINADO = "Sistema Compatible Indeterminado (SCI)"
    INCOMPATIBLE = "Sistema Incompatible (SI)"


### 4. DATACLASSES INMUTABLES

@dataclass(frozen=True)
class OperacionElemental:
    """Representa un paso atómico aplicado durante el escalonamiento matricial."""

    tipo: TipoOperacionElemental
    fila_destino: int
    descripcion: str
    fila_origen: int | None = None
    factor: Escalar | None = None

if TYPE_CHECKING:
    from exactapy_core.matriz import Matriz


@dataclass(frozen=True)
class ResultadoEscalonamiento:
    """Resultado completo del algoritmo de Gauss-Jordan (Ejercicio 4)."""

    rref: Matriz
    pasos: tuple[OperacionElemental, ...]
    columnas_pivote: tuple[int, ...]
    intercambios_realizados: int


@dataclass(frozen=True)
class SolucionSistema:
    """Resultado completo de resolver y clasificar Ax = b (Ejercicio 5)."""

    clasificacion: ClasificacionSistema
    rango_a: int
    rango_ampliada: int
    solucion_particular: Vector | None
    base_nucleo: tuple[Vector, ...]
    pasos_gauss: tuple[OperacionElemental, ...]

@dataclass(frozen=True)
class PasoIteracion:
    """Estado de un paso individual en un método numérico de búsqueda de raíces."""

    iteracion: int
    aproximacion: float
    valor_f: float
    error_estimado: float


@dataclass(frozen=True)
class ResultadoRaiz:
    """Reporte completo de convergencia y traza de un método de búsqueda de raíces."""

    raiz_aproximada: float
    iteraciones_realizadas: int
    convergio: bool
    historial_iteraciones: tuple[PasoIteracion, ...]


class TipoExtremo(Enum):
    """Clasificación de un punto crítico según el criterio de la segunda derivada."""

    MINIMO_LOCAL = "Mínimo Local"
    MAXIMO_LOCAL = "Máximo Local"
    PUNTO_INFLEXION_O_DEGENERADO = "Punto de Inflexión o Degenerado"


@dataclass(frozen=True)
class PuntoCritico:
    """Representa un punto donde f'(x) = 0 junto con su clasificación."""

    x: float
    valor_f: float
    segunda_derivada: float
    clasificacion: TipoExtremo


@dataclass(frozen=True)
class ReporteFuncion:
    """Reporte integral del estudio de una función simbólica en un intervalo [a, b]."""

    derivada_primera: str
    derivada_segunda: str
    raices_aproximadas: tuple[float, ...]
    puntos_criticos: tuple[PuntoCritico, ...]
    integral_definida: float
