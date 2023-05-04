from transliterate import translit, detect_language


def to_latin(string, replace_char=''):
    lang = detect_language(string)
    transliterated = translit(string, lang, reversed=True)
    latin_string = ''
    for char in transliterated:
        if char.isalnum() or char in ['-', '_']:
            latin_string += char
        else:
            latin_string += replace_char
    return latin_string
