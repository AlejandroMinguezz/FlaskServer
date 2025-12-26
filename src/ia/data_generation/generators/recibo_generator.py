"""
Generador de recibos sintéticos.
"""

from ..base_generator import BaseDocumentGenerator


class ReciboGenerator(BaseDocumentGenerator):
    """Genera recibos de servicios y pagos sintéticos."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.tipos_recibo = [
            ("Recibo de luz", "Compañía Eléctrica", "consumo eléctrico"),
            ("Recibo de agua", "Aguas Municipales", "consumo de agua"),
            ("Recibo de gas", "Gas Natural", "consumo de gas"),
            ("Recibo de alquiler", "Inmobiliaria", "alquiler de vivienda"),
            ("Recibo de comunidad", "Comunidad de Propietarios", "gastos de comunidad"),
            ("Recibo de teléfono", "Operador Telecomunicaciones", "servicios de telefonía"),
            ("Recibo de internet", "Proveedor Internet", "servicio de internet")
        ]

    def generate_document(self) -> str:
        """Genera un recibo sintético."""

        tipo_nombre, empresa_tipo, concepto = self.random_choice(self.tipos_recibo)
        num_recibo = f"{self.random_int(2020, 2025)}{self.random_int(100000, 999999)}"
        fecha_emision = self.fake.date_between(start_date='-1y', end_date='today').strftime('%d/%m/%Y')

        # Empresa/Entidad
        empresa = f"{empresa_tipo} {self.fake.city()}" if empresa_tipo in ["Aguas Municipales"] else self.fake.company()
        cif = self.generate_cif()

        # Titular
        titular = self.fake.name()
        direccion = self.fake.address().replace('\n', ', ')
        cuenta = f"ES{self.random_int(10, 99)} {self.random_int(1000, 9999)} {self.random_int(1000, 9999)} {self.random_int(10, 99)} {self.random_int(1000000000, 9999999999)}"

        # Periodo
        mes_anterior = self.fake.date_between(start_date='-2m', end_date='-1m')
        periodo_desde = mes_anterior.strftime('%d/%m/%Y')
        periodo_hasta = self.fake.date_between(start_date='-1m', end_date='today').strftime('%d/%m/%Y')

        # Conceptos según tipo
        if "luz" in tipo_nombre or "agua" in tipo_nombre or "gas" in tipo_nombre:
            consumo = self.random_int(50, 500)
            precio_unidad = self.random_float(0.10, 0.25, 3)
            importe_consumo = consumo * precio_unidad
            termino_fijo = self.random_float(10, 30)
            impuestos = importe_consumo * 0.05
            total = importe_consumo + termino_fijo + impuestos

            texto = f"""{tipo_nombre.upper()}

Número de recibo: {num_recibo}
Fecha de emisión: {fecha_emision}
Periodo de facturación: {periodo_desde} - {periodo_hasta}

DATOS DEL SUMINISTRADOR:
{empresa}
CIF: {cif}

DATOS DEL TITULAR:
Nombre: {titular}
Dirección de suministro: {direccion}
Cuenta de domiciliación: {cuenta}

DETALLE DEL CONSUMO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Consumo periodo: {consumo} kWh
Precio por unidad: {self.format_currency(precio_unidad)}/kWh
Importe consumo: {self.format_currency(importe_consumo):>30}

Término fijo: {self.format_currency(termino_fijo):>30}
Impuestos (5%): {self.format_currency(impuestos):>30}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL A PAGAR: {self.format_currency(total):>30}

Cargo en cuenta: {fecha_emision}
Forma de pago: Domiciliación bancaria
"""

        else:  # Alquiler, comunidad, servicios
            importe = self.random_float(300, 1500)

            texto = f"""{tipo_nombre.upper()}

Número de recibo: {num_recibo}
Fecha: {fecha_emision}
Periodo: {periodo_desde} - {periodo_hasta}

EMISOR:
{empresa}
CIF: {cif}

PAGADOR:
{titular}
Dirección: {direccion}

CONCEPTO: {concepto.capitalize()}

IMPORTE: {self.format_currency(importe)}

Forma de pago: Domiciliación bancaria
Cuenta: {cuenta}

Recibí conforme el importe arriba indicado.

Firma: ___________________

"""

        return texto
