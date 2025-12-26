"""
Data augmentation techniques for document text
"""

import random
import re


def add_spaces(text, probability=0.1):
    """Randomly add extra spaces"""
    result = []
    for char in text:
        result.append(char)
        if char == ' ' and random.random() < probability:
            result.append(' ')
    return ''.join(result)


def remove_spaces(text, probability=0.05):
    """Randomly remove some spaces"""
    result = []
    skip_next_space = False

    for char in text:
        if char == ' ' and random.random() < probability:
            skip_next_space = True
            continue
        result.append(char)

    return ''.join(result)


def simulate_ocr_errors(text, probability=0.02):
    """Simulate common OCR errors"""
    ocr_substitutions = {
        'o': '0',
        'O': '0',
        'l': '1',
        'I': '1',
        'S': '5',
        's': '5',
        'B': '8',
        'E': 'F',
        'e': 'c',
        'a': 'á',
        'e': 'é',
        'i': 'í',
        'o': 'ó',
        'u': 'ú',
    }

    result = []
    for char in text:
        if char in ocr_substitutions and random.random() < probability:
            result.append(ocr_substitutions[char])
        else:
            result.append(char)

    return ''.join(result)


def change_case_randomly(text, probability=0.03):
    """Randomly change case of some letters"""
    result = []
    for char in text:
        if char.isalpha() and random.random() < probability:
            result.append(char.swapcase())
        else:
            result.append(char)

    return ''.join(result)


def add_line_breaks(text, probability=0.05):
    """Add random line breaks"""
    lines = text.split('\n')
    result = []

    for line in lines:
        words = line.split()
        new_words = []

        for word in words:
            new_words.append(word)
            if random.random() < probability:
                new_words.append('\n')

        result.append(' '.join(new_words))

    return '\n'.join(result)


def remove_punctuation_randomly(text, probability=0.05):
    """Randomly remove punctuation"""
    punctuation = '.,;:!?'
    result = []

    for char in text:
        if char in punctuation and random.random() < probability:
            continue
        result.append(char)

    return ''.join(result)


def shuffle_lines_slightly(text, probability=0.02):
    """Shuffle adjacent lines with low probability"""
    lines = text.split('\n')

    i = 0
    while i < len(lines) - 1:
        if random.random() < probability:
            # Swap with next line
            lines[i], lines[i + 1] = lines[i + 1], lines[i]
            i += 2  # Skip the swapped line
        else:
            i += 1

    return '\n'.join(lines)


def apply_augmentation(text, intensity='light'):
    """
    Apply multiple augmentation techniques to text

    Args:
        text: Original text
        intensity: 'light', 'medium', or 'heavy'

    Returns:
        Augmented text
    """
    intensity_map = {
        'light': {
            'add_spaces': 0.03,
            'remove_spaces': 0.02,
            'ocr_errors': 0.01,
            'case_changes': 0.01,
            'line_breaks': 0.02,
            'remove_punct': 0.02,
            'shuffle_lines': 0.01,
        },
        'medium': {
            'add_spaces': 0.07,
            'remove_spaces': 0.04,
            'ocr_errors': 0.03,
            'case_changes': 0.02,
            'line_breaks': 0.04,
            'remove_punct': 0.04,
            'shuffle_lines': 0.02,
        },
        'heavy': {
            'add_spaces': 0.12,
            'remove_spaces': 0.08,
            'ocr_errors': 0.06,
            'case_changes': 0.05,
            'line_breaks': 0.08,
            'remove_punct': 0.08,
            'shuffle_lines': 0.04,
        },
    }

    if intensity not in intensity_map:
        intensity = 'light'

    probs = intensity_map[intensity]

    # Apply augmentations
    augmented = text

    if random.random() < 0.5:
        augmented = add_spaces(augmented, probs['add_spaces'])

    if random.random() < 0.5:
        augmented = remove_spaces(augmented, probs['remove_spaces'])

    if random.random() < 0.5:
        augmented = simulate_ocr_errors(augmented, probs['ocr_errors'])

    if random.random() < 0.3:
        augmented = change_case_randomly(augmented, probs['case_changes'])

    if random.random() < 0.4:
        augmented = add_line_breaks(augmented, probs['line_breaks'])

    if random.random() < 0.3:
        augmented = remove_punctuation_randomly(augmented, probs['remove_punct'])

    if random.random() < 0.2:
        augmented = shuffle_lines_slightly(augmented, probs['shuffle_lines'])

    return augmented


def generate_variations(text, num_variations=3, intensity='light'):
    """
    Generate multiple augmented variations of a text

    Args:
        text: Original text
        num_variations: Number of variations to generate
        intensity: Augmentation intensity ('light', 'medium', 'heavy')

    Returns:
        List of augmented texts
    """
    variations = []

    for _ in range(num_variations):
        augmented = apply_augmentation(text, intensity)
        variations.append(augmented)

    return variations
