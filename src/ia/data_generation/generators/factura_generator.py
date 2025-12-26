"""
Generador de facturas sintéticas.
"""

from ..base_generator import BaseDocumentGenerator


class FacturaGenerator(BaseDocumentGenerator):
    """Genera facturas comerciales sintéticas."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.conceptos = [
            "Servicio de consultoría",
            "Desarrollo de software",
            "Mantenimiento web",
            "Diseño gráfico",
            "Asesoramiento técnico",
            "Formación presencial",
            "Licencia de software",
            "Hosting y dominio",
            "Soporte técnico",
            "Auditoría informática",
            "Material de oficina",
            "Equipamiento informático",
            "Servicios profesionales",
            "Redacción de contenidos",
            "Marketing digital"
        ]

        self.formas_pago = [
            "Transferencia bancaria",
            "Domiciliación bancaria",
            "Tarjeta de crédito",
            "Efectivo",
            "Cheque"
        ]

    def generate_document(self) -> str:
        """Genera una factura sintética."""

        # Datos básicos
        num_factura = f"{self.random_int(2020, 2025)}/{self.random_int(1, 9999):04d}"
        fecha = self.fake.date_between(start_date='-2y', end_date='today').strftime('%d/%m/%Y')

        # Proveedor
        empresa_prov = self.fake.company()
        cif_prov = self.generate_cif()
        dir_prov = self.fake.address().replace('\n', ', ')
        tel_prov = self.generate_phone()

        # Cliente
        empresa_cliente = self.fake.company()
        cif_cliente = self.generate_cif()
        dir_cliente = self.fake.address().replace('\n', ', ')

        # Líneas de factura (1-5 conceptos)
        num_lineas = self.random_int(1, 5)
        lineas = []
        subtotal = 0

        for i in range(num_lineas):
            concepto = self.random_choice(self.conceptos)
            cantidad = self.random_int(1, 10)
            precio_unit = self.random_float(50, 500)
            total_linea = cantidad * precio_unit
            subtotal += total_linea

            lineas.append({
                'concepto': concepto,
                'cantidad': cantidad,
                'precio': precio_unit,
                'total': total_linea
            })

        # Cálculos
        iva_percent = self.random_choice([21, 10, 4])  # IVA en España
        base_imponible = subtotal
        iva_importe = base_imponible * (iva_percent / 100)
        total = base_imponible + iva_importe

        # Forma de pago
        forma_pago = self.random_choice(self.formas_pago)

        # Construir factura
        texto = f"""FACTURA N.º {num_factura}

Fecha de emisión: {fecha}

DATOS DEL PROVEEDOR:
{empresa_prov}
CIF: {cif_prov}
Dirección: {dir_prov}
Teléfono: {tel_prov}

DATOS DEL CLIENTE:
{empresa_cliente}
NIF/CIF: {cif_cliente}
Dirección: {dir_cliente}

DETALLE DE LA FACTURA:

"""

        # Añadir líneas
        texto += "CONCEPTO                          CANTIDAD    PRECIO UNIT.    TOTAL\n"
        texto += "-" * 70 + "\n"
        for linea in lineas:
            texto += f"{linea['concepto']:<30}  {linea['cantidad']:>4}    {self.format_currency(linea['precio']):>12}  {self.format_currency(linea['total']):>12}\n"

        texto += "-" * 70 + "\n"
        texto += f"\nBase imponible: {self.format_currency(base_imponible):>20}\n"
        texto += f"IVA ({iva_percent}%): {self.format_currency(iva_importe):>20}\n"
        texto += f"\nTOTAL A PAGAR: {self.format_currency(total):>20}\n"
        texto += f"\nForma de pago: {forma_pago}\n"

        # Añadir variaciones opcionales
        if self.random_int(1, 3) == 1:
            texto += f"\nObservaciones: {self.fake.sentence()}\n"

        return texto
