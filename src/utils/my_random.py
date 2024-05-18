import random
import string

STRING_DIGITS = string.ascii_letters + string.digits


def generate_random_string(length=4):
    random_string = ''.join(random.choice(STRING_DIGITS) for _ in range(length))
    return random_string

