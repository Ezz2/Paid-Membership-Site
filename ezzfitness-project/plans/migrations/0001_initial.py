# Generated by Django 4.2.4 on 2023-08-16 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FitnessPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=225)),
                ('text', models.TextField()),
                ('premium', models.BooleanField(default=True)),
            ],
        ),
    ]
