"""Módulo Vista (main.py) - Sistema de Gestión Académica.

Implementa la capa de presentación mediante consola interactiva.
Utiliza polimorfismo para renderizar entidades heterogéneas (Estudiantes, Materias, Matrículas)
a través de una única función de visualización: mostrar_lista().
"""

from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EstudianteController, MateriaController, MatriculaController

# Instanciación coordinada de controladores
estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    """Solicita y valida un número entero desde la consola."""
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def pedir_flotante(etiqueta):
    """Solicita y valida un número decimal desde la consola."""
    try:
        return float(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    """Desempaqueta y muestra en color la tupla (exito, mensaje)."""
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """POLIMORFISMO: Muestra una colección de cualquier modelo llamando a str(objeto)."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    """Itera sobre la representación en diccionario de un objeto de dominio."""
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# SECCIÓN 1: ESTUDIANTES
# =====================================================================

def crear_estudiante():
    imprimir_titulo("REGISTRAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet (ej. EST2026001): "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("LISTA DE ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "No hay estudiantes registrados.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    encontrados = estudiantes.buscar(termino)
    mostrar_lista(encontrados, f"No se hallaron coincidencias para '{termino}'.")
    pausa()


def ver_estudiante():
    imprimir_titulo("CONSULTAR ESTUDIANTE POR ID")
    id_est = pedir_entero("Id del estudiante: ")
    est = estudiantes.obtener(id_est)
    if est is None:
        imprimir_error("Estudiante no encontrado")
    else:
        mostrar_detalle(est)
        prom = matriculas.promedio_de_estudiante(est.id)
        imprimir_info(f"Promedio general: {prom:.2f}")
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_est = pedir_entero("Id del estudiante: ")
    est = estudiantes.obtener(id_est)
    if est is None:
        imprimir_error("Estudiante no encontrado")
        return pausa()

    imprimir_info(f"Editando a: {est.etiqueta()}")
    print("Deje en blanco el campo si no desea modificarlo.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(est, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes.actualizar(id_est, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_est = pedir_entero("Id del estudiante: ")
    est = estudiantes.obtener(id_est)
    if est is None:
        imprimir_error("Estudiante no encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {est.etiqueta()}")
    if confirmar("¿Confirma la eliminación permanente?"):
        mostrar_resultado(*estudiantes.eliminar(id_est))
    else:
        imprimir_info("Operación cancelada.")
    pausa()


# =====================================================================
# SECCIÓN 2: MATERIAS
# =====================================================================

def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre de la materia: "),
        "codigo": input("Código (ej. MAT101): "),
        "creditos": input("Créditos (1 a 10): "),
        "cupos": input(f"Cupos disponibles (máx {Materia.CUPOS_MAXIMOS}): "),
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("CATÁLOGO DE MATERIAS")
    mostrar_lista(materias.leer(), "No hay materias registradas.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(materias.buscar(termino), f"Sin materias coincidentes con '{termino}'.")
    pausa()


def ver_materia():
    imprimir_titulo("CONSULTAR MATERIA POR ID")
    id_mat = pedir_entero("Id de la materia: ")
    mat = materias.obtener(id_mat)
    if mat is None:
        imprimir_error("Materia no encontrada")
    else:
        mostrar_detalle(mat)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_mat = pedir_entero("Id de la materia: ")
    mat = materias.obtener(id_mat)
    if mat is None:
        imprimir_error("Materia no encontrada")
        return pausa()

    imprimir_info(f"Editando: {mat.etiqueta()}")
    print("Deje en blanco el campo si no desea modificarlo.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(mat, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*materias.actualizar(id_mat, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_mat = pedir_entero("Id de la materia: ")
    mat = materias.obtener(id_mat)
    if mat is None:
        imprimir_error("Materia no encontrada")
        return pausa()

    imprimir_info(f"Se eliminará: {mat.etiqueta()}")
    if confirmar("¿Confirma la eliminación?"):
        mostrar_resultado(*materias.eliminar(id_mat))
    else:
        imprimir_info("Operación cancelada.")
    pausa()


# =====================================================================
# SECCIÓN 3: MATRÍCULAS
# =====================================================================

def registrar_matricula():
    imprimir_titulo("MATRICULAR ESTUDIANTE")
    imprimir_info("Estudiantes disponibles:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("\nMaterias disponibles:")
    mostrar_lista(materias.leer())

    id_est = pedir_entero("\nId del estudiante: ")
    id_mat = pedir_entero("Id de la materia: ")
    periodo = input("Período lectivo (ej. 2026-1): ").strip()
    nota_input = input("Nota inicial (opcional, 0 a 20 / Enter para omitir): ").strip()

    if id_est is None or id_mat is None or not periodo:
        imprimir_error("Los datos de estudiante, materia y período son obligatorios")
        return pausa()

    datos = {
        "estudiante_id": id_est,
        "materia_id": id_mat,
        "periodo": periodo,
    }
    if nota_input:
        datos["nota"] = nota_input

    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS ACTIVAS")
    mostrar_lista(matriculas.leer(), "No hay matrículas registradas.")
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA ACADÉMICA")
    id_matr = pedir_entero("Id de la matrícula: ")
    matr = matriculas.obtener(id_matr)
    if matr is None:
        imprimir_error("Matrícula no encontrada")
        return pausa()

    imprimir_info(f"Matrícula actual: {matr.etiqueta()}")
    nota_val = pedir_flotante("Ingrese la nueva calificación (0.0 a 20.0): ")
    if nota_val is None:
        imprimir_error("Valor de nota inválido")
        return pausa()

    mostrar_resultado(*matriculas.registrar_nota(id_matr, nota_val))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO ACADÉMICO OFICIAL")
    id_matr = pedir_entero("Id de la matrícula: ")
    cert = matriculas.certificado(id_matr)
    if cert is None:
        imprimir_error("No se encontró la matrícula solicitada")
    else:
        print(cert)
    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_matr = pedir_entero("Id de la matrícula a retirar: ")
    matr = matriculas.obtener(id_matr)
    if matr is None:
        imprimir_error("Matrícula no encontrada")
        return pausa()

    imprimir_info(f"Se retirará: {matr.etiqueta()}")
    if confirmar("Se devolverá el cupo a la materia respectiva. ¿Confirma el retiro?"):
        mostrar_resultado(*matriculas.eliminar(id_matr))
    else:
        imprimir_info("Operación cancelada.")
    pausa()


def resumen_academico():
    imprimir_titulo("RESUMEN INSTITUCIONAL")
    print(f"  Estudiantes registrados : {len(estudiantes.leer())}")
    print(f"  Carreras activas        : {', '.join(estudiantes.carreras()) or 'Ninguna'}")
    print(f"  Total de materias       : {len(materias.leer())}")
    sin_cupo = materias.materias_sin_cupo()
    print(f"  Materias sin cupo       : {', '.join(m.nombre for m in sin_cupo) or 'Ninguna'}")
    print(f"  Matrículas totales      : {len(matriculas.leer())}")
    print(f"  Matrículas aprobadas    : {matriculas.total_aprobadas()}")
    pausa()


# =====================================================================
# MENÚS MODULARES
# =====================================================================

MENU_ESTUDIANTES = {
    "1": ("Registrar estudiante", crear_estudiante),
    "2": ("Listar todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por Id", ver_estudiante),
    "5": ("Actualizar datos", actualizar_estudiante),
    "6": ("Eliminar estudiante", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Listar materias", listar_materias),
    "3": ("Buscar materia", buscar_materia),
    "4": ("Ver por Id", ver_materia),
    "5": ("Actualizar materia", actualizar_materia),
    "6": ("Eliminar materia", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular estudiante", registrar_matricula),
    "2": ("Ver todas las matrículas", listar_matriculas),
    "3": ("Registrar calificación", registrar_nota),
    "4": ("Generar certificado oficial", ver_certificado),
    "5": ("Retirar matrícula (libera cupo)", retirar_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    """Bucle unificado de navegación por teclado mediante despachador de diccionario."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Seleccione una opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción inválida.")
            pausa()
            continue

        _, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA DE GESTIÓN ACADÉMICA (POO / MVC)")
        print("  1. Módulo de Estudiantes")
        print("  2. Módulo de Materias")
        print("  3. Módulo de Matrículas")
        print("  4. Resumen y Estadísticas")
        print("  0. Salir\n")

        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("GESTIÓN DE ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("GESTIÓN DE MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("GESTIÓN DE MATRÍCULAS", MENU_MATRICULAS)
        elif tecla == "4":
            resumen_academico()
        elif tecla == "0":
            imprimir_info("¡Gracias por utilizar el Sistema Académico! 👋")
            break
        else:
            imprimir_error("Opción no válida.")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma finalizado por el usuario.")
