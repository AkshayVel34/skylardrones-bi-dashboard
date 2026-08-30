import re


def clean_text(value):
    """
    Clean text values coming from Monday.com.
    Handles null, empty, N/A and similar values.
    """

    if value is None:
        return ""

    value = str(value).strip()

    if value.lower() in [
        "",
        "null",
        "none",
        "n/a",
        "na",
        "nan",
        "-"
    ]:
        return ""

    return value


def clean_number(value):
    """
    Convert messy numeric values into float.

    Examples:
        '1,000'      -> 1000.0
        '₹50,000'    -> 50000.0
        '50%'        -> 50.0
        ''           -> None
        'N/A'        -> None
    """

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    # Handle common representations of missing data
    if value.lower() in [
        "null",
        "none",
        "n/a",
        "na",
        "nan",
        "-"
    ]:
        return None

    # Remove common formatting
    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("$", "")
    value = value.replace("€", "")
    value = value.replace("%", "")

    # Extract numeric portion
    match = re.search(r"-?\d+(?:\.\d+)?", value)

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def normalize_percentage(value):
    """
    Convert percentage values into a number between 0 and 1.

    Examples:
        '50%' -> 0.50
        '75'  -> 0.75
        '0.5' -> 0.50
    """

    number = clean_number(value)

    if number is None:
        return None

    if number > 1:
        return number / 100

    return number