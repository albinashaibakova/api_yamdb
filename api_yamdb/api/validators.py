import re

from django.core.exceptions import ValidationError

from reviews.constants import INVALID_CHAR, USER_PROFILE_PATH


def validator_for_username(username):
    if username == USER_PROFILE_PATH:
        raise ValidationError(f'Cannot use username {USER_PROFILE_PATH}')

    elif not re.search(INVALID_CHAR, username):
        raise ValidationError('Invalid username')

    return username
