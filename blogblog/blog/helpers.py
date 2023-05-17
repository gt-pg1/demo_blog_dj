from unidecode import unidecode


def to_latin(string, replace_char=''):
    """
    Transliterates a string to its Latin representation.

    Args:
        string (str): The string to transliterate.
        replace_char (str, optional): The character to use as a replacement for non-alphanumeric characters.
            Defaults to an empty string.

    Returns:
        str: The transliterated string.
    """
    transliterated = unidecode(string)
    latin_string = ''.join(
        char
        if char.isalnum() or char in ['-', '_']
        else replace_char
        for char in transliterated
    )
    return latin_string
