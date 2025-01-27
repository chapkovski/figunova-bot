# Generated by Django 2.1.7 on 2019-03-05 11:57

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyQuote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('quote', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'ordering': ['-timestamp'],
                'get_latest_by': 'timestamp',
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='currency',
            options={'get_latest_by': 'timestamp', 'ordering': ['-timestamp']},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'get_latest_by': 'timestamp', 'ordering': ['-timestamp']},
        ),
        migrations.RemoveField(
            model_name='currency',
            name='rate',
        ),
    ]
