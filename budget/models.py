from django.db import models

# Create your models here.

from django.db import models


class Payment(models.Model):
    amount = models.FloatField()
    description = models.CharField(max_length=100000)


