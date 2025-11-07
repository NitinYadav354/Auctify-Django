from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max, Count
from .utils import get_current_price

from .models import *
from .forms import *


def index(request):
    listings = AuctionListing.objects.all()
    current_price = get_current_price(listings)
    listings = [listings[i : i + 3] for i in range(0, len(listings), 3)]

    if request.user.is_authenticated:
        watchlist = User.objects.get(pk=request.user.id).watchlist.all()
        watchlist_count = watchlist.count()
    else:
        watchlist_count = None

    return render(
        request,
        "auctions/index.html",
        {
            "listings": listings,
            "current_price": current_price,
            "watchlist_count": watchlist_count,
        },
    )


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if "next" in request.session and request.session["next"] != None:
                next_url = request.session["next"]
            else:
                next_url = request.POST.get("next", reverse("index"))
            return HttpResponseRedirect(next_url)
        else:
            if "next" not in request.session and request.POST.get("next") != None:
                request.session["next"] = request.POST.get("next")
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        if request.GET.get("next"):
            request.session["next"] = request.GET.get("next")
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        return HttpResponseRedirect(reverse("login"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url="/login")
def create_listing(request):
    watchlist = User.objects.get(pk=request.user.id).watchlist.all()
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            discription = form.cleaned_data["discription"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            listed_by = request.POST.get("listed_by")
            listing = AuctionListing(
                title=title,
                discription=discription,
                starting_bid=starting_bid,
                image_url=image_url,
                category=category,
                listed_by=User.objects.get(username=listed_by),
            )
            listing.save()
            return HttpResponseRedirect(reverse("bid", args=[listing.id]))
        else:
            return render(
                request,
                "auctions/create_listing.html",
                {
                    "form": form,
                    "watchlist_count": watchlist.count(),
                },
            )

    return render(
        request,
        "auctions/create_listing.html",
        {
            "form": CreateListingForm(),
            "watchlist_count": watchlist.count(),
        },
    )


def show_categories(request, category_name):
    listings = AuctionListing.objects.filter(category=category_name)
    current_price = get_current_price(listings)
    watchlist = []
    if request.user.is_authenticated:
        watchlist = User.objects.get(pk=request.user.id).watchlist.all()

    if request.GET.get("category"):
        category_name = request.GET.get("category")
        query = request.GET.get("q")
        if category_name == "Any":
            listings = AuctionListing.objects.filter(title__icontains=query)
            current_price = get_current_price(listings)
        else:
            listings = AuctionListing.objects.filter(
                category=category_name, title__icontains=query
            )
            current_price = get_current_price(listings)

    return render(
        request,
        "auctions/show_category.html",
        {
            "listings": listings,
            "current_price": current_price,
            "category_name": category_name,
            "watchlist_count": len(watchlist),
        },
    )


@login_required(login_url="/login")
def manage_listing(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(item=listing_id)
    watchlist_count = User.objects.get(pk=request.user.id).watchlist.all()
    if request.user.watchlist.filter(pk=listing_id).exists():
        watchlist = True
    else:
        watchlist = False

    number_of_bids = Bid.objects.filter(item=listing_id).count()
    if number_of_bids > 0:
        latest_bid = Bid.objects.filter(item=listing_id).aggregate(Max("bid_time"))
        latest_bid_time = latest_bid["bid_time__max"]
        latest_bid = Bid.objects.filter(
            item=listing_id, bid_time=latest_bid_time
        ).first()
        bidder = User.objects.get(username=latest_bid.bidder)
        bidder_name = bidder.username
        latest_bid = latest_bid.current_bid
    else:
        latest_bid = None
        latest_bid_time = listing.created_at
        bidder_name = None

    if listing.active:
        close_auction = False
        winner_email = None
        seller_email = None
    else:
        winner_email = bidder.email
        seller_email = listing.listed_by.email
        close_auction = True

    if request.method == "POST" and listing.active:
        form = BidForm(request.POST)

        if form.is_valid():
            form_has_error = False
            if form.cleaned_data["comment"]:
                Comment(
                    item=listing,
                    author=request.user,
                    comment=request.POST.get("comment"),
                ).save()
                return HttpResponseRedirect(reverse("bid_success", args=[listing_id]))

            if form.cleaned_data["bid"]:
                if request.user.username != listing.listed_by.username:
                    bid = form.cleaned_data["bid"]
                    starting_price = listing.starting_bid
                    if latest_bid:
                        if bid > latest_bid:
                            Bid(
                                bidder=request.user, item=listing, current_bid=bid
                            ).save()
                        else:
                            form_has_error = True
                            form.add_error(
                                "bid", "Bid should be larger than the current bid."
                            )
                    else:
                        if bid >= starting_price:
                            Bid(
                                bidder=request.user, item=listing, current_bid=bid
                            ).save()
                        else:
                            form_has_error = True
                            form.add_error(
                                "bid", "Bid should be as large as the starting bid."
                            )
                else:
                    form_has_error = True
                    form.add_error("bid", "You can't bid on your listings.")

                if form_has_error:
                    return render(
                        request,
                        "auctions/bid.html",
                        {
                            "form": form,
                            "listing": listing,
                            "latest_bid": latest_bid,
                            "latest_bid_time": latest_bid_time,
                            "bidder_name": bidder_name,
                            "number_of_bids": number_of_bids,
                            "comments": comments,
                            "watchlist": watchlist,
                            "watchlist_count": watchlist_count.count(),
                            "close": close_auction,
                            "winner_email": winner_email,
                            "seller_email": seller_email,
                        },
                    )
                else:
                    return HttpResponseRedirect(
                        reverse("bid_success", args=[listing_id])
                    )
        else:
            return render(
                request,
                "auctions/bid.html",
                {
                    "form": form,
                    "listing": listing,
                    "latest_bid": latest_bid,
                    "latest_bid_time": latest_bid_time,
                    "bidder_name": bidder_name,
                    "number_of_bids": number_of_bids,
                    "comments": comments,
                    "watchlist": watchlist,
                    "watchlist_count": watchlist_count.count(),
                    "close": close_auction,
                    "winner_email": winner_email,
                    "seller_email": seller_email,
                },
            )

    return render(
        request,
        "auctions/bid.html",
        {
            "form": BidForm(),
            "listing": listing,
            "latest_bid": latest_bid,
            "latest_bid_time": latest_bid_time,
            "bidder_name": bidder_name,
            "number_of_bids": number_of_bids,
            "comments": comments,
            "watchlist": watchlist,
            "watchlist_count": watchlist_count.count(),
            "close": close_auction,
            "winner_email": winner_email,
            "seller_email": seller_email,
        },
    )


@login_required(login_url="/login")
def bid_success(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(item=listing_id)
    watchlist_count = User.objects.get(pk=request.user.id).watchlist.all()
    if request.user.watchlist.filter(pk=listing_id).exists():
        watchlist = True
    else:
        watchlist = False

    number_of_bids = Bid.objects.filter(item=listing_id).count()
    if number_of_bids > 0:
        latest_bid = Bid.objects.filter(item=listing_id).aggregate(Max("bid_time"))
        latest_bid_time = latest_bid["bid_time__max"]
        latest_bids = Bid.objects.filter(item=listing_id, bid_time=latest_bid_time)
        latest_bid = latest_bids.first()
        bidder = User.objects.get(username=latest_bid.bidder)
        bidder_name = bidder.username
        latest_bid = latest_bid.current_bid
    else:
        latest_bid = None
        latest_bid_time = listing.created_at
        bidder_name = None

    if listing.active:
        close_auction = False
        winner_email = None
        seller_email = None
    else:
        winner_email = bidder.email
        seller_email = listing.listed_by.email
        close_auction = True

    return render(
        request,
        "auctions/bid.html",
        {
            "form": BidForm(),
            "listing": listing,
            "latest_bid": latest_bid,
            "latest_bid_time": latest_bid_time,
            "bidder_name": bidder_name,
            "number_of_bids": number_of_bids,
            "comments": comments,
            "watchlist": watchlist,
            "watchlist_count": watchlist_count.count(),
            "close": close_auction,
            "winner_email": winner_email,
            "seller_email": seller_email,
        },
    )


@login_required(login_url="/login")
def manage_watchlist(request, action=None, listing_id=None):
    if listing_id:
        listing = AuctionListing.objects.get(pk=listing_id)

    if action == "add":
        request.user.watchlist.add(listing)
    elif action == "remove":
        request.user.watchlist.remove(listing)
    else:
        watchlist = User.objects.get(pk=request.user.id).watchlist.all()
        current_price = get_current_price(watchlist)
        return render(
            request,
            "auctions/watchlist.html",
            {
                "watchlist_items": watchlist,
                "watchlist_count": watchlist.count(),
                "current_price": current_price,
            },
        )

    return HttpResponseRedirect(reverse("bid_success", args=[listing_id]))


def close_auction(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    listing.active = False
    listing.save()
    return HttpResponseRedirect(reverse("bid", args=[listing_id]))
