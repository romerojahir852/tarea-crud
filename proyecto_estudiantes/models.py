"""Módulo de Modelos del Dominio (models.py) - Sistema Académico.

Implementa POO avanzada con:
- Herencia: ModeloBase -> Persona -> Estudiante; ModeloBase -> Materia, Matricula.
- Polimorfismo: etiqueta() implementado en cada modelo y usado en ModeloBase.__str__().
- Métodos de clase: @classmethod desde_diccionario() en ModeloBase.
- Métodos estáticos: @staticmethod es_nota_valida() y es_credito_valido() en Materia.
"""

from datetime import date


# =====================================================================
# CLASE BASE: Comportamiento e identidad compartida por todos los modelos
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos del sistema académico. Guarda el id primario."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        """Método de clase: reconstruye una instancia desde un diccionario JSON.

        Usa cls(id_registro, **datos) para que funcione en cualquier subclase.
        """
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def a_diccionario(self):
        """Serialización base a diccionario."""
        return {"id": self.id}

    def etiqueta(self):
        """POLIMORFISMO: Cada subclase define cómo presentarse."""
        return f"registro {self.id}"

    def __str__(self):
        """Presentación polimórfica que aprovecha etiqueta()."""
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona representa a cualquier individuo en el sistema
# =====================================================================
class Persona(ModeloBase):
    """Modelo intermedio para personas con datos personales básicos."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre.strip().title()
        self.apellido = apellido.strip().title()
        self.email = email.strip().lower()

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona con carnet universitario y carrera académica."""

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = str(carnet).strip().upper()
        self.carrera = str(carrera).strip().title()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera or 'sin carrera'}"


# =====================================================================
# MODELO: Materia (Equivale a Producto en Ventas)
# =====================================================================
class Materia(ModeloBase):
    """Representa una asignatura académica con cupos y reglas estáticas."""

    # ATRIBUTOS ESTÁTICOS / DE CLASE (Reglas institucionales)
    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14.0
    total_creadas = 0

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre = str(nombre).strip().title()
        self.codigo = str(codigo).strip().upper()
        self.creditos = int(creditos)
        self.cupos = int(cupos)
        Materia.total_creadas += 1

    # MÉTODOS ESTÁTICOS: Validaciones de reglas independientes de la instancia
    @staticmethod
    def es_nota_valida(valor):
        """Valida si una calificación numérica está en la escala de 0 a 20."""
        try:
            nota = float(valor)
            return 0.0 <= nota <= 20.0
        except (TypeError, ValueError):
            return False

    @staticmethod
    def es_credito_valido(valor):
        """Valida que los créditos académicos estén en el rango reglamentario 1 a 10."""
        try:
            c = int(valor)
            return 1 <= c <= 10
        except (TypeError, ValueError):
            return False

    # MÉTODOS DE INSTANCIA
    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if self.cupos > 0:
            self.cupos -= 1
            return True
        return False

    def liberar_cupo(self):
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1
            return True
        return False

    def sin_cupos(self):
        return self.cupos <= 0

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        alerta = " ⚠ sin cupos" if self.sin_cupos() else f" · cupos {self.cupos}"
        return f"{self.nombre} ({self.codigo}) · {self.creditos} créditos{alerta}"


# =====================================================================
# MODELO: Matricula (Equivale a Venta en Ventas)
# =====================================================================
class Matricula(ModeloBase):
    """Enlaza a un Estudiante con una Materia para un período académico."""

    def __init__(self, id_registro, estudiante_id, materia_id, periodo,
                 nota=0.0, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo).strip()
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        """Determina si la materia está aprobada según NOTA_APROBACION."""
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        """Estado formal calculado dinámicamente; no se persiste en el JSON."""
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · est. {self.estudiante_id} · mat. {self.materia_id} · "
                f"[{self.periodo}] · nota {self.nota:.1f} ({self.estado()})")
