"""Interfaz interactiva de consola (CLI) para ExactaPy usando Rich."""

from fractions import Fraction
from rich.console import Console
from rich.panel import Panel
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table

from exactapy_core.algebra import base_nucleo, escalonar_gauss_jordan, resolver_sistema
from exactapy_core.analisis_num import biseccion_bolzano, integrar_simpson
from exactapy_core.definiciones import ExactaPyError
from exactapy_core.expresiones import (
    Constante,
    Coseno,
    Exponencial,
    Expresion,
    Logaritmo,
    Seno,
    Variable,
    analizar_funcion_en_intervalo,
    polinomio_taylor,
)
from exactapy_core.matriz import Matriz

console = Console()


def leer_matriz(titulo: str = "Ingreso de Matriz") -> Matriz:
    """Solicita al usuario una matriz sobre Q fila por fila."""
    console.print(f"\n[bold cyan]{titulo}[/bold cyan]")
    filas_n: int = IntPrompt.ask("Cantidad de filas", default=3)
    grilla: list[list[str]] = []
    console.print("[dim]Ingresá cada fila separada por espacios (ej: 1 -2 3/4):[/dim]")
    for i in range(filas_n):
        linea: str = Prompt.ask(f"Fila {i + 1}")
        grilla.append(linea.strip().split())
    return Matriz(grilla)


def leer_vector(longitud: int) -> list[Fraction]:
    """Solicita al usuario un vector de términos independientes sobre Q."""
    console.print(
        f"[dim]Ingresá {longitud} valores separados por espacios (ej: 1 5 -4):[/dim]"
    )
    linea: str = Prompt.ask("Vector b")
    partes: list[str] = linea.strip().split()
    if len(partes) != longitud:
        raise ValueError(f"Se esperaban {longitud} componentes y se recibieron {len(partes)}.")
    return [Fraction(p) for p in partes]


def mostrar_matriz(m: Matriz, titulo: str) -> None:
    """Renderiza una Matriz como tabla formateada dentro de un Panel."""
    tabla = Table(title=titulo, show_header=False, box=None)
    for _ in range(m.columnas):
        tabla.add_column(justify="right")
    for i in range(m.filas):
        tabla.add_row(*(str(m[i, j]) for j in range(m.columnas)))
    console.print(Panel(tabla, expand=False))


def elegir_expresion_catalogo() -> Expresion:
    """Permite elegir una función simbólica predefinida construida con el AST."""
    x = Variable("x")
    catalogo: dict[str, tuple[str, Expresion]] = {
        "1": ("f(x) = x^3 - 3x", (x ** 3) - Constante(3.0) * x),
        "2": ("f(x) = x^5 - (5/3)x^3", (x ** 5) - (Constante(5.0) / Constante(3.0)) * (x ** 3)),
        "3": ("f(x) = sin(x)", Seno(x)),
        "4": ("f(x) = cos(x)", Coseno(x)),
        "5": ("f(x) = e^x - 2", Exponencial(x) - Constante(2.0)),
        "6": ("f(x) = ln(x) - 1", Logaritmo(x) - Constante(1.0)),
    }
    tabla = Table(title="Catálogo de Funciones Simbólicas")
    tabla.add_column("Opción", style="cyan", justify="center")
    tabla.add_column("Expresión", style="green")
    for clave, (etiqueta, _) in catalogo.items():
        tabla.add_row(clave, etiqueta)
    console.print(tabla)

    eleccion: str = Prompt.ask("Elegí una función", choices=list(catalogo.keys()), default="1")
    return catalogo[eleccion][1]


def opcion_gauss_jordan() -> None:
    """Flujo interactivo para Gauss-Jordan, base del núcleo y exportación LaTeX."""
    try:
        matriz_a: Matriz = leer_matriz("Matriz A para Gauss-Jordan")
        res = escalonar_gauss_jordan(matriz_a)

        mostrar_matriz(matriz_a, "Matriz Original (A)")

        tabla_pasos = Table(title="Traza de Operaciones Elementales")
        tabla_pasos.add_column("#", justify="right", style="cyan")
        tabla_pasos.add_column("Operación", style="green")
        for idx, paso in enumerate(res.pasos, start=1):
            tabla_pasos.add_row(str(idx), paso.descripcion)
        console.print(tabla_pasos)

        mostrar_matriz(res.rref, "Forma Escalonada Reducida (RREF)")
        console.print(f"[bold]Columnas pivote:[/bold] {res.columnas_pivote}")
        console.print(f"[bold]Intercambios de fila:[/bold] {res.intercambios_realizados}")

        nucleo = base_nucleo(matriz_a)
        nucleo_str = [[str(c) for c in vec] for vec in nucleo]
        console.print(f"[bold]Base del Núcleo (Ker A):[/bold] {nucleo_str or 'Trivial ({0})'}")
        console.print(f"[bold]LaTeX (RREF):[/bold] [yellow]{res.rref.to_latex()}[/yellow]")
    except (ValueError, ExactaPyError) as err:
        console.print(f"[bold red]Error:[/bold red] {err}")


def opcion_resolver_sistema() -> None:
    """Flujo interactivo para resolución de sistemas Ax = b por Rouché-Frobenius."""
    try:
        matriz_a: Matriz = leer_matriz("Matriz de coeficientes A")
        vector_b: list[Fraction] = leer_vector(matriz_a.filas)
        sol = resolver_sistema(matriz_a, vector_b)

        console.print(f"\n[bold cyan]Clasificación:[/bold cyan] {sol.clasificacion.value}")
        if sol.solucion_particular is not None:
            part_str = [str(c) for c in sol.solucion_particular]
            console.print(f"[bold green]Solución particular:[/bold green] {part_str}")
        if sol.base_nucleo:
            hom_str = [[str(c) for c in vec] for vec in sol.base_nucleo]
            console.print(f"[bold green]Base del sistema homogéneo:[/bold green] {hom_str}")
        console.print(f"[bold]Pasos aplicados:[/bold] {len(sol.pasos_gauss)}")
    except (ValueError, ExactaPyError) as err:
        console.print(f"[bold red]Error:[/bold red] {err}")


def opcion_analisis_numerico() -> None:
    """Flujo interactivo para Bolzano (Bisección) e Integración por Simpson."""
    try:
        expr: Expresion = elegir_expresion_catalogo()
        a: float = FloatPrompt.ask("Extremo izquierdo a", default=-2.0)
        b: float = FloatPrompt.ask("Extremo derecho b", default=2.0)
        tol: float = FloatPrompt.ask("Tolerancia", default=1e-6)

        console.print(f"\n[bold]Función elegida (LaTeX):[/bold] [yellow]{expr.to_latex()}[/yellow]")

        n_simpson: int = IntPrompt.ask("Subintervalos pares para Simpson", default=20)
        area: float = integrar_simpson(expr.evaluar, a, b, n_simpson)
        console.print(f"[bold green]Integral definida (Simpson):[/bold green] {area:.8f}")

        if expr.evaluar(a) * expr.evaluar(b) < 0:
            res_raiz = biseccion_bolzano(expr.evaluar, a, b, tol)
            console.print(
                f"[bold green]Raíz por Bolzano:[/bold green] {res_raiz.raiz_aproximada:.8f} "
                f"(en {res_raiz.iteraciones_realizadas} iteraciones)"
            )
        else:
            console.print(
                "[yellow]Aviso:[/yellow] f(a) y f(b) no tienen signos opuestos; se omite Bolzano directo."
            )
    except (ValueError, ZeroDivisionError, ExactaPyError) as err:
        console.print(f"[bold red]Error:[/bold red] {err}")


def opcion_estudio_y_taylor() -> None:
    """Flujo interactivo para Derivación, Polinomio de Taylor y Estudio de Función."""
    try:
        expr: Expresion = elegir_expresion_catalogo()
        a: float = FloatPrompt.ask("Extremo izquierdo a", default=-2.0)
        b: float = FloatPrompt.ask("Extremo derecho b", default=2.0)
        subintervalos: int = IntPrompt.ask("Cantidad de subintervalos", default=40)

        reporte = analizar_funcion_en_intervalo(expr, a, b, subintervalos=subintervalos)

        console.print(f"\n[bold]f(x) (LaTeX):[/bold] [yellow]{expr.to_latex()}[/yellow]")
        console.print(f"[bold]f'(x):[/bold] {reporte.derivada_primera}")
        console.print(f"[bold]f''(x):[/bold] {reporte.derivada_segunda}")
        console.print(
            f"[bold]Raíces aproximadas:[/bold] {[round(r, 6) for r in reporte.raices_aproximadas]}"
        )
        console.print(f"[bold]Integral definida:[/bold] {reporte.integral_definida:.6f}")

        tabla_pc = Table(title="Puntos Críticos Detectados")
        tabla_pc.add_column("x", justify="right", style="cyan")
        tabla_pc.add_column("f(x)", justify="right")
        tabla_pc.add_column("f''(x)", justify="right")
        tabla_pc.add_column("Clasificación", style="green")
        for pc in reporte.puntos_criticos:
            tabla_pc.add_row(
                f"{pc.x:.6f}",
                f"{pc.valor_f:.6f}",
                f"{pc.segunda_derivada:.6f}",
                pc.clasificacion.value,
            )
        console.print(tabla_pc)

        x0: float = FloatPrompt.ask("\nCentro x0 para Polinomio de Taylor", default=0.0)
        orden: int = IntPrompt.ask("Orden n del Polinomio de Taylor", default=3)
        taylor: Expresion = polinomio_taylor(expr, x0, orden)
        console.print(f"[bold cyan]Polinomio de Taylor P_{orden}(x):[/bold cyan] {taylor}")
        console.print(f"[bold]LaTeX (Taylor):[/bold] [yellow]{taylor.to_latex()}[/yellow]")
    except (ValueError, ZeroDivisionError, ExactaPyError) as err:
        console.print(f"[bold red]Error:[/bold red] {err}")


def main() -> None:
    """Punto de entrada de la interfaz CLI de ExactaPy."""
    while True:
        console.print(
            Panel.fit(
                "[bold cyan]ExactaPy[/bold cyan] - Álgebra Lineal y Análisis I\n\n"
                "[1] Escalonamiento Gauss-Jordan paso a paso + Núcleo\n"
                "[2] Resolver Sistema Lineal (Rouché-Frobenius)\n"
                "[3] Análisis Numérico (Bolzano + Simpson)\n"
                "[4] Estudio Completo de Función + Polinomio de Taylor\n"
                "[0] Salir",
                title="Menú Principal",
            )
        )
        opcion: str = Prompt.ask("Elegí una opción", choices=["0", "1", "2", "3", "4"])

        if opcion == "0":
            console.print("[green]¡Chau![/green]")
            break
        if opcion == "1":
            opcion_gauss_jordan()
        elif opcion == "2":
            opcion_resolver_sistema()
        elif opcion == "3":
            opcion_analisis_numerico()
        elif opcion == "4":
            opcion_estudio_y_taylor()


if __name__ == "__main__":
    main()
