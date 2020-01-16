from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    From AbstractUser relevant fields

    username
    first_name
    last_name
    email

    See baseclass for full details
    """

    phone = models.IntegerField(null=True)
    invite_code = models.CharField(max_length=64)

    # Ask non null field values during createsuperuser
    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ['phone']