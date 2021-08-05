from datetime import datetime, timezone

from django.core.mail import send_mail
from rest_framework.exceptions import PermissionDenied, ValidationError

from potok_users.config import Config
from potok_users.models import AccountVerificationCode

config = Config()

VERIFICATION_CODE_CREATION_THRESHOLD = 60


def create_account_verification_code(user):
    if AccountVerificationCode.objects.filter(user=user).exists():
        last_code_date = AccountVerificationCode.objects.get(user=user).date
        timedelta = datetime.now(timezone.utc) - last_code_date
        if timedelta.total_seconds() < VERIFICATION_CODE_CREATION_THRESHOLD:
            raise PermissionDenied('Last code was sent less than 60 seconds ago. Try again later.')
    AccountVerificationCode.objects.filter(user=user).delete()
    verification_code = AccountVerificationCode.objects.create_code(user)
    send_account_verification_code(verification_code)
    return verification_code


def send_account_verification_code(verification_code):
    send_mail(
        "Email verification",
        f"""
        Hello! 
        Thank you for your registration in Potok. Please use the code below to verify your email:

        {verification_code.code}

        Thanks!

        Potok team
        """,
        config["email_host_user"],
        [verification_code.email],
    )


def does_account_verification_code_exist(user, code):
    account_verification_code = AccountVerificationCode.objects.get(user=user)
    if account_verification_code.code == code:
        return True
    else:
        account_verification_code.attempts += 1
        account_verification_code.save()
        if account_verification_code.attempts >= 3:
            account_verification_code.delete()
            raise ValidationError("Verification code is invalid. Please, try to resend code.")
        raise ValidationError("Verification code is wrong. Please, try again.")
