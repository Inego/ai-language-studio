import copy
import random
import string

STRING_DIGITS = string.ascii_letters + string.digits


def generate_random_string(length=4):
    random_string = ''.join(random.choice(STRING_DIGITS) for _ in range(length))
    return random_string


def weighted_random_choice(elements):
    n = len(elements)
    total_weight = n * (n + 1) // 2  # Sum of the first n natural numbers
    rand_value = random.randint(1, total_weight)  # Generate a random value in the range [1, total_weight]

    cumulative_weight = 0
    for i in range(n):
        cumulative_weight += (n - i)  # Weight for the i-th element (n, n-1, ..., 1)
        if rand_value <= cumulative_weight:
            return elements[i]


def select_and_remove(elements, n):
    elements_copy = copy.copy(elements)
    selected_elements = []

    for _ in range(n):
        if not elements_copy:
            break
        chosen_element = weighted_random_choice(elements_copy)
        selected_elements.append(chosen_element)
        elements_copy.remove(chosen_element)

    return selected_elements
