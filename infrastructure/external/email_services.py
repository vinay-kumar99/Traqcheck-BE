from django.core.mail import send_mail
from django.conf import settings
from domains.candidates.interfaces import IEmailService


class EmailService(IEmailService):
    
    def send_email(self, to_email: str, subject: str, message: str) -> bool:
        try:
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False