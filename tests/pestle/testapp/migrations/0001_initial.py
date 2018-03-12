# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-12 15:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pestle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Errored',
            fields=[
                ('task_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pestle.Task')),
            ],
            bases=('pestle.task',),
        ),
        migrations.CreateModel(
            name='Finished',
            fields=[
                ('task_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='pestle.Task')),
                ('flag', models.BooleanField(default=False)),
            ],
            bases=('pestle.task',),
        ),
    ]
