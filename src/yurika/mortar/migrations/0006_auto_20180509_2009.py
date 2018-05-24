# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-09 20:09
from __future__ import unicode_literals

from django.db import migrations, models
import yurika.mortar.models


class Migration(migrations.Migration):

    dependencies = [
        ('mortar', '0005_auto_20180509_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawler',
            name='allowed_domains',
            field=models.TextField(blank=True, help_text='List of domains to allow (separated by newlines).', validators=[yurika.mortar.models.validate_domains]),
        ),
        migrations.AlterField(
            model_name='crawler',
            name='blocked_domains',
            field=models.TextField(blank=True, help_text='List of domains to block (separated by newlines).', validators=[yurika.mortar.models.validate_domains]),
        ),
    ]
