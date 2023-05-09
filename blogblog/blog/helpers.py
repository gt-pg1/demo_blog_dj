from unidecode import unidecode


def to_latin(string, replace_char=''):
    transliterated = unidecode(string)
    latin_string = ''
    for char in transliterated:
        if char.isalnum() or char in ['-', '_']:
            latin_string += char
        else:
            latin_string += replace_char
    return latin_string
