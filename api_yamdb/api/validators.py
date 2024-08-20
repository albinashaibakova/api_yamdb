import re

from django.core.exceptions import ValidationError

from reviews.constants import INVALID_CHAR, INVALID_USERNAME


def validator_for_username(username):
    if username == INVALID_USERNAME:
        raise ValidationError(f'Cannot use username {INVALID_USERNAME}')

    elif not re.search(INVALID_CHAR, username):
        raise ValidationError('Invalid username')

    return username
