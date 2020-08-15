# Generated by Django 3.1 on 2020-08-12 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=64)),
                ('code_l', models.CharField(blank=True, max_length=64, unique=True)),
                ('type', models.CharField(choices=[('percent', 'percent'), ('value', 'value')], max_length=16)),
                ('expires', models.DateTimeField(blank=True, null=True)),
                ('value', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('bound', models.BooleanField(default=False)),
                ('repeat', models.IntegerField(default=0)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClaimedPromoCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redeemed', models.DateTimeField(auto_now_add=True)),
                ('promoCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='promo_codes.promocode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]