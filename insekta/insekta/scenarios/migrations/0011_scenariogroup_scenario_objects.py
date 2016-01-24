# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-24 17:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scenarios', '0010_remove_scenariogroup_scenarios'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariogroup',
            name='scenario_objects',
            field=models.ManyToManyField(related_name='groups', through='scenarios.ScenarioGroupEntry', to='scenarios.Scenario'),
        ),
    ]
