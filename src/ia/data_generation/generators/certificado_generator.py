"""
Generador de certificados sintéticos.
"""

from ..base_generator import BaseDocumentGenerator


class CertificadoGenerator(BaseDocumentGenerator):
    """Genera certificados oficiales sintéticos."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.tipos = [
            "CERTIFICADO DE EMPRESA",
            "CERTIFICADO ACADÉMICO",
            "CERTIFICADO MÉDICO",
            "CERTIFICADO DE EMPADRONAMIENTO",
            "CERTIFICADO DE ANTECEDENTES PENALES",
            "CERTIFICADO DE TRABAJO"
        ]

    def generate_document(self) -> str:
        """Genera un certificado sintético."""

        tipo = self.random_choice(self.tipos)
        fecha = self.fake.date_between(start_date='-1y', end_date='today').strftime('%d de %B de %Y')
        lugar = self.fake.city()
        num_registro = f"{self.random_int(2020, 2025)}/{self.random_int(1, 9999):05d}"

        if "EMPRESA" in tipo or "TRABAJO" in tipo:
            persona = self.fake.name()
            dni = self.fake.ssn()
            empresa = self.fake.company()
            cif = self.generate_cif()
            cargo = self.random_choice([
                "Director de Recursos Humanos",
                "Gerente",
                "Representante Legal",
                "Administrador"
            ])
            puesto_trabajador = self.random_choice([
                "Técnico Administrativo", "Analista", "Comercial", "Contable"
            ])
            fecha_inicio = self.fake.date_between(start_date='-5y', end_date='-1y').strftime('%d/%m/%Y')
            activo = self.random_choice([True, False])

            texto = f"""{tipo}

Nº de registro: {num_registro}

{empresa}, con CIF {cif}, y domicilio social en {self.fake.address().replace(chr(10), ', ')},

CERTIFICA:

Que Don/Doña {persona}, con DNI {dni}, {'presta' if activo else 'prestó'} sus servicios en esta empresa como {puesto_trabajador} desde el día {fecha_inicio}{'.' if not activo else ' hasta la fecha actual.'}

{'El trabajador se encuentra actualmente en activo.' if activo else f'El trabajador causó baja el día {self.fake.date_between(start_date="-1y", end_date="today").strftime("%d/%m/%Y")}.'}

Durante su permanencia en la empresa ha demostrado {'profesionalidad, dedicación y compromiso' if self.random_int(1, 2) == 1 else 'responsabilidad y competencia en sus funciones'}.

Y para que conste y surta los efectos oportunos, se expide el presente certificado en {lugar}, a {fecha}.

A petición del interesado.



Fdo.: {self.fake.name()}
{cargo}
{empresa}
"""

        elif "ACADÉMICO" in tipo:
            alumno = self.fake.name()
            dni = self.fake.ssn()
            centro = f"Universidad de {self.fake.city()}"
            titulo = self.random_choice([
                "Grado en Administración y Dirección de Empresas",
                "Grado en Ingeniería Informática",
                "Grado en Derecho",
                "Máster en Finanzas",
                "Grado en Psicología"
            ])
            nota = self.random_float(6.0, 9.5, 1)

            texto = f"""{tipo}

{centro}
Registro nº: {num_registro}

CERTIFICA:

Que Don/Doña {alumno}, con DNI {dni}, ha cursado los estudios correspondientes al {titulo} en este centro universitario durante el curso académico {self.random_int(2018, 2023)}-{self.random_int(2019, 2024)}.

Nota media del expediente académico: {nota}

El interesado ha superado la totalidad de los créditos necesarios para la obtención del título correspondiente.

Y para que conste y a petición del interesado, se expide el presente certificado en {lugar}, a {fecha}.

EL SECRETARIO ACADÉMICO



Fdo.: {self.fake.name()}
"""

        else:  # Otros certificados (médico, empadronamiento, etc.)
            persona = self.fake.name()
            dni = self.fake.ssn()
            autoridad = f"{self.random_choice(['Ayuntamiento de', 'Juzgado de', 'Registro Civil de'])} {lugar}"

            texto = f"""{tipo}

{autoridad}
Expediente: {num_registro}

CERTIFICA:

Que según los datos obrantes en este {self.random_choice(['registro', 'organismo', 'departamento'])}, Don/Doña {persona}, con DNI {dni}, {self.fake.sentence()}

Esta certificación se expide a petición del interesado y para los fines que estime convenientes.

En {lugar}, a {fecha}.



EL SECRETARIO



Fdo.: {self.fake.name()}
"""

        return texto
