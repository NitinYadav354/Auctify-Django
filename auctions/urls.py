from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/create", views.create_listing, name="create"),
    path(
        "listings/categories/<str:category_name>",
        views.show_categories,
        name="category",
    ),
    path("listing/bid/<int:listing_id>", views.manage_listing, name="bid"),
    path("listing/bid/success/<int:listing_id>", views.bid_success, name="bid_success"),
    path(
        "listing/watchlist/<str:action>/<int:listing_id>",
        views.manage_watchlist,
        name="watchlist",
    ),
    path("user/watchlist/view", views.manage_watchlist, name="view_watchlist"),
    path("listing/bid/<int:listing_id>/close", views.close_auction, name="close"),
]
