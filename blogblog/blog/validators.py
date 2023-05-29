from django.core.validators import RegexValidator

phone_regex = r'^\+?1?\d{9,15}$'
phone_validator = RegexValidator(
    regex=phone_regex,
    message="Enter a valid phone number."
)