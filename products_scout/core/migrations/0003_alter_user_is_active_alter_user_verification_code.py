# Generated by Django 5.1.3 on 2024-11-19 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cart_chathistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='verification_code',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True),
        ),
    ]