"""
reserva.py
Clase Reserva: integra cliente, servicio, duración y estado.
Implementa confirmar(), cancelar() y procesar() con manejo de excepciones
(try/except/else/finally y encadenamiento con "raise ... from ...").
"""

from entidades import Cliente, Entidad
from excepciones import (CalculoInconsistenteError, OperacionNoPermitidaError,
                         ReservaError, ServicioInvalidoError,
                         ServicioNoDisponibleError)
from logger_fj import obtener_logger
from servicios import Servicio

logger = obtener_logger()


class Reserva(Entidad):
    """Reserva de un servicio por parte de un cliente."""

    _PREFIJO = "RES"
    # Estados posibles: PENDIENTE -> CONFIRMADA -> PROCESADA  (o CANCELADA)

    def __init__(self, cliente, servicio, horas):
        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un servicio válido.")
        # Encadenamiento: el error original (ServicioInvalidoError) queda como causa
        try:
            servicio.validar_parametros(horas)
        except ServicioInvalidoError as e:
            raise ReservaError(f"No se pudo crear la reserva: {e.mensaje}") from e
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")
        self._cliente = cliente
        self._servicio = servicio
        self._horas = horas
        self._estado = "PENDIENTE"
        self._costo = None
        super().__init__()

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    def confirmar(self):
        """PENDIENTE -> CONFIRMADA."""
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva en estado {self._estado}."
            )
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._servicio.nombre}' dejó de estar disponible."
            )
        self._estado = "CONFIRMADA"
        return self

    def cancelar(self):
        """Cancela una reserva que aún no ha sido procesada."""
        if self._estado in ("CANCELADA", "PROCESADA"):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva en estado {self._estado}."
            )
        self._estado = "CANCELADA"
        return self

    def procesar(self, impuesto=None, descuento=0.0):
        """CONFIRMADA -> PROCESADA, calculando el costo final (método sobrecargado)."""
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas CONFIRMADAS (estado actual: {self._estado})."
            )
        try:
            costo = self._servicio.calcular_costo_total(self._horas, impuesto, descuento)
        except CalculoInconsistenteError as e:
            # Encadenamiento de excepciones: conserva la causa original
            raise ReservaError(f"No se pudo procesar la reserva {self.id}: {e.mensaje}") from e
        else:
            # Se ejecuta SOLO si el cálculo no falló
            self._costo = costo
            self._estado = "PROCESADA"
            return costo
        finally:
            # Se ejecuta siempre, haya o no error
            logger.debug(f"Intento de procesar {self.id} finalizado (estado: {self._estado}).")

    def mostrar_descripcion(self):
        costo = f"${self._costo:,.2f}" if self._costo is not None else "pendiente"
        return (f"{self.id} | {self._cliente.nombre} -> {self._servicio.nombre} "
                f"| {self._horas} h | {self._estado} | costo: {costo}")

    def __str__(self):
        return self.mostrar_descripcion()
