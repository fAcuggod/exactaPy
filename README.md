# ExactaPy: Álgebra Lineal y Análisis Matemático I

Motor matemático local desarrollado desde cero en **Python 3.10+** con fines de aprendizaje en Programación Orientada a Objetos (POO), programación funcional, cálculo numérico y simbólico.

Todos los algoritmos algebraicos operan sobre el cuerpo de los números racionales ($\mathbb{Q}$) mediante `fractions.Fraction`, eliminando errores de redondeo de punto flotante (IEEE 754).

---

## Arquitectura del Proyecto

* `definiciones.py`: Tipos de datos estructurados (`Enum`, `dataclass`), alias de tipos y jerarquía de excepciones.
* `matriz.py`: **[TP 0]** Tipo Abstracto de Datos `Matriz` sobre $\mathbb{Q}$ y sobrecarga de operadores.
* `algebra.py`: **[TP 1]** Eliminación de Gauss-Jordan paso a paso, Rouché-Frobenius, determinantes y subespacios.
* `analisis_num.py`: **[TP 2]** Bisección (Bolzano), Newton-Raphson, Secante e integración numérica.
* `expresiones.py`: **[TP 3]** Árboles de expresión simbólica, derivación por regla de la cadena y Polinomio de Taylor.
* `tests/`: Suite de tests unitarios de caja blanca y validación con Oráculo.

---

## Comandos Útiles de Desarrollo

### 1. Chequeo de tipado estático (Mypy)

Para verificar que todas las firmas y variables respeten sus tipos:
```bash
python3 -m mypy --strict definiciones.py matriz.py
```
### 2. Ejecutar los casos de test
Para correr las pruebas unitarias del TP 0:
```bash
python3 -m unittest tests/test_matriz.py
```
Para evaluar líneas y ramas cubiertas por los tests y generar el reporte visual:
```bash
python3 -m coverage run --include=matriz.py,algebra.py --branch -m unittest discover -s tests
python3 -m coverage report -m
python3 -m coverage html
<<<<<<< HEAD
=======
```
>>>>>>> 300a975ea1f238709b8ac92ef304bc37de69b5c8
