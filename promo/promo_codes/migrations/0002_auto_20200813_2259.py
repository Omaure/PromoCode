# Generated by Django 3.1 on 2020-08-13 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promo_codes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promocode',
            name='code',
            field=models.CharField(help_text='Promo Code', max_length=64, verbose_name='Promo Code'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='code_l',
            field=models.CharField(blank=True, help_text='Lower Case Promo Code', max_length=64, unique=True, verbose_name='Lower Case Promo Code'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='created',
            field=models.DateTimeField(auto_now_add=True, help_text='Creation Time', verbose_name='Creation Time'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='type',
            field=models.CharField(choices=[('percent', 'percent'), ('value', 'value')], help_text='Creation Time', max_length=16, verbose_name='Creation Time'),
        ),
        migrations.AlterField(
            model_name='promocode',
            name='updated',
            field=models.DateTimeField(auto_now=True, help_text='Update Time', verbose_name='Update Time'),
        ),
    ]
