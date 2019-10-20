from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Participants(User):
    gender = models.IntegerField(default=0, choices=(
        (0, 'Male'),
        (1, 'Female')
    ))
    contact_number = models.CharField(max_length=50)
    is_loggedin = models.BooleanField(default=False)
    searching_pair = models.BooleanField(default=False)
