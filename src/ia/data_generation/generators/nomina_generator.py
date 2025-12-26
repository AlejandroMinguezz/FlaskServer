"""
Generador de nóminas sintéticas.
"""

from ..base_generator import BaseDocumentGenerator


class NominaGenerator(BaseDocumentGenerator):
    """Genera nóminas de trabajadores sintéticas."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.categorias = [
            "Oficial Administrativo",
            "Técnico Superior",
            "Analista Programador",
            "Auxiliar Administrativo",
            "Jefe de Departamento",
            "Comercial",
            "Contable",
            "Operario",
            "Encargado",
            "Director"
        ]

        self.meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

    def generate_document(self) -> str:
        """Genera una nómina sintética."""

        # Datos del trabajador
        nombre = self.fake.name()
        dni = self.fake.ssn()
        categoria = self.random_choice(self.categorias)
        mes = self.random_choice(self.meses)
        año = self.random_int(2020, 2025)

        # Datos de la empresa
        empresa = self.fake.company()
        cif_empresa = self.generate_cif()

        # Devengos
        salario_base = self.random_float(1000, 3000)
        complemento_destino = self.random_float(100, 500)
        complemento_especifico = self.random_float(50, 300)
        paga_extra = self.random_float(0, salario_base / 12) if self.random_int(1, 3) == 1 else 0
        antigüedad = self.random_float(0, salario_base * 0.1)

        total_devengos = salario_base + complemento_destino + complemento_especifico + paga_extra + antigüedad

        # Deducciones
        irpf_percent = self.random_choice([15, 18, 21, 24])
        ss_percent = self.random_float(6.0, 6.5, 1)

        contingencias_comunes = total_devengos * 0.047
        desempleo = total_devengos * 0.0155
        formacion = total_devengos * 0.001
        total_ss = contingencias_comunes + desempleo + formacion

        irpf = total_devengos * (irpf_percent / 100)

        total_deducciones = total_ss + irpf

        # Líquido
        liquido = total_devengos - total_deducciones

        # Construir nómina
        texto = f"""NÓMINA DE {mes.upper()} DE {año}

DATOS DE LA EMPRESA:
{empresa}
CIF: {cif_empresa}

DATOS DEL TRABAJADOR:
Nombre: {nombre}
DNI: {dni}
Categoría Profesional: {categoria}
Grupo de Cotización: {self.random_int(1, 11)}

DEVENGOS:
---------------------------------------------------------------------------
Salario base                                    {self.format_currency(salario_base):>20}
Complemento de destino                          {self.format_currency(complemento_destino):>20}
Complemento específico                          {self.format_currency(complemento_especifico):>20}
"""

        if antigüedad > 0:
            texto += f"Antigüedad                                      {self.format_currency(antigüedad):>20}\n"

        if paga_extra > 0:
            texto += f"Prorrata paga extra                             {self.format_currency(paga_extra):>20}\n"

        texto += f"""---------------------------------------------------------------------------
TOTAL DEVENGOS:                                 {self.format_currency(total_devengos):>20}

DEDUCCIONES:
---------------------------------------------------------------------------
Contingencias comunes ({ss_percent:.2f}%)                  {self.format_currency(contingencias_comunes):>20}
Desempleo                                       {self.format_currency(desempleo):>20}
Formación profesional                           {self.format_currency(formacion):>20}
TOTAL SEGURIDAD SOCIAL:                         {self.format_currency(total_ss):>20}

IRPF ({irpf_percent}%)                                         {self.format_currency(irpf):>20}
---------------------------------------------------------------------------
TOTAL DEDUCCIONES:                              {self.format_currency(total_deducciones):>20}

===========================================================================
LÍQUIDO A PERCIBIR:                             {self.format_currency(liquido):>20}
===========================================================================

Firma del trabajador:                           Sello de la empresa:



"""

        return texto
