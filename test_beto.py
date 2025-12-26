"""
Script de prueba para verificar la inferencia con BETO.
"""
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ia.clasificadores.beto.inferencia import ejecutar_beto


def test_clasificacion():
    """Prueba el clasificador con textos de ejemplo."""

    print("="*80)
    print("PRUEBA DE CLASIFICACIÓN CON BETO")
    print("="*80)
    print()

    # Textos de ejemplo para cada categoría
    ejemplos = {
        "Factura": """
            FACTURA Nº 2024-001
            Fecha: 15/03/2024

            Proveedor: Empresa S.L.
            CIF: B12345678

            Cliente: Juan Pérez
            NIF: 12345678A

            Concepto          Cantidad    Precio Unit.    Total
            Producto A             5         10.00 €      50.00 €
            Producto B             2         25.00 €      50.00 €

            Base Imponible:                              100.00 €
            IVA (21%):                                    21.00 €
            TOTAL A PAGAR:                               121.00 €
        """,

        "Recibo": """
            RECIBO DE PAGO

            Recibí de: María González
            La cantidad de: 500.00 euros
            En concepto de: Mensualidad de alquiler
            Correspondiente a: Marzo 2024

            Fecha: 01/03/2024

            Titular: Pedro Rodríguez
            Firma: _________________
        """,

        "CV": """
            CURRICULUM VITAE

            Ana María López García

            DATOS PERSONALES
            Teléfono: 600 123 456
            Email: ana.lopez@email.com

            FORMACIÓN ACADÉMICA
            - Licenciatura en Administración de Empresas
              Universidad Complutense de Madrid (2015-2019)
            - Máster en Dirección de Proyectos
              ESADE (2019-2020)

            EXPERIENCIA LABORAL
            Project Manager - Tech Solutions S.L.
            2020 - Presente

            IDIOMAS
            - Español: Nativo
            - Inglés: C1
            - Francés: B2

            HABILIDADES
            - Gestión de proyectos
            - Liderazgo de equipos
            - Office 365
        """,

        "Pagaré": """
            PAGARÉ
        """,

        "Contrato": """
            CONTRATO LABORAL INDEFINIDO

            En Madrid, a 1 de febrero de 2024

            REUNIDOS

            De una parte, TECH INNOVATORS S.L., con CIF B98765432,
            representada por Don Luis García Pérez.

            De otra parte, Doña Laura Sánchez Martín, con DNI 11223344A.

            CLÁUSULAS

            PRIMERA: La empresa contrata los servicios profesionales del trabajador
            como Desarrollador Senior.

            SEGUNDA: El presente contrato tiene carácter indefinido.

            TERCERA: La jornada laboral será de 40 horas semanales.

            CUARTA: El salario bruto anual será de 45.000 euros.

            Y en prueba de conformidad, ambas partes firman el presente contrato.

            Firma Empresa: _________    Firma Trabajador: _________
        """
    }

    # Probar cada ejemplo
    for tipo_esperado, texto in ejemplos.items():
        print(f"\n{'='*80}")
        print(f"Probando: {tipo_esperado}")
        print(f"{'='*80}")

        tipo, confianza, nombre, carpeta = ejecutar_beto(texto)

        print(f"[OK] Tipo clasificado:     {tipo}")
        print(f"[OK] Confianza:            {confianza:.2%}")
        print(f"[OK] Nombre sugerido:      {nombre}")
        print(f"[OK] Carpeta sugerida:     {carpeta}")

        # Verificar si la clasificación fue correcta
        if tipo.lower() == tipo_esperado.lower():
            print("[SUCCESS] CLASIFICACION CORRECTA")
        else:
            print(f"[WARNING] CLASIFICACION INCORRECTA (Esperado: {tipo_esperado})")

    print(f"\n{'='*80}")
    print("PRUEBA COMPLETADA")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_clasificacion()