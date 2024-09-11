from django.core.mail import send_mail
from django.conf import settings


class Util:
    @staticmethod
    def send_email(data):
        send_mail(
            data['subject'],
            data['body'],
            settings.DEFAULT_FROM_EMAIL,
            [data['to_email']],
            fail_silently= False,
            html_message=data.get('html_body', None)
        )