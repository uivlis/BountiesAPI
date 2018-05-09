# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-05 20:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('analytics', '0001_initial'), ('analytics', '0002_auto_20180502_0054'), ('analytics', '0003_auto_20180503_0305'), ('analytics', '0004_auto_20180503_0342'), ('analytics', '0005_bountiestimeline_schema'), ('analytics', '0006_auto_20180504_0536')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BountiesTimeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('bounties_issued', models.PositiveIntegerField(default=0)),
                ('fulfillments_submitted', models.PositiveIntegerField(default=0)),
                ('fulfillments_accepted', models.PositiveIntegerField(default=0)),
                ('fulfillments_pending_acceptance', models.PositiveIntegerField(default=0)),
                ('fulfillment_acceptance_rate', models.FloatField(default=0)),
                ('bounty_fulfilled_rate', models.FloatField(default=0)),
                ('avg_fulfiller_acceptance_rate', models.FloatField(default=0)),
                ('avg_fulfillment_amount', models.FloatField(default=0)),
                ('total_fulfillment_amount', models.DecimalField(decimal_places=0, default=0, max_digits=64)),
                ('bounty_draft', models.PositiveIntegerField(default=0)),
                ('bounty_active', models.PositiveIntegerField(default=0)),
                ('bounty_completed', models.PositiveIntegerField(default=0)),
                ('bounty_expired', models.PositiveIntegerField(default=0)),
                ('bounty_dead', models.PositiveIntegerField(default=0)),
                ('bounties_issued_cum', models.PositiveIntegerField(default=0)),
                ('fulfillments_accepted_cum', models.PositiveIntegerField(default=0)),
                ('fulfillments_submitted_cum', models.PositiveIntegerField(default=0)),
                ('schema', models.CharField(blank=True, max_length=64)),
            ],
        ),
    ]