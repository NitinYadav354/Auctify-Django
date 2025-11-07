from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    discription = models.CharField(max_length=255)
    starting_bid = models.IntegerField()
    image_url = models.URLField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=64, blank=True, null=True)
    active = models.BooleanField(default=True)
    listed_by = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="listings"
    )
    created_at = models.DateTimeField(auto_now_add=True)


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        AuctionListing, blank=True, related_name="watchers"
    )


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    item = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="bids"
    )
    current_bid = models.IntegerField()
    bid_time = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    item = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=64)
    comment_time = models.DateTimeField(auto_now_add=True)
