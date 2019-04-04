# Generated by Django 2.2 on 2019-04-04 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_auto_20190403_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payer',
            name='show_cats',
            field=models.NullBooleanField(verbose_name='Show categories when the payment is registered'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='budget.Category'),
        ),
    ]
