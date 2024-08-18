from django.core.mail import send_mail

from api_yamdb.settings import EMAIL_ADDRESS


def send_confirmation_email(email, confirmation_code):
    send_mail(
        subject='Confirmation code',
        message=f'Your confirmation code is {confirmation_code}',
        from_email=EMAIL_ADDRESS,
        recipient_list=[email, ]
    )
