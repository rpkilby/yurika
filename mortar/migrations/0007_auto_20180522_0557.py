# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-22 05:57
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.encoder
import jsonfield.fields
import mortar.models


class Migration(migrations.Migration):

    dependencies = [
        ('mortar', '0006_auto_20180509_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crawler',
            name='config',
            field=jsonfield.fields.JSONField(blank=True, default=dict, dump_kwargs={'cls': jsonfield.encoder.JSONEncoder, 'separators': (',', ':')}, help_text='Override settings for Scrapy.', load_kwargs={}, validators=[mortar.models.validate_dict]),
        ),
    ]