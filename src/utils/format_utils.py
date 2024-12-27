def remove_fenced_lines(text):
    """
    Removes the first and/or last line of a multi-line string if they start with triple backticks (```).

    Args:
        text: The multi-line string.

    Returns:
        The string with the fenced lines removed, or the original string if no fenced lines are found.
    """

    lines = text.splitlines()

    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines)
