import re

from django.core.exceptions import ValidationError

from api.constants import INVALID_USERNAME


def validator_for_username(username):
    if username == INVALID_USERNAME:
        raise ValidationError(f'Cannot use username {INVALID_USERNAME}')

    elif not re.search(r'^[-a-zA-Z0-9_]+$', username):
        raise ValidationError('Invalid username')

    return username
