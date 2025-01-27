# Generated by Django 2.1.7 on 2019-03-04 21:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('rate', models.FloatField()),
                ('name', models.CharField(max_length=100)),
                ('payer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='currencies', to='budget.Payer')),
            ],
        ),
    ]
