from django.core.exceptions import ValidationError
import re


def validate_phone_number(value):
    """Validate phone number format for supported countries"""
    patterns = {
        'Uzbekistan': r'^\+998\d{9}$',
        'Russia': r'^\+7\d{10}$',
        'USA': r'^\+1\d{10}$'
    }

    for country, pattern in patterns.items():
        if re.fullmatch(pattern, value):
            return

    raise ValidationError(
        "Invalid phone number format. Valid formats: "
        "Uzbekistan: +998901234567, "
        "Russia: +79123456789, "
        "USA: +11234567890"
    )


def get_country_from_phone(phone_number):
    """Determine country from phone number"""
    if phone_number.startswith('+998'):
        return 'Uzbekistan'
    elif phone_number.startswith('+7'):
        return 'Russia'
    elif phone_number.startswith('+1'):
        return 'USA'
    return None
