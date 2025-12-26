"""
Generador de presupuestos sintéticos.
"""

from ..base_generator import BaseDocumentGenerator


class PresupuestoGenerator(BaseDocumentGenerator):
    """Genera presupuestos comerciales sintéticos."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.servicios = [
            "Instalación eléctrica",
            "Reforma integral",
            "Pintura y decoración",
            "Desarrollo web",
            "Diseño de interiores",
            "Mantenimiento informático",
            "Asesoría legal",
            "Auditoría contable",
            "Servicio de limpieza",
            "Consultoría empresarial",
            "Traducción de documentos",
            "Formación especializada"
        ]

    def generate_document(self) -> str:
        """Genera un presupuesto sintético."""

        num_presupuesto = f"PPTO-{self.random_int(2020, 2025)}-{self.random_int(1, 9999):04d}"
        fecha = self.fake.date_between(start_date='-1y', end_date='today').strftime('%d/%m/%Y')
        validez = self.random_choice([15, 30, 60, 90])

        # Empresa que emite
        empresa = self.fake.company()
        cif = self.generate_cif()
        direccion = self.fake.address().replace('\n', ', ')
        telefono = self.generate_phone()
        email = self.fake.company_email()

        # Cliente
        cliente = self.fake.name() if self.random_int(1, 2) == 1 else self.fake.company()

        # Partidas (2-6)
        num_partidas = self.random_int(2, 6)
        partidas = []
        subtotal = 0

        for i in range(num_partidas):
            servicio = self.random_choice(self.servicios)
            cantidad = self.random_int(1, 10)
            precio = self.random_float(100, 2000)
            total_partida = cantidad * precio
            subtotal += total_partida

            partidas.append({
                'servicio': servicio,
                'cantidad': cantidad,
                'precio': precio,
                'total': total_partida
            })

        # Cálculos
        iva = subtotal * 0.21
        total = subtotal + iva

        texto = f"""PRESUPUESTO

Número de presupuesto: {num_presupuesto}
Fecha de emisión: {fecha}
Validez: {validez} días

DE:
{empresa}
CIF: {cif}
{direccion}
Teléfono: {telefono}
Email: {email}

PARA:
{cliente}

DESCRIPCIÓN DE LOS TRABAJOS:

"""

        for i, p in enumerate(partidas, 1):
            texto += f"{i}. {p['servicio']}\n"
            texto += f"   Cantidad: {p['cantidad']} | Precio unitario: {self.format_currency(p['precio'])} | Total: {self.format_currency(p['total'])}\n\n"

        texto += "-" * 70 + "\n"
        texto += f"Base imponible: {self.format_currency(subtotal):>30}\n"
        texto += f"IVA (21%): {self.format_currency(iva):>30}\n"
        texto += f"TOTAL PRESUPUESTO: {self.format_currency(total):>30}\n"
        texto += "-" * 70 + "\n\n"

        texto += f"""CONDICIONES:

- Presupuesto válido durante {validez} días desde la fecha de emisión.
- Forma de pago: {self.random_choice(['50% al inicio y 50% a la entrega', 'Pago único a la entrega', 'Pago contra factura'])}.
- Plazo de ejecución: {self.random_choice([7, 15, 30, 45])} días hábiles.
- Este presupuesto no incluye IVA de materiales adicionales no especificados.

Para aceptar este presupuesto, por favor firme y devuelva una copia.

Atentamente,

{empresa}
"""

        return texto
