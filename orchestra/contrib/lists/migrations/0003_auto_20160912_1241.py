# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-09-12 10:41
from __future__ import unicode_literals

from django.db import migrations, models
import orchestra.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0002_auto_20160912_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='address_name',
            field=models.CharField(blank=True, max_length=64, validators=[orchestra.core.validators.validate_name], verbose_name='address name'),
        ),
        migrations.AlterField(
            model_name='list',
            name='name',
            field=models.CharField(help_text='Default list address &lt;name&gt;@grups.pangea.org', max_length=64, unique=True, validators=[orchestra.core.validators.validate_name], verbose_name='name'),
        ),
    ]
