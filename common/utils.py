import re

from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives


# JWT Token
class JwtToken:
    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


# For Email
class CasperMail:
    @staticmethod
    def send_mail1(email, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=[email], **kwargs)

    @staticmethod
    def send_mail(to, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        email = EmailMessage(subject=subject, body=message, from_email=from_email, to=[to], **kwargs)
        email.send(fail_silently=True)

    # send multi alternative email
    @staticmethod
    def send_multi_alternative_email(to, subject, text_content, html_content, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        email = EmailMultiAlternatives(subject=subject, body=text_content, from_email=from_email, to=[to], **kwargs)
        email.attach_alternative(html_content, "text/html")
        email.send()


class Validators:

    # Method to validate email
    @staticmethod
    def validate_email(email):
        if not email or not email.strip():
            return False
        if not re.match(re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$'), email):
            return False
        return True

    # Method to validate password
    @staticmethod
    def validate_password(password):
        if not password or not password.strip():
            return False
        if not re.match(re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'), password):
            return False
        return True

    # Method to check password and confirm password
    @staticmethod
    def is_password_equal(password, confirm_password):
        return password == confirm_password

    # Method to validate username
    @staticmethod
    def validate_username(username):
        if not username or not username.strip():
            return False
        if not re.match(re.compile(r'^[a-zA-Z0-9_]{3,20}$'), username):
            return False
        return True

    # Method to validate name
    @staticmethod
    def validate_name(name):
        if not name or not name.strip():
            return False
        if not re.match(re.compile(r'^[a-zA-Z]{3,20}$'), name):
            return False
        return True

    # Method to validate phone number
    @staticmethod
    def validate_phone_number(phone_number):
        if not phone_number or not phone_number.strip():
            return False
        if not re.match(re.compile(r'^[0-9]{10}$'), phone_number):
            return False
        return True

    # Method to check if email is already used
    @staticmethod
    def is_email_exists(email, model):
        return model.objects.filter(email=email).exists()

    # Method to check if phone is already used
    @staticmethod
    def is_phone_exists(phone, model):
        return model.objects.filter(phone=phone).exists()

    # Method to check if username is already used
    @staticmethod
    def is_username_exists(username, model):
        return model.objects.filter(username=username).exists()

    # Method to check if gstin is already used
    @staticmethod
    def is_gstin_exists(gstin, model):
        return model.objects.filter(gstin=gstin).exists()
