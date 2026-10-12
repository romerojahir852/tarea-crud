"""Módulo Controlador (views.py) - Sistema Académico.

Implementa la lógica del negocio mediante tres controladores especializados
que heredan de la clase base abstracta CrudBase.

Utiliza estratégicamente las cuatro colecciones nativas de Python:
- list  : Para mantener secuencias mutables de objetos en memoria (self.lista).
- tuple : Para campos inmutables y retornos consistentes (exito, mensaje).
- set   : Para validar unicidad O(1) de emails, carnets, códigos y evitar matrículas duplicadas.
- dict  : Para mapear registros, agrupamientos con setdefault y serialización JSON.
"""

from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE ABSTRACTA (CrudBase)
# =====================================================================
class CrudBase(ABC):
    """Contrato abstracto que formaliza las 7 operaciones requeridas para todo controlador."""

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR: Estudiantes
# =====================================================================
class EstudianteController(CrudBase):
    """Gestiona el ciclo de vida de los estudiantes y garantiza unicidad de identidad."""

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = [e.a_diccionario() for e in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Valida obligatoriedad, formato de correo y unicidad de email y carnet."""
        # TUPLA: Campos obligatorios al crear
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        # Validación de email
        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO: Búsqueda O(1) para prevenir duplicados
            emails_usados = {e.email for e in self.lista if e.id != id_actual}
            if email in emails_usados:
                return f"El email '{email}' ya se encuentra registrado"

        # Validación de carnet único
        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            if carnet == "":
                return "El carnet no puede estar vacío"
            # CONJUNTO: Verificación de carnet único
            carnets_usados = {e.carnet for e in self.lista if e.id != id_actual}
            if carnet in carnets_usados:
                return f"El carnet '{carnet}' ya pertenece a otro estudiante"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for e in self.lista:
            if e.id == id_estudiante:
                return e
        return None

    def buscar(self, texto):
        texto = str(texto).strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for e in self.lista:
            if (texto in e.nombre.lower()
                    or texto in e.apellido.lower()
                    or texto in e.email.lower()
                    or texto in e.carnet.lower()
                    or texto in e.carrera.lower()):
                encontrados.append(e)
        return encontrados

    def siguiente(self):
        mayor = 0
        for e in self.lista:
            if e.id > mayor:
                mayor = e.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        # CONJUNTOS: Diferencia para detectar campos inválidos
        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado exitosamente"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras(self):
        """CONJUNTO ordenado de carreras registradas sin duplicación."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR: Materias
# =====================================================================
class MateriaController(CrudBase):
    """Gestiona el catálogo de asignaturas académicas y la disponibilidad de cupos."""

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = [m.a_diccionario() for m in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo", "creditos"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            if codigo == "":
                return "El código de materia no puede estar vacío"
            # CONJUNTO: Validación de código único
            codigos_usados = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos_usados:
                return f"El código de materia '{codigo}' ya existe"

        if "creditos" in datos:
            if not Materia.es_credito_valido(datos["creditos"]):
                return "Los créditos deben ser un número entero entre 1 y 10"

        if "cupos" in datos:
            try:
                cupos = int(datos["cupos"])
                if cupos < 0 or cupos > Materia.CUPOS_MAXIMOS:
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except (TypeError, ValueError):
                return "Los cupos deben ser un número entero válido"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for m in self.lista:
            if m.id == id_materia:
                return m
        return None

    def buscar(self, texto):
        texto = str(texto).strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for m in self.lista:
            if texto in m.nombre.lower() or texto in m.codigo.lower():
                encontrados.append(m)
        return encontrados

    def siguiente(self):
        mayor = 0
        for m in self.lista:
            if m.id > mayor:
                mayor = m.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cupos = int(datos.get("cupos", 0)) if str(datos.get("cupos", "")).strip() != "" else 0
        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(datos["creditos"]),
            cupos
        )
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "codigo", "creditos", "cupos"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def materias_sin_cupo(self):
        """Retorna las asignaturas que no disponen de cupos para matrícula."""
        return [m for m in self.lista if m.sin_cupos()]


# =====================================================================
# CONTROLADOR: Matrículas
# =====================================================================
class MatriculaController(CrudBase):
    """Coordina las relaciones académicas entre Estudiantes y Materias."""

    def __init__(self, estudiantes_controller, materias_controller, archivo="data/matriculas.json"):
        self.estudiantes = estudiantes_controller
        self.materias = materias_controller
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = [m.a_diccionario() for m in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        periodo = str(datos.get("periodo", "")).strip()
        if periodo == "":
            return "El período académico es obligatorio (ej. 2026-1)"

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe una materia con id {materia_id}"

        # Al crear matrícula nueva, verificar cupos
        if id_actual is None and not materia.hay_cupo():
            return f"Cupos agotados para la materia '{materia.nombre}'"

        # CONJUNTO DE TUPLAS: Evitar matrícula duplicada en la misma materia y período
        tuplas_existentes = {
            (m.estudiante_id, m.materia_id, m.periodo)
            for m in self.lista if m.id != id_actual
        }
        if (estudiante_id, materia_id, periodo) in tuplas_existentes:
            return f"El estudiante ya está matriculado en '{materia.nombre}' para el período {periodo}"

        # Validación opcional de nota inicial
        if "nota" in datos and str(datos["nota"]).strip() != "":
            if not Materia.es_nota_valida(datos["nota"]):
                return "La nota debe ser un número entre 0 y 20"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for m in self.lista:
            if m.id == id_matricula:
                return m
        return None

    def buscar(self, texto):
        texto = str(texto).strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for m in self.lista:
            if texto in m.periodo.lower() or texto in m.fecha:
                encontradas.append(m)
        return encontradas

    def siguiente(self):
        mayor = 0
        for m in self.lista:
            if m.id > mayor:
                mayor = m.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        nota = float(datos.get("nota", 0.0)) if str(datos.get("nota", "")).strip() != "" else 0.0

        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos["periodo"]).strip(),
            nota
        )

        # Efecto colateral controlado: descuenta cupo en la materia asociada
        materia.ocupar_cupo()
        self.materias.guardar()

        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula {matricula.id} registrada con éxito"

    def actualizar(self, id_matricula, datos):
        """Permite actualizar nota o período; no permite alterar identidades directamente."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        if "nota" in datos:
            if not Materia.es_nota_valida(datos["nota"]):
                return False, "La nota debe estar entre 0 y 20"
            matricula.nota = float(datos["nota"])

        if "periodo" in datos:
            periodo = str(datos["periodo"]).strip()
            if periodo == "":
                return False, "El período no puede estar vacío"
            matricula.periodo = periodo

        self.guardar()
        return True, f"Matrícula {id_matricula} actualizada"

    def registrar_nota(self, id_matricula, nota):
        """Asigna o actualiza la nota de una matrícula existente."""
        if not Materia.es_nota_valida(nota):
            return False, "La nota debe ser un número entre 0 y 20"

        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota de matrícula {id_matricula} registrada: {matricula.nota:.1f} ({matricula.estado()})"

    def eliminar(self, id_matricula):
        """Retira una matrícula y restituye el cupo a la materia respectiva."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo liberado"

    def certificado(self, id_matricula):
        """Genera el certificado oficial cruzando datos con índices de acceso directo."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        estudiante = self.estudiantes.obtener(matricula.estudiante_id)
        materia = self.materias.obtener(matricula.materia_id)

        nom_est = estudiante.nombre_completo() if estudiante else "Estudiante no encontrado"
        carnet_est = estudiante.carnet if estudiante else "N/A"
        nom_mat = materia.nombre if materia else "Materia no encontrada"
        cod_mat = materia.codigo if materia else "N/A"
        cred_mat = materia.creditos if materia else 0

        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {nom_est}   ({carnet_est})\n"
        texto += f"Materia   : {nom_mat}   ({cod_mat}) · {cred_mat} créditos\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota:.1f}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO de LISTAS: {estudiante_id: [matriculas]}."""
        agrupadas = {}
        for m in self.lista:
            agrupadas.setdefault(m.estudiante_id, []).append(m)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        """Calcula la media académica de un estudiante."""
        matriculas = [m for m in self.lista if m.estudiante_id == id_estudiante]
        if not matriculas:
            return 0.0
        return round(sum(m.nota for m in matriculas) / len(matriculas), 2)

    def total_aprobadas(self):
        """Contabiliza el total de matrículas que han alcanzado la nota de aprobación."""
        return sum(1 for m in self.lista if m.esta_aprobada())
