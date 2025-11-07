from django.db.models import Max
from .models import *


def get_current_price(listings):
    current_price = {}

    for listing in listings:
        price = listing.bids.aggregate(Max("current_bid"))["current_bid__max"]
        if price is None:
            current_price[listing.id] = listing.starting_bid
        else:
            current_price[listing.id] = price

    return current_price
