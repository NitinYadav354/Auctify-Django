# Auctions Django Project

## Overview

The Auctions Django Project is an online auction platform implemented in Python using the Django web framework. This README provides an overview of the project, its features, structure, Django admin interface configuration, and instructions on how to run it.

## Features

- **User Authentication:** Users can create accounts, log in, and log out securely.
- **Listing Management:** Users can create, view, and manage listings for various items.
- **Bidding:** Users can place bids on listings, and the system keeps track of the highest bid.
- **Category Filtering:** Listings can be filtered by category for easy navigation.
- **Watchlist:** Users can add and remove listings from their watchlist.
- **Comments:** Users can leave comments on listings.
- **Auction Closure:** The system allows for closing auctions and declaring winners.

## Demo

Explore a live demo of the Auctions Django app in action:

[![Auctions Django app Demo](https://i.ytimg.com/vi/bQvHZ2pio2E/maxresdefault.jpg)](https://youtu.be/uXsCpjPq1oI)

## Django Admin Interface

The Django admin interface provides an administrative panel for managing the application's data. Key features include:

- **AuctionListing:** Detailed view of auction listings with various display options.
- **User:** User management with a filterable watchlist field for easy association.
- **Bid:** Bid management, displaying relevant information about each bid.
- **Comment:** Comment management, allowing administrators to review and moderate user comments.

To access the Django admin interface, create a superuser account by running the following commands:

```bash
cd auctions
python manage.py createsuperuser
```

Then, start the development server:

```bash
python manage.py runserver
```

Access the admin interface at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and log in using the superuser credentials.

## Project Structure

- `auctions/`: Main Django application
- `migrations/`: Database migration files
- `static/`: Static files (CSS, images, JavaScript)
- `templates/`: HTML templates
- `admin.py`: Admin configurations
- `models.py`: Database models
- `urls.py`: URL configurations
- `views.py`: Views and controllers
- `commerce/`: Django project settings
  - `settings.py`: Project settings
  - `urls.py`: Project-level URL configurations
  - `manage.py`: Django management script

## How to Run

1. Ensure you have Python installed.
2. Navigate to the project directory:

   ```bash
   cd auctions
   ```

3. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

4. Create a superuser (admin) account:

   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Access the application at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Technologies

- Django
- Bootstrap
- AnimeJS

## Contributing

Feel free to contribute through issues or pull requests.

## License

This project is licensed under the MIT License.
