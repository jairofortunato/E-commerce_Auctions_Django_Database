# Generated by Django 4.1.7 on 2023-03-17 18:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_category_listing_users_watching_alter_listing_owner_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='watchlist',
            field=models.ManyToManyField(blank=True, null=True, related_name='ListingWatchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]