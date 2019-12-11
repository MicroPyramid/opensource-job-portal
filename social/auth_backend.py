"""Log in to Django without providing a password."""

from django.contrib.auth.backends import ModelBackend
from peeldb.models import User
from django.contrib.auth.hashers import check_password
from django.db.models import Q


class PasswordlessAuthBackend(ModelBackend):

    """Custom authentication in djnago without providing a password."""

    def authenticate(self, username=None, password=None):
        try:
            # Try to find a user matching your username
            user = User.objects.get(Q(username=username) | Q(email=username))
            if password:
                if check_password(password, user.password):
                    return user
                return None
            return user
        except User.DoesNotExist:
            # No user was found, return None - triggers default login failed
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
