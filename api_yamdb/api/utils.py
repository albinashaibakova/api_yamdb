from django.conf import settings
from django.core.mail import send_mail


def send_confirmation_email(email, confirmation_code):
    send_mail(
        subject='Confirmation code',
        message=f'Your confirmation code is {confirmation_code}',
        from_email=settings.EMAIL_ADDRESS,
        recipient_list=[email]
    )
