"""
entidades.py
Clase abstracta Entidad y clase Cliente (encapsulación + validaciones robustas).
"""

import re
from abc import ABC, abstractmethod

from excepciones import ClienteInvalidoError, ParametroFaltanteError


class Entidad(ABC):
    """Clase abstracta que representa cualquier entidad general del sistema."""

    _PREFIJO = "ENT"
    _contadores = {}  # contador de identificadores por prefijo

    def __init__(self):
        # Genera un identificador legible, por ejemplo CLI-001
        n = Entidad._contadores.get(self._PREFIJO, 0) + 1
        Entidad._contadores[self._PREFIJO] = n
        self._id = f"{self._PREFIJO}-{n:03d}"

    @property
    def id(self):
        """Identificador de solo lectura."""
        return self._id

    @abstractmethod
    def mostrar_descripcion(self):
        """Cada entidad debe describirse a sí misma (polimorfismo)."""


class Cliente(Entidad):
    """Cliente de Software FJ. Los datos personales son atributos privados."""

    _PREFIJO = "CLI"
    _PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
    _PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$")

    def __init__(self, nombre=None, documento=None, correo=None, telefono=None):
        # 1) Parámetros faltantes: se valida ANTES de generar el id,
        #    para no "gastar" identificadores en objetos que fallan.
        datos = {"nombre": nombre, "documento": documento,
                 "correo": correo, "telefono": telefono}
        faltantes = [k for k, v in datos.items() if v is None or str(v).strip() == ""]
        if faltantes:
            raise ParametroFaltanteError(
                f"Faltan datos obligatorios del cliente: {', '.join(faltantes)}."
            )
        # 2) Cada asignación pasa por su setter, que valida el formato
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        super().__init__()

    # ---------- nombre ----------
    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = str(valor).strip()
        if len(valor) < 3 or not self._PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(
                f"Nombre inválido '{valor}': solo letras y mínimo 3 caracteres."
            )
        self.__nombre = valor.title()

    # ---------- documento ----------
    @property
    def documento(self):
        return self.__documento

    @documento.setter
    def documento(self, valor):
        valor = str(valor).strip()
        if not valor.isdigit() or not 6 <= len(valor) <= 12:
            raise ClienteInvalidoError(
                f"Documento inválido '{valor}': debe tener entre 6 y 12 dígitos."
            )
        self.__documento = valor

    # ---------- correo ----------
    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        valor = str(valor).strip().lower()
        if not self._PATRON_CORREO.match(valor):
            raise ClienteInvalidoError(f"Correo inválido '{valor}'.")
        self.__correo = valor

    # ---------- teléfono ----------
    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = str(valor).strip()
        if not valor.isdigit() or not 7 <= len(valor) <= 10:
            raise ClienteInvalidoError(
                f"Teléfono inválido '{valor}': debe tener entre 7 y 10 dígitos."
            )
        self.__telefono = valor

    def mostrar_descripcion(self):
        # El documento se muestra parcialmente enmascarado (privacidad)
        oculto = "*" * (len(self.documento) - 3) + self.documento[-3:]
        return f"{self.id} | {self.nombre} | Doc: {oculto} | {self.correo}"

    def __str__(self):
        return self.mostrar_descripcion()
