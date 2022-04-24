# Generated by Django 3.0.6 on 2020-06-02 17:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('covidapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('suggestion', models.CharField(blank='true', default='', max_length=400, null='true', verbose_name='Suggestions(if any)_')),
                ('email', models.EmailField(max_length=254, unique='true', verbose_name='Your Email')),
                ('rating', models.IntegerField(blank='true', default=1, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
            ],
        ),
        migrations.DeleteModel(
            name='jsonfiles',
        ),
    ]
