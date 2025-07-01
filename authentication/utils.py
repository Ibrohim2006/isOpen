from django.core.exceptions import ValidationError
import re


def validate_phone_number(value):
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
