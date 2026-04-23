from django.db import models
from django.contrib.gis.db import models as gismodels
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    USER_ROLES = (
        ('user', 'User'),
        ('editor', 'Editor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, null=True, blank=True, default="None")
    place_name = models.CharField(max_length=100, default="Unspecified")
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    position = gismodels.PointField(blank=True, null=True, srid=4326, geography=True)
    lat = models.FloatField()
    lng = models.FloatField()
    images = models.ManyToManyField("Image", blank=True)
    category = models.CharField(max_length=100, default="others", verbose_name="")


class Image(models.Model):
    image = models.FileField()