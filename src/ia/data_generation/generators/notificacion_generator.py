"""
Generador de notificaciones administrativas sintéticas.
"""

from ..base_generator import BaseDocumentGenerator


class NotificacionGenerator(BaseDocumentGenerator):
    """Genera notificaciones de organismos públicos sintéticas."""

    def __init__(self, locale='es_ES', seed=None):
        super().__init__(locale, seed)

        self.organismos = [
            "Agencia Tributaria",
            "Seguridad Social",
            "Ayuntamiento",
            "Juzgado de lo Social",
            "Tesorería General de la Seguridad Social",
            "Consejería de Hacienda",
            "Servicio Público de Empleo"
        ]

        self.tipos_notificacion = [
            "NOTIFICACIÓN DE RESOLUCIÓN",
            "REQUERIMIENTO DE DOCUMENTACIÓN",
            "APERTURA DE PROCEDIMIENTO SANCIONADOR",
            "NOTIFICACIÓN DE LIQUIDACIÓN",
            "COMUNICACIÓN ADMINISTRATIVA",
            "CITACIÓN COMPARECENCIA"
        ]

    def generate_document(self) -> str:
        """Genera una notificación administrativa sintética."""

        organismo = self.random_choice(self.organismos)
        tipo = self.random_choice(self.tipos_notificacion)
        expediente = f"EXP/{self.random_int(2020, 2025)}/{self.random_int(10000, 99999)}"
        fecha = self.fake.date_between(start_date='-6m', end_date='today').strftime('%d de %B de %Y')
        lugar = self.fake.city()

        # Destinatario
        destinatario = self.fake.name() if self.random_int(1, 2) == 1 else self.fake.company()
        nif = self.fake.ssn() if ' ' in destinatario else self.generate_cif()
        direccion = self.fake.address().replace('\n', ', ')

        texto = f"""{organismo.upper()}
{lugar}

{tipo}

Expediente: {expediente}
Fecha: {fecha}

DESTINATARIO:
{destinatario}
NIF/CIF: {nif}
Domicilio: {direccion}

"""

        if "REQUERIMIENTO" in tipo:
            plazo = self.random_choice([10, 15, 20, 30])
            texto += f"""Por medio de la presente se le REQUIERE para que, en el plazo de {plazo} DÍAS HÁBILES contados desde el día siguiente a la recepción de esta notificación, presente la siguiente documentación:

1. {self.fake.sentence()}
2. {self.fake.sentence()}
3. {self.fake.sentence()}

La no aportación de la documentación requerida en el plazo señalado podrá dar lugar a la paralización del procedimiento y, en su caso, al archivo de las actuaciones.

RECURSOS:

Contra el presente acto, que no pone fin a la vía administrativa, podrá interponer RECURSO DE ALZADA ante {self.random_choice(['el Director General', 'el Delegado Provincial', 'el Secretario General'])} en el plazo de UN MES contado desde el día siguiente a su notificación.
"""

        elif "SANCIONADOR" in tipo:
            plazo_alegaciones = self.random_choice([10, 15])
            importe = self.random_float(300, 3000)

            texto += f"""Se le comunica la APERTURA DE PROCEDIMIENTO SANCIONADOR en base a los siguientes:

HECHOS:

{self.fake.paragraph(nb_sentences=3)}

Los hechos descritos podrían ser constitutivos de infracción {self.random_choice(['leve', 'grave'])} según lo dispuesto en la normativa vigente.

SANCIÓN PROPUESTA: {self.format_currency(importe)}

TRÁMITE DE ALEGACIONES:

Dispone de un plazo de {plazo_alegaciones} DÍAS HÁBILES para formular alegaciones y presentar los documentos e informaciones que estime pertinentes.

De no formularse alegaciones en el plazo indicado, la presente propuesta de resolución podrá ser elevada a definitiva.

INSTRUCTOR DEL EXPEDIENTE:
{self.fake.name()}
"""

        elif "LIQUIDACIÓN" in tipo:
            importe = self.random_float(500, 5000)
            plazo_pago = self.random_choice([10, 15, 20])

            texto += f"""Se procede a notificar la siguiente LIQUIDACIÓN:

CONCEPTO: {self.random_choice(['Impuesto sobre Bienes Inmuebles', 'Tasa por licencia de apertura', 'Cuota de Seguridad Social', 'Impuesto de Actividades Económicas'])}

PERIODO: {self.random_choice(['Ejercicio', 'Trimestre', 'Mes'])} {self.random_int(1, 12)}/{self.random_int(2020, 2024)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Base imponible: {self.format_currency(importe * 0.8):>30}
Recargos e intereses: {self.format_currency(importe * 0.2):>30}

TOTAL A INGRESAR: {self.format_currency(importe):>30}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PLAZO DE INGRESO: {plazo_pago} días hábiles desde la recepción de esta notificación.

En caso de disconformidad, podrá interponer RECURSO DE REPOSICIÓN en el plazo de UN MES.
"""

        else:  # RESOLUCIÓN o COMUNICACIÓN
            texto += f"""Por medio de la presente se le comunica que, con fecha {fecha}, se ha dictado la siguiente RESOLUCIÓN:

{self.fake.paragraph(nb_sentences=4)}

Por todo ello, SE RESUELVE:

PRIMERO.- {self.fake.sentence()}

SEGUNDO.- {self.fake.sentence()}

TERCERO.- Contra la presente resolución, que {'pone fin' if self.random_int(1, 2) == 1 else 'no pone fin'} a la vía administrativa, cabe interponer los siguientes recursos:

- RECURSO {'CONTENCIOSO-ADMINISTRATIVO' if self.random_int(1, 2) == 1 else 'DE ALZADA'} en el plazo de {'DOS MESES' if self.random_int(1, 2) == 1 else 'UN MES'} desde la notificación.
"""

        texto += f"""

En {lugar}, a {fecha}



EL {self.random_choice(['DIRECTOR', 'SECRETARIO', 'JEFE DE SERVICIO'])}



Fdo.: {self.fake.name()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DILIGENCIA: Notificado al interesado en la dirección indicada en fecha _______

"""

        return texto
