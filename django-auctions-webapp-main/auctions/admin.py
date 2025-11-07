from django.contrib import admin
from .models import *


# Register your models here.
class AuctionListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "discription",
        "listed_by",
        "starting_bid",
        "image_url",
        "created_at",
        "active",
    )


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email")
    filter_horizontal = ("watchlist",)


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "current_bid", "bidder", "bid_time")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "author", "comment")


admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
