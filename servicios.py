"""
servicios.py
Clase abstracta Servicio y tres servicios especializados:
ReservaSala, AlquilerEquipo y AsesoriaEspecializada.

Polimorfismo: cada servicio sobrescribe calcular_costo(), describir() y
validar_parametros(). Sobrecarga: calcular_costo_total() acepta 1, 2 o 3
argumentos (horas / + impuesto / + descuento); en Python se simula con
parámetros opcionales.
"""

from abc import abstractmethod

from entidades import Entidad
from excepciones import CalculoInconsistenteError, ServicioInvalidoError


class Servicio(Entidad):
    """Clase abstracta base de todos los servicios de Software FJ."""

    _PREFIJO = "SRV"
    IVA_DEFECTO = 0.19  # impuesto por defecto (19 %)

    def __init__(self, nombre, tarifa_hora, disponible=True):
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El servicio necesita un nombre válido.")
        if isinstance(tarifa_hora, bool) or not isinstance(tarifa_hora, (int, float)) \
                or tarifa_hora <= 0:
            raise ServicioInvalidoError(
                f"Tarifa por hora inválida: {tarifa_hora!r} (debe ser un número positivo)."
            )
        self._nombre = nombre.strip()
        self._tarifa_hora = float(tarifa_hora)
        self.disponible = bool(disponible)
        super().__init__()

    # ---------- propiedades de solo lectura ----------
    @property
    def nombre(self):
        return self._nombre

    @property
    def tarifa_hora(self):
        return self._tarifa_hora

    # ---------- métodos abstractos (cada hijo los sobrescribe) ----------
    @abstractmethod
    def calcular_costo(self, horas):
        """Costo base del servicio, sin impuestos ni descuentos."""

    @abstractmethod
    def describir(self):
        """Descripción textual del servicio."""

    @abstractmethod
    def validar_parametros(self, horas):
        """Valida la duración solicitada; lanza ServicioInvalidoError si no es válida."""

    # ---------- utilidades comunes ----------
    def _validar_horas(self, horas, maximo):
        """Validación común de horas: numérico, positivo y dentro del máximo."""
        if isinstance(horas, bool) or not isinstance(horas, (int, float)):
            raise ServicioInvalidoError(f"La duración debe ser numérica, se recibió {horas!r}.")
        if horas <= 0:
            raise ServicioInvalidoError("La duración debe ser mayor que cero.")
        if horas > maximo:
            raise ServicioInvalidoError(
                f"{self.nombre}: la duración máxima es {maximo} h (se pidieron {horas} h)."
            )

    def mostrar_descripcion(self):
        return self.describir()

    def __str__(self):
        return self.describir()

    # ---------- método SOBRECARGADO ----------
    def calcular_costo_total(self, horas, impuesto=None, descuento=0.0):
        """
        Variantes de uso:
          calcular_costo_total(horas)                      -> costo + IVA por defecto
          calcular_costo_total(horas, impuesto)            -> costo + impuesto indicado
          calcular_costo_total(horas, impuesto, descuento) -> con descuento aplicado
        """
        self.validar_parametros(horas)
        if impuesto is None:
            impuesto = self.IVA_DEFECTO
        # Un porcentaje fuera de 0..1 hace el cálculo inconsistente
        if not 0 <= impuesto <= 1:
            raise CalculoInconsistenteError(f"Impuesto fuera de rango (0-1): {impuesto}.")
        if not 0 <= descuento < 1:
            raise CalculoInconsistenteError(f"Descuento fuera de rango (0-1): {descuento}.")
        base = self.calcular_costo(horas)
        total = base * (1 - descuento) * (1 + impuesto)
        if total <= 0:
            raise CalculoInconsistenteError(f"El costo calculado no es válido: {total}.")
        return round(total, 2)


class ReservaSala(Servicio):
    """Reserva de salas de reuniones por horas."""

    MAX_HORAS = 12

    def __init__(self, nombre, tarifa_hora, capacidad, disponible=True):
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioInvalidoError(f"Capacidad inválida: {capacidad!r}.")
        self._capacidad = capacidad
        super().__init__(nombre, tarifa_hora, disponible)

    def validar_parametros(self, horas):
        self._validar_horas(horas, self.MAX_HORAS)

    def calcular_costo(self, horas, proyector=False):
        # Parámetro opcional: el proyector suma un recargo por hora
        costo = self.tarifa_hora * horas
        if proyector:
            costo += 10000 * horas
        # Jornada completa (8 h o más): 10 % de descuento
        if horas >= 8:
            costo *= 0.90
        return costo

    def describir(self):
        return (f"{self.id} | Sala '{self.nombre}' | Capacidad: {self._capacidad} personas "
                f"| ${self.tarifa_hora:,.0f}/h")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos tecnológicos."""

    MAX_HORAS = 72
    SEGURO = 0.05  # 5 % de seguro sobre el alquiler

    def __init__(self, nombre, tarifa_hora, tipo_equipo, disponible=True):
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ServicioInvalidoError("El tipo de equipo es obligatorio.")
        self._tipo_equipo = tipo_equipo.strip()
        super().__init__(nombre, tarifa_hora, disponible)

    def validar_parametros(self, horas):
        self._validar_horas(horas, self.MAX_HORAS)

    def calcular_costo(self, horas):
        return self.tarifa_hora * horas * (1 + self.SEGURO)

    def describir(self):
        return (f"{self.id} | Equipo '{self.nombre}' ({self._tipo_equipo}) "
                f"| ${self.tarifa_hora:,.0f}/h + seguro {self.SEGURO:.0%}")


class AsesoriaEspecializada(Servicio):
    """Asesoría con especialistas; el nivel modifica la tarifa."""

    MAX_HORAS = 8
    NIVELES = {"junior": 1.0, "senior": 1.5}

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="junior", disponible=True):
        if nivel not in self.NIVELES:
            raise ServicioInvalidoError(
                f"Nivel '{nivel}' no válido. Opciones: {', '.join(self.NIVELES)}."
            )
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ServicioInvalidoError("La especialidad es obligatoria.")
        self._especialidad = especialidad.strip()
        self._nivel = nivel
        super().__init__(nombre, tarifa_hora, disponible)

    def validar_parametros(self, horas):
        self._validar_horas(horas, self.MAX_HORAS)

    def calcular_costo(self, horas):
        return self.tarifa_hora * horas * self.NIVELES[self._nivel]

    def describir(self):
        return (f"{self.id} | Asesoría '{self.nombre}' | {self._especialidad} "
                f"({self._nivel}) | ${self.tarifa_hora:,.0f}/h")
