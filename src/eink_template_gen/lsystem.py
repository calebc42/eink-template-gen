"""
L-System Engine

Generates a command string based on a set of rules,
but does not perform any drawing.
"""


def generate_lsystem_string(axiom, rules, iterations):
    """
    Generates a fractal command string using L-System rules.

    Args:
        axiom (str): The starting string (e.g., "F").
        rules (dict): A dictionary of substitution rules (e.g., {"F": "F+G"}).
        iterations (int): The number of times to apply the rules.

    Returns:
        str: The final, complex command string.
    """
    current_string = axiom

    for _ in range(iterations):
        next_string = ""
        for char in current_string:
            # Substitute the char if it's in rules, otherwise keep it
            next_string += rules.get(char, char)
        current_string = next_string

    return current_string
