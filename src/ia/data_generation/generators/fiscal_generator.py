"""
Generador de documentos fiscales sintéticos.
"""

from ..base_generator import BaseDocumentGenerator


class FiscalGenerator(BaseDocumentGenerator):
    """Genera declaraciones fiscales sintéticas."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.modelos = [
            ("Modelo 100", "Declaración de la Renta IRPF"),
            ("Modelo 130", "Pago fraccionado IRPF - Autónomos"),
            ("Modelo 303", "IVA Trimestral"),
            ("Modelo 390", "Resumen anual IVA"),
            ("Modelo 190", "Retenciones e ingresos a cuenta")
        ]

    def generate_document(self) -> str:
        """Genera un documento fiscal sintético."""

        modelo_num, modelo_desc = self.random_choice(self.modelos)
        ejercicio = self.random_int(2020, 2024)
        fecha = self.fake.date_between(start_date='-1y', end_date='today').strftime('%d/%m/%Y')

        # Contribuyente
        if self.random_int(1, 3) == 1:
            contribuyente = self.fake.company()
            nif = self.generate_cif()
            tipo = "Persona Jurídica"
        else:
            contribuyente = self.fake.name()
            nif = self.fake.ssn()
            tipo = "Persona Física"

        direccion = self.fake.address().replace('\n', ', ')

        texto = f"""AGENCIA TRIBUTARIA
{modelo_num} - {modelo_desc}

Ejercicio: {ejercicio}
Fecha de presentación: {fecha}

DATOS DEL CONTRIBUYENTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nombre/Razón social: {contribuyente}
NIF/CIF: {nif}
Tipo: {tipo}
Domicilio fiscal: {direccion}

"""

        if "IRPF" in modelo_desc:
            # Rendimientos
            rendimientos_trabajo = self.random_float(15000, 45000)
            rendimientos_capital = self.random_float(0, 5000)
            rendimientos_actividades = self.random_float(0, 30000)

            base_general = rendimientos_trabajo + rendimientos_capital
            base_ahorro = self.random_float(0, 10000)

            # Deducciones
            deduccion_vivienda = self.random_float(0, 5000)
            otras_deducciones = self.random_float(0, 2000)

            # Cuotas
            cuota_integra = base_general * 0.20 + base_ahorro * 0.19  # Simplificado
            deducciones_total = deduccion_vivienda + otras_deducciones
            cuota_liquida = max(0, cuota_integra - deducciones_total)

            # Retenciones
            retenciones = self.random_float(cuota_liquida * 0.7, cuota_liquida * 1.1)

            resultado = cuota_liquida - retenciones

            texto += f"""LIQUIDACIÓN DEL IMPUESTO:

1. RENDIMIENTOS:
   Rendimientos del trabajo: {self.format_currency(rendimientos_trabajo):>25}
   Rendimientos del capital: {self.format_currency(rendimientos_capital):>25}
   Actividades económicas: {self.format_currency(rendimientos_actividades):>25}

2. BASE IMPONIBLE:
   Base imponible general: {self.format_currency(base_general):>25}
   Base imponible del ahorro: {self.format_currency(base_ahorro):>25}

3. CUOTA ÍNTEGRA: {self.format_currency(cuota_integra):>30}

4. DEDUCCIONES:
   Deducción por vivienda: {self.format_currency(deduccion_vivienda):>25}
   Otras deducciones: {self.format_currency(otras_deducciones):>25}
   Total deducciones: {self.format_currency(deducciones_total):>25}

5. CUOTA LÍQUIDA: {self.format_currency(cuota_liquida):>30}

6. RETENCIONES Y PAGOS A CUENTA:
   Retenciones trabajo: {self.format_currency(retenciones):>25}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESULTADO: {'A DEVOLVER' if resultado < 0 else 'A INGRESAR'}: {self.format_currency(abs(resultado)):>20}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        elif "IVA" in modelo_desc:
            trimestre = self.random_choice(["1T", "2T", "3T", "4T"])

            # IVA devengado
            base_21 = self.random_float(10000, 50000)
            cuota_21 = base_21 * 0.21
            base_10 = self.random_float(0, 20000)
            cuota_10 = base_10 * 0.10

            iva_devengado = cuota_21 + cuota_10

            # IVA soportado
            base_sop_21 = self.random_float(5000, 30000)
            cuota_sop_21 = base_sop_21 * 0.21
            base_sop_10 = self.random_float(0, 10000)
            cuota_sop_10 = base_sop_10 * 0.10

            iva_soportado = cuota_sop_21 + cuota_sop_10

            resultado_iva = iva_devengado - iva_soportado

            texto += f"""AUTOLIQUIDACIÓN DEL IVA
Periodo: {trimestre}/{ejercicio}

I. IVA DEVENGADO:
   Operaciones al 21%
   Base imponible: {self.format_currency(base_21):>30}
   Cuota IVA: {self.format_currency(cuota_21):>30}

   Operaciones al 10%
   Base imponible: {self.format_currency(base_10):>30}
   Cuota IVA: {self.format_currency(cuota_10):>30}

   TOTAL IVA DEVENGADO: {self.format_currency(iva_devengado):>30}

II. IVA SOPORTADO DEDUCIBLE:
   Operaciones al 21%
   Base imponible: {self.format_currency(base_sop_21):>30}
   Cuota IVA: {self.format_currency(cuota_sop_21):>30}

   Operaciones al 10%
   Base imponible: {self.format_currency(base_sop_10):>30}
   Cuota IVA: {self.format_currency(cuota_sop_10):>30}

   TOTAL IVA SOPORTADO: {self.format_currency(iva_soportado):>30}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESULTADO: {'A COMPENSAR' if resultado_iva < 0 else 'A INGRESAR'}: {self.format_currency(abs(resultado_iva)):>20}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        texto += f"""
Lugar de presentación: {self.fake.city()}
Fecha: {fecha}

Firma del contribuyente:



___________________________
"""

        return texto
