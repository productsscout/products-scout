# Generated by Django 5.1.3 on 2024-11-27 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_user_phone_number_user_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='terms_accepted',
            field=models.BooleanField(default=False),
        ),
    ]