

_latin_to_cyrillic_1 = {
        'A': 'А', 'a': 'а',
        'B': 'Б', 'b': 'б',
        'V': 'В', 'v': 'в',
        'G': 'Г', 'g': 'г',
        'D': 'Д', 'd': 'д',
        'Đ': 'Ђ', 'đ': 'ђ',
        'E': 'Е', 'e': 'е',
        'Ž': 'Ж', 'ž': 'ж',
        'Z': 'З', 'z': 'з',
        'I': 'И', 'i': 'и',
        'J': 'Ј', 'j': 'ј',
        'K': 'К', 'k': 'к',
        'L': 'Л', 'l': 'л',
        'M': 'М', 'm': 'м',
        'N': 'Н', 'n': 'н',
        'O': 'О', 'o': 'о',
        'P': 'П', 'p': 'п',
        'R': 'Р', 'r': 'р',
        'S': 'С', 's': 'с',
        'T': 'Т', 't': 'т',
        'Ć': 'Ћ', 'ć': 'ћ',
        'U': 'У', 'u': 'у',
        'F': 'Ф', 'f': 'ф',
        'H': 'Х', 'h': 'х',
        'C': 'Ц', 'c': 'ц',
        'Č': 'Ч', 'č': 'ч',
        'Š': 'Ш', 'š': 'ш',
    }


def latin_to_cyrillic(src: str):
    result = ""

    current_index = 0

    src_len = len(src)
    src_len_1 = src_len - 1

    while current_index < src_len:
        c = src[current_index]
        if current_index < src_len_1:
            next_c = src[current_index + 1]
            if c == 'L' and (next_c == 'j' or next_c == 'J'):
                result += 'Љ'
                current_index += 2
                continue
            elif c == 'l' and next_c == 'j':
                result += 'љ'
                current_index += 2
                continue
            elif c == 'N' and (next_c == 'j' or next_c == 'J'):
                result += 'Њ'
                current_index += 2
                continue
            elif c == 'n' and next_c == 'j':
                result += 'њ'
                current_index += 2
                continue
            elif c == 'D' and (next_c == 'ž' or next_c == 'Ž'):
                result += 'Џ'
                current_index += 2
                continue
            elif c == 'd' and next_c == 'ž':
                result += 'џ'
                current_index += 2
                continue
        mapped = _latin_to_cyrillic_1.get(c)
        result += (mapped if mapped else c)
        current_index += 1

    return result
