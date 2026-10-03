# E-Commerce Web

A server-rendered e-commerce website built with Django. Customers can browse and search products, manage a cart, pay for orders through Stripe or Razorpay, view their order history, and buy a monthly Stripe subscription. Staff users get a small dashboard for managing categories, brands, and products with multiple images.

## Highlights

- Custom user model with email login, mobile number, and Stripe customer and subscription IDs
- Registration with password-strength rules and automatic Stripe customer creation
- Password reset by email using Django's token generator
- Product catalog with categories, brands, multiple images per product, and related products
- Shop page with pagination (6 products per page) and a JSON product-name search endpoint
- Per-user cart with quantity updates and item removal through JSON endpoints
- Order history built from the cart after a successful payment
- Stripe cart checkout (the view needs a fix before it works; see Payments and Webhooks)
- Stripe Checkout for monthly subscriptions (three fixed plans: 20, 40, and 60 INR)
- Subscription upgrade, downgrade, and cancellation through the Stripe API
- Stripe webhook that keeps the user's subscription flag in sync
- Razorpay order creation for cart payments (front-end button is currently disabled)
- Subscription middleware that redirects non-subscribers away from `/wishlist/`
- Dashboard for categories, brands, and products, with soft delete for categories and brands
- Service worker that shows an offline page when the network is unavailable
- Celery configured with a Redis broker and the `django-celery-beat` database scheduler

## Technology

| Area | Technology |
| --- | --- |
| Framework | Django 5.0.4 (pinned in `requiments.txt`) |
| Database | SQLite (`db.sqlite3`) |
| Templates | Django templates, custom CSS, vanilla JavaScript, Font Awesome |
| Authentication | Django session authentication with a custom `User` model |
| Payments | Stripe 9.10.0, Razorpay 1.4.2 |
| Background tasks | Celery, Redis, `django-celery-beat` |
| Image handling | Pillow 10.3.0 |
| Encryption | `cryptography` (Fernet) for product IDs in update URLs |
| Environment | `django-dotenv` loads `.env` in `manage.py` |
| Email | Gmail SMTP through Django's SMTP backend |

## Architecture

```text
Browser
  |
  v
Django views (app/views.py) ---- SQLite
  |                               +-- Users, categories, brands
  |                               +-- Products and product images
  |                               +-- Cart items and order items
  |
  +-- Stripe ---------- Customers, Checkout sessions, subscriptions, webhooks
  +-- Razorpay -------- Order creation for cart payments
  +-- Gmail SMTP ------ Password reset emails
  +-- Redis ----------- Celery broker and result backend
```

## Project Structure

```text
ecommerce_web/
├── app/
│   ├── migrations/          Database migrations
│   ├── templatetags/
│   │   └── cutom_filters.py  divide_by_hundred filter for Stripe amounts
│   ├── admin.py             Admin registration for all models
│   ├── commonpassword.py    Password-strength checks
│   ├── decorators.py        login_required, superuser_required, admin_login_required
│   ├── emailhelper.py       Email sending helper
│   ├── middleware.py        SubscriptionMiddleware
│   ├── models.py            User, Category, Brand, Product, ProductImage, CartItem, OrderItems
│   ├── untils.py            Fernet encrypt and decrypt helpers
│   ├── url.py               Application routes
│   └── views.py             All views, payment, and webhook handling
├── ecommerce_web/
│   ├── celery.py            Celery application
│   ├── settings.py          Django settings
│   ├── urls.py              Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── static/                  CSS, images, script.js, service-worker.js
├── tamplates/               HTML templates
├── manage.py
└── requiments.txt
```

## Data Model

| Model | Purpose |
| --- | --- |
| `User` | Extends `AbstractUser`; logs in with `email`; stores `mobile_number`, `stripe_customer_id`, `stripe_subscription_id`, and `is_subscrib` |
| `Category` | Product category with an `isDeleted` flag (`True` means visible, `False` means soft-deleted) |
| `Brand` | Product brand with the same `isDeleted` flag |
| `Product` | Name, description, rate, category, brand, and the user who created it |
| `ProductImage` | Image files for a product, stored under `media/product_images/`; the file is removed from disk on delete |
| `CartItem` | A user's cart line with quantity and cached image URL |
| `OrderItems` | A purchased line item copied from the cart after payment |

## Routes

All routes are defined in `app/url.py` and included at the site root. The Django admin is available at `/admin/`.

### Storefront

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Home page with all products |
| GET | `/shop/` | Paginated product list; supports `?q=` filter and `?page=` |
| GET | `/search/?q=<text>` | JSON list of matching product names |
| GET | `/sproduct/<product_id>/` | Product detail page with images and products from the same category |
| GET | `/blog/` | Static blog page |
| GET | `/about/` | Static about page |
| GET | `/contact/` | Static contact page |
| GET | `/wishlist/` | Placeholder page; requires an active subscription for logged-in users |
| GET | `/network_error/` | Offline page used by the service worker |

### Accounts

| Method | Path | Description |
| --- | --- | --- |
| GET, POST | `/signup/` | Register a user and create a matching Stripe customer |
| GET, POST | `/login/` | Log in with email and password |
| GET | `/signout/` | Log out |
| GET, POST | `/userprofile/` | View and update name, username, email, and mobile number |
| GET, POST | `/sendlink/` | Send a password reset link by email |
| GET, POST | `/resetpassword/<uid>/<token>/` | Set a new password |

### Cart and Orders

| Method | Path | Description |
| --- | --- | --- |
| GET | `/cart/` | View the cart (login required) |
| GET | `/cart/<product_id>` | Add a product to the cart and redirect to `/cart/` |
| POST | `/update_quantity_cart/` | JSON body `cart_item_id`, `update_quantity` |
| POST | `/remove_from_cart/` | JSON body `cart_item_id` |
| POST | `/pay_order/` | Create a Razorpay order from JSON body `amount` |
| GET | `/success_payment/` | Move cart items to orders after Razorpay payment |
| GET | `/checkout_session/<user_id>` | Start Stripe payment for the cart |
| GET | `/pay_success?session_id=<id>` | Move cart items to orders after Stripe payment |
| GET | `/orders/` | List the user's ordered items |

### Subscriptions

| Method | Path | Description |
| --- | --- | --- |
| GET | `/subscriptions/` | Show the three plans and the user's current Stripe subscription |
| GET | `/checkout_subscription/<amount>/` | Create a Stripe Checkout session in subscription mode |
| GET | `/subscription_pay_succcess/?session_id=<id>` | Save the subscription ID and mark the user as subscribed |
| GET | `/update_subscription/<amount>/` | Switch the subscription to a new monthly price |
| GET | `/cancel_subscription/` | Cancel the Stripe subscription |
| POST | `/stripe_webhook/` | Stripe webhook endpoint |

### Dashboard

The dashboard link is shown in the header for superusers.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/dashboard/` | Dashboard home |
| GET, POST | `/category/` | Create a category |
| GET | `/category_view/` | List visible categories |
| POST | `/category_update/` | JSON body `category_id`, `categoryName` |
| POST | `/category_delete/` | Soft-delete; JSON body `category_id` |
| GET, POST | `/brand/` | Create a brand |
| GET | `/brand_view/` | List visible brands |
| POST | `/brand_update/` | JSON body `brand_id`, `brand` |
| POST | `/brand_delete/` | Soft-delete; JSON body `brand_id` |
| GET, POST | `/productadd/` | Create a product with one or more images |
| GET | `/product_view/` | List products with encrypted IDs for editing |
| GET, POST | `/product_update/<encrypted_id>/` | Update a product and replace its images |
| POST | `/product_delete/` | Delete a product; JSON body `product_id` |

## Payments and Webhooks

### Stripe customer

When a user registers, `stripe.Customer.create` is called with the user's email and username, and the returned ID is saved in `User.stripe_customer_id`.

### Stripe subscription flow

```text
/subscriptions/
  |  user picks a plan (20, 40, or 60)
  v
/checkout_subscription/<amount>/
  |  stripe.checkout.Session.create(mode="subscription",
  |  monthly INR price, customer=stripe_customer_id,
  |  client_reference_id=user.id)
  v
Stripe hosted checkout
  |
  v
/subscription_pay_succcess/?session_id=...
  |  retrieves the session, saves session.subscription to
  |  stripe_subscription_id, sets is_subscrib=True
  v
/subscriptions/
```

- **Change plan:** `/update_subscription/<amount>/` creates a new Stripe product and monthly price, then calls `stripe.Subscription.modify` on the existing subscription item.
- **Cancel:** `/cancel_subscription/` calls `stripe.Subscription.delete` and sets `is_subscrib=False`.

### Stripe webhook

`/stripe_webhook/` verifies the `Stripe-Signature` header with `STRIPE_WEBHOOK_SECRET` and then looks up the user by `stripe_customer_id`:

| Event | Effect |
| --- | --- |
| `customer.subscription.created` | `is_subscrib = True` |
| `invoice.payment_succeeded` | `is_subscrib = True` |
| `customer.subscription.deleted` | `is_subscrib = False` |
| `invoice.payment_failed` | `is_subscrib = False` |

### Stripe cart payment

The cart page's "proceed to checkout" button submits to `/checkout_session/<user_id>`. The view adds up the cart total in paise and is meant to send the user to Stripe with a success URL of `/pay_success?session_id=...`. After payment, `pay_success` retrieves the Checkout session, copies cart items into `OrderItems`, and clears the cart.

The view currently passes Checkout Session arguments (`line_items`, `mode`, `success_url`) to `stripe.PaymentIntent.create`, and Stripe rejects that call. It needs to use `stripe.checkout.Session.create` before this flow works.

### Razorpay cart payment

The cart template has a `payrazorpay()` function that loads `checkout.js` from Razorpay:

1. `POST /pay_order/` creates a Razorpay order in INR with `payment_capture=1`.
2. The Razorpay checkout modal opens with the returned order ID.
3. On success, the browser goes to `/success_payment/`, which copies cart items into `OrderItems` and clears the cart.

The Razorpay button is commented out in `tamplates/cart.html`, so the Stripe button is the active checkout path. The payment signature is not verified on the server.

## Celery

`ecommerce_web/celery.py` defines the Celery application `ecommerce_web` with these settings:

- Broker and result backend: `redis://localhost:6379/0`
- Scheduler: `django_celery_beat.schedulers:DatabaseScheduler`
- Timezone: `Asia/Kolkata`
- `beat_schedule` is empty, and `autodiscover_tasks()` is enabled

There is no `tasks.py`. The only tasks are the sample `debug_task` and `task_fun` in `celery.py`, so the site does not need a worker to run. Periodic tasks can be added through the `django-celery-beat` models in the Django admin.

## Getting Started

### Requirements

- Python 3.13 (the bundled virtual environment was created with 3.13.5)
- Redis, if you plan to run Celery
- A Stripe test account and the Stripe CLI for webhooks
- A Razorpay test account, if you enable the Razorpay button
- A Gmail account with an app password for password reset emails

### Installation

```powershell
git clone <your-repository-url>
cd ecommerce_web

python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requiments.txt
```

`requiments.txt` does not list the Celery packages, but `django_celery_beat` is in `INSTALLED_APPS`. Install them separately or Django will not start:

```powershell
pip install celery django-celery-beat redis
```

### Environment Variables

Create a `.env` file in the project root. It is loaded by `django-dotenv` when you run `manage.py` and is listed in `.gitignore`.

```env
EMAIL_USER=your-gmail-address
EMAIL_PASS=your-gmail-app-password
```

| Variable | Used for |
| --- | --- |
| `EMAIL_USER` | `EMAIL_HOST_USER` for Gmail SMTP |
| `EMAIL_PASS` | `EMAIL_HOST_PASSWORD` for Gmail SMTP |

These payment settings are hard-coded in `ecommerce_web/settings.py` rather than read from the environment. Replace them with your own test keys:

| Setting | Purpose |
| --- | --- |
| `STRIPE_SECRET_KEY` | Server-side Stripe API key |
| `STRIPE_PUBLISHABLE_KEY` | Passed to the cart template |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature verification |
| `KEY` | Razorpay key ID |
| `SECRET` | Razorpay key secret |

The Razorpay key ID is also written directly in `tamplates/cart.html`.

### Database Setup

```powershell
python manage.py migrate
python manage.py createsuperuser
```

`createsuperuser` asks for an email, since `email` is the `USERNAME_FIELD`, and a username. Log in at `/login/` with that email to reach `/dashboard/`. Create at least one category and one brand before adding products.

### Run the Development Server

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The Stripe success and cancel URLs and the password reset link point to `127.0.0.1:8000` or `localhost:8000`, so use port 8000.

### Stripe Webhook Forwarding

```powershell
stripe login
stripe listen --forward-to localhost:8000/stripe_webhook/
```

Copy the `whsec_...` signing secret printed by the CLI into `STRIPE_WEBHOOK_SECRET` in `settings.py`.

### Celery Worker and Beat (optional)

Start Redis on `localhost:6379`, then run each process in its own terminal:

```powershell
celery -A ecommerce_web worker -l info --pool=solo
celery -A ecommerce_web beat -l info
```

## Notes

- `DEBUG = True`, `ALLOWED_HOSTS = []`, and the `SECRET_KEY` are hard-coded in `settings.py`, so this configuration is for local development only.
- Uploaded media is served by Django only when `DEBUG` is `True`.
- The project has no automated tests (`app/tests.py` is empty).
