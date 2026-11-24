"""
logger_fj.py
Configuración del archivo de logs. Es el ÚNICO uso de archivos del sistema
(el enunciado prohíbe bases de datos; solo se permiten archivos para eventos y errores).
"""

import logging
import os

# El log se guarda en la carpeta "logs" junto a este archivo
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "software_fj.log")


def obtener_logger():
    """Devuelve el logger único de la aplicación (se configura solo la primera vez)."""
    logger = logging.getLogger("SoftwareFJ")
    if not logger.handlers:
        os.makedirs(os.path.dirname(RUTA_LOG), exist_ok=True)
        logger.setLevel(logging.DEBUG)
        manejador = logging.FileHandler(RUTA_LOG, encoding="utf-8")
        manejador.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
        )
        logger.addHandler(manejador)
        logger.propagate = False  # evita duplicar mensajes en consola
    return logger
