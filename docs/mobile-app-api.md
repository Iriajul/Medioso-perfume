# Mad Perfume — Mobile App API Handover

Everything the customer app needs from the backend: auth, catalog, cart and checkout, Stripe payments, loyalty, rewards and notifications. Response shapes and field names below are exactly what the API returns. Samples were captured from the running API; some values (and the reward examples) are illustrative.

| | |
|---|---|
| **Staging base URL** | `https://staging-api.bpmstudio.pt/api/v1` |
| **Interactive docs (Swagger)** | `https://staging-api.bpmstudio.pt/api/docs/` |
| **Stripe publishable key (sandbox)** | Ask the backend owner (`pk_test_…`) |
| **Content type** | `application/json`, except avatar upload (`multipart/form-data`) |

All paths below are relative to the base URL, e.g. `POST /app/auth/login/` → `https://staging-api.bpmstudio.pt/api/v1/app/auth/login/`. Trailing slashes are required.

---

## 1. Conventions

### Authentication

Send the access token on every protected request:

```
Authorization: Bearer <access>
```

- **Access token** lives 60 minutes; **refresh token** lives 30 days.
- Refresh tokens **rotate**: every refresh returns a new `refresh`, and the old one stops working. Always store the newest pair.
- On `401`, call `POST /auth/refresh/` once; if that also fails, send the user to login.
- Access token claims include `user_id`, `full_name`, `email`.

### Pagination

List endpoints marked **paginated** return 20 items per page. Use `?page=2`, `?page=3`…

```json
{ "count": 42, "next": "https://…/?page=2", "previous": null, "results": [ … ] }
```

Categories, banners, cart, and rewards are **not** paginated (plain arrays/objects).

### Errors

| Status | Meaning | Body |
|---|---|---|
| `400` | Validation error | `{ "field": ["message"] }` or `{ "detail": "message" }` (sometimes `{ "detail": ["message"] }`) |
| `401` | Missing/expired token | `{ "detail": "Authentication credentials were not provided." }` |
| `403` | Not allowed | `{ "detail": "…" }` |
| `404` | Not found (or belongs to another user) | `{ "detail": "No … matches the given query." }` |
| `429` | Rate limited | `{ "detail": "Request was throttled. Expected available in N seconds." }` |

Show the first message of whichever field is present. Auth endpoints (register, login, reset, change password) are limited to **10 requests/minute**.

### Formats

- Money is a **string** with 2 decimals: `"160.00"`. Currency is USD.
- Dates are ISO 8601 UTC: `"2026-09-15T11:01:56.357376Z"`; `estimated_delivery` is a date `"2026-09-18"`.
- Image fields are absolute Cloudinary URLs, or `""`/`null` when missing.

### Enum values

| Field | Values |
|---|---|
| Product `concentration` | `eau_de_parfum`, `eau_de_toilette`, `extrait_de_parfum`, `cologne`, `perfume_oil`, `home_fragrance` |
| Category `type` | `classic`, `premium`, `exotic`, `seasonal`, `niche` |
| Order `status` | `pending_payment`, `paid`, `processing`, `shipped`, `delivered`, `cancelled` |
| Order `payment_method` | `card`, `cod` (cash on delivery) |
| Loyalty `tier` | `silver` (0), `gold` (2,500), `platinum` (7,500), `diamond` (15,000) — by lifetime points |
| Transaction `kind` / `reason` / `channel` | `earned`, `redeemed` / `purchase`, `review`, `reward` / `app`, `branch` |
| Reward `category` | `physical_product`, `experience`, `service` |
| Reward `eligibility` | `all`, `gold`, `platinum`, `diamond` (minimum tier) |
| Notification `category` | `offers`, `rewards`, `orders` |
| User `language` | `en`, `ar`, `he` |
| Device `platform` | `ios`, `android` |

---

## 2. Screen → endpoint map

| Screen | Endpoints |
|---|---|
| Sign Up | `POST /app/auth/register/` |
| Login | `POST /app/auth/login/` |
| Reset Password Code | `POST /app/auth/password-reset/code/` → `…/verify/` → `POST /auth/password-reset/confirm/` |
| Home | `GET /app/banners/`, `GET /app/categories/`, `GET /app/products/?is_featured=true`, `GET /app/products/?ordering=-created_at` |
| Product Categories | `GET /app/categories/` |
| Product Listing | `GET /app/products/?category=…&search=…&ordering=…` |
| Product Details | `GET /app/products/{id}/`, `GET /app/products/{id}/reviews/`, `POST /app/saved-products/` |
| Saved Items | `GET /app/saved-products/`, `DELETE /app/saved-products/{product_id}/` |
| Cart | `GET/POST/PATCH/DELETE /app/cart/` |
| Checkout | `GET /app/me/` (prefill address), `POST /app/orders/` + Stripe PaymentSheet |
| Order Success / Order Tracking | `GET /app/orders/{id}/` |
| Branches / Branch Details | `GET /app/branches/?search=…` or `?lat=&lng=`, `GET /app/branches/{id}/` |
| Loyalty | `GET /app/loyalty/` |
| Points History | `GET /app/loyalty/transactions/` |
| Earn Points Information | `GET /app/loyalty/` (`earn_rates`, `tiers`) |
| Rewards / Reward Details | `GET /app/rewards/`, `GET /app/rewards/{id}/`, `POST /app/rewards/{id}/redeem/` |
| Redeemed Rewards List | `GET /app/redemptions/` |
| Notifications | `GET /app/notifications/?category=…`, `PATCH /app/notifications/{id}/`, `POST /app/notifications/read-all/` |
| Profile and Settings / Edit Profile | `GET/PATCH /app/me/` |
| Settings (notification toggles, language) | `PATCH /app/me/` |
| Security | `POST /app/me/change-password/` |
| Logout | `POST /auth/logout/`, `DELETE /app/devices/{token}/` |

---

## 3. Auth

### Register — `POST /app/auth/register/`

Public. Returns tokens, so the user is signed in immediately.

```json
{
  "full_name": "Sophia Laurent",
  "email": "sophia@example.com",
  "phone": "+33612345678",
  "password": "Velvet#Oud2026"
}
```

`201`
```json
{ "access": "eyJhbGciOi…", "refresh": "eyJhbGciOi…" }
```

`400` examples
```json
{ "email": ["An account with this email already exists."] }
{ "phone": ["An account with this phone number already exists."] }
{ "password": ["The password is too similar to the email."] }
```

Password rules: at least 8 characters, at least one number and one special character (`!@#$%`…), not a common password, not all numbers, not too similar to the name/email. The same rules apply to reset and change password.

### Login — `POST /app/auth/login/`

Public. `identifier` is the email **or** phone number.

```json
{ "identifier": "sophia@example.com", "password": "Velvet#Oud2026" }
```

`200`
```json
{ "access": "eyJhbGciOi…", "refresh": "eyJhbGciOi…" }
```

`400`
```json
{ "detail": ["Invalid email/phone or password."] }
```

### Refresh token — `POST /auth/refresh/`

```json
{ "refresh": "eyJhbGciOi…" }
```

`200` — store **both** values (the refresh token rotates)
```json
{ "access": "eyJhbGciOi…", "refresh": "eyJhbGciOi…" }
```

### Logout — `POST /auth/logout/`

Revokes the refresh token. Also unregister the device token (section 4).

```json
{ "refresh": "eyJhbGciOi…" }
```

`200` `{}`

### Forgot password (3 steps)

**1. Send code** — `POST /app/auth/password-reset/code/`

```json
{ "email": "sophia@example.com" }
```

`204` (always, even for unknown emails). The user receives a 6-digit code, valid for **10 minutes**.

**2. Verify code** — `POST /app/auth/password-reset/verify/`

```json
{ "email": "sophia@example.com", "code": "482913" }
```

`200`
```json
{ "uid": "Mjc", "token": "cx2k1a-6f0c1d3e9b8a7c6d5e4f3a2b1c0d9e8f" }
```

`400` — wrong/expired code (a code locks after 5 wrong attempts; request a new one)
```json
{ "code": "Invalid or expired code." }
```

**3. Set new password** — `POST /auth/password-reset/confirm/`

```json
{ "uid": "Mjc", "token": "cx2k1a-6f0c…", "password": "Amber#Musk2027" }
```

`204`. All existing sessions are signed out; log in with the new password.

---

## 4. Profile, settings, devices

### Get profile — `GET /app/me/`

`200`
```json
{
  "id": 27,
  "full_name": "Sophia Laurent",
  "email": "sophia@example.com",
  "phone": "+33612345678",
  "shipping_address": "",
  "avatar_url": "",
  "language": "en",
  "push_enabled": true,
  "notify_collections": true,
  "notify_rewards": true,
  "notify_orders": true,
  "points_balance": 0,
  "tier": "silver"
}
```

### Update profile / settings — `PATCH /app/me/`

Send only the fields that change. Editable: `full_name`, `email`, `phone`, `shipping_address`, `language`, `push_enabled`, `notify_collections`, `notify_rewards`, `notify_orders`, `avatar`.

```json
{ "shipping_address": "14 Rue de la Paix, Paris", "language": "en", "notify_rewards": false }
```

`200` — the full profile (same shape as GET).

**Avatar upload:** send `multipart/form-data` with an `avatar` file (PNG/JPG/WebP, max 10 MB). The response contains the new `avatar_url`.

`400` examples
```json
{ "phone": ["An account with this phone number already exists."] }
{ "avatar": ["Image must be PNG, JPG or WebP."] }
```

### Change password — `POST /app/me/change-password/`

```json
{ "current_password": "Velvet#Oud2026", "password": "Amber#Musk2027" }
```

`204`. Refresh tokens are revoked (signed out everywhere): send the user to login.

### Register device for push — `POST /app/devices/`

Call after login and whenever the FCM token changes.

```json
{ "token": "fcm-registration-token", "platform": "ios" }
```

`201`
```json
{ "token": "fcm-registration-token", "platform": "ios" }
```

### Remove device — `DELETE /app/devices/{token}/`

Call on logout. `204`.

> Push delivery goes live once Firebase credentials are added on the backend; registering tokens now is safe.

---

## 5. Catalog

Catalog endpoints are **public**. Send the token anyway when signed in, so `is_saved` is correct.

### Categories — `GET /app/categories/`

`200` (array)
```json
[
  {
    "id": 7,
    "name": "Floral",
    "type": "classic",
    "description": "Light, blooming, romantic",
    "image_url": "https://res.cloudinary.com/…/categories/imqd6bpngwlw8kfkl5an.jpg"
  }
]
```

### Home banners — `GET /app/banners/`

Only banners active today. `200` (array)
```json
[
  {
    "id": 1,
    "title": "Summer Essence 2024",
    "image_url": "https://res.cloudinary.com/…/banners/sfqwvmb4z7ebjcsm3he0.jpg",
    "starts_on": "2026-09-12",
    "ends_on": "2026-09-27"
  }
]
```

### Products — `GET /app/products/` (paginated)

| Query param | Example | Notes |
|---|---|---|
| `search` | `?search=oud` | name, brand, scent notes, description, category |
| `category` | `?category=7` | category id |
| `concentration` | `?concentration=eau_de_parfum` | |
| `brand` | `?brand=MAD PERFUME` | case-insensitive |
| `min_price` / `max_price` | `?min_price=100&max_price=250` | |
| `is_featured` | `?is_featured=true` | |
| `ordering` | `price`, `-price`, `-created_at` (new arrivals, default), `-sold` (best sellers), `-rating` | |

`200`
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 9,
      "name": "Alpine Mist",
      "brand": "MAD PERFUME",
      "category": 11,
      "category_name": "Musk",
      "concentration": "extrait_de_parfum",
      "size": "100ml",
      "notes": ["Oud", "Saffron"],
      "price": "160.00",
      "image_url": "https://res.cloudinary.com/…/products/cluklxv5usuv7vjc0ab3.jpg",
      "rating": 4.5,
      "reviews_count": 12,
      "is_saved": false,
      "in_stock": true
    }
  ]
}
```

### Product detail — `GET /app/products/{id}/`

Same fields as the list, plus `description`, all `image_urls`, and the boutiques that stock it.

`200`
```json
{
  "id": 9,
  "name": "Alpine Mist",
  "brand": "MAD PERFUME",
  "category": 11,
  "category_name": "Musk",
  "concentration": "extrait_de_parfum",
  "size": "100ml",
  "notes": ["Oud", "Saffron"],
  "price": "160.00",
  "image_url": "https://res.cloudinary.com/…/cluklxv5usuv7vjc0ab3.jpg",
  "rating": 4.5,
  "reviews_count": 12,
  "is_saved": false,
  "in_stock": true,
  "description": "Alpine Mist notes",
  "image_urls": ["https://res.cloudinary.com/…/cluklxv5usuv7vjc0ab3.jpg"],
  "branches": [
    { "id": 5, "name": "Dubai Mall", "city": "Dubai" },
    { "id": 3, "name": "London Bond St.", "city": "London" }
  ]
}
```

### Reviews — `GET /app/products/{id}/reviews/` (paginated)

`200`
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user_name": "Sophia Laurent",
      "rating": 5,
      "comment": "A masterpiece of balance.",
      "created_at": "2026-09-15T11:01:56.583965Z"
    }
  ]
}
```

### Write a review — `POST /app/products/{id}/reviews/` 🔒

Allowed once per product, only for products in the user's **delivered** orders. Earns **+50 points**.

```json
{ "rating": 5, "comment": "A masterpiece of balance." }
```

`201` — the review (same shape as above).

`400`
```json
{ "detail": "You can review products from your delivered orders." }
{ "detail": "You have already reviewed this product." }
```

### Saved items 🔒

| Action | Request | Response |
|---|---|---|
| List (paginated) | `GET /app/saved-products/` | Product list items (same shape as `/app/products/`) with `is_saved: true` |
| Save | `POST /app/saved-products/` `{ "product": 9 }` | `201` `{ "product": 9 }` (saving twice is fine) |
| Unsave | `DELETE /app/saved-products/{product_id}/` | `204` |

---

## 6. Boutiques

### Branches — `GET /app/branches/` (paginated, public)

- `?search=paris` — name, city, country, address.
- `?lat=48.86&lng=2.33` — nearest first (only branches with coordinates).
- Default order: flagship first, then by name.

`200`
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "name": "Paris Flagship",
      "is_flagship": true,
      "address": "75 Avenue des Champs-Élysées, 75008 Paris, France",
      "city": "Paris",
      "country": "France",
      "phone": "+33 1 45 61 98 01",
      "email": "paris@madperfume.com",
      "weekday_opens": "10:00:00",
      "weekday_closes": "21:00:00",
      "sunday_opens": "11:00:00",
      "sunday_closes": "19:00:00",
      "latitude": "48.871400",
      "longitude": "2.302000",
      "image_url": "https://res.cloudinary.com/…/branches/z1fcrbcmubb0b3xkjdju.jpg"
    }
  ]
}
```

### Branch detail — `GET /app/branches/{id}/`

Same object as a list item.

---

## 7. Cart 🔒

### Get cart — `GET /app/cart/`

`200`
```json
{
  "items": [
    {
      "id": 2,
      "product": 9,
      "name": "Alpine Mist",
      "category_name": "Musk",
      "variant": "100ml / Extrait de Parfum",
      "price": "160.00",
      "image_url": "https://res.cloudinary.com/…/cluklxv5usuv7vjc0ab3.jpg",
      "quantity": 1,
      "line_total": "160.00"
    }
  ],
  "items_count": 1,
  "subtotal": "160.00"
}
```

### Add to cart — `POST /app/cart/`

Adding a product already in the cart **increases** its quantity.

```json
{ "product": 9, "quantity": 1 }
```

`201` — the cart item (same shape as `items[]`). `category_name` is the collection label shown above the product name on the Cart screen.

`400`
```json
{ "quantity": ["Only 14 left in stock."] }
```

### Change quantity — `PATCH /app/cart/{item_id}/`

```json
{ "quantity": 2 }
```

`200` — the updated cart item (`line_total` recalculated).

### Remove item — `DELETE /app/cart/{item_id}/`

`204`

> Tax (8%) and shipping (currently free) are calculated at checkout. Show the cart `subtotal` on the Cart screen, and the order totals returned by checkout on the payment step.

---

## 8. Checkout & orders 🔒

### Place order — `POST /app/orders/`

Turns the whole cart into an order, reserves stock, and empties the cart.

**Headers**

```
Authorization: Bearer <access>
Idempotency-Key: 6f1c2b8e-5d4a-4c3b-9a8f-1e2d3c4b5a69
```

**Body**

```json
{
  "shipping_name": "Sophia Laurent",
  "shipping_address": "14 Rue de la Paix",
  "shipping_city": "Paris",
  "shipping_phone": "+33612345678",
  "payment_method": "card"
}
```

| Field | Required | Notes |
|---|---|---|
| `shipping_name` | yes | |
| `shipping_address` | yes | |
| `shipping_city` | yes | |
| `shipping_phone` | no | defaults to the profile phone |
| `payment_method` | yes | `card` or `cod` |

**`201` (new order)** or **`200` (same Idempotency-Key sent again)**

```json
{
  "id": 35,
  "number": "MAD-00035",
  "status": "pending_payment",
  "channel": "app",
  "branch_name": null,
  "created_at": "2026-09-15T11:01:56.357376Z",
  "estimated_delivery": "2026-09-18",
  "items": [
    {
      "product": 9,
      "product_name": "Alpine Mist",
      "variant": "100ml / Extrait de Parfum",
      "notes": ["Oud", "Saffron"],
      "image_url": "https://res.cloudinary.com/…/cluklxv5usuv7vjc0ab3.jpg",
      "unit_price": "160.00",
      "quantity": 2,
      "line_total": "320.00"
    }
  ],
  "events": [
    { "status": "pending_payment", "created_at": "2026-09-15T11:01:56.361788Z" }
  ],
  "subtotal": "320.00",
  "shipping_fee": "0.00",
  "tax": "25.60",
  "total": "345.60",
  "payment_method": "card",
  "card_last4": "",
  "shipping_name": "Sophia Laurent",
  "shipping_address": "14 Rue de la Paix",
  "shipping_city": "Paris",
  "shipping_phone": "+33612345678",
  "client_secret": "pi_3UFu6k9yKJ8HwCNM0mbMZ7cs_secret_…"
}
```

- `card` → `status: "pending_payment"` and a Stripe `client_secret` (see section 9).
- `cod` → `status: "processing"`, `client_secret: null`, and the invoice email is sent immediately.

`400`
```json
{ "detail": "Your cart is empty." }
{ "detail": "Alpine Mist: only 1 left in stock." }
{ "payment_method": ["\"paypal\" is not a valid choice."] }
```

### Order history — `GET /app/orders/` (paginated)

Newest first. Each item has the same shape as the checkout response, without `client_secret`.

### Order detail / tracking — `GET /app/orders/{id}/`

Same shape. Use `events` for the tracking timeline (oldest first) and `estimated_delivery` for the ETA. Order items keep the name, variant and scent `notes` as they were when the order was placed, so history survives later product edits.

```json
"events": [
  { "status": "pending_payment", "created_at": "2026-09-15T11:01:56Z" },
  { "status": "paid",            "created_at": "2026-09-15T11:02:10Z" },
  { "status": "processing",      "created_at": "2026-09-15T13:40:00Z" },
  { "status": "shipped",         "created_at": "2026-09-16T09:15:00Z" },
  { "status": "delivered",       "created_at": "2026-09-18T15:30:00Z" }
]
```

Status changes after checkout are made by staff in the admin dashboard; the customer receives an `orders` notification for each one. Points (5 per $1) are awarded when an app order is **delivered**.

---

## 9. Payments (Stripe)

Card payments use **Stripe PaymentSheet** with a PaymentIntent that the backend creates. The app never sends card details to our API.

### Setup

- Stripe SDK: [`flutter_stripe`](https://pub.dev/packages/flutter_stripe) / [`@stripe/stripe-react-native`](https://github.com/stripe/stripe-react-native) / native iOS/Android SDK.
- Publishable key: the sandbox `pk_test_…` key (from the backend owner). A live key is provided for production.
- `merchantDisplayName`: `MAD PERFUME`. No Stripe Customer or ephemeral key is needed.

### Flow

```
App                               Backend                           Stripe
 │ 1. POST /app/orders/            │                                  │
 │    Idempotency-Key: <uuid>      │── create PaymentIntent ─────────▶│
 │◀── order + client_secret ───────│                                  │
 │ 2. initPaymentSheet(client_secret)                                 │
 │ 3. presentPaymentSheet() ─────────────────────────────────────────▶│ card / 3-D Secure
 │◀──────────────────────────────────────────────────── success ──────│
 │                                 │◀── webhook payment_intent.succeeded
 │                                 │    order → paid, invoice email
 │ 4. GET /app/orders/{id}/ until status == "paid"                    │
 │ 5. Show Order Success                                              │
```

1. **Checkout:** generate a UUID when the user taps **Place order** and send it as `Idempotency-Key`. Call `POST /app/orders/` with `payment_method: "card"`.
2. **Init:** `initPaymentSheet` with `paymentIntentClientSecret = client_secret` and `merchantDisplayName = "MAD PERFUME"`.
3. **Pay:** `presentPaymentSheet()`.
4. **Confirm:** on success, poll `GET /app/orders/{id}/` every 2 seconds (up to about 30 seconds) until `status` is `paid`. The webhook usually lands within a few seconds.
5. **Success screen:** show Order Success with `number`, `total`, `estimated_delivery`, `card_last4`.

**Never mark the order paid in the app** based on the sheet result alone. Only the backend (via the Stripe webhook) sets `paid`.

### Idempotency-Key rules (important)

- Generate **one UUID per checkout attempt**, when the user taps **Place order**. Keep it in memory until the order is paid or the user leaves checkout.
- If the request times out, the app goes to background, or the user taps twice, **resend with the same key**. You get the same order (`200`) and the same `client_secret`; no duplicate order, no double stock reservation, no double charge.
- If the user **cancels or closes the PaymentSheet**, the order stays `pending_payment`. To try again, call `POST /app/orders/` with the **same key** to get the `client_secret` back, then present the sheet again.
- Do **not** create a new key for a retry of the same order. The cart is already empty after the first checkout, so a new key returns `400 "Your cart is empty."`.
- Only start a new key when the user builds a new cart.
- Keys: any string up to 64 characters; UUID v4 recommended. Keys are per user.

### Cash on delivery

`payment_method: "cod"` → order is `processing` immediately, no Stripe step, invoice emailed right away. Go straight to Order Success.

### Invoice email

The customer receives a branded invoice email (items, subtotal, tax, shipping, total, payment method, shipping address):

- **Card:** after Stripe confirms the payment (webhook).
- **Cash on delivery:** when the order is placed.

No app action is needed.

### Test cards (sandbox)

| Card number | Result |
|---|---|
| `4242 4242 4242 4242` | Succeeds |
| `4000 0025 0000 3155` | Requires 3-D Secure authentication |
| `4000 0000 0000 9995` | Declined (insufficient funds) |

Use any future expiry date, any 3-digit CVC, and any postal code.

---

## 10. Loyalty & rewards 🔒

Earning: **5 points per $1** on delivered app orders, **3 points per $1** in boutiques, **+50** per product review. The tier is based on lifetime points; redeeming does not lower the tier.

### Loyalty summary — `GET /app/loyalty/`

`200`
```json
{
  "points_balance": 4478,
  "lifetime_points": 4478,
  "tier": "gold",
  "next_tier": "platinum",
  "points_to_next_tier": 3022,
  "tier_progress": 39,
  "tiers": { "silver": 0, "gold": 2500, "platinum": 7500, "diamond": 15000 },
  "earn_rates": { "app": 5, "branch": 3, "review": 50 },
  "recent_activity": [
    {
      "id": 26,
      "reference": "MAD-00036",
      "title": "Purchase: Dubai Mall",
      "kind": "earned",
      "reason": "purchase",
      "channel": "branch",
      "branch_name": "Dubai Mall",
      "purchase_amount": "900.00",
      "points": 2700,
      "balance_after": 4478,
      "created_at": "2026-09-15T11:01:56.662204Z"
    },
    {
      "id": 25,
      "reference": "RV-00025",
      "title": "Product Review: Alpine Mist",
      "kind": "earned",
      "reason": "review",
      "channel": "app",
      "branch_name": null,
      "purchase_amount": "0.00",
      "points": 50,
      "balance_after": 1778,
      "created_at": "2026-09-15T11:01:56.588754Z"
    }
  ]
}
```

- `recent_activity` holds the latest 5 entries.
- At the top tier: `next_tier: null`, `points_to_next_tier: 0`, `tier_progress: 100`.
- `points` is negative for redemptions (e.g. `-400`); show it in red.

### Points history — `GET /app/loyalty/transactions/` (paginated)

Filters: `?channel=app|branch`, `?kind=earned|redeemed`. Items have the same shape as `recent_activity`.

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 24,
      "reference": "MAD-00035",
      "title": "Purchase: Mobile App",
      "kind": "earned",
      "reason": "purchase",
      "channel": "app",
      "branch_name": null,
      "purchase_amount": "345.60",
      "points": 1728,
      "balance_after": 1728,
      "created_at": "2026-09-15T11:01:56.516832Z"
    }
  ]
}
```

### Rewards shop — `GET /app/rewards/`

Active rewards, cheapest first (not paginated). Filter: `?category=experience`.

`200`
```json
[
  {
    "id": 3,
    "name": "$20 Voucher",
    "points_required": 400,
    "category": "service",
    "eligibility": "all",
    "description": "Use on your next boutique purchase.",
    "image_url": "https://res.cloudinary.com/…/rewards/voucher.jpg",
    "can_redeem": true
  },
  {
    "id": 5,
    "name": "Private Reserve: Oud & Santal",
    "points_required": 5000,
    "category": "physical_product",
    "eligibility": "platinum",
    "description": "Access our most exclusive vintage…",
    "image_url": "https://res.cloudinary.com/…/rewards/reserve.jpg",
    "can_redeem": false
  }
]
```

`can_redeem` is `true` when the user has enough points **and** their tier meets `eligibility`. Use it to enable **Redeem Now** and the "Available to redeem" label.

### Reward detail — `GET /app/rewards/{id}/`

Same object as a list item.

### Redeem — `POST /app/rewards/{id}/redeem/`

No body. Deducts the points and creates a voucher.

`201`
```json
{
  "id": 31,
  "voucher_code": "RD-00031",
  "reward": 3,
  "name": "$20 Voucher",
  "image_url": "https://res.cloudinary.com/…/rewards/voucher.jpg",
  "points": 400,
  "status": "processing",
  "created_at": "2026-09-15T12:10:00Z",
  "fulfilled_at": null
}
```

`400`
```json
{ "detail": "This reward isn't available for your points or tier yet." }
```

The user shows `voucher_code` at a boutique ("How to use": visit a boutique → present voucher → collect).

### Redeemed rewards — `GET /app/redemptions/` (paginated)

Items have the same shape as the redeem response. `status` is `processing` until the boutique hands the reward over, then `delivered` (with `fulfilled_at` set).

---

## 11. Notifications 🔒

### Inbox — `GET /app/notifications/` (paginated)

Filters: `?category=offers|rewards|orders`, `?is_read=false`. Newest first.

`200`
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 14,
      "category": "rewards",
      "title": "Gold Status Achievement",
      "body": "Congratulations, you have reached Gold tier. New rewards are now unlocked.",
      "order": null,
      "order_number": null,
      "is_read": false,
      "created_at": "2026-09-15T11:01:56.659514Z"
    },
    {
      "id": 13,
      "category": "orders",
      "title": "Order delivered",
      "body": "Order MAD-00035 has been delivered. Enjoy your fragrance.",
      "order": 35,
      "order_number": "MAD-00035",
      "is_read": false,
      "created_at": "2026-09-15T11:01:56.512077Z"
    }
  ]
}
```

- **Grouping:** group by `category` for the screen sections: `offers` = Offers & Curations, `rewards` = Loyalty & Rewards, `orders` = Order Status.
- **Tapping:** when `order` is set, tapping opens Order Tracking for that order.
- **Sources:**
  - `offers`: broadcasts from the admin.
  - `rewards`: new tier reached, reward redeemed.
  - `orders`: every status change.

### Unread badge — `GET /app/notifications/unread-count/`

`200` `{ "unread": 3 }`

### Mark one read — `PATCH /app/notifications/{id}/`

```json
{ "is_read": true }
```

`200` — the notification.

### Mark all read — `POST /app/notifications/read-all/`

`204`

---

## 12. Not available yet

- **Shipping Journey (courier steps):** not part of the backend. The Order Tracking screen's courier timeline ("Arrived at Courier Sort Facility"…) has no data source — the admin dashboard doesn't track couriers. Build the tracking screen from `events` (the status circles) only and leave that section out.
- **Not built yet:** Google / Apple sign-in, favourite boutiques, courier step-by-step shipment tracking, product text in Arabic/Hebrew (content is currently single-language).
- **Push notifications:** the inbox works now; register device tokens (section 4) so push works as soon as Firebase is configured.
