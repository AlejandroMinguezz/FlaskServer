"""
Template generators for synthetic document creation
"""

from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker(['es_ES', 'es_MX'])


def generate_factura():
    """Generate synthetic invoice (factura)"""
    num_factura = f"F{random.randint(1000, 9999)}/{datetime.now().year}"
    fecha = fake.date_between(start_date='-1y', end_date='today')

    # Generate items
    num_items = random.randint(1, 5)
    items = []
    subtotal = 0

    for i in range(num_items):
        concepto = random.choice([
            "Servicios de consultoría",
            "Desarrollo de software",
            "Mantenimiento informático",
            "Licencias de software",
            "Soporte técnico",
            "Alojamiento web",
            "Diseño gráfico"
        ])
        cantidad = random.randint(1, 10)
        precio = round(random.uniform(50, 500), 2)
        total = round(cantidad * precio, 2)
        items.append(f"{concepto:40} {cantidad:5} {precio:10.2f}€ {total:12.2f}€")
        subtotal += total

    iva_rate = 0.21
    iva = round(subtotal * iva_rate, 2)
    total = round(subtotal + iva, 2)

    text = f"""
FACTURA N.º {num_factura}
Fecha de emisión: {fecha.strftime('%d/%m/%Y')}

DATOS DEL EMISOR:
Empresa: {fake.company()}
CIF: {fake.bothify(text='?########?').upper()}
Dirección: {fake.street_address()}
{fake.city()}, {fake.postcode()}
Tel: {fake.phone_number()}

DATOS DEL CLIENTE:
Cliente: {fake.company()}
NIF/CIF: {fake.bothify(text='?########?').upper()}
Dirección: {fake.street_address()}
{fake.city()}, {fake.postcode()}

DETALLE DE LA FACTURA:
{'─' * 80}
CONCEPTO                                 CANT.    PRECIO        TOTAL
{'─' * 80}
{chr(10).join(items)}
{'─' * 80}

Base imponible:                                               {subtotal:12.2f}€
IVA ({iva_rate*100:.0f}%):                                                {iva:12.2f}€
{'═' * 80}
TOTAL FACTURA:                                                {total:12.2f}€
{'═' * 80}

FORMA DE PAGO: Transferencia bancaria
VENCIMIENTO: {(fecha + timedelta(days=30)).strftime('%d/%m/%Y')}
"""
    return text.strip()


def generate_nomina():
    """Generate synthetic payroll (nómina)"""
    mes = random.choice(['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
    año = datetime.now().year

    nombre = fake.name()
    dni = fake.bothify(text='########?').upper()
    categoria = random.choice(['Técnico Superior', 'Técnico Medio', 'Administrativo',
                              'Operario', 'Directivo'])

    salario_base = round(random.uniform(1200, 3500), 2)
    complementos = round(random.uniform(100, 500), 2)
    total_devengos = round(salario_base + complementos, 2)

    irpf_rate = random.choice([0.15, 0.19, 0.24])
    ss_rate = 0.0635

    irpf = round(total_devengos * irpf_rate, 2)
    ss = round(total_devengos * ss_rate, 2)
    total_deducciones = round(irpf + ss, 2)

    liquido = round(total_devengos - total_deducciones, 2)

    text = f"""
NÓMINA - {mes.upper()} {año}

DATOS DEL TRABAJADOR:
Nombre: {nombre}
DNI: {dni}
Categoría profesional: {categoria}
Grupo de cotización: Grupo 2

EMPRESA:
{fake.company()}
CIF: {fake.bothify(text='?########?').upper()}

PERIODO DE LIQUIDACIÓN: {mes} {año}
{'═' * 70}

DEVENGOS:
{'─' * 70}
Salario base                                         {salario_base:10.2f}€
Complementos salariales                              {complementos:10.2f}€
{'─' * 70}
TOTAL DEVENGOS                                       {total_devengos:10.2f}€

DEDUCCIONES:
{'─' * 70}
IRPF ({irpf_rate*100:.0f}%)                                             {irpf:10.2f}€
Seguridad Social ({ss_rate*100:.2f}%)                          {ss:10.2f}€
{'─' * 70}
TOTAL DEDUCCIONES                                    {total_deducciones:10.2f}€

{'═' * 70}
LÍQUIDO A PERCIBIR                                   {liquido:10.2f}€
{'═' * 70}

Fecha de pago: {fake.date_this_month().strftime('%d/%m/%Y')}
Método de pago: Transferencia bancaria
"""
    return text.strip()


def generate_contrato():
    """Generate synthetic contract (contrato)"""
    tipo_contrato = random.choice(['CONTRATO DE TRABAJO', 'CONTRATO DE ARRENDAMIENTO',
                                  'CONTRATO DE PRESTACIÓN DE SERVICIOS', 'CONTRATO MERCANTIL'])

    fecha = fake.date_between(start_date='-2y', end_date='today')
    vigencia_meses = random.choice([6, 12, 24, 36])

    text = f"""
{tipo_contrato}

En {fake.city()}, a {fecha.strftime('%d de %B de %Y')}

REUNIDOS:

DE UNA PARTE:
{fake.name()}, mayor de edad, con DNI {fake.bothify(text='########?').upper()},
actuando en nombre y representación de {fake.company()},
con CIF {fake.bothify(text='?########?').upper()},
con domicilio en {fake.street_address()}, {fake.city()}.
En adelante, "LA PARTE CONTRATANTE".

DE OTRA PARTE:
{fake.name()}, mayor de edad, con DNI {fake.bothify(text='########?').upper()},
con domicilio en {fake.street_address()}, {fake.city()}.
En adelante, "LA PARTE CONTRATADA".

EXPONEN:

Primero. Que la PARTE CONTRATANTE tiene interés en contratar los servicios
profesionales de la PARTE CONTRATADA.

Segundo. Que la PARTE CONTRATADA dispone de la capacidad, medios y conocimientos
necesarios para la prestación de dichos servicios.

CLÁUSULAS:

PRIMERA. OBJETO DEL CONTRATO
El presente contrato tiene por objeto la prestación de servicios profesionales
en el ámbito de {random.choice(['consultoría', 'desarrollo', 'asesoría', 'gestión'])}.

SEGUNDA. DURACIÓN
El contrato tendrá una vigencia de {vigencia_meses} meses, contados desde
la fecha de firma, pudiendo prorrogarse por acuerdo de las partes.

TERCERA. RETRIBUCIÓN
Por los servicios prestados, la PARTE CONTRATANTE abonará la cantidad de
{random.randint(1500, 5000)}€ mensuales, más el IVA correspondiente.

CUARTA. RESCISIÓN
Cualquiera de las partes podrá rescindir el presente contrato con un preaviso
mínimo de 30 días.

QUINTA. JURISDICCIÓN
Las partes se someten a los Juzgados y Tribunales de {fake.city()} para
cualquier controversia que pudiera derivarse del presente contrato.

Y en prueba de conformidad, firman el presente contrato por duplicado y a un
solo efecto en el lugar y fecha indicados en el encabezamiento.

LA PARTE CONTRATANTE                    LA PARTE CONTRATADA

Fdo.: _________________                 Fdo.: _________________
"""
    return text.strip()


def generate_presupuesto():
    """Generate synthetic budget/quote (presupuesto)"""
    num_presupuesto = f"P{random.randint(1000, 9999)}/{datetime.now().year}"
    fecha = fake.date_between(start_date='-3m', end_date='today')
    validez_dias = random.choice([15, 30, 45])

    num_items = random.randint(2, 6)
    items = []
    subtotal = 0

    for i in range(num_items):
        concepto = random.choice([
            "Instalación de sistema",
            "Configuración de red",
            "Migración de datos",
            "Formación de usuarios",
            "Auditoría de seguridad",
            "Optimización de rendimiento"
        ])
        precio = round(random.uniform(200, 2000), 2)
        items.append(f"{concepto:45} {precio:12.2f}€")
        subtotal += precio

    iva = round(subtotal * 0.21, 2)
    total = round(subtotal + iva, 2)

    text = f"""
PRESUPUESTO N.º {num_presupuesto}
Fecha: {fecha.strftime('%d/%m/%Y')}
Validez: {validez_dias} días

EMPRESA:
{fake.company()}
CIF: {fake.bothify(text='?########?').upper()}
Dirección: {fake.street_address()}
{fake.city()}, {fake.postcode()}
Tel: {fake.phone_number()}
Email: {fake.company_email()}

CLIENTE:
{fake.company()}
Atención: {fake.name()}

PRESUPUESTO PARA: {random.choice(['Proyecto de implantación', 'Servicios IT',
                                  'Consultoría técnica', 'Desarrollo a medida'])}

{'═' * 70}
CONCEPTO                                             IMPORTE
{'═' * 70}
{chr(10).join(items)}
{'─' * 70}

Subtotal:                                            {subtotal:12.2f}€
IVA (21%):                                           {iva:12.2f}€
{'═' * 70}
TOTAL PRESUPUESTO:                                   {total:12.2f}€
{'═' * 70}

CONDICIONES:
- Presupuesto válido por {validez_dias} días desde la fecha de emisión
- Precios con IVA incluido
- Forma de pago: 50% al inicio, 50% al finalizar
- Plazo de ejecución: {random.randint(2, 8)} semanas

Para aceptar este presupuesto, firme y devuelva una copia.

Atentamente,
{fake.name()}
Director Comercial
"""
    return text.strip()


def generate_recibo():
    """Generate synthetic receipt (recibo)"""
    tipo_recibo = random.choice(['Recibo de luz', 'Recibo de agua', 'Recibo de gas',
                                'Recibo de alquiler', 'Recibo de comunidad'])
    fecha = fake.date_between(start_date='-6m', end_date='today')
    periodo_inicio = fecha
    periodo_fin = fecha + timedelta(days=random.choice([30, 60, 90]))

    if 'luz' in tipo_recibo or 'agua' in tipo_recibo or 'gas' in tipo_recibo:
        consumo = random.randint(100, 500)
        unidad = 'kWh' if 'luz' in tipo_recibo else 'm³' if 'agua' in tipo_recibo or 'gas' in tipo_recibo else 'unidades'
        precio_unidad = round(random.uniform(0.10, 0.25), 4)
        importe_consumo = round(consumo * precio_unidad, 2)
        otros_conceptos = round(random.uniform(10, 30), 2)
        total = round(importe_consumo + otros_conceptos, 2)

        detalle = f"""
PERIODO DE FACTURACIÓN: {periodo_inicio.strftime('%d/%m/%Y')} - {periodo_fin.strftime('%d/%m/%Y')}

CONSUMO:
Lectura anterior:                                    {random.randint(10000, 50000)} {unidad}
Lectura actual:                                      {random.randint(10000, 50000)} {unidad}
Consumo del periodo:                                 {consumo} {unidad}
Precio por {unidad}:                                       {precio_unidad}€

Importe por consumo:                                 {importe_consumo:10.2f}€
Alquiler de equipos:                                 {otros_conceptos:10.2f}€
"""
    else:
        total = round(random.uniform(300, 1200), 2)
        detalle = f"""
CONCEPTO: {tipo_recibo}
Periodo: {periodo_inicio.strftime('%B %Y')}
"""

    text = f"""
{tipo_recibo.upper()}

DATOS DEL TITULAR:
{fake.name()}
DNI: {fake.bothify(text='########?').upper()}
Dirección de suministro: {fake.street_address()}
{fake.city()}, {fake.postcode()}

NÚMERO DE RECIBO: {fake.bothify(text='R-########')}
FECHA DE EMISIÓN: {fecha.strftime('%d/%m/%Y')}
{detalle}
{'═' * 70}
TOTAL A PAGAR:                                       {total:10.2f}€
{'═' * 70}

FECHA DE CARGO: {(fecha + timedelta(days=7)).strftime('%d/%m/%Y')}
IBAN: ES{fake.random_int(min=10, max=99)} {fake.random_int(min=1000, max=9999)} {fake.random_int(min=1000, max=9999)} {fake.random_int(min=1000, max=9999)} {fake.random_int(min=1000, max=9999)}

Para cualquier consulta, llame al {fake.phone_number()}
"""
    return text.strip()


def generate_certificado():
    """Generate synthetic certificate (certificado)"""
    tipo = random.choice([
        'CERTIFICADO DE EMPRESA',
        'CERTIFICADO ACADÉMICO',
        'CERTIFICADO DE ASISTENCIA',
        'CERTIFICADO MÉDICO'
    ])

    fecha = fake.date_between(start_date='-1y', end_date='today')
    nombre = fake.name()

    if 'EMPRESA' in tipo:
        content = f"""
{fake.name()}, en calidad de Director/a de Recursos Humanos de {fake.company()},
con CIF {fake.bothify(text='?########?').upper()},

CERTIFICA:

Que D./Dña. {nombre}, con DNI {fake.bothify(text='########?').upper()},
ha prestado servicios en esta empresa desde el {fake.date_between(start_date='-5y', end_date='-1y').strftime('%d/%m/%Y')}
hasta el {fecha.strftime('%d/%m/%Y')}, desempeñando el puesto de
{random.choice(['Técnico/a', 'Administrativo/a', 'Responsable', 'Analista'])}.

Durante este periodo, ha demostrado profesionalidad, dedicación y
cumplimiento de sus funciones de manera satisfactoria.
"""
    elif 'ACADÉMICO' in tipo:
        content = f"""
El/La que suscribe, {fake.name()}, en calidad de Secretario/a Académico/a
de {random.choice(['Universidad', 'Centro de Formación', 'Instituto'])} {fake.company()},

CERTIFICA:

Que D./Dña. {nombre}, con DNI {fake.bothify(text='########?').upper()},
ha completado satisfactoriamente el programa de estudios correspondiente a
{random.choice(['Grado en', 'Máster en', 'Curso de'])} {random.choice(['Ingeniería', 'Administración', 'Gestión', 'Tecnología'])},
con una calificación media de {round(random.uniform(6.5, 9.5), 2)} sobre 10.
"""
    else:
        periodo_inicio = fake.date_between(start_date='-6m', end_date='-1m')
        periodo_fin = periodo_inicio + timedelta(days=random.choice([5, 10, 15, 30]))

        content = f"""
El/La que suscribe, {fake.name()}, con número de colegiado/a {random.randint(1000, 9999)},

CERTIFICA:

Que D./Dña. {nombre}, con DNI {fake.bothify(text='########?').upper()},
{random.choice(['ha asistido al curso', 'ha participado en', 'ha completado el programa'])}
denominado "{random.choice(['Formación en', 'Taller de', 'Seminario sobre'])}
{random.choice(['Gestión', 'Liderazgo', 'Comunicación', 'Tecnología'])}",
celebrado los días {periodo_inicio.strftime('%d/%m/%Y')} al {periodo_fin.strftime('%d/%m/%Y')},
con una duración de {random.choice([20, 30, 40, 60])} horas lectivas.
"""

    text = f"""
{tipo}

{content}

Y para que así conste y surta los efectos oportunos, expido el presente
certificado en {fake.city()}, a {fecha.strftime('%d de %B de %Y')}.

Fdo.: _________________
{fake.name()}
"""
    return text.strip()


def generate_fiscal():
    """Generate synthetic tax document (documento fiscal)"""
    año = random.randint(datetime.now().year - 3, datetime.now().year - 1)
    modelo = random.choice(['100', '130', '303', '390'])

    nombre = fake.name()
    nif = fake.bothify(text='########?').upper()

    text = f"""
AGENCIA TRIBUTARIA
MINISTERIO DE HACIENDA

MODELO {modelo} - DECLARACIÓN

EJERCICIO FISCAL: {año}
PERIODO: {random.choice(['Anual', '1T', '2T', '3T', '4T'])}

DATOS DEL DECLARANTE:
Apellidos y nombre: {nombre}
NIF: {nif}
Domicilio fiscal: {fake.street_address()}
{fake.city()}, {fake.postcode()}

LIQUIDACIÓN:
{'═' * 70}

Base imponible:                                      {round(random.uniform(20000, 80000), 2):12.2f}€
Retenciones y pagos a cuenta:                        {round(random.uniform(3000, 15000), 2):12.2f}€
Deducciones aplicadas:                               {round(random.uniform(500, 3000), 2):12.2f}€

{'─' * 70}
Cuota resultante:                                    {round(random.uniform(1000, 8000), 2):12.2f}€
{'═' * 70}

RESULTADO: {random.choice(['A DEVOLVER', 'A INGRESAR', 'NEGATIVO'])}

Fecha de presentación: {fake.date_between(start_date=f'-{datetime.now().year - año}y', end_date='today').strftime('%d/%m/%Y')}
Número de justificante: {fake.bothify(text='########')}

Este documento tiene carácter informativo y NO sustituye a la declaración oficial.
"""
    return text.strip()


def generate_notificacion():
    """Generate synthetic administrative notice (notificación administrativa)"""
    fecha = fake.date_between(start_date='-1y', end_date='today')
    num_expediente = fake.bothify(text='EXP/####/####')

    text = f"""
ADMINISTRACIÓN PÚBLICA
{random.choice(['AYUNTAMIENTO DE', 'DIPUTACIÓN DE', 'JUNTA DE'])} {fake.city().upper()}

NOTIFICACIÓN ADMINISTRATIVA

EXPEDIENTE N.º: {num_expediente}
FECHA: {fecha.strftime('%d/%m/%Y')}

INTERESADO/A:
{fake.name()}
DNI: {fake.bothify(text='########?').upper()}
Domicilio: {fake.street_address()}
{fake.city()}, {fake.postcode()}

ASUNTO: {random.choice([
    'Resolución de expediente administrativo',
    'Comunicación de trámite',
    'Requerimiento de documentación',
    'Notificación de resolución'
])}

Por la presente se le notifica que, con fecha {fecha.strftime('%d/%m/%Y')},
se ha dictado resolución en el expediente de referencia, por la que se
{random.choice([
    'aprueba la solicitud presentada',
    'requiere subsanación de la documentación',
    'concede la licencia solicitada',
    'inicia procedimiento de inspección'
])}.

FUNDAMENTOS DE DERECHO:
- Ley 39/2015, de 1 de octubre, del Procedimiento Administrativo Común
- Normativa específica aplicable al caso

RESOLUCIÓN:
{random.choice([
    'Se estima la solicitud presentada',
    'Se requiere la presentación de documentación adicional',
    'Se concede un plazo de 10 días hábiles para alegaciones',
    'Se procede a la inscripción en el registro correspondiente'
])}.

RECURSOS:
Contra la presente resolución, que agota la vía administrativa, podrá
interponer recurso contencioso-administrativo ante el Juzgado de lo
Contencioso-Administrativo en el plazo de DOS MESES contados desde el
día siguiente a su notificación.

Fdo.: {fake.name()}
{random.choice(['Secretario/a General', 'Jefe/a de Servicio', 'Director/a General'])}
"""
    return text.strip()


def generate_otro():
    """Generate generic document (otro)"""
    text = f"""
DOCUMENTO GENERAL

Fecha: {fake.date_between(start_date='-1y', end_date='today').strftime('%d/%m/%Y')}

{fake.company()}
{fake.street_address()}
{fake.city()}, {fake.postcode()}

Asunto: {random.choice([
    'Comunicación interna',
    'Informe de seguimiento',
    'Acta de reunión',
    'Memoria descriptiva'
])}

{fake.text(max_nb_chars=500)}

Atentamente,
{fake.name()}
"""
    return text.strip()


# Map category IDs to generator functions
GENERATORS = {
    'factura': generate_factura,
    'nomina': generate_nomina,
    'contrato': generate_contrato,
    'presupuesto': generate_presupuesto,
    'recibo': generate_recibo,
    'certificado': generate_certificado,
    'fiscal': generate_fiscal,
    'notificacion': generate_notificacion,
    'otro': generate_otro,
}


def generate_document(category_id):
    """Generate a synthetic document for the given category"""
    if category_id not in GENERATORS:
        raise ValueError(f"Unknown category: {category_id}")

    return GENERATORS[category_id]()
