def format_dictionary(data: dict) -> str:
    """
    Convert a dictionary to a string with each key-value pair on a new line.
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary.")

    # Convert each key-value pair into a formatted string
    formatted_lines = []
    for key, value in data.items():
        formatted_line = f"{key.capitalize()}: {value}"
        formatted_lines.append(formatted_line)

    # Join all formatted lines into a single string
    result = '\n'.join(formatted_lines)

    return result