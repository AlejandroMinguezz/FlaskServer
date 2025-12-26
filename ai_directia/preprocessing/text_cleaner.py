"""
Text cleaning and preprocessing module
"""

import re
import unicodedata


def normalize_whitespace(text):
    """
    Normalize whitespace in text
    - Replace multiple spaces with single space
    - Remove leading/trailing whitespace
    - Normalize line breaks
    """
    # Replace multiple spaces with single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Normalize line breaks
    text = re.sub(r'\n\s*\n+', '\n\n', text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)

    return text.strip()


def remove_special_characters(text, keep_punctuation=True):
    """
    Remove or normalize special characters

    Args:
        text: Input text
        keep_punctuation: If True, keep basic punctuation (.,;:!?-)

    Returns:
        Cleaned text
    """
    if keep_punctuation:
        # Keep letters, numbers, spaces, and basic punctuation
        text = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9\s.,;:!?\-€$%]', '', text)
    else:
        # Keep only letters, numbers, and spaces
        text = re.sub(r'[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9\s]', '', text)

    return text


def normalize_unicode(text):
    """
    Normalize unicode characters (NFD -> NFC)
    """
    return unicodedata.normalize('NFC', text)


def remove_accents(text):
    """
    Remove accents from characters
    """
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def to_lowercase(text):
    """
    Convert text to lowercase
    """
    return text.lower()


def remove_numbers(text):
    """
    Remove all numbers from text
    """
    return re.sub(r'\d+', '', text)


def remove_urls(text):
    """
    Remove URLs from text
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_pattern, '', text)


def remove_emails(text):
    """
    Remove email addresses from text
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.sub(email_pattern, '', text)


def remove_extra_lines(text, max_consecutive_newlines=2):
    """
    Remove excessive line breaks
    """
    pattern = r'\n{' + str(max_consecutive_newlines + 1) + r',}'
    replacement = '\n' * max_consecutive_newlines
    return re.sub(pattern, replacement, text)


def clean_text(text, operations=None):
    """
    Clean text with specified operations

    Args:
        text: Input text
        operations: List of operations to apply. If None, apply default cleaning.
                   Available operations:
                   - 'normalize_whitespace'
                   - 'normalize_unicode'
                   - 'remove_special_chars'
                   - 'remove_urls'
                   - 'remove_emails'
                   - 'remove_numbers'
                   - 'remove_accents'
                   - 'lowercase'
                   - 'remove_extra_lines'

    Returns:
        Cleaned text
    """
    if operations is None:
        # Default cleaning pipeline
        operations = [
            'normalize_unicode',
            'normalize_whitespace',
            'remove_urls',
            'remove_emails',
            'remove_extra_lines',
        ]

    # Apply operations in order
    for op in operations:
        if op == 'normalize_whitespace':
            text = normalize_whitespace(text)
        elif op == 'normalize_unicode':
            text = normalize_unicode(text)
        elif op == 'remove_special_chars':
            text = remove_special_characters(text, keep_punctuation=True)
        elif op == 'remove_special_chars_all':
            text = remove_special_characters(text, keep_punctuation=False)
        elif op == 'remove_urls':
            text = remove_urls(text)
        elif op == 'remove_emails':
            text = remove_emails(text)
        elif op == 'remove_numbers':
            text = remove_numbers(text)
        elif op == 'remove_accents':
            text = remove_accents(text)
        elif op == 'lowercase':
            text = to_lowercase(text)
        elif op == 'remove_extra_lines':
            text = remove_extra_lines(text)

    return text


def tokenize_simple(text):
    """
    Simple word tokenization

    Returns:
        List of tokens
    """
    # Split on whitespace and punctuation
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens


def remove_stopwords(tokens, language='spanish'):
    """
    Remove stopwords from token list

    Args:
        tokens: List of tokens
        language: Language for stopwords ('spanish' or 'english')

    Returns:
        List of tokens without stopwords
    """
    try:
        import nltk
        from nltk.corpus import stopwords

        # Download stopwords if not already downloaded
        try:
            stop_words = set(stopwords.words(language))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            stop_words = set(stopwords.words(language))

        return [token for token in tokens if token not in stop_words]

    except ImportError:
        # If NLTK is not available, use a basic Spanish stopwords list
        spanish_stopwords = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'haber',
            'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo', 'todo',
            'pero', 'más', 'hacer', 'o', 'poder', 'decir', 'este', 'ir', 'otro', 'ese',
            'la', 'si', 'me', 'ya', 'ver', 'porque', 'dar', 'cuando', 'él', 'muy',
            'sin', 'vez', 'mucho', 'saber', 'qué', 'sobre', 'mi', 'alguno', 'mismo',
            'yo', 'también', 'hasta', 'año', 'dos', 'querer', 'entre', 'así', 'primero',
            'desde', 'grande', 'eso', 'ni', 'nos', 'llegar', 'pasar', 'tiempo', 'ella',
            'sí', 'día', 'uno', 'bien', 'poco', 'deber', 'entonces', 'poner', 'cosa',
            'tanto', 'hombre', 'parecer', 'nuestro', 'tan', 'donde', 'ahora', 'parte',
            'después', 'vida', 'quedar', 'siempre', 'creer', 'hablar', 'llevar', 'dejar',
        }

        if language == 'spanish':
            stop_words = spanish_stopwords
        else:
            stop_words = set()  # Empty set for unknown languages

        return [token for token in tokens if token not in stop_words]


def preprocess_text(text, remove_stop=True, language='spanish'):
    """
    Complete preprocessing pipeline

    Args:
        text: Input text
        remove_stop: Whether to remove stopwords
        language: Language for stopwords

    Returns:
        Preprocessed text string
    """
    # Clean text
    cleaned = clean_text(text, operations=[
        'normalize_unicode',
        'normalize_whitespace',
        'remove_urls',
        'remove_emails',
        'lowercase',
    ])

    # Tokenize
    tokens = tokenize_simple(cleaned)

    # Remove stopwords if requested
    if remove_stop:
        tokens = remove_stopwords(tokens, language=language)

    # Join back to string
    return ' '.join(tokens)
