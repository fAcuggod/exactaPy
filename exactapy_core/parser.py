"""Parser seguro de descenso recursivo: convierte texto matemático en AST Expresion."""

from dataclasses import dataclass
from enum import Enum, auto
import math

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
)


class TipoToken(Enum):
    NUMERO = auto()
    VARIABLE = auto()
    CONSTANTE_MAT = auto()
    FUNCION = auto()
    MAS = auto()
    MENOS = auto()
    POR = auto()
    DIV = auto()
    POT = auto()
    PAR_IZQ = auto()
    PAR_DER = auto()
    FIN = auto()


@dataclass(frozen=True)
class Token:
    tipo: TipoToken
    valor: str


_FUNCIONES_VALIDAS: frozenset[str] = frozenset({"sin", "sen", "cos", "exp", "ln", "log", "sqrt"})
_CONSTANTES_MAT: dict[str, float] = {"pi": math.pi, "e": math.e}


def _tokenizar(texto: str) -> list[Token]:
    """Convierte una cadena matemática en una lista de tokens validados."""
    tokens: list[Token] = []
    i: int = 0
    n: int = len(texto)

    while i < n:
        ch: str = texto[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit() or ch == ".":
            inicio = i
            puntos = 0
            while i < n and (texto[i].isdigit() or texto[i] == "."):
                if texto[i] == ".":
                    puntos += 1
                i += 1
            if puntos > 1 or texto[inicio:i] == ".":
                raise ValueError(f"Número mal formado: '{texto[inicio:i]}'")
            tokens.append(Token(TipoToken.NUMERO, texto[inicio:i]))
            continue

        if ch.isalpha():
            inicio = i
            while i < n and texto[i].isalpha():
                i += 1
            palabra = texto[inicio:i].lower()
            if palabra == "x":
                tokens.append(Token(TipoToken.VARIABLE, "x"))
            elif palabra in _CONSTANTES_MAT:
                tokens.append(Token(TipoToken.CONSTANTE_MAT, palabra))
            elif palabra in _FUNCIONES_VALIDAS:
                tokens.append(Token(TipoToken.FUNCION, palabra))
            else:
                raise ValueError(f"Identificador o función desconocida: '{palabra}'")
            continue

        if ch == "+":
            tokens.append(Token(TipoToken.MAS, ch))
        elif ch == "-":
            tokens.append(Token(TipoToken.MENOS, ch))
        elif ch == "*":
            if i + 1 < n and texto[i + 1] == "*":
                tokens.append(Token(TipoToken.POT, "**"))
                i += 1
            else:
                tokens.append(Token(TipoToken.POR, ch))
        elif ch == "/":
            tokens.append(Token(TipoToken.DIV, ch))
        elif ch == "^":
            tokens.append(Token(TipoToken.POT, ch))
        elif ch == "(":
            tokens.append(Token(TipoToken.PAR_IZQ, ch))
        elif ch == ")":
            tokens.append(Token(TipoToken.PAR_DER, ch))
        else:
            raise ValueError(f"Carácter no permitido en la expresión: '{ch}'")
        i += 1

    tokens.append(Token(TipoToken.FIN, ""))
    return tokens


class _ParserDescensoRecursivo:
    """Analizador sintáctico que construye el AST de Expresion."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens: list[Token] = tokens
        self._pos: int = 0

    def _actual(self) -> Token:
        return self._tokens[self._pos]

    def _avanzar(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _esperar(self, tipo: TipoToken, mensaje: str) -> Token:
        if self._actual().tipo != tipo:
            raise ValueError(mensaje)
        return self._avanzar()

    def parsear(self) -> Expresion:
        if self._actual().tipo == TipoToken.FIN:
            raise ValueError("La expresión no puede estar vacía.")
        nodo = self._expresion()
        if self._actual().tipo != TipoToken.FIN:
            raise ValueError(f"Token inesperado al final de la expresión: '{self._actual().valor}'")
        return nodo

    def _expresion(self) -> Expresion:
        nodo = self._termino()
        while self._actual().tipo in (TipoToken.MAS, TipoToken.MENOS):
            op = self._avanzar().tipo
            derecho = self._termino()
            if op == TipoToken.MAS:
                nodo = Suma(nodo, derecho)
            else:
                nodo = nodo - derecho
        return nodo

    def _termino(self) -> Expresion:
        nodo = self._unario()
        inicios_implicitos = (
            TipoToken.VARIABLE,
            TipoToken.CONSTANTE_MAT,
            TipoToken.FUNCION,
            TipoToken.PAR_IZQ,
        )
        while True:
            tipo = self._actual().tipo
            if tipo == TipoToken.POR:
                self._avanzar()
                nodo = Producto(nodo, self._unario())
            elif tipo == TipoToken.DIV:
                self._avanzar()
                nodo = Cociente(nodo, self._unario())
            elif tipo in inicios_implicitos:
                # Multiplicación implícita: 3x, 2sin(x), (x+1)(x-1)
                nodo = Producto(nodo, self._potencia())
            else:
                break
        return nodo

    def _unario(self) -> Expresion:
        if self._actual().tipo == TipoToken.MAS:
            self._avanzar()
            return self._unario()
        if self._actual().tipo == TipoToken.MENOS:
            self._avanzar()
            return Producto(Constante(-1.0), self._unario())
        return self._potencia()

    def _potencia(self) -> Expresion:
        es_base_euler = (
            self._actual().tipo == TipoToken.CONSTANTE_MAT and self._actual().valor == "e"
        )
        base = self._primario()
        if self._actual().tipo == TipoToken.POT:
            self._avanzar()
            pos_inicio = self._pos
            exponente = self._unario()
            if es_base_euler:
                return Exponencial(exponente)
            tiene_variable = any(
                t.tipo == TipoToken.VARIABLE for t in self._tokens[pos_inicio : self._pos]
            )
            if tiene_variable:
                raise ValueError(
                    "Los exponentes con la variable 'x' solo están soportados en base 'e' (ej: e^x)."
                )
            return Potencia(base, exponente.evaluar(0.0))
        return base

    def _primario(self) -> Expresion:
        tok = self._actual()

        if tok.tipo == TipoToken.NUMERO:
            self._avanzar()
            return Constante(float(tok.valor))

        if tok.tipo == TipoToken.VARIABLE:
            self._avanzar()
            return Variable("x")

        if tok.tipo == TipoToken.CONSTANTE_MAT:
            self._avanzar()
            return Constante(_CONSTANTES_MAT[tok.valor])

        if tok.tipo == TipoToken.FUNCION:
            nombre = self._avanzar().valor
            self._esperar(TipoToken.PAR_IZQ, f"Se esperaba '(' después de '{nombre}'.")
            arg = self._expresion()
            self._esperar(TipoToken.PAR_DER, f"Falta cerrar ')' en la función '{nombre}'.")
            return self._construir_funcion(nombre, arg)

        if tok.tipo == TipoToken.PAR_IZQ:
            self._avanzar()
            nodo = self._expresion()
            self._esperar(TipoToken.PAR_DER, "Falta cerrar un paréntesis ')'.")
            return nodo

        raise ValueError(f"Expresión inesperada cerca de '{tok.valor or 'fin de línea'}'.")

    def _construir_funcion(self, nombre: str, arg: Expresion) -> Expresion:
        if nombre in ("sin", "sen"):
            return Seno(arg)
        if nombre == "cos":
            return Coseno(arg)
        if nombre == "exp":
            return Exponencial(arg)
        if nombre in ("ln", "log"):
            return Logaritmo(arg)
        return Potencia(arg, 0.5)  # sqrt


def parsear_expresion(texto: str) -> Expresion:
    """Traduce un string matemático (ej. 'x^3 - 3x + sin(x)') a un árbol Expresion.

    PRE: texto es una expresión matemática bien formada en la variable 'x'.
    Args:
        texto (str): Fórmula ingresada por el usuario.
    Returns:
        Expresion: Árbol de sintaxis abstracta listo para evaluar, derivar o exportar a LaTeX.
    Raises:
        ValueError: Si la expresión está vacía, tiene sintaxis inválida o símbolos no soportados.
    """
    tokens = _tokenizar(texto)
    return _ParserDescensoRecursivo(tokens).parsear()
