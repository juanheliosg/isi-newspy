# Generated by Django 2.2.9 on 2020-05-05 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200505_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consulta',
            name='fecha_final',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consulta',
            name='fecha_inicial',
            field=models.DateField(blank=True, null=True),
        ),
    ]
