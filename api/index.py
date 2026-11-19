"""Backend Serverless (FastAPI) para ExactaPy Web en Vercel."""

from fractions import Fraction
import math
import os
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from exactapy_core.algebra import base_nucleo, escalonar_gauss_jordan, resolver_sistema
from exactapy_core.definiciones import ExactaPyError
from exactapy_core.expresiones import (
    Expresion,
    analizar_funcion_en_intervalo,
    polinomio_taylor,
)
from exactapy_core.matriz import Matriz
from exactapy_core.parser import parsear_expresion

app = FastAPI(
    title="ExactaPy API",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatrizRequest(BaseModel):
    matriz: list[list[str]] = Field(..., min_length=1, max_length=8)


class SistemaRequest(BaseModel):
    matriz_a: list[list[str]] = Field(..., min_length=1, max_length=8)
    vector_b: list[str] = Field(..., min_length=1, max_length=8)


class EstudioFuncionRequest(BaseModel):
    expresion: str = Field(..., min_length=1, max_length=200)
    a: float = -3.0
    b: float = 3.0
    subintervalos: int = Field(default=60, ge=10, le=500)
    taylor_x0: float = 0.0
    taylor_orden: int = Field(default=3, ge=0, le=10)



def _validar_matriz_y_construir(grilla: list[list[str]]) -> Matriz:
    for fila in grilla:
        if len(fila) == 0 or len(fila) > 8:
            raise ValueError("Cada fila debe tener entre 1 y 8 columnas.")
    return Matriz(grilla)


def _muestrear_curva(expr: Expresion, a: float, b: float, puntos: int = 120) -> list[dict[str, float | None]]:
    """Genera pares (x, y) seguros para graficar en el frontend."""
    paso = (b - a) / (puntos - 1)
    muestras: list[dict[str, float | None]] = []
    for i in range(puntos):
        x_val = a + i * paso
        try:
            y_val = expr.evaluar(x_val)
            y_limpio = round(y_val, 6) if math.isfinite(y_val) and abs(y_val) < 1e6 else None
        except (ValueError, ZeroDivisionError, OverflowError):
            y_limpio = None
        muestras.append({"x": round(x_val, 6), "y": y_limpio})
    return muestras



router = APIRouter()

@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "engine": "ExactaPy Core"}

@router.post("/gauss-jordan")
def endpoint_gauss_jordan(req: MatrizRequest) -> dict[str, Any]:
    try:
        matriz_a = _validar_matriz_y_construir(req.matriz)
        res = escalonar_gauss_jordan(matriz_a)
        nucleo = base_nucleo(matriz_a)

        return {
            "matriz_original_latex": matriz_a.to_latex(),
            "rref_latex": res.rref.to_latex(),
            "pasos": [paso.descripcion for paso in res.pasos],
            "columnas_pivote": list(res.columnas_pivote),
            "cantidad_intercambios": res.intercambios_realizados,
            "base_nucleo": [[str(c) for c in vec] for vec in nucleo],
        }
    except (ValueError, ExactaPyError) as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@router.post("/sistema")
def endpoint_sistema(req: SistemaRequest) -> dict[str, Any]:
    try:
        matriz_a = _validar_matriz_y_construir(req.matriz_a)
        if len(req.vector_b) != matriz_a.filas:
            raise ValueError(f"El vector b debe tener {matriz_a.filas} componentes.")
        vector_b = [Fraction(val) for val in req.vector_b]

        sol = resolver_sistema(matriz_a, vector_b)
        return {
            "matriz_a_latex": matriz_a.to_latex(),
            "clasificacion": sol.clasificacion.value,
            "solucion_particular": (
                [str(c) for c in sol.solucion_particular]
                if sol.solucion_particular is not None
                else None
            ),
            "base_homogeneo": [[str(c) for c in vec] for vec in sol.base_nucleo],
            "pasos": [paso.descripcion for paso in sol.pasos_gauss],
        }
    except (ValueError, ExactaPyError) as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@router.post("/estudio-funcion")
def endpoint_estudio_funcion(req: EstudioFuncionRequest) -> dict[str, Any]:
    try:
        if req.a >= req.b:
            raise ValueError("El extremo izquierdo 'a' debe ser estrictamente menor que 'b'.")

        expr = parsear_expresion(req.expresion)
        reporte = analizar_funcion_en_intervalo(
            expr, req.a, req.b, subintervalos=req.subintervalos
        )
        taylor = polinomio_taylor(expr, req.taylor_x0, req.taylor_orden)

        d1 = expr.derivar()
        d2 = d1.derivar()

        return {
            "funcion_latex": expr.to_latex(),
            "derivada_primera_latex": d1.to_latex(),
            "derivada_segunda_latex": d2.to_latex(),
            "taylor_latex": taylor.to_latex(),
            "raices_aproximadas": [round(r, 6) for r in reporte.raices_aproximadas],
            "integral_definida": round(reporte.integral_definida, 6),
            "puntos_criticos": [
                {
                    "x": round(pc.x, 6),
                    "y": round(pc.valor_f, 6),
                    "segunda_derivada": round(pc.segunda_derivada, 6),
                    "clasificacion": pc.clasificacion.value,
                }
                for pc in reporte.puntos_criticos
            ],
            "curva_f": _muestrear_curva(expr, req.a, req.b),
            "curva_taylor": _muestrear_curva(taylor, req.a, req.b),
        }
    except (ValueError, ZeroDivisionError, ExactaPyError) as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

# Vercel invoca la función con la ruta original (/api/...), pero se monta
# también sin prefijo por si el runtime entrega la ruta ya recortada.
app.include_router(router, prefix="/api")
app.include_router(router)

# En Vercel, public/ lo sirve la CDN: no se monta StaticFiles para que el
# catch-all "/" nunca interfiera con el enrutamiento de la función.
# Localmente (uvicorn) sí se sirve el frontend desde la misma app.
_PUBLIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")

if not os.environ.get("VERCEL") and os.path.isdir(_PUBLIC_DIR):
    app.mount("/", StaticFiles(directory=_PUBLIC_DIR, html=True), name="static")
