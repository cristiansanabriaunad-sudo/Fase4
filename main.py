"""
main.py - Software FJ
Sistema integral de gestión de clientes, servicios y reservas (sin base de datos).

Simula 30 operaciones completas (válidas e inválidas) para demostrar que la
aplicación continúa funcionando aun cuando ocurran errores. Todos los errores y
eventos quedan registrados en logs/software_fj.log.

Ejecución:  python main.py
"""

from gestor import GestorFJ
from logger_fj import RUTA_LOG, obtener_logger


def main():
    logger = obtener_logger()
    logger.info("=== Inicio de la simulación Software FJ ===")
    fj = GestorFJ()

    print("=" * 70)
    print(" SOFTWARE FJ - Simulación de operaciones")
    print("=" * 70)

    # ---------------- CLIENTES (válidos e inválidos) ----------------
    ana = fj.registrar_cliente("ana maría gómez", "1020304050", "ana@correo.com", "3001234567")  # válido
    fj.registrar_cliente("Pedro Ruiz", "12345", "pedro@correo.com", "3007654321")                # documento inválido
    fj.registrar_cliente("Luis Pérez", "9988776655", "luis-correo.com", "3112223344")            # correo inválido
    fj.registrar_cliente("Marta Díaz", None, "marta@correo.com", "3105556677")                   # parámetro faltante
    carlos = fj.registrar_cliente("Carlos Torres", "5544332211", "carlos@correo.com", "3209998877")  # válido
    fj.registrar_cliente("Ana Duplicada", "1020304050", "otra@correo.com", "3001112233")         # duplicado

    # ---------------- SERVICIOS (correctos e incorrectos) ----------------
    sala = fj.crear_servicio("sala", nombre="Sala Ejecutiva", tarifa_hora=50000, capacidad=10)
    equipo = fj.crear_servicio("equipo", nombre="Portátil Pro", tarifa_hora=8000,
                               tipo_equipo="Laptop")
    proyector = fj.crear_servicio("equipo", nombre="Video Beam", tarifa_hora=12000,
                                  tipo_equipo="Proyector", disponible=False)
    asesoria = fj.crear_servicio("asesoria", nombre="Arquitectura de Software",
                                 tarifa_hora=90000, especialidad="Software", nivel="senior")
    fj.crear_servicio("asesoria", nombre="Asesoría Rara", tarifa_hora=80000,
                      especialidad="Datos", nivel="experto")       # nivel inválido
    fj.crear_servicio("hotel", nombre="Hotel FJ", tarifa_hora=1000)  # tipo desconocido
    fj.crear_servicio("sala", nombre="Sala Incompleta", tarifa_hora=40000)  # falta capacidad
    fj.crear_servicio("equipo", nombre="Tarifa Negativa", tarifa_hora=-5,
                      tipo_equipo="Tablet")                         # tarifa inválida

    # ---------------- RESERVAS (exitosas y fallidas) ----------------
    r1 = fj.crear_reserva(ana, sala, 4)            # válida
    r2 = fj.crear_reserva(carlos, equipo, 24)      # válida
    r3 = fj.crear_reserva(carlos, asesoria, 2)     # válida
    fj.crear_reserva(ana, sala, 20)                # duración excede el máximo (error encadenado)
    fj.crear_reserva(ana, proyector, 3)            # servicio no disponible
    fj.crear_reserva(None, sala, 2)                # cliente inválido

    # ---------------- CONFIRMAR / PROCESAR / CANCELAR ----------------
    fj.confirmar_reserva(r1)                       # OK
    fj.confirmar_reserva(r1)                       # ya confirmada -> operación no permitida
    fj.procesar_reserva(r1, 0.19, 0.10)            # OK (con impuesto y descuento)
    fj.procesar_reserva(r1)                        # ya procesada -> error
    fj.confirmar_reserva(r2)
    fj.procesar_reserva(r2, descuento=1.5)         # descuento inconsistente (error encadenado)
    fj.procesar_reserva(r2)                        # OK (solo IVA por defecto)
    fj.cancelar_reserva(r1)                        # no se puede cancelar una procesada
    fj.cancelar_reserva(r3)                        # OK
    fj.procesar_reserva(None)                      # error inesperado: la app sigue viva

    # ---------------- POLIMORFISMO ----------------
    print("\n" + "-" * 70)
    print(" Catálogo de servicios (misma llamada, distinto comportamiento)")
    print("-" * 70)
    for servicio in fj.servicios:
        try:
            print(servicio.describir())
            print(f"    4 h con IVA: ${servicio.calcular_costo_total(4):,.2f}")
        except Exception as e:  # noqa: BLE001
            print(f"    No se pudo calcular: {e}")

    print("\n" + "-" * 70)
    print(" Reservas")
    print("-" * 70)
    for reserva in fj.reservas:
        print(reserva)

    # ---------------- RESUMEN ----------------
    print("\n" + "=" * 70)
    print(f" Operaciones: {fj.operaciones} | Exitosas: {fj.exitosas} | "
          f"Fallidas controladas: {fj.fallidas}")
    print(f" La aplicación terminó SIN interrupciones. Log: {RUTA_LOG}")
    print("=" * 70)
    logger.info(f"=== Fin de la simulación: {fj.operaciones} operaciones, "
                f"{fj.exitosas} exitosas, {fj.fallidas} fallidas ===")


if __name__ == "__main__":
    main()
