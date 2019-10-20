from django.db import models
from account.models import Participants


# Create your models here.
class Game(models.Model):
    player1 = models.ForeignKey(Participants, related_name='player1')
    player2 = models.ForeignKey(Participants, related_name='player2')
    score = models.IntegerField()
    is_playing = models.BooleanField(default=False)


class PrimaryImages(models.Model):
    primary_image = models.URLField(null=False, blank=False)


class SecondaryImages(models.Model):
    secondary_image = models.URLField(null=False, blank=False)


class SharedPair(models.Model):
    sharedplayer1 = models.ForeignKey(Participants, related_name='sharedplayer1')
    sharedplayer2 = models.ForeignKey(Participants, related_name='sharedplayer2')
    is_pair = models.BooleanField(default=False)
