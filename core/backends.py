# custom_auth_backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MultiFieldModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return None
        # Check multiple fields for authentication
        user = User.objects.filter(email=username).first()
        if not user:
            user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            return user
        return None