"""
Clase base para generadores de documentos sintéticos.
"""

import random
from abc import ABC, abstractmethod
from typing import List, Dict
from faker import Faker


class BaseDocumentGenerator(ABC):
    """
    Clase base abstracta para generadores de documentos sintéticos.
    Cada tipo de documento hereda de esta clase e implementa generate_document().
    """

    def __init__(self, locale='es_ES', seed=None):
        """
        Args:
            locale: Locale de Faker (español por defecto)
            seed: Semilla para reproducibilidad
        """
        self.fake = Faker(locale)
        if seed:
            Faker.seed(seed)
            random.seed(seed)

    @abstractmethod
    def generate_document(self) -> str:
        """
        Genera un documento sintético.
        Debe ser implementado por cada subclase.

        Returns:
            str: Texto del documento generado
        """
        pass

    def generate_multiple(self, count: int) -> List[str]:
        """
        Genera múltiples documentos.

        Args:
            count: Número de documentos a generar

        Returns:
            Lista de textos de documentos
        """
        return [self.generate_document() for _ in range(count)]

    def random_choice(self, items: List) -> any:
        """Selecciona un elemento aleatorio de una lista."""
        return random.choice(items)

    def random_float(self, min_val: float, max_val: float, decimals: int = 2) -> float:
        """Genera un float aleatorio con precisión específica."""
        value = random.uniform(min_val, max_val)
        return round(value, decimals)

    def random_int(self, min_val: int, max_val: int) -> int:
        """Genera un entero aleatorio."""
        return random.randint(min_val, max_val)

    def format_currency(self, amount: float) -> str:
        """Formatea cantidad como moneda."""
        return f"{amount:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")

    def generate_cif(self) -> str:
        """Genera un CIF/NIF español sintético."""
        letter = random.choice('ABCDEFGHJNPQRSUVW')
        numbers = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        control = random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        return f"{letter}{numbers}{control}"

    def generate_phone(self) -> str:
        """Genera un teléfono español."""
        prefixes = ['6', '7', '9']
        prefix = random.choice(prefixes)
        if prefix in ['6', '7']:
            return f"{prefix}{random.randint(10000000, 99999999)}"
        else:
            return f"{prefix}{random.randint(1, 9)}{random.randint(1000000, 9999999)}"
