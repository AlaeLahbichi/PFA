# Generated by Django 5.2 on 2025-04-13 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0014_remove_colocationoffer_postal_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='Sex',
            field=models.CharField(choices=[('Homme', 'Homme'), ('Femme', 'Femme')], default='Homme', max_length=255),
        ),
    ]
