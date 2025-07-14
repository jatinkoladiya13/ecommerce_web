# E-Commerce Website – Django Project

A complete e-commerce web application built with **Django**, featuring product browsing, user authentication, cart and wishlist management, payment integration (Stripe), order tracking, and subscription plans.

---
## Key Features

### User Functions
- `GET /signup/` – Register new user
- `POST /login/` – Login existing user
- `GET /signout/` – Logout
- `GET /userprofile/` – View user profile
- `POST /sendlink/` – Send password reset link
- `GET /resetpassword/<uid>/<token>/` – Reset password

---

### Shopping Features
- `GET /shop/` – Browse all products
- `GET /sproduct/<id>/` – View single product details
- `GET /search/` – Search products
- `GET /category/` – Manage product categories
- `GET /brand/` – Manage product brands
- `POST /productadd/` – Add product (admin)
- `GET /product_view/` – View product list (admin)
- `POST /product_update/<id>/` – Update product
- `POST /product_delete/` – Delete product

---

### Cart & Wishlist
- `GET /cart/` – View cart
- `POST /cart/<product_id>` – Add to cart
- `POST /update_quantity_cart/` – Update cart item quantity
- `POST /remove_from_cart/` – Remove item from cart
- `GET /wishlist/` – View wishlist (basic setup)

---

### Orders & Payments
- `POST /pay_order/` – Start payment process
- `GET /success_payment/` – Redirect after payment success
- `GET /orders/` – View all user orders
- `GET /checkout_session/<user_id>` – Initiate Stripe checkout session
- `GET /pay_success` – Payment success page

---

### Subscriptions
- `GET /subscriptions/` – Show available subscription plans
- `GET /checkout_subscription/<amount>/` – Start subscription payment
- `GET /subscription_pay_succcess/` – Subscription payment success
- `POST /stripe_webhook/` – Handle Stripe webhooks
- `GET /update_subscription/<amount>/` – Update subscription plan
- `GET /cancel_subscription/` – Cancel active subscription

---

### Other Pages
- `GET /` – Homepage
- `GET /blog/` – Blog page
- `GET /about/` – About Us
- `GET /contact/` – Contact page
- `GET /dashboard/` – Admin/User dashboard
- `GET /network_error/` – Fallback error page

---

## Tech Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, Bootstrap, JavaScript
- **Database**: SQLite (dev)
- **Payments**: Stripe and razorpay Integration
- **Authentication**: Session-based
- **Subscriptions**: Stripe recurring billing

---
