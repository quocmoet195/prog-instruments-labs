import csv
import re
from checksum import calculate_checksum, serialize_result

MY_VARIANT = 83
PATTERNS = {
    "email": "^[\\w._%+-]+@[\\w.-]+\.[a-zA-Z]{2,}$",
    "height": "^[0-2]\.\d{2}$",
    "snils": "^\\d{11}$",
    "passport": "^\d{2}\s\d{2}\s\d{6}$",
    "occupation": "^[a-zA-Zа-яА-ЯёЁ\s-]+$",
    "longitude": "^(-?\\d{1,3}(\\.\\d{1,})?)$",
    "hex_color": "^#([\\w]{6}|[\\w]{3})$",
    "issn": "^\d{4}-\d{4}$",
    "locale_code": "^[a-z]{2,3}(-[a-z]{2})?$",
    "time": "^([0-1]\\d|2[0-3]):[0-5]\\d:[0-5]\\d\\.\\d{1,6}$"
}


def check_line(line: list[str]) -> bool:
    """
    Validates a list of values against predefined regex patterns.

    Args:
        line (list[str]): A list of strings to be validated, where each string corresponds
                          to a specific field in the order defined by PATTERNS.

    Returns:
        bool: True if all values in `line` match their respective patterns in PATTERNS;
              False if any value does not match.
    """
    for i, key in enumerate(PATTERNS.keys()):
        if not re.match(PATTERNS[key], line[i]):
            return False
    return True