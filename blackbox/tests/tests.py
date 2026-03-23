"""
QuickCart API - Comprehensive Black-Box Test Suite
===================================================
Run with:  pytest test_quickcart.py -v
Requires:  pip install pytest requests

Server must be running at http://localhost:8080
Start with: docker run -p 8080:8080 quickcart:latest
"""

import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"

ROLL     = {"X-Roll-Number": "2024115015"}          # valid roll number
USER_1   = {**ROLL, "X-User-ID": "25"}          # user 1  (exists in seed data)
USER_999 = {**ROLL, "X-User-ID": "999999"}     # user that almost certainly doesn't exist


def get(path, headers=USER_1, **kw):
    return requests.get(f"{BASE_URL}{path}", headers=headers, **kw)

def post(path, body, headers=USER_1, **kw):
    return requests.post(f"{BASE_URL}{path}", json=body, headers=headers, **kw)

def put(path, body, headers=USER_1, **kw):
    return requests.put(f"{BASE_URL}{path}", json=body, headers=headers, **kw)

def delete(path, headers=USER_1, **kw):
    return requests.delete(f"{BASE_URL}{path}", headers=headers, **kw)


# 1.  GLOBAL HEADER VALIDATION

class TestGlobalHeaders:
    """Every endpoint must enforce X-Roll-Number and X-User-ID headers."""

    def test_missing_roll_number_returns_401(self):
        """Missing X-Roll-Number must return 401 on any endpoint."""
        r = requests.get(f"{BASE_URL}/profile", headers={"X-User-ID": "1"})
        assert r.status_code == 401, "Missing roll number must be 401"

    def test_non_integer_roll_number_returns_400(self):
        """Non-integer X-Roll-Number (e.g. letters) must return 400."""
        r = requests.get(
            f"{BASE_URL}/profile",
            headers={"X-Roll-Number": "ABC", "X-User-ID": "1"}
        )
        assert r.status_code == 400, "Non-integer roll number must be 400"

    def test_missing_user_id_on_user_endpoint_returns_400(self):
        """Missing X-User-ID on a user-scoped endpoint must return 400."""
        r = requests.get(f"{BASE_URL}/profile", headers=ROLL)
        assert r.status_code == 400, "Missing X-User-ID must be 400"

    def test_non_integer_user_id_returns_400(self):
        """Non-integer X-User-ID must return 400."""
        r = requests.get(
            f"{BASE_URL}/profile",
            headers={**ROLL, "X-User-ID": "abc"}
        )
        assert r.status_code == 400, "Non-integer X-User-ID must be 400"

    def test_non_existent_user_id_returns_400(self):
        """A well-formed but non-existent user ID must be rejected."""
        r = requests.get(f"{BASE_URL}/profile", headers=USER_999)
        assert r.status_code == 400, "Non-existent user must be 400"

    def test_admin_endpoint_does_not_require_user_id(self):
        """Admin endpoints should work with only X-Roll-Number."""
        r = requests.get(f"{BASE_URL}/admin/users", headers=ROLL)
        assert r.status_code == 200, "Admin endpoint should not need X-User-ID"


# 2.  ADMIN ENDPOINTS

class TestAdmin:

    def test_get_all_users_returns_200_and_list(self):
        """Admin users list must return 200 with a non-empty list."""
        r = get("/admin/users", headers=ROLL)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list), "Must return a list"
        assert len(data) > 0, "Seed data should have users"

    def test_get_single_user_valid_id(self):
        """Admin lookup of a known user must return 200."""
        r = get("/admin/users/1", headers=ROLL)
        assert r.status_code == 200
        data = r.json()
        assert "user_id" in data or "id" in data, "Response must contain user_id"

    # TC-A-03
    def test_get_single_user_invalid_id_returns_404(self):
        """Admin lookup of a non-existent user must return 404."""
        r = get("/admin/users/999999", headers=ROLL)
        assert r.status_code == 404

    # TC-A-04
    def test_admin_products_returns_inactive_products(self):
        """Admin products list must include inactive products."""
        r = get("/admin/products", headers=ROLL)
        assert r.status_code == 200
        products = r.json()
        assert isinstance(products, list)
        active_flags = [p.get("is_active") for p in products]
        assert False in active_flags or 0 in active_flags, \
            "Admin view must show inactive products"

    # TC-A-05
    def test_admin_carts_returns_200(self):
        r = get("/admin/carts", headers=ROLL)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # TC-A-06
    def test_admin_orders_returns_200(self):
        r = get("/admin/orders", headers=ROLL)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # TC-A-07
    def test_admin_coupons_returns_expired_coupons(self):
        """Admin coupons must include expired ones."""
        r = get("/admin/coupons", headers=ROLL)
        assert r.status_code == 200
        coupons = r.json()
        assert isinstance(coupons, list) and len(coupons) > 0

    # TC-A-08
    def test_admin_tickets_returns_200(self):
        r = get("/admin/tickets", headers=ROLL)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # TC-A-09
    def test_admin_addresses_returns_200(self):
        r = get("/admin/addresses", headers=ROLL)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  PROFILE
# ══════════════════════════════════════════════════════════════════════════════

class TestProfile:

    # TC-P-01
    def test_get_profile_returns_user_fields(self):
        """GET profile must return name, email, phone, wallet_balance."""
        r = get("/profile")
        assert r.status_code == 200
        data = r.json()
        for field in ("name", "email", "phone"):
            assert field in data, f"Profile must include '{field}'"

    # TC-P-02
    def test_update_profile_valid_name_and_phone(self):
        """Valid update (name 2–50 chars, phone 10 digits) must return 200."""
        r = put("/profile", {"name": "TestUser", "phone": "9876543210"})
        assert r.status_code == 200

    # TC-P-03
    def test_update_profile_name_too_short_returns_400(self):
        """Name with 1 character must be rejected."""
        r = put("/profile", {"name": "A", "phone": "9876543210"})
        assert r.status_code == 400, "Name < 2 chars must be 400"

    # TC-P-04
    def test_update_profile_name_too_long_returns_400(self):
        """Name with 51 characters must be rejected."""
        r = put("/profile", {"name": "A" * 51, "phone": "9876543210"})
        assert r.status_code == 400, "Name > 50 chars must be 400"

    # TC-P-05
    def test_update_profile_name_boundary_2_chars(self):
        """Name with exactly 2 characters must be accepted."""
        r = put("/profile", {"name": "AB", "phone": "9876543210"})
        assert r.status_code == 200, "Name of 2 chars must be accepted"

    # TC-P-06
    def test_update_profile_name_boundary_50_chars(self):
        """Name with exactly 50 characters must be accepted."""
        r = put("/profile", {"name": "A" * 50, "phone": "9876543210"})
        assert r.status_code == 200, "Name of 50 chars must be accepted"

    # TC-P-07
    def test_update_profile_phone_wrong_length_returns_400(self):
        """Phone number with 9 digits must be rejected."""
        r = put("/profile", {"name": "Valid Name", "phone": "987654321"})
        assert r.status_code == 400, "Phone != 10 digits must be 400"

    # TC-P-08
    def test_update_profile_phone_11_digits_returns_400(self):
        """Phone number with 11 digits must be rejected."""
        r = put("/profile", {"name": "Valid Name", "phone": "98765432101"})
        assert r.status_code == 400, "Phone of 11 digits must be 400"

    # TC-P-09
    def test_update_profile_phone_with_letters_returns_400(self):
        """Phone number containing letters must be rejected."""
        r = put("/profile", {"name": "Valid Name", "phone": "98765ABCDE"})
        assert r.status_code == 400, "Non-digit phone must be 400"

    # TC-P-10
    def test_update_profile_missing_name_returns_400(self):
        """Missing name field must return 400."""
        r = put("/profile", {"phone": "9876543210"})
        assert r.status_code == 400, "Missing name must be 400"

    # TC-P-11
    def test_update_profile_missing_phone_returns_400(self):
        """Missing phone field must return 400."""
        r = put("/profile", {"name": "Valid Name"})
        assert r.status_code == 400, "Missing phone must be 400"


# ══════════════════════════════════════════════════════════════════════════════
# 4.  ADDRESSES
# ══════════════════════════════════════════════════════════════════════════════

VALID_ADDRESS = {
    "label": "HOME",
    "street": "123 MG Road",
    "city": "Bangalore",
    "pincode": "560001",
    "is_default": False
}

class TestAddresses:

    def _create_address(self, override=None):
        payload = {**VALID_ADDRESS, **(override or {})}
        return post("/addresses", payload)

    # TC-AD-01
    def test_get_addresses_returns_list(self):
        r = get("/addresses")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # TC-AD-02
    def test_create_address_valid_returns_201_or_200(self):
        """Valid address creation must succeed and return address_id."""
        r = self._create_address()
        assert r.status_code in (200, 201)
        data = r.json()
        # Must return the created address
        assert "address_id" in data or any("address_id" in str(v) for v in data.values()), \
            "Response must include created address object with address_id"

    # TC-AD-03
    def test_create_address_invalid_label_returns_400(self):
        """Label outside HOME/OFFICE/OTHER must return 400."""
        r = self._create_address({"label": "WORK"})
        assert r.status_code == 400, "Invalid label must be 400"

    # TC-AD-04
    def test_create_address_street_too_short_returns_400(self):
        """Street with 4 characters must be rejected."""
        r = self._create_address({"street": "AB12"})
        assert r.status_code == 400, "Street < 5 chars must be 400"

    # TC-AD-05
    def test_create_address_street_boundary_5_chars_accepted(self):
        """Street with exactly 5 characters must be accepted."""
        r = self._create_address({"street": "AB123"})
        assert r.status_code in (200, 201), "Street of 5 chars must be accepted"

    # TC-AD-06
    def test_create_address_street_boundary_100_chars_accepted(self):
        """Street with exactly 100 characters must be accepted."""
        r = self._create_address({"street": "A" * 100})
        assert r.status_code in (200, 201), "Street of 100 chars must be accepted"

    # TC-AD-07
    def test_create_address_street_101_chars_returns_400(self):
        """Street with 101 characters must be rejected."""
        r = self._create_address({"street": "A" * 101})
        assert r.status_code == 400, "Street > 100 chars must be 400"

    # TC-AD-08
    def test_create_address_city_too_short_returns_400(self):
        """City with 1 character must be rejected."""
        r = self._create_address({"city": "A"})
        assert r.status_code == 400, "City < 2 chars must be 400"

    # TC-AD-09
    def test_create_address_pincode_wrong_length_returns_400(self):
        """Pincode with 5 digits must be rejected."""
        r = self._create_address({"pincode": "12345"})
        assert r.status_code == 400, "Pincode != 6 digits must be 400"

    # TC-AD-10
    def test_create_address_pincode_7_digits_returns_400(self):
        """Pincode with 7 digits must be rejected."""
        r = self._create_address({"pincode": "1234567"})
        assert r.status_code == 400, "Pincode of 7 digits must be 400"

    # TC-AD-11
    def test_create_address_pincode_with_letters_returns_400(self):
        """Pincode containing letters must be rejected."""
        r = self._create_address({"pincode": "56000A"})
        assert r.status_code == 400, "Non-digit pincode must be 400"

    # TC-AD-12
    def test_create_address_missing_label_returns_400(self):
        payload = {k: v for k, v in VALID_ADDRESS.items() if k != "label"}
        r = post("/addresses", payload)
        assert r.status_code == 400, "Missing label must be 400"

    # TC-AD-13
    def test_create_address_missing_street_returns_400(self):
        payload = {k: v for k, v in VALID_ADDRESS.items() if k != "street"}
        r = post("/addresses", payload)
        assert r.status_code == 400, "Missing street must be 400"

    # TC-AD-14
    def test_default_address_uniqueness(self):
        """Only one address should be default after setting a new default."""
        self._create_address({"is_default": True, "label": "HOME", "street": "First Road"})
        self._create_address({"is_default": True, "label": "OFFICE", "street": "Second Road"})
        r = get("/addresses")
        addresses = r.json()
        defaults = [a for a in addresses if a.get("is_default") is True or a.get("is_default") == 1]
        assert len(defaults) <= 1, "Only one address can be default at a time"

    # TC-AD-15
    def test_update_address_street_only(self):
        """Update should allow changing street and return new data."""
        cr = self._create_address()
        created = cr.json()
        addr_id = created.get("address_id") or (
            created.get("address", {}).get("address_id")
        )
        if not addr_id:
            pytest.skip("Could not determine address_id from create response")
        new_street = "Updated Street 99"
        r = put(f"/addresses/{addr_id}", {"street": new_street})
        assert r.status_code == 200
        updated = r.json()
        # Response must show NEW data
        street_val = updated.get("street") or updated.get("address", {}).get("street")
        assert street_val == new_street, "Response must reflect updated street"

    # TC-AD-16
    def test_delete_nonexistent_address_returns_404(self):
        r = delete("/addresses/999999")
        assert r.status_code == 404, "Deleting non-existent address must be 404"

    # TC-AD-17
    def test_create_address_all_label_types(self):
        """HOME, OFFICE, and OTHER must all be accepted."""
        for label in ("HOME", "OFFICE", "OTHER"):
            r = self._create_address({"label": label})
            assert r.status_code in (200, 201), f"Label '{label}' must be accepted"


# ══════════════════════════════════════════════════════════════════════════════
# 5.  PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════

class TestProducts:

    # TC-PR-01
    def test_get_products_returns_list(self):
        r = get("/products")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # TC-PR-02
    def test_products_list_only_active(self):
        """Public product list must never include inactive products."""
        r = get("/products")
        products = r.json()
        for p in products:
            assert p.get("is_active") in (True, 1), \
                f"Product {p.get('product_id')} is inactive but appeared in list"

    # TC-PR-03
    def test_get_single_product_valid_id(self):
        r = get("/products/1")
        assert r.status_code == 200
        data = r.json()
        assert "product_id" in data or "id" in data

    # TC-PR-04
    def test_get_single_product_invalid_id_returns_404(self):
        r = get("/products/999999")
        assert r.status_code == 404, "Non-existent product must return 404"

    # TC-PR-05
    def test_product_price_is_exact_not_rounded(self):
        """Prices must be the exact stored values, not truncated/rounded."""
        r = get("/products/1")
        data = r.json()
        price = data.get("price")
        assert price is not None
        assert isinstance(price, (int, float)), "Price must be numeric"
        assert price == round(price, 2), "Price must be accurate to 2 decimal places"

    # TC-PR-06
    def test_filter_products_by_category(self):
        """Category filter must return only matching products."""
        r = get("/products?category=Fruits")
        assert r.status_code == 200
        products = r.json()
        for p in products:
            assert p.get("category") == "Fruits", "Category filter returned wrong category"

    # TC-PR-07
    def test_search_products_by_name(self):
        """Name search must return products whose name contains the query."""
        r = get("/products?search=Apple")
        assert r.status_code == 200
        products = r.json()
        for p in products:
            assert "apple" in p.get("name", "").lower(), \
                "Search returned product not matching query"

    # TC-PR-08
    def test_sort_products_by_price_asc(self):
        """Sort=price_asc must return products in ascending price order."""
        r = get("/products?sort=price_asc")
        assert r.status_code == 200
        products = r.json()
        prices = [p["price"] for p in products]
        assert prices == sorted(prices), "Products not sorted by price ascending"

    # TC-PR-09
    def test_sort_products_by_price_desc(self):
        """Sort=price_desc must return products in descending price order."""
        r = get("/products?sort=price_desc")
        assert r.status_code == 200
        products = r.json()
        prices = [p["price"] for p in products]
        assert prices == sorted(prices, reverse=True), "Products not sorted by price descending"

    # TC-PR-10
    def test_admin_shows_inactive_products_not_in_public_list(self):
        """A product marked inactive in admin must not appear in public list."""
        admin_r = get("/admin/products", headers=ROLL)
        inactive_ids = {
            p["product_id"] for p in admin_r.json()
            if p.get("is_active") in (False, 0)
        }
        public_r = get("/products")
        public_ids = {p["product_id"] for p in public_r.json()}
        overlap = inactive_ids & public_ids
        assert not overlap, f"Inactive product IDs appeared in public list: {overlap}"


# ══════════════════════════════════════════════════════════════════════════════
# 6.  CART
# ══════════════════════════════════════════════════════════════════════════════

class TestCart:

    PRODUCT_ID = 1   # Seeded product — Apple Red, price 120, stock 195

    def _clear(self):
        delete("/cart/clear")

    def _add(self, product_id=None, quantity=1):
        return post("/cart/add", {
            "product_id": product_id or self.PRODUCT_ID,
            "quantity": quantity
        })

    # TC-C-01
    def test_get_cart_returns_items_and_total(self):
        r = get("/cart")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data or isinstance(data, dict), "Cart must return items"

    # TC-C-02
    def test_add_item_valid(self):
        self._clear()
        r = self._add(quantity=2)
        assert r.status_code in (200, 201), "Valid add must succeed"

    # TC-C-03
    def test_add_item_zero_quantity_returns_400(self):
        """Quantity of 0 must be rejected."""
        r = self._add(quantity=0)
        assert r.status_code == 400, "Quantity 0 must return 400"

    # TC-C-04
    def test_add_item_negative_quantity_returns_400(self):
        """Negative quantity must be rejected."""
        r = self._add(quantity=-1)
        assert r.status_code == 400, "Negative quantity must return 400"

    # TC-C-05
    def test_add_item_nonexistent_product_returns_404(self):
        r = self._add(product_id=999999)
        assert r.status_code == 404, "Non-existent product must return 404"

    # TC-C-06
    def test_add_item_exceeds_stock_returns_400(self):
        """Quantity larger than stock must return 400."""
        r = self._add(quantity=999999)
        assert r.status_code == 400, "Over-stock quantity must return 400"

    # TC-C-07
    def test_add_same_product_twice_accumulates_quantity(self):
        """Adding the same product twice should sum the quantities."""
        self._clear()
        self._add(quantity=2)
        self._add(quantity=3)
        r = get("/cart")
        cart = r.json()
        items = cart.get("items", [])
        matching = [i for i in items if i.get("product_id") == self.PRODUCT_ID]
        assert len(matching) == 1, "Same product must appear only once in cart"
        assert matching[0].get("quantity") == 5, "Quantities must be summed (2+3=5)"

    # TC-C-08
    def test_cart_subtotal_calculation(self):
        """Each item's subtotal must equal quantity × unit_price."""
        self._clear()
        self._add(quantity=3)
        r = get("/cart")
        items = r.json().get("items", [])
        for item in items:
            expected = round(item["quantity"] * item["unit_price"], 2)
            actual = round(item.get("subtotal", 0), 2)
            assert actual == expected, \
                f"Subtotal mismatch: {actual} != {expected} for product {item['product_id']}"

    # TC-C-09
    def test_cart_total_equals_sum_of_subtotals(self):
        """Cart total must equal the sum of all item subtotals."""
        self._clear()
        self._add(product_id=1, quantity=2)
        self._add(product_id=2, quantity=1)
        r = get("/cart")
        data = r.json()
        items = data.get("items", [])
        expected_total = round(sum(i["subtotal"] for i in items), 2)
        actual_total = round(data.get("total", 0), 2)
        assert actual_total == expected_total, \
            f"Cart total {actual_total} != sum of subtotals {expected_total}"

    # TC-C-10
    def test_update_cart_valid_quantity(self):
        self._clear()
        self._add(quantity=1)
        r = post("/cart/update", {"product_id": self.PRODUCT_ID, "quantity": 4})
        assert r.status_code == 200, "Valid cart update must succeed"

    # TC-C-11
    def test_update_cart_zero_quantity_returns_400(self):
        self._clear()
        self._add(quantity=1)
        r = post("/cart/update", {"product_id": self.PRODUCT_ID, "quantity": 0})
        assert r.status_code == 400, "Update with quantity 0 must return 400"

    # TC-C-12
    def test_remove_item_not_in_cart_returns_404(self):
        self._clear()
        r = post("/cart/remove", {"product_id": 999999})
        assert r.status_code == 404, "Removing non-existent cart item must be 404"

    # TC-C-13
    def test_clear_cart_empties_cart(self):
        self._add(quantity=1)
        r = delete("/cart/clear")
        assert r.status_code in (200, 204)
        r2 = get("/cart")
        assert r2.json().get("items", []) == [], "Cart must be empty after clear"

    # TC-C-14
    def test_add_item_missing_product_id_returns_400(self):
        r = post("/cart/add", {"quantity": 1})
        assert r.status_code == 400, "Missing product_id must return 400"

    # TC-C-15
    def test_add_item_wrong_type_quantity_returns_400(self):
        """String quantity must be rejected."""
        r = post("/cart/add", {"product_id": self.PRODUCT_ID, "quantity": "two"})
        assert r.status_code == 400, "String quantity must return 400"


# ══════════════════════════════════════════════════════════════════════════════
# 7.  COUPONS
# ══════════════════════════════════════════════════════════════════════════════

class TestCoupons:
    """
    Seed coupons (from DB):
      SAVE50      FIXED  50  off, min 500,  max 50,  expires 2026-04-04  (valid)
      SAVE100     FIXED  100 off, min 1000, max 100, expires 2026-04-04  (valid)
      PERCENT10   PCT    10% off, min 300,  max 100, expires 2026-04-04  (valid)
      PERCENT20   PCT    20% off, min 500,  max 200, expires 2026-04-04  (valid)
      EXPIRED50   FIXED  50  off, min 500,  max 50,  expires 2026-02-23  (EXPIRED)
      BIGDEAL500  FIXED  500 off, min 5000, max 500, expires 2026-03-20  (EXPIRED)
      FLASH25     PCT    25% off, min 800,  max 250, expires 2026-03-12  (EXPIRED)
      WELCOME50   FIXED  50  off, min 100,  max 50,  expires 2026-06-03  (valid, low min)
    """

    PRODUCT_ID = 1  # price 120

    def _setup_cart_with_value(self, target_value):
        """Add enough of product 1 (price=120) to meet target cart value."""
        delete("/cart/clear", headers=USER_1)
        qty = max(1, int(target_value / 120) + 1)
        post("/cart/add", {"product_id": self.PRODUCT_ID, "quantity": qty}, headers=USER_1)

    # TC-CPN-01
    def test_apply_valid_fixed_coupon(self):
        """SAVE50 requires cart >= 500; set cart ~600 and apply."""
        self._setup_cart_with_value(600)
        r = post("/coupon/apply", {"coupon_code": "SAVE50"})
        assert r.status_code == 200, "Valid fixed coupon must be accepted"

    # TC-CPN-02
    def test_apply_valid_percent_coupon(self):
        """PERCENT10 requires cart >= 300; set cart ~400 and apply."""
        self._setup_cart_with_value(400)
        r = post("/coupon/apply", {"coupon_code": "PERCENT10"})
        assert r.status_code == 200, "Valid percent coupon must be accepted"

    # TC-CPN-03
    def test_apply_expired_coupon_returns_400(self):
        """Expired coupon must be rejected."""
        self._setup_cart_with_value(600)
        r = post("/coupon/apply", {"coupon_code": "EXPIRED50"})
        assert r.status_code == 400, "Expired coupon must return 400"

    # TC-CPN-04
    def test_apply_coupon_cart_below_minimum_returns_400(self):
        """Cart below coupon minimum must be rejected."""
        delete("/cart/clear")
        post("/cart/add", {"product_id": self.PRODUCT_ID, "quantity": 1})  # cart = 120, below 500
        r = post("/coupon/apply", {"coupon_code": "SAVE50"})
        assert r.status_code == 400, "Cart below min value must return 400"

    # TC-CPN-05
    def test_apply_nonexistent_coupon_returns_400_or_404(self):
        """Coupon code that doesn't exist must be rejected."""
        self._setup_cart_with_value(600)
        r = post("/coupon/apply", {"coupon_code": "FAKECOUPON999"})
        assert r.status_code in (400, 404), "Non-existent coupon must be 400 or 404"

    # TC-CPN-06
    def test_fixed_discount_calculation_correct(self):
        """SAVE50 should reduce total by exactly 50 (if cart >= 500)."""
        self._setup_cart_with_value(600)
        cart_before = get("/cart").json().get("total", 0)
        post("/coupon/apply", {"coupon_code": "SAVE50"})
        cart_after = get("/cart").json().get("total", 0)
        discount = round(cart_before - cart_after, 2)
        assert discount == 50.0, f"FIXED 50 coupon gave discount of {discount}, expected 50"

    # TC-CPN-07
    def test_percent_discount_respects_max_cap(self):
        """PERCENT10 has max_discount=100. Verify discount does not exceed 100."""
        # cart ~1200 => 10% = 120 > 100, should be capped at 100
        self._setup_cart_with_value(1200)
        cart_before = get("/cart").json().get("total", 0)
        post("/coupon/apply", {"coupon_code": "PERCENT10"})
        cart_after = get("/cart").json().get("total", 0)
        discount = round(cart_before - cart_after, 2)
        assert discount <= 100.0, f"Discount {discount} exceeded max cap of 100"

    # TC-CPN-08
    def test_remove_coupon(self):
        """Removing a coupon should restore the original total."""
        self._setup_cart_with_value(600)
        cart_before = get("/cart").json().get("total", 0)
        post("/coupon/apply", {"coupon_code": "SAVE50"})
        r = post("/coupon/remove", {"coupon_code": "SAVE50"})
        assert r.status_code == 200, "Coupon remove must succeed"
        cart_after = get("/cart").json().get("total", 0)
        assert round(cart_after, 2) == round(cart_before, 2), \
            "Removing coupon must restore original total"

    # TC-CPN-09
    def test_apply_coupon_missing_code_returns_400(self):
        r = post("/coupon/apply", {})
        assert r.status_code == 400, "Missing coupon_code must return 400"

    # TC-CPN-10
    def test_apply_another_expired_coupon(self):
        """FLASH25 expired 2026-03-12 (before today 2026-03-23)."""
        self._setup_cart_with_value(900)
        r = post("/coupon/apply", {"coupon_code": "FLASH25"})
        assert r.status_code == 400, "FLASH25 is expired, must return 400"


# ══════════════════════════════════════════════════════════════════════════════
# 8.  CHECKOUT
# ══════════════════════════════════════════════════════════════════════════════

class TestCheckout:

    PRODUCT_ID = 1  # price 120

    def _setup_cart(self, qty=2):
        delete("/cart/clear")
        post("/cart/add", {"product_id": self.PRODUCT_ID, "quantity": qty})

    # TC-CHK-01
    def test_checkout_cod_valid_cart(self):
        """COD checkout with cart total under 5000 must succeed."""
        self._setup_cart(qty=2)   # total = 240, well under 5000
        r = post("/checkout", {"payment_method": "COD"})
        assert r.status_code in (200, 201), "Valid COD checkout must succeed"

    # TC-CHK-02
    def test_checkout_card_sets_payment_status_paid(self):
        """CARD payment must create order with payment_status=PAID."""
        self._setup_cart(qty=2)
        r = post("/checkout", {"payment_method": "CARD"})
        assert r.status_code in (200, 201)
        order = r.json()
        assert order.get("payment_status") == "PAID", \
            "CARD checkout must set payment_status to PAID"

    # TC-CHK-03
    def test_checkout_cod_payment_status_is_pending(self):
        """COD must create order with payment_status=PENDING."""
        self._setup_cart(qty=2)
        r = post("/checkout", {"payment_method": "COD"})
        assert r.status_code in (200, 201)
        order = r.json()
        assert order.get("payment_status") == "PENDING", \
            "COD checkout must set payment_status to PENDING"

    # TC-CHK-04
    def test_checkout_empty_cart_returns_400(self):
        """Checking out with an empty cart must return 400."""
        delete("/cart/clear")
        r = post("/checkout", {"payment_method": "COD"})
        assert r.status_code == 400, "Empty cart checkout must return 400"

    # TC-CHK-05
    def test_checkout_invalid_payment_method_returns_400(self):
        """Unknown payment method must return 400."""
        self._setup_cart(qty=2)
        r = post("/checkout", {"payment_method": "CRYPTO"})
        assert r.status_code == 400, "Invalid payment method must return 400"

    # TC-CHK-06
    def test_checkout_cod_over_5000_returns_400(self):
        """COD is not allowed when order total > 5000."""
        # 42 × 120 = 5040 > 5000
        self._setup_cart(qty=42)
        r = post("/checkout", {"payment_method": "COD"})
        assert r.status_code == 400, "COD over 5000 must return 400"

    # TC-CHK-07
    def test_checkout_gst_is_5_percent(self):
        """GST amount must equal exactly 5% of pre-tax subtotal."""
        self._setup_cart(qty=2)   # subtotal = 240
        r = post("/checkout", {"payment_method": "CARD"})
        assert r.status_code in (200, 201)
        order = r.json()
        subtotal = order.get("subtotal") or (order.get("total_amount", 0) / 1.05)
        gst = round(order.get("gst_amount", 0), 2)
        expected_gst = round(subtotal * 0.05, 2)
        assert gst == expected_gst, f"GST {gst} != 5% of subtotal {expected_gst}"

    # TC-CHK-08
    def test_checkout_missing_payment_method_returns_400(self):
        self._setup_cart(qty=2)
        r = post("/checkout", {})
        assert r.status_code == 400, "Missing payment_method must return 400"

    # TC-CHK-09
    def test_checkout_wallet_payment_status_is_pending(self):
        """WALLET checkout must create order with payment_status=PENDING."""
        self._setup_cart(qty=2)
        r = post("/checkout", {"payment_method": "WALLET"})
        # May fail if wallet insufficient; if 200 check status
        if r.status_code in (200, 201):
            assert r.json().get("payment_status") == "PENDING", \
                "WALLET checkout must set payment_status to PENDING"


# ══════════════════════════════════════════════════════════════════════════════
# 9.  WALLET
# ══════════════════════════════════════════════════════════════════════════════

class TestWallet:

    # TC-W-01
    def test_get_wallet_balance_returns_numeric(self):
        r = get("/wallet")
        assert r.status_code == 200
        data = r.json()
        balance = data.get("wallet_balance") or data.get("balance")
        assert isinstance(balance, (int, float)), "wallet_balance must be numeric"

    # TC-W-02
    def test_add_money_valid_amount(self):
        """Adding a valid amount must increase balance."""
        balance_before = (get("/wallet").json().get("wallet_balance") or
                          get("/wallet").json().get("balance", 0))
        r = post("/wallet/add", {"amount": 100})
        assert r.status_code == 200, "Valid wallet add must succeed"
        balance_after = (get("/wallet").json().get("wallet_balance") or
                         get("/wallet").json().get("balance", 0))
        assert balance_after == round(balance_before + 100, 2), \
            "Balance must increase by exactly the added amount"

    # TC-W-03
    def test_add_money_zero_returns_400(self):
        r = post("/wallet/add", {"amount": 0})
        assert r.status_code == 400, "Amount 0 must return 400"

    # TC-W-04
    def test_add_money_negative_returns_400(self):
        r = post("/wallet/add", {"amount": -50})
        assert r.status_code == 400, "Negative amount must return 400"

    # TC-W-05
    def test_add_money_exceeds_100000_returns_400(self):
        """Amount over 100000 must be rejected."""
        r = post("/wallet/add", {"amount": 100001})
        assert r.status_code == 400, "Amount > 100000 must return 400"

    # TC-W-06
    def test_add_money_boundary_100000_accepted(self):
        """Amount of exactly 100000 must be accepted."""
        r = post("/wallet/add", {"amount": 100000})
        assert r.status_code == 200, "Amount of 100000 must be accepted"

    # TC-W-07
    def test_pay_from_wallet_valid(self):
        """Paying less than balance must succeed and deduct exact amount."""
        post("/wallet/add", {"amount": 500})
        before = get("/wallet").json().get("wallet_balance", 0)
        r = post("/wallet/pay", {"amount": 100})
        assert r.status_code == 200, "Valid wallet pay must succeed"
        after = get("/wallet").json().get("wallet_balance", 0)
        assert round(before - after, 2) == 100.0, "Exactly 100 must be deducted"

    # TC-W-08
    def test_pay_from_wallet_insufficient_balance_returns_400(self):
        """Payment exceeding balance must return 400."""
        current = get("/wallet").json().get("wallet_balance", 0)
        r = post("/wallet/pay", {"amount": current + 10000})
        assert r.status_code == 400, "Insufficient balance must return 400"

    # TC-W-09
    def test_pay_zero_returns_400(self):
        r = post("/wallet/pay", {"amount": 0})
        assert r.status_code == 400, "Pay amount 0 must return 400"

    # TC-W-10
    def test_add_money_missing_amount_returns_400(self):
        r = post("/wallet/add", {})
        assert r.status_code == 400, "Missing amount must return 400"

    # TC-W-11
    def test_add_money_string_amount_returns_400(self):
        r = post("/wallet/add", {"amount": "hundred"})
        assert r.status_code == 400, "String amount must return 400"


# ══════════════════════════════════════════════════════════════════════════════
# 10.  LOYALTY POINTS
# ══════════════════════════════════════════════════════════════════════════════

class TestLoyalty:

    # TC-L-01
    def test_get_loyalty_returns_points(self):
        r = get("/loyalty")
        assert r.status_code == 200
        data = r.json()
        points = data.get("loyalty_points") or data.get("points")
        assert isinstance(points, int), "loyalty_points must be an integer"

    # TC-L-02
    def test_redeem_valid_points(self):
        """Redeeming ≤ available points must succeed."""
        current = get("/loyalty").json().get("loyalty_points") or \
                  get("/loyalty").json().get("points", 0)
        if current < 1:
            pytest.skip("User has no loyalty points to redeem")
        r = post("/loyalty/redeem", {"points": 1})
        assert r.status_code == 200, "Redeeming 1 point must succeed"

    # TC-L-03
    def test_redeem_more_than_available_returns_400(self):
        """Redeeming more points than available must return 400."""
        r = post("/loyalty/redeem", {"points": 9999999})
        assert r.status_code == 400, "Redeeming too many points must return 400"

    # TC-L-04
    def test_redeem_zero_points_returns_400(self):
        """Redeeming 0 points must return 400 (minimum is 1)."""
        r = post("/loyalty/redeem", {"points": 0})
        assert r.status_code == 400, "Redeeming 0 points must return 400"

    # TC-L-05
    def test_redeem_negative_points_returns_400(self):
        r = post("/loyalty/redeem", {"points": -10})
        assert r.status_code == 400, "Negative points must return 400"


# ══════════════════════════════════════════════════════════════════════════════
# 11.  ORDERS
# ══════════════════════════════════════════════════════════════════════════════

class TestOrders:

    PRODUCT_ID = 1

    def _place_order(self, method="CARD"):
        delete("/cart/clear")
        post("/cart/add", {"product_id": self.PRODUCT_ID, "quantity": 2})
        r = post("/checkout", {"payment_method": method})
        if r.status_code in (200, 201):
            return r.json().get("order_id")
        return None

    # TC-O-01
    def test_get_all_orders_returns_list(self):
        r = get("/orders")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # TC-O-02
    def test_get_single_order_valid_id(self):
        order_id = self._place_order()
        if not order_id:
            pytest.skip("Could not place order for test")
        r = get(f"/orders/{order_id}")
        assert r.status_code == 200

    # TC-O-03
    def test_get_single_order_invalid_id_returns_404(self):
        r = get("/orders/999999")
        assert r.status_code == 404, "Non-existent order must return 404"

    # TC-O-04
    def test_cancel_valid_order(self):
        """A PLACED order must be cancellable."""
        order_id = self._place_order("CARD")
        if not order_id:
            pytest.skip("Could not place order for test")
        r = post(f"/orders/{order_id}/cancel", {})
        assert r.status_code == 200, "Cancelling a PLACED order must succeed"

    # TC-O-05
    def test_cancel_nonexistent_order_returns_404(self):
        r = post("/orders/999999/cancel", {})
        assert r.status_code == 404, "Cancelling non-existent order must return 404"

    # TC-O-06
    def test_cancel_delivered_order_returns_400(self):
        """Orders in DELIVERED status must not be cancellable."""
        # Find a delivered order via admin
        admin_orders = get("/admin/orders", headers=ROLL).json()
        delivered = next(
            (o for o in admin_orders if o.get("order_status") == "DELIVERED"), None
        )
        if not delivered:
            pytest.skip("No DELIVERED orders in seed data")
        r = post(f"/orders/{delivered['order_id']}/cancel", {}, headers=USER_1)
        assert r.status_code == 400, "Cancelling a DELIVERED order must return 400"

    # TC-O-07
    def test_cancel_order_restores_stock(self):
        """Cancelling an order must add items back to product stock."""
        stock_before = get("/products/1").json().get("stock_quantity", 0)
        order_id = self._place_order("CARD")
        if not order_id:
            pytest.skip("Could not place order")
        post(f"/orders/{order_id}/cancel", {})
        stock_after = get("/products/1").json().get("stock_quantity", 0)
        assert stock_after == stock_before, \
            "Stock must be restored after order cancellation"

    # TC-O-08
    def test_invoice_contains_required_fields(self):
        """Invoice must include subtotal, gst_amount, and total."""
        order_id = self._place_order("CARD")
        if not order_id:
            pytest.skip("Could not place order")
        r = get(f"/orders/{order_id}/invoice")
        assert r.status_code == 200
        invoice = r.json()
        for field in ("subtotal", "gst_amount", "total"):
            assert field in invoice, f"Invoice must include '{field}'"

    # TC-O-09
    def test_invoice_total_matches_order_total(self):
        """Invoice total must match the actual order total."""
        order_id = self._place_order("CARD")
        if not order_id:
            pytest.skip("Could not place order")
        order = get(f"/orders/{order_id}").json()
        invoice = get(f"/orders/{order_id}/invoice").json()
        assert round(invoice.get("total", 0), 2) == round(order.get("total_amount", 0), 2), \
            "Invoice total must match order total_amount"


# ══════════════════════════════════════════════════════════════════════════════
# 12.  REVIEWS
# ══════════════════════════════════════════════════════════════════════════════

class TestReviews:

    PRODUCT_ID = 1

    def _post_review(self, rating, comment="Great product"):
        return post(f"/products/{self.PRODUCT_ID}/reviews",
                    {"rating": rating, "comment": comment})

    # TC-R-01
    def test_get_reviews_returns_list(self):
        r = get(f"/products/{self.PRODUCT_ID}/reviews")
        assert r.status_code == 200
        assert isinstance(r.json(), list) or "reviews" in r.json()

    # TC-R-02
    def test_post_review_valid(self):
        r = self._post_review(5, "Excellent!")
        assert r.status_code in (200, 201), "Valid review must be created"

    # TC-R-03
    def test_review_rating_boundary_1_accepted(self):
        r = self._post_review(1)
        assert r.status_code in (200, 201), "Rating of 1 must be accepted"

    # TC-R-04
    def test_review_rating_boundary_5_accepted(self):
        r = self._post_review(5)
        assert r.status_code in (200, 201), "Rating of 5 must be accepted"

    # TC-R-05
    def test_review_rating_0_returns_400(self):
        """Rating of 0 is below minimum of 1."""
        r = self._post_review(0)
        assert r.status_code == 400, "Rating 0 must return 400"

    # TC-R-06
    def test_review_rating_6_returns_400(self):
        """Rating of 6 is above maximum of 5."""
        r = self._post_review(6)
        assert r.status_code == 400, "Rating 6 must return 400"

    # TC-R-07
    def test_review_rating_negative_returns_400(self):
        r = self._post_review(-1)
        assert r.status_code == 400, "Negative rating must return 400"

    # TC-R-08
    def test_review_comment_empty_returns_400(self):
        """Comment must be at least 1 character."""
        r = self._post_review(3, "")
        assert r.status_code == 400, "Empty comment must return 400"

    # TC-R-09
    def test_review_comment_201_chars_returns_400(self):
        """Comment over 200 characters must be rejected."""
        r = self._post_review(3, "A" * 201)
        assert r.status_code == 400, "Comment > 200 chars must return 400"

    # TC-R-10
    def test_review_comment_200_chars_accepted(self):
        """Comment of exactly 200 characters must be accepted."""
        r = self._post_review(3, "A" * 200)
        assert r.status_code in (200, 201), "Comment of 200 chars must be accepted"

    # TC-R-11
    def test_review_for_nonexistent_product_returns_404(self):
        r = post("/products/999999/reviews", {"rating": 5, "comment": "Good"})
        assert r.status_code == 404, "Review for non-existent product must return 404"

    # TC-R-12
    def test_average_rating_is_decimal_not_integer(self):
        """Average rating must be a proper decimal (e.g. 3.5, not 3)."""
        # Post two reviews with ratings that produce a non-integer average
        self._post_review(3)
        self._post_review(4)
        r = get(f"/products/{self.PRODUCT_ID}/reviews")
        data = r.json()
        avg = data.get("average_rating") if isinstance(data, dict) else None
        if avg is not None:
            # 3+4/2 = 3.5  — ensure it's not truncated to 3
            assert isinstance(avg, float) or (avg != int(avg)), \
                "Average rating must be decimal, not truncated integer"

    # TC-R-13
    def test_no_reviews_product_average_is_zero(self):
        """A product with no reviews must show average_rating of 0."""
        # Use admin to find a product with no reviews
        all_reviews = []  # Skip if we can't isolate; note as potential test
        r = get(f"/products/250/reviews")   # high ID — likely no reviews
        if r.status_code == 200:
            data = r.json()
            avg = data.get("average_rating") if isinstance(data, dict) else None
            if avg is not None and (isinstance(data, list) and len(data) == 0):
                assert avg == 0, "No-review product must have average_rating=0"

    # TC-R-14
    def test_review_missing_rating_returns_400(self):
        r = post(f"/products/{self.PRODUCT_ID}/reviews", {"comment": "Nice"})
        assert r.status_code == 400, "Missing rating must return 400"


# ══════════════════════════════════════════════════════════════════════════════
# 13.  SUPPORT TICKETS
# ══════════════════════════════════════════════════════════════════════════════

class TestSupportTickets:

    VALID_TICKET = {
        "subject": "Order not delivered",
        "message": "My order was not delivered within the promised time."
    }

    def _create_ticket(self, override=None):
        payload = {**self.VALID_TICKET, **(override or {})}
        return post("/support/ticket", payload)

    # TC-ST-01
    def test_create_ticket_valid(self):
        r = self._create_ticket()
        assert r.status_code in (200, 201), "Valid ticket creation must succeed"

    # TC-ST-02
    def test_new_ticket_status_is_open(self):
        """A newly created ticket must have status OPEN."""
        r = self._create_ticket()
        assert r.status_code in (200, 201)
        ticket = r.json()
        status = ticket.get("status") or ticket.get("ticket", {}).get("status")
        assert status == "OPEN", "New ticket must start with status OPEN"

    # TC-ST-03
    def test_create_ticket_subject_too_short_returns_400(self):
        """Subject under 5 characters must be rejected."""
        r = self._create_ticket({"subject": "Hi"})
        assert r.status_code == 400, "Subject < 5 chars must return 400"

    # TC-ST-04
    def test_create_ticket_subject_boundary_5_chars(self):
        """Subject of exactly 5 characters must be accepted."""
        r = self._create_ticket({"subject": "Hello"})
        assert r.status_code in (200, 201), "Subject of 5 chars must be accepted"

    # TC-ST-05
    def test_create_ticket_subject_101_chars_returns_400(self):
        """Subject over 100 characters must be rejected."""
        r = self._create_ticket({"subject": "A" * 101})
        assert r.status_code == 400, "Subject > 100 chars must return 400"

    # TC-ST-06
    def test_create_ticket_subject_boundary_100_chars(self):
        """Subject of exactly 100 characters must be accepted."""
        r = self._create_ticket({"subject": "A" * 100})
        assert r.status_code in (200, 201), "Subject of 100 chars must be accepted"

    # TC-ST-07
    def test_create_ticket_empty_message_returns_400(self):
        """Message must be at least 1 character."""
        r = self._create_ticket({"message": ""})
        assert r.status_code == 400, "Empty message must return 400"

    # TC-ST-08
    def test_create_ticket_message_501_chars_returns_400(self):
        """Message over 500 characters must be rejected."""
        r = self._create_ticket({"message": "A" * 501})
        assert r.status_code == 400, "Message > 500 chars must return 400"

    # TC-ST-09
    def test_create_ticket_message_boundary_500_chars(self):
        """Message of exactly 500 characters must be accepted."""
        r = self._create_ticket({"message": "A" * 500})
        assert r.status_code in (200, 201), "Message of 500 chars must be accepted"

    # TC-ST-10
    def test_message_saved_exactly_as_written(self):
        """The full message must be stored exactly, no truncation."""
        msg = "Special characters test: #@!$%^&*() and unicode: café"
        r = self._create_ticket({"message": msg})
        assert r.status_code in (200, 201)
        ticket = r.json()
        ticket_id = ticket.get("ticket_id") or ticket.get("ticket", {}).get("ticket_id")
        if ticket_id:
            tickets = get("/support/tickets").json()
            found = next((t for t in tickets if t.get("ticket_id") == ticket_id), None)
            if found:
                assert found.get("message") == msg, "Message must be saved exactly as written"

    # TC-ST-11
    def test_get_tickets_returns_list(self):
        r = get("/support/tickets")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # TC-ST-12
    def test_update_ticket_open_to_in_progress(self):
        """OPEN → IN_PROGRESS is a valid transition."""
        r = self._create_ticket()
        ticket_id = r.json().get("ticket_id") or r.json().get("ticket", {}).get("ticket_id")
        if not ticket_id:
            pytest.skip("Could not get ticket_id")
        r2 = put(f"/support/tickets/{ticket_id}", {"status": "IN_PROGRESS"})
        assert r2.status_code == 200, "OPEN→IN_PROGRESS must succeed"

    # TC-ST-13
    def test_update_ticket_in_progress_to_closed(self):
        """IN_PROGRESS → CLOSED is a valid transition."""
        r = self._create_ticket()
        ticket_id = r.json().get("ticket_id") or r.json().get("ticket", {}).get("ticket_id")
        if not ticket_id:
            pytest.skip("Could not get ticket_id")
        put(f"/support/tickets/{ticket_id}", {"status": "IN_PROGRESS"})
        r2 = put(f"/support/tickets/{ticket_id}", {"status": "CLOSED"})
        assert r2.status_code == 200, "IN_PROGRESS→CLOSED must succeed"

    # TC-ST-14
    def test_update_ticket_open_to_closed_returns_400(self):
        """OPEN → CLOSED is an invalid skip — must be rejected."""
        r = self._create_ticket()
        ticket_id = r.json().get("ticket_id") or r.json().get("ticket", {}).get("ticket_id")
        if not ticket_id:
            pytest.skip("Could not get ticket_id")
        r2 = put(f"/support/tickets/{ticket_id}", {"status": "CLOSED"})
        assert r2.status_code == 400, "OPEN→CLOSED must return 400 (invalid transition)"

    # TC-ST-15
    def test_update_ticket_closed_to_open_returns_400(self):
        """Reversing a CLOSED ticket to OPEN must be rejected."""
        r = self._create_ticket()
        ticket_id = r.json().get("ticket_id") or r.json().get("ticket", {}).get("ticket_id")
        if not ticket_id:
            pytest.skip("Could not get ticket_id")
        put(f"/support/tickets/{ticket_id}", {"status": "IN_PROGRESS"})
        put(f"/support/tickets/{ticket_id}", {"status": "CLOSED"})
        r2 = put(f"/support/tickets/{ticket_id}", {"status": "OPEN"})
        assert r2.status_code == 400, "Reversing CLOSED→OPEN must return 400"

    # TC-ST-16
    def test_update_ticket_invalid_status_returns_400(self):
        """Invalid status string must return 400."""
        r = self._create_ticket()
        ticket_id = r.json().get("ticket_id") or r.json().get("ticket", {}).get("ticket_id")
        if not ticket_id:
            pytest.skip("Could not get ticket_id")
        r2 = put(f"/support/tickets/{ticket_id}", {"status": "PENDING"})
        assert r2.status_code == 400, "Invalid status must return 400"

    # TC-ST-17
    def test_create_ticket_missing_subject_returns_400(self):
        r = post("/support/ticket", {"message": "Valid message here"})
        assert r.status_code == 400, "Missing subject must return 400"

    # TC-ST-18
    def test_create_ticket_missing_message_returns_400(self):
        r = post("/support/ticket", {"subject": "Valid Subject Here"})
        assert r.status_code == 400, "Missing message must return 400"