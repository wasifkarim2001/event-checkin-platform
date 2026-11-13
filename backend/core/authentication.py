import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

# No view imports here: DRF loads this module while rest_framework.views is still importing.

logger = logging.getLogger(__name__)


def is_expired(token):
    return token.created < timezone.now() - timedelta(hours=settings.TOKEN_TTL_HOURS)


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if is_expired(token):
            token.delete()
            logger.info("token expired", extra={"user_id": user.pk})
            raise AuthenticationFailed("Token has expired.")
        return user, token
