from django.test import TestCase
from django.urls import reverse

from .models import User, AuctionListing, Bid, Comment


class UserAuthTests(TestCase):
	def test_register_get(self):
		resp = self.client.get(reverse("register"))
		self.assertEqual(resp.status_code, 200)

	def test_register_post_creates_user_and_redirects(self):
		resp = self.client.post(
			reverse("register"),
			{
				"username": "tester",
				"email": "tester@example.com",
				"password": "password123",
				"confirmation": "password123",
			},
		)
		# successful register redirects to login
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(User.objects.filter(username="tester").exists())


class ListingTests(TestCase):
	def setUp(self):
		# Create a user to list items
		self.user = User.objects.create_user(
			username="owner", email="owner@example.com", password="ownerpass"
		)

	def test_create_requires_login(self):
		resp = self.client.get(reverse("create"))
		# login_required should redirect to /login
		self.assertIn(resp.status_code, (301, 302))
		self.assertIn("/login", resp.url)

	def test_create_listing_post(self):
		self.client.login(username="owner", password="ownerpass")
		data = {
			"title": "Test Item",
			"discription": "A nice item",
			"starting_bid": "10",
			"image_url": "",
			"category": "Unspecified",
			"listed_by": "owner",
		}
		resp = self.client.post(reverse("create"), data)
		# after successful creation view redirects to bid page
		self.assertIn(resp.status_code, (301, 302))
		self.assertTrue(AuctionListing.objects.filter(title="Test Item").exists())


class BidTests(TestCase):
	def setUp(self):
		# seller and bidder
		self.seller = User.objects.create_user(
			username="seller", email="s@example.com", password="sellerspwd"
		)
		self.bidder = User.objects.create_user(
			username="bidder", email="b@example.com", password="bidderpwd"
		)
		# create a listing by seller
		self.listing = AuctionListing.objects.create(
			title="Widget",
			discription="Useful",
			starting_bid=10,
			image_url="",
			category="Unspecified",
			listed_by=self.seller,
		)

	def test_bid_successful(self):
		# bidder logs in and posts a valid bid
		self.client.login(username="bidder", password="bidderpwd")
		resp = self.client.post(reverse("bid", args=[self.listing.id]), {"bid": "15"})
		# successful bid should redirect to bid_success
		self.assertIn(resp.status_code, (301, 302))
		self.assertTrue(Bid.objects.filter(item=self.listing, bidder=self.bidder).exists())

	def test_bid_too_low(self):
		self.client.login(username="bidder", password="bidderpwd")
		# bid below starting bid
		resp = self.client.post(reverse("bid", args=[self.listing.id]), {"bid": "5"})
		# should not create a bid
		self.assertFalse(Bid.objects.filter(item=self.listing, bidder=self.bidder).exists())
		# view should re-render the bid form (status 200)
		self.assertEqual(resp.status_code, 200)

	def test_owner_cannot_bid_on_own_item(self):
		self.client.login(username="seller", password="sellerspwd")
		resp = self.client.post(reverse("bid", args=[self.listing.id]), {"bid": "20"})
		self.assertFalse(Bid.objects.filter(item=self.listing, bidder=self.seller).exists())
		self.assertEqual(resp.status_code, 200)


class WatchlistTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="watcher", email="w@example.com", password="watchpwd"
		)
		self.owner = User.objects.create_user(
			username="owner2", email="o2@example.com", password="owner2pwd"
		)
		self.listing = AuctionListing.objects.create(
			title="ToWatch",
			discription="Keep an eye on it",
			starting_bid=10,
			image_url="",
			category="Unspecified",
			listed_by=self.owner,
		)

	def test_add_and_remove_watchlist(self):
		self.client.login(username="watcher", password="watchpwd")
		# add to watchlist
		resp = self.client.get(reverse("watchlist", args=["add", self.listing.id]))
		# should redirect to bid_success
		self.assertIn(resp.status_code, (301, 302))
		self.assertTrue(self.user.watchlist.filter(pk=self.listing.id).exists())

		# view watchlist
		resp = self.client.get(reverse("view_watchlist"))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "ToWatch")

		# remove from watchlist
		resp = self.client.get(reverse("watchlist", args=["remove", self.listing.id]))
		self.assertIn(resp.status_code, (301, 302))
		self.assertFalse(self.user.watchlist.filter(pk=self.listing.id).exists())


class CategoryAndCloseTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="catuser", email="c@example.com", password="catpwd"
		)
		self.listing = AuctionListing.objects.create(
			title="Car 1",
			discription="A car",
			starting_bid=50,
			image_url="",
			category="Cars",
			listed_by=self.user,
		)

	def test_show_category(self):
		resp = self.client.get(reverse("category", args=["Cars"]))
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, "Car 1")

	def test_close_auction(self):
		# closing should set active to False and redirect to bid view
		resp = self.client.get(reverse("close", args=[self.listing.id]))
		self.assertIn(resp.status_code, (301, 302))
		self.listing.refresh_from_db()
		self.assertFalse(self.listing.active)

