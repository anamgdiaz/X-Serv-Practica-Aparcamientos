# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Aparcamiento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entidad', models.CharField(max_length=10)),
                ('nombre', models.CharField(max_length=128)),
                ('descripcion', models.TextField()),
                ('accesibilidad', models.CharField(max_length=1)),
                ('content_url', models.CharField(max_length=256)),
                ('localizacion', models.CharField(max_length=128)),
                ('clase_vial', models.CharField(max_length=128)),
                ('tipo_num', models.CharField(max_length=1)),
                ('num', models.CharField(max_length=10)),
                ('localidad', models.CharField(max_length=32)),
                ('provincia', models.CharField(max_length=32)),
                ('codigo_postal', models.CharField(max_length=32)),
                ('barrio', models.CharField(max_length=32)),
                ('distrito', models.CharField(max_length=32)),
                ('coordenada_x', models.CharField(max_length=32)),
                ('coordenada_y', models.CharField(max_length=32)),
                ('contador_coments', models.IntegerField(default=0)),
                ('telefono', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Comentario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coment', models.TextField()),
                ('aparcamiento', models.ForeignKey(to='aparcamientos.Aparcamiento')),
            ],
        ),
        migrations.CreateModel(
            name='Seleccionados',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha_seleccion', models.DateField()),
                ('aparcamiento', models.ForeignKey(to='aparcamientos.Aparcamiento')),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo_pagina', models.CharField(max_length=25)),
                ('letra', models.FloatField(default=11)),
                ('color', models.CharField(max_length=32)),
                ('nombre', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='seleccionados',
            name='selector',
            field=models.ForeignKey(to='aparcamientos.Usuario'),
        ),
    ]
