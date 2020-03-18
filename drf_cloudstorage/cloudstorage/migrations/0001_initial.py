# Generated by Django 2.2.11 on 2020-03-18 15:04

import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloudFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False,
                                        verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=50)),
                ('url', models.URLField()),
                ('upload_resp',
                 django.contrib.postgres.fields.jsonb.JSONField(blank=True, editable=False,
                                                                null=True)),
                ('content_field', models.CharField(blank=True, max_length=50, null=True)),
                ('object_id', models.CharField(max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('content_type',
                 models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE,
                                   to='contenttypes.ContentType')),
                ('owner', models.ForeignKey(blank=True, default=None, editable=False, null=True,
                                            on_delete=django.db.models.deletion.SET_NULL,
                                            to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'cloudstorage_file',
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view'),
            },
        ),
    ]
