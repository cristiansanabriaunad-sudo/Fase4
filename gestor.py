"""
gestor.py
GestorFJ: administra las listas internas de clientes, servicios y reservas
(sin base de datos). Toda operación pasa por _ejecutar(), que captura los
errores, los registra en el log y mantiene la aplicación estable.
"""

from entidades import Cliente
from excepciones import (ClienteInvalidoError, ErrorSoftwareFJ,
                         ParametroFaltanteError, ServicioInvalidoError)
from logger_fj import obtener_logger
from reserva import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala

logger = obtener_logger()


class GestorFJ:
    """Fachada del sistema Software FJ."""

    TIPOS_SERVICIO = {
        "sala": ReservaSala,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada,
    }

    def __init__(self):
        self._clientes = []    # listas internas en lugar de base de datos
        self._servicios = []
        self._reservas = []
        self.operaciones = 0
        self.exitosas = 0
        self.fallidas = 0

    # ------------------------------------------------------------------
    # Motor de ejecución segura: try / except / else / finally
    # ------------------------------------------------------------------
    def _ejecutar(self, descripcion, funcion, *args, **kwargs):
        """Ejecuta una operación sin permitir que un error detenga el programa."""
        self.operaciones += 1
        print(f"\n[{self.operaciones:02d}] {descripcion}")
        try:
            resultado = funcion(*args, **kwargs)
        except ErrorSoftwareFJ as e:
            # Error controlado del dominio
            self.fallidas += 1
            causa = f" | causa original: {e.__cause__}" if e.__cause__ else ""
            logger.error(f"{descripcion} -> {e}{causa}")
            print(f"     ERROR controlado: {e}")
            if e.__cause__:
                print(f"     (causa original: {e.__cause__})")
            return None
        except Exception as e:  # noqa: BLE001  (error inesperado: la app NO se cae)
            self.fallidas += 1
            logger.critical(f"{descripcion} -> error inesperado "
                            f"{type(e).__name__}: {e}", exc_info=True)
            print(f"     ERROR inesperado ({type(e).__name__}): {e}")
            return None
        else:
            # Solo si no hubo excepciones
            self.exitosas += 1
            logger.info(f"{descripcion} -> OK")
            print(f"     OK: {resultado}")
            return resultado
        finally:
            # Siempre se ejecuta
            logger.debug(f"Fin de operación: {descripcion}")

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------
    def registrar_cliente(self, nombre=None, documento=None, correo=None, telefono=None):
        return self._ejecutar(f"Registrar cliente ({nombre!r})", self._crear_cliente,
                              nombre, documento, correo, telefono)

    def crear_servicio(self, tipo, **parametros):
        return self._ejecutar(f"Crear servicio tipo '{tipo}'",
                              self._crear_servicio, tipo, parametros)

    def crear_reserva(self, cliente, servicio, horas):
        return self._ejecutar("Crear reserva", self._crear_reserva, cliente, servicio, horas)

    def confirmar_reserva(self, reserva):
        return self._ejecutar("Confirmar reserva", lambda: reserva.confirmar())

    def cancelar_reserva(self, reserva):
        return self._ejecutar("Cancelar reserva", lambda: reserva.cancelar())

    def procesar_reserva(self, reserva, impuesto=None, descuento=0.0):
        return self._ejecutar(
            f"Procesar reserva (impuesto={impuesto}, descuento={descuento})",
            lambda: reserva.procesar(impuesto, descuento))

    # ------------------------------------------------------------------
    # Lógica interna
    # ------------------------------------------------------------------
    def _crear_cliente(self, nombre, documento, correo, telefono):
        cliente = Cliente(nombre, documento, correo, telefono)
        # Regla de negocio: no se permiten documentos duplicados
        if any(c.documento == cliente.documento for c in self._clientes):
            raise ClienteInvalidoError(f"Ya existe un cliente con documento {cliente.documento}.")
        self._clientes.append(cliente)
        return cliente

    def _crear_servicio(self, tipo, parametros):
        clase = self.TIPOS_SERVICIO.get(str(tipo).lower())
        if clase is None:
            raise ServicioInvalidoError(
                f"Tipo de servicio desconocido '{tipo}'. "
                f"Opciones: {', '.join(self.TIPOS_SERVICIO)}."
            )
        try:
            servicio = clase(**parametros)
        except TypeError as e:
            # Parámetros faltantes o sobrantes -> excepción propia encadenada
            raise ParametroFaltanteError(f"Parámetros incorrectos para '{tipo}': {e}") from e
        self._servicios.append(servicio)
        return servicio

    def _crear_reserva(self, cliente, servicio, horas):
        reserva = Reserva(cliente, servicio, horas)
        self._reservas.append(reserva)
        return reserva

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    @property
    def clientes(self):
        return list(self._clientes)

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)
