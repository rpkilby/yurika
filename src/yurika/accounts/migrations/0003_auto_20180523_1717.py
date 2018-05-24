# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-23 17:17
from __future__ import unicode_literals

import yurika.accounts.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='account',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'base_manager_name': 'objects'},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', yurika.accounts.models.UserManager()),
            ],
        ),
    ]
