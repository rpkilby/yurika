# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-23 20:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20180523_1717'),
        ('mortar', '0007_auto_20180522_0557'),
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlerAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Account')),
                ('crawler', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mortar.Crawler')),
            ],
        ),
    ]