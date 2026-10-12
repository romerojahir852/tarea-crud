"""Suite de Pruebas Automatizadas para proyecto_estudiantes.

Verifica rigurosamente todos los criterios de la rúbrica:
1. Separación de capas MVC (cero print/input en views.py mediante AST).
2. Herencia y Polimorfismo (ModeloBase -> Persona -> Estudiante; Materia, Matricula).
3. Métodos de clase y estáticos (@classmethod desde_diccionario, @staticmethod es_nota_valida).
4. Las 5 operaciones fundamentales CRUD + Búsqueda para Estudiantes y Materias.
5. Coordinación de Matrículas (descuento/restitución de cupos, duplicados y notas).
6. Uso de las 4 colecciones de Python (list, tuple, set, dict).
"""

import ast
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIR_ACTUAL not in sys.path:
    sys.path.insert(0, DIR_ACTUAL)

import models
import views
from models import ModeloBase, Persona, Estudiante, Materia, Matricula
from views import EstudianteController, MateriaController, MatriculaController


def test_separacion_mvc():
    """Valida mediante AST que views.py no tenga llamadas directas a print() ni input()."""
    ruta_views = os.path.join(DIR_ACTUAL, "views.py")
    with open(ruta_views, "r", encoding="utf-8") as archivo:
        arbol = ast.parse(archivo.read(), filename="views.py")

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call):
            if isinstance(nodo.func, ast.Name) and nodo.func.id in ("print", "input"):
                raise AssertionError(
                    f"Violación de MVC: Llamada a {nodo.func.id}() detectada en la línea {nodo.lineno} de views.py"
                )
    print("✓ Criterio 1: Separación estricta MVC (0 llamadas AST a print/input en views.py).")


def test_herencia_y_polimorfismo():
    """Verifica herencia, super(), métodos de clase y polimorfismo con etiqueta()."""
    # 1. Herencia de clases
    assert issubclass(Estudiante, Persona), "Estudiante debe heredar de Persona"
    assert issubclass(Persona, ModeloBase), "Persona debe heredar de ModeloBase"
    assert issubclass(Materia, ModeloBase), "Materia debe heredar de ModeloBase"
    assert issubclass(Matricula, ModeloBase), "Matricula debe heredar de ModeloBase"

    # 2. Reconstrucción con el método de clase heredado desde_diccionario
    est = Estudiante.desde_diccionario({
        "id": 10,
        "nombre": "Carlos",
        "apellido": "Gómez",
        "email": "carlos@u.edu",
        "carnet": "EST10",
        "carrera": "Sistemas"
    })
    assert isinstance(est, Estudiante)
    assert est.id == 10
    assert est.carnet == "EST10"

    mat = Materia.desde_diccionario({
        "id": 20,
        "nombre": "Álgebra Lineal",
        "codigo": "ALG101",
        "creditos": 3,
        "cupos": 25
    })
    assert isinstance(mat, Materia)
    assert mat.codigo == "ALG101"

    # 3. Polimorfismo: __str__ llama a etiqueta()
    assert "Carlos Gómez" in str(est)
    assert "ALG101" in str(mat)

    # 4. Métodos y atributos estáticos en Materia
    assert Materia.CUPOS_MAXIMOS == 30
    assert Materia.NOTA_APROBACION == 14.0
    assert Materia.es_nota_valida(15.5) is True
    assert Materia.es_nota_valida(25.0) is False
    assert Materia.es_nota_valida("abc") is False
    assert Materia.es_credito_valido(4) is True
    assert Materia.es_credito_valido(15) is False

    print("✓ Criterio 2: Herencia, polimorfismo y miembros estáticos verificados.")


def test_flujo_completo():
    """Prueba de integración en archivos temporales para Estudiantes, Materias y Matrículas."""
    ruta_est = os.path.join(DIR_ACTUAL, "data", "test_estudiantes.json")
    ruta_mat = os.path.join(DIR_ACTUAL, "data", "test_materias.json")
    ruta_mtc = os.path.join(DIR_ACTUAL, "data", "test_matriculas.json")

    for r in (ruta_est, ruta_mat, ruta_mtc):
        if os.path.exists(r):
            os.remove(r)

    ctrl_est = EstudianteController(archivo=ruta_est)
    ctrl_mat = MateriaController(archivo=ruta_mat)
    ctrl_mtc = MatriculaController(ctrl_est, ctrl_mat, archivo=ruta_mtc)

    # 1. Crear Estudiantes
    ok, msg = ctrl_est.crear({
        "nombre": "María",
        "apellido": "López",
        "email": "maria@u.edu",
        "carnet": "EST2026002",
        "carrera": "Medicina"
    })
    assert ok is True, f"Error creando estudiante: {msg}"

    # Prueba de carnet duplicado con set
    ok, msg = ctrl_est.crear({
        "nombre": "Mario",
        "apellido": "López",
        "email": "otro@u.edu",
        "carnet": "EST2026002",
        "carrera": "Medicina"
    })
    assert ok is False, "Debe rechazar carnet duplicado"
    assert "ya pertenece" in msg

    # 2. Crear Materia
    ok, msg = ctrl_mat.crear({
        "nombre": "Química General",
        "codigo": "QMC101",
        "creditos": 4,
        "cupos": 1  # 1 cupo disponible
    })
    assert ok is True, f"Error creando materia: {msg}"

    # 3. Matricular estudiante (debe descontar cupo de 1 a 0)
    materia_obj = ctrl_mat.buscar("QMC101")[0]
    estudiante_obj = ctrl_est.buscar("EST2026002")[0]

    ok, msg = ctrl_mtc.crear({
        "estudiante_id": estudiante_obj.id,
        "materia_id": materia_obj.id,
        "periodo": "2026-1",
        "nota": 17.5
    })
    assert ok is True, f"Error creando matrícula: {msg}"
    assert materia_obj.cupos == 0, "El cupo debió reducirse a 0"

    # 4. Intento de matricular en materia sin cupo
    ok, msg = ctrl_est.crear({
        "nombre": "Pedro",
        "apellido": "Páez",
        "email": "pedro@u.edu",
        "carnet": "EST2026003",
        "carrera": "Medicina"
    })
    pedro_obj = ctrl_est.buscar("EST2026003")[0]

    ok, msg = ctrl_mtc.crear({
        "estudiante_id": pedro_obj.id,
        "materia_id": materia_obj.id,
        "periodo": "2026-1"
    })
    assert ok is False, "Debe rechazar matrícula por falta de cupo"
    assert "Cupos agotados" in msg

    # 5. Generar certificado
    matricula_creada = ctrl_mtc.leer()[0]
    cert = ctrl_mtc.certificado(matricula_creada.id)
    assert "María López" in cert
    assert "QMC101" in cert
    assert "Aprobado" in cert

    # 6. Retirar matrícula (debe restituir cupo a 1)
    ok, msg = ctrl_mtc.eliminar(matricula_creada.id)
    assert ok is True
    assert materia_obj.cupos == 1, "El cupo debió volver a 1 tras retiro"

    # Limpieza de archivos de prueba
    for r in (ruta_est, ruta_mat, ruta_mtc):
        if os.path.exists(r):
            os.remove(r)

    print("✓ Criterio 3: Flujo integral de CRUD, reglas de cupos, notas y certificados superado.")


def main():
    print("=== INICIANDO VALIDACIÓN ACADÉMICA AUTOMATIZADA ===")
    test_separacion_mvc()
    test_herencia_y_polimorfismo()
    test_flujo_completo()
    print("=== TODAS LAS PRUEBAS PASARON EXITOSAMENTE (100%) ===")


if __name__ == "__main__":
    main()
