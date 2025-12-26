"""
Generador de contratos sintéticos.
"""

from ..base_generator import BaseDocumentGenerator


class ContratoGenerator(BaseDocumentGenerator):
    """Genera contratos laborales y de servicios sintéticos."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.tipos_contrato = [
            ("CONTRATO DE TRABAJO", "laboral"),
            ("CONTRATO DE ARRENDAMIENTO", "arrendamiento"),
            ("CONTRATO DE PRESTACIÓN DE SERVICIOS", "servicios"),
            ("CONTRATO INDEFINIDO", "laboral"),
            ("CONTRATO TEMPORAL", "laboral")
        ]

        self.jornadas = ["completa", "parcial", "intensiva"]

    def generate_document(self) -> str:
        """Genera un contrato sintético."""

        tipo_titulo, tipo_categoria = self.random_choice(self.tipos_contrato)
        fecha = self.fake.date_between(start_date='-2y', end_date='today').strftime('%d de %B de %Y')
        lugar = self.fake.city()

        # Partes contratantes
        if tipo_categoria == "laboral":
            parte_a = self.fake.company()
            cif_a = self.generate_cif()
            parte_b = self.fake.name()
            dni_b = self.fake.ssn()

            salario = self.random_float(18000, 45000)
            jornada = self.random_choice(self.jornadas)
            puesto = self.random_choice([
                "Técnico Administrativo", "Analista", "Comercial",
                "Desarrollador", "Contable", "Gestor"
            ])

            texto = f"""{tipo_titulo}

En {lugar}, a {fecha}

REUNIDOS

DE UNA PARTE, {parte_a}, con CIF {cif_a}, en adelante denominada "LA EMPRESA".

Y DE OTRA PARTE, {parte_b}, con DNI {dni_b}, en adelante denominado "EL TRABAJADOR".

EXPONEN

Que ambas partes se reconocen mutuamente capacidad legal suficiente para formalizar el presente contrato de trabajo, y al efecto

ACUERDAN

Las siguientes cláusulas:

PRIMERA.- Objeto del contrato
LA EMPRESA contrata a EL TRABAJADOR para prestar sus servicios profesionales como {puesto}.

SEGUNDA.- Duración
El presente contrato tiene carácter {self.random_choice(['indefinido', 'temporal'])}, iniciándose en la fecha de firma del presente documento.

TERCERA.- Jornada laboral
La jornada de trabajo será de tipo {jornada}, con arreglo al calendario laboral vigente.

CUARTA.- Retribución
El salario bruto anual será de {self.format_currency(salario)}, a abonar en 14 pagas.

QUINTA.- Periodo de prueba
Se establece un periodo de prueba de {self.random_choice([1, 2, 3])} meses.

SEXTA.- Régimen de Seguridad Social
EL TRABAJADOR quedará afiliado al Régimen General de la Seguridad Social.

SÉPTIMA.- Legislación aplicable
El presente contrato se regirá por lo dispuesto en el Estatuto de los Trabajadores y demás normas concordantes.

Y en prueba de conformidad, firman el presente contrato en el lugar y fecha indicados.

LA EMPRESA                                    EL TRABAJADOR



Fdo.: ___________________                   Fdo.: ___________________
"""

        else:  # Otros tipos de contrato
            parte_a = self.fake.company()
            cif_a = self.generate_cif()
            parte_b = self.fake.company() if tipo_categoria == "servicios" else self.fake.name()
            cif_b = self.generate_cif() if tipo_categoria == "servicios" else self.fake.ssn()

            precio = self.random_float(5000, 50000)

            texto = f"""{tipo_titulo}

En {lugar}, a {fecha}

REUNIDOS

DE UNA PARTE, {parte_a}, con CIF {cif_a}, en adelante "LA PARTE CONTRATANTE".

Y DE OTRA PARTE, {parte_b}, con {'CIF' if tipo_categoria == 'servicios' else 'DNI'} {cif_b}, en adelante "LA PARTE CONTRATADA".

EXPONEN

Que ambas partes acuerdan celebrar el presente contrato de {tipo_categoria}, que se regirá por las siguientes

CLÁUSULAS

PRIMERA.- Objeto del contrato
{self.fake.paragraph(nb_sentences=2)}

SEGUNDA.- Obligaciones de las partes
LA PARTE CONTRATADA se compromete a {self.fake.sentence()}
LA PARTE CONTRATANTE se compromete a {self.fake.sentence()}

TERCERA.- Precio
El precio total del contrato asciende a {self.format_currency(precio)}.

CUARTA.- Duración
El presente contrato tendrá una duración de {self.random_int(6, 36)} meses, pudiendo prorrogarse previo acuerdo de las partes.

QUINTA.- Resolución
Ambas partes podrán resolver el contrato mediante comunicación escrita con {self.random_choice([15, 30, 60])} días de antelación.

SEXTA.- Legislación aplicable
El presente contrato se rige por la legislación española vigente.

SÉPTIMA.- Fuero
Para cualquier controversia derivada del presente contrato, las partes se someten a los juzgados y tribunales de {self.fake.city()}.

Y en prueba de conformidad, las partes firman el presente contrato.

LA PARTE CONTRATANTE                          LA PARTE CONTRATADA



Fdo.: ___________________                   Fdo.: ___________________
"""

        return texto
