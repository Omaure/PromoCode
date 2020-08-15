# Generated by Django 3.1 on 2020-08-14 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promo_codes', '0005_auto_20200814_0243'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='claimedpromocode',
            name='company',
        ),
        migrations.RemoveField(
            model_name='claimedpromocode',
            name='item',
        ),
        migrations.RemoveField(
            model_name='claimedpromocode',
            name='service',
        ),
        migrations.RemoveField(
            model_name='claimedpromocode',
            name='total_price',
        ),
        migrations.RemoveField(
            model_name='claimedpromocode',
            name='typeOfPayment',
        ),
        migrations.AlterField(
            model_name='claimedpromocode',
            name='redeemed',
            field=models.DateTimeField(auto_now_add=True, help_text='Is the ', verbose_name='User'),
        ),
    ]