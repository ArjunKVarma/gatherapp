from django.db import models
from django.contrib.gis.db import models as gismodels
from datetime import datetime
from django.utils import timezone
  

class Event(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000, null=True, blank=True, default="None")
    place_name = models.CharField(max_length=100, default="Unspecified")
    date = models.DateField(default=timezone.now().date())
    time = models.TimeField(default=timezone.now().time())
    position = gismodels.PointField(blank=True, null=True, srid=4326, geography=True)
    lat = models.FloatField()
    lng = models.FloatField()
    images = models.ManyToManyField("Image",blank=True)
    category = models.CharField(max_length=100, default="others", verbose_name="")

class Image(models.Model):
    image = models.FileField()