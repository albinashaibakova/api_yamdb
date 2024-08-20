from datetime import datetime

from django.core.exceptions import ValidationError


def validate_year(value: int):
    if value < 0:
        raise ValidationError({"year": 'Year must be positive'})
    if value > int(datetime.now().year):
        raise ValidationError(
            {"year": 'Year should be less than current year'}
        )
