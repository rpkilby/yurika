# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-07 16:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AIDictionary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('filepath', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Dictionaries',
                'verbose_name': 'Dictionary',
            },
        ),
        migrations.CreateModel(
            name='AIDictionaryObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('dictionary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='words', to='mortar.AIDictionary')),
            ],
            options={
                'verbose_name_plural': 'Words',
                'verbose_name': 'Word',
            },
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotype', models.CharField(choices=[('S', 'Sentence'), ('P', 'Paragraph')], default='P', max_length=1, verbose_name='Annotation Type')),
                ('content', models.TextField()),
                ('begin', models.IntegerField(default=0)),
                ('end', models.IntegerField(default=0)),
                ('score', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('regex', models.CharField(blank=True, max_length=255, null=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('dictionary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mortar.AIDictionary')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='mortar.Category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.URLField()),
                ('crawled_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('assigned', models.ManyToManyField(related_name='projects', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
                ('editors', models.ManyToManyField(related_name='editor_trees', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_trees', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trees', to='mortar.Project')),
            ],
            options={
                'verbose_name_plural': 'Trees',
                'verbose_name': 'Tree',
            },
        ),
        migrations.CreateModel(
            name='DictionaryAnnotation',
            fields=[
                ('annotation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='mortar.Annotation')),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mortar.AIDictionaryObject')),
            ],
            bases=('mortar.annotation',),
        ),
        migrations.CreateModel(
            name='RegexAnnotation',
            fields=[
                ('annotation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='mortar.Annotation')),
            ],
            bases=('mortar.annotation',),
        ),
        migrations.AddField(
            model_name='category',
            name='projecttree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='mortar.ProjectTree'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to='mortar.Document'),
        ),
        migrations.AddField(
            model_name='annotation',
            name='projecttree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to='mortar.ProjectTree'),
        ),
        migrations.AddField(
            model_name='regexannotation',
            name='rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mortar.Category'),
        ),
    ]
