from django.db import models

# Create your models here.

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=10000)
    emoji = models.CharField(max_length=100)


class Payment(models.Model):
    class Meta:
        ordering = ['-timestamp']

    amount = models.FloatField()
    description = models.CharField(max_length=100000)
    timestamp = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(to='Payer', related_name='payments', on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category',related_name='payments', on_delete=models.CASCADE, null=True)
    update = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return f'{self.creator} заплатил {self.amount} за {self.description}'


class Payer(models.Model):
    first_name = models.CharField(max_length=100000, null=True, blank=True)
    last_name = models.CharField(max_length=100000, null=True, blank=True)
    telegram_id = models.CharField(max_length=100000, unique=True, primary_key=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
