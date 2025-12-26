"""
Data augmentation para documentos sintéticos.
Aplica transformaciones para simular errores OCR, variaciones de formato, etc.
"""

import random
import re


def augment_text(text: str, augmentation_level: str = "medium") -> str:
    """
    Aplica data augmentation a un texto para simular variaciones reales.

    Args:
        text: Texto original
        augmentation_level: Nivel de augmentation ("low", "medium", "high")

    Returns:
        Texto modificado
    """

    # Configurar probabilidades según nivel
    probs = {
        "low": {"typo": 0.01, "space": 0.02, "case": 0.01, "ocr": 0.01},
        "medium": {"typo": 0.03, "space": 0.05, "case": 0.03, "ocr": 0.03},
        "high": {"typo": 0.07, "space": 0.10, "case": 0.07, "ocr": 0.07}
    }

    prob = probs.get(augmentation_level, probs["medium"])

    # Aplicar transformaciones
    text = simulate_ocr_errors(text, probability=prob["ocr"])
    text = add_typos(text, probability=prob["typo"])
    text = vary_spacing(text, probability=prob["space"])
    text = vary_case(text, probability=prob["case"])

    return text


def simulate_ocr_errors(text: str, probability: float = 0.03) -> str:
    """
    Simula errores típicos de OCR.
    """

    # Sustituciones comunes en OCR
    ocr_substitutions = {
        'o': ['0', 'O'],
        '0': ['o', 'O'],
        'l': ['1', 'I', '|'],
        '1': ['l', 'I', '|'],
        'I': ['1', 'l', '|'],
        'S': ['5', '$'],
        '5': ['S'],
        'B': ['8'],
        '8': ['B'],
        'G': ['6'],
        'Z': ['2'],
        'A': ['4'],
        'rn': ['m'],
        'vv': ['w'],
        'cl': ['d']
    }

    result = []
    i = 0
    while i < len(text):
        # Intentar sustituciones de 2 caracteres primero
        if i < len(text) - 1:
            two_char = text[i:i+2]
            if two_char in ocr_substitutions and random.random() < probability:
                result.append(random.choice(ocr_substitutions[two_char]))
                i += 2
                continue

        # Sustituciones de 1 carácter
        char = text[i]
        if char in ocr_substitutions and random.random() < probability:
            result.append(random.choice(ocr_substitutions[char]))
        else:
            result.append(char)
        i += 1

    return ''.join(result)


def add_typos(text: str, probability: float = 0.02) -> str:
    """
    Añade errores tipográficos aleatorios.
    """

    words = text.split()
    result = []

    for word in words:
        if len(word) > 3 and random.random() < probability:
            typo_type = random.choice(['swap', 'duplicate', 'delete'])

            if typo_type == 'swap' and len(word) > 2:
                # Intercambiar dos letras adyacentes
                pos = random.randint(0, len(word) - 2)
                word = word[:pos] + word[pos+1] + word[pos] + word[pos+2:]

            elif typo_type == 'duplicate':
                # Duplicar una letra
                pos = random.randint(0, len(word) - 1)
                word = word[:pos] + word[pos] + word[pos:]

            elif typo_type == 'delete' and len(word) > 4:
                # Eliminar una letra
                pos = random.randint(1, len(word) - 2)  # No eliminar primera/última
                word = word[:pos] + word[pos+1:]

        result.append(word)

    return ' '.join(result)


def vary_spacing(text: str, probability: float = 0.05) -> str:
    """
    Varía los espacios (añade o quita espacios extra).
    """

    # Añadir espacios extra aleatorios
    if random.random() < probability:
        text = re.sub(r' ', '  ', text, count=random.randint(3, 10))

    # Quitar algunos espacios (palabras pegadas)
    words = text.split()
    result = []
    i = 0
    while i < len(words):
        if i < len(words) - 1 and random.random() < probability * 0.3:
            # Pegar dos palabras
            result.append(words[i] + words[i+1])
            i += 2
        else:
            result.append(words[i])
            i += 1

    text = ' '.join(result)

    # Añadir saltos de línea extra ocasionalmente
    if random.random() < probability * 0.5:
        text = text.replace('. ', '.\n', random.randint(1, 3))

    return text


def vary_case(text: str, probability: float = 0.02) -> str:
    """
    Varía mayúsculas/minúsculas aleatoriamente.
    """

    result = []
    for char in text:
        if char.isalpha() and random.random() < probability:
            # Invertir caso
            if char.isupper():
                result.append(char.lower())
            else:
                result.append(char.upper())
        else:
            result.append(char)

    return ''.join(result)


def remove_random_sections(text: str, probability: float = 0.1) -> str:
    """
    Elimina secciones aleatorias del texto (simular páginas dañadas).
    """

    if random.random() > probability:
        return text

    lines = text.split('\n')
    if len(lines) < 5:
        return text

    # Eliminar 1-3 líneas aleatorias
    num_to_remove = random.randint(1, min(3, len(lines) // 3))
    for _ in range(num_to_remove):
        if lines:
            lines.pop(random.randint(0, len(lines) - 1))

    return '\n'.join(lines)


def add_noise_characters(text: str, probability: float = 0.01) -> str:
    """
    Añade caracteres de ruido aleatorios (simular escaneos de mala calidad).
    """

    noise_chars = ['.', ',', '-', '_', '·', '~', '`']
    result = []

    for char in text:
        result.append(char)
        if random.random() < probability:
            result.append(random.choice(noise_chars))

    return ''.join(result)


def generate_variants(text: str, num_variants: int = 3) -> list:
    """
    Genera múltiples variantes de un mismo texto aplicando diferentes niveles de augmentation.

    Args:
        text: Texto original
        num_variants: Número de variantes a generar

    Returns:
        Lista de textos variantes (incluye el original)
    """

    variants = [text]  # Incluir original

    levels = ["low", "medium", "high"]

    for i in range(num_variants):
        level = levels[i % len(levels)]
        variant = augment_text(text, augmentation_level=level)
        variants.append(variant)

    return variants
