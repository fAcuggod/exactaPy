"""Definiciones de tipos, estructuras de datos inmutables y excepciones de ExactaPy"""

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import TypeAlias
from collections.abc import Sequence

### 1. ALIAS DE TIPOS

# Un Escalar es siempre un racional (Fraction).
Escalar: TypeAlias = Fraction

# Cuando el usuario crea una matriz, puede pasarnos enteros, strings ("3/4") o Fractions.
EntradaEscalar: TypeAlias = int | str | Fraction

# Un Vector es una lista de escalares.
Vector: TypeAlias = list[Escalar]

# Una Grilla de entrada es una secuencia de filas con valores convertibles a Fraction.
GrillaEntrada: TypeAlias = Sequence[Sequence[EntradaEscalar]]


### 2. JERARQUÍA DE EXCEPCIONES PERSONALIZADAS

class ExactaPyError(Exception):
    """Excepción base para todos los errores matemáticos del motor ExactaPy."""


class DimensionesIncompatiblesError(ExactaPyError):
    """Se lanza cuando las dimensiones de dos matrices impiden operar entre sí."""


class MatrizNoCuadradaError(ExactaPyError):
    """Se lanza al solicitar determinante o inversa de una matriz rectangular."""


class MatrizSingularError(ExactaPyError):
    """Se lanza al intentar invertir una matriz con determinante nulo (no inversible)."""


### 3. ENUMERADOS (Conjuntos cerrados de constantes simbólicas)

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


### 4. DATACLASSES INMUTABLES (Objetos de transferencia de resultados para TP 1)

@dataclass(frozen=True)
class OperacionElemental:
    """Representa un paso atómico aplicado durante el escalonamiento matricial."""

    tipo: TipoOperacionElemental
    fila_destino: int
    descripcion: str
    fila_origen: int | None = None
    factor: Escalar | None = None
