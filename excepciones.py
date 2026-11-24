"""
excepciones.py
Excepciones personalizadas del sistema Software FJ.

Todas heredan de ErrorSoftwareFJ, de modo que el sistema pueda capturar
cualquier error propio con un solo "except ErrorSoftwareFJ" y, al mismo tiempo,
distinguir cada caso con un tipo específico.
"""


class ErrorSoftwareFJ(Exception):
    """Excepción base de la aplicación (incluye un código de error)."""

    codigo = "FJ-000"

    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje

    def __str__(self):
        # Formato uniforme: [CODIGO] mensaje
        return f"[{self.codigo}] {self.mensaje}"


class ClienteInvalidoError(ErrorSoftwareFJ):
    """Datos de cliente inválidos (formato, duplicados, etc.)."""
    codigo = "FJ-100"


class ParametroFaltanteError(ErrorSoftwareFJ):
    """Falta un parámetro obligatorio al crear un objeto u operación."""
    codigo = "FJ-110"


class ServicioInvalidoError(ErrorSoftwareFJ):
    """Parámetros de servicio inválidos (tarifa, horas, tipo, etc.)."""
    codigo = "FJ-200"


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio solicitado no está disponible."""
    codigo = "FJ-210"


class ReservaError(ErrorSoftwareFJ):
    """Error general durante la creación o gestión de una reserva."""
    codigo = "FJ-300"


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """Operación inválida para el estado actual (p. ej. cancelar una reserva procesada)."""
    codigo = "FJ-310"


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """El cálculo de costos produjo valores inconsistentes."""
    codigo = "FJ-400"
