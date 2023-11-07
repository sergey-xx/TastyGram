from django.core.exceptions import ValidationError


def time_validator(value):
    """Валидатор времени приготовления Рецепта."""
    if value < 1:
        raise ValidationError(
            'Время приготовления не может быть менее 1 минуты')
