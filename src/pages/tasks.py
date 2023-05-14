from django.conf import settings
from django.core.mail import send_mail
from huey.contrib.djhuey import task


@task()
def background_send_contact_form_email(subject: str, message: str) -> int:
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.POSTMARK_SENDER,
        recipient_list=[settings.EMAIL_RECIPIENT],
    )
