from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# Category
class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

# Auction Listing
class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    users_watching = models.ManyToManyField(User, blank=True, related_name='watchlist')
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="ListingWatchlist")

    def __str__(self):
        return f"{self.title}, {self.starting_bid}"
    
# Bid
class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bidder.user} bid {self.amount} on {self.listing.title}"

# Comments
class Comment(models.Model):
    text = models.CharField(max_length=256)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

