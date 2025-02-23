from django.core.exceptions import ValidationError
from string import ascii_letters

numbers = '0123456789'
ascii_letters_with_numbers = ascii_letters + numbers


def validate_phone_number(value: str):
    if not value.isnumeric() or value[:2] != '09':
        raise ValidationError('شماره تلفن نادرست است.')
    return value

def validate_username(value: str):
    if value.isnumeric():
        raise ValidationError('نام کاربری نمیتواند عدد باشد.')
    elif value[0] in numbers:
        raise ValidationError('نام کاربری نمیتواند با عدد شروع شود.')
    elif len(value) <= 4:
        raise ValidationError('نام کاربری باید از 4 حرف بیشتر باشد.')
    for ch in value:
        if ch not in ascii_letters_with_numbers:
            raise ValidationError('نام کاربری باید انگلیسی باشد.')
    return value
