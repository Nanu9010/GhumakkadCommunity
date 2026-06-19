For this project, I would answer those decisions like this:

### 1. Architecture

**Choose: Django REST API + Django Templates initially (Hybrid Monolith)**

Why:

* Faster development.
* Easier deployment.
* Lower hosting cost.
* Better for SEO (travel websites depend heavily on SEO).

Structure:

```text
skytravel/
│
├── accounts/
├── tours/
├── hotels/
├── restaurants/
├── bookings/
├── payments/
├── reviews/
├── blogs/
├── api/
├── dashboard/
│
├── templates/
├── static/
└── media/
```

Later:

```text
Django REST API
      ↓
React / Next.js
      ↓
Mobile Apps (Flutter)
```

Do **not** start with React unless you already have traffic and revenue. Most beginners waste months building frontend architecture instead of launching.

---

### 2. Authentication

**Use Django Allauth**

Include:

✅ Email Login
✅ Google Login
✅ OTP Email Verification
✅ Password Reset

Skip for V1:

❌ Facebook Login
❌ Twitter Login
❌ LinkedIn Login

Reason:

Google Login alone handles 90%+ of social logins.

---

### 3. Razorpay Features

For Version 1:

#### Required

✅ UPI
✅ Credit Cards
✅ Debit Cards
✅ Net Banking
✅ Wallets
✅ Booking Refunds
✅ Payment Webhooks
✅ GST Invoice Generation

#### Not Required Initially

❌ EMI
❌ Subscriptions
❌ Razorpay Wallet System

Reason:

Travel bookings are mostly one-time purchases.

---

### Additional Decisions I Would Lock Before Coding

#### Booking Flow

```text
Search Destination
      ↓
View Tour
      ↓
Select Date
      ↓
Travelers Count
      ↓
Apply Coupon
      ↓
Pay with Razorpay
      ↓
Booking Confirmation
      ↓
Invoice Email
```

---

#### User Roles

```text
Admin

Tour Operator

Traveler
```

---

#### Review System

Allow:

```text
★★★★★ Rating

Review Text

Photo Upload

Helpful Votes
```

Only verified customers can review.

---

#### Maps

Start with:

```text
Google Maps API
```

Not OpenStreetMap.

Travel websites live or die by map quality.

---

#### AI Features

V1:

```text
AI Travel Planner

Budget
Days
Country
Interests

↓

Generate Itinerary
```

V2:

```text
AI Hotel Recommendations
AI Tour Recommendations
AI Budget Optimization
```

---

### Features I Would Remove

These sound impressive but slow down launch:

❌ Chat System
❌ Real-time Messaging
❌ Multi-vendor Marketplace Payouts
❌ Loyalty Points System
❌ Cryptocurrency Payments
❌ Affiliate Program

Launch first.

---

### Features I Would Add

✅ Multi-language support

Languages:

* English
* Hindi
* Marathi

✅ Currency Switcher

* INR
* USD
* EUR
* GBP

✅ Coupons

```text
WELCOME10
SUMMER25
NEWUSER50
```

✅ Wishlist

✅ Recently Viewed

✅ Compare Tours

---

If your goal is to actually compete with GetYourGuide/TripAdvisor-style products, my next question is:

**Who creates the tours?**

1. Admin manually adds tours.
This single decision changes about 40% of the database design and development effort.
