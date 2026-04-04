from datetime import date
from decimal import Decimal
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy import func

from .models import Category, Coupon, Order, OrderItem, Product, Review, User, db

api = Blueprint("api", __name__, url_prefix="/api")
bcrypt = Bcrypt()


def model_to_dict_product(product):
    avg_rating = db.session.query(func.avg(Review.rating)).filter(Review.product_id == product.id).scalar()
    return {
        "id": product.id,
        "name": product.name,
        "price": float(product.price),
        "description": product.description,
        "image_url": product.image_url,
        "stock_quantity": product.stock_quantity,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else None,
        "avg_rating": round(float(avg_rating), 1) if avg_rating else 0,
    }


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            uid = int(get_jwt_identity())
            user = User.query.get(uid)
            if not user or user.role not in roles:
                return jsonify({"message": "Forbidden"}), 403
            if user.status != "active":
                return jsonify({"message": "Account inactive"}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


@api.post("/auth/register")
def register():
    data = request.get_json() or {}
    required = ["username", "email", "password"]
    if not all(data.get(k) for k in required):
        return jsonify({"message": "Missing required fields"}), 400

    if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
        return jsonify({"message": "Username or email already exists"}), 409

    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    user = User(username=data["username"], email=data["email"], password=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registered successfully"}), 201


@api.post("/auth/login")
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not bcrypt.check_password_hash(user.password, data.get("password", "")):
        return jsonify({"message": "Invalid credentials"}), 401
    if user.status != "active":
        return jsonify({"message": "Account inactive"}), 403

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(
        {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }
    )


@api.get("/products")
def list_products():
    q = Product.query
    keyword = request.args.get("search")
    category_id = request.args.get("category_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    if keyword:
        q = q.filter(Product.name.ilike(f"%{keyword}%"))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)

    products = q.order_by(Product.created_at.desc()).all()
    return jsonify([model_to_dict_product(p) for p in products])


@api.get("/products/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = (
        Product.query.filter(Product.category_id == product.category_id, Product.id != product.id)
        .order_by(Product.created_at.desc())
        .limit(4)
        .all()
    )
    reviews = (
        Review.query.filter_by(product_id=product_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return jsonify(
        {
            "product": model_to_dict_product(product),
            "related_products": [model_to_dict_product(r) for r in related],
            "reviews": [
                {
                    "id": rv.id,
                    "username": rv.user.username,
                    "rating": rv.rating,
                    "comment": rv.comment,
                    "created_at": rv.created_at.isoformat(),
                }
                for rv in reviews
            ],
        }
    )


@api.get("/categories")
def list_categories():
    return jsonify([{"id": c.id, "name": c.name} for c in Category.query.all()])


@api.post("/reviews")
@jwt_required()
def create_review():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    product_id = data.get("product_id")
    rating = data.get("rating")

    purchased = (
        db.session.query(OrderItem.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.user_id == uid, Order.status == "delivered", OrderItem.product_id == product_id)
        .first()
    )
    if not purchased:
        return jsonify({"message": "Only users who bought this product can review"}), 403

    if not rating or int(rating) not in [1, 2, 3, 4, 5]:
        return jsonify({"message": "Rating must be 1-5"}), 400

    review = Review(user_id=uid, product_id=product_id, rating=int(rating), comment=data.get("comment", ""))
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review submitted"}), 201


@api.post("/coupons/validate")
def validate_coupon():
    code = (request.get_json() or {}).get("code", "").upper().strip()
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    if not coupon or (coupon.expiry_date and coupon.expiry_date < date.today()):
        return jsonify({"valid": False, "message": "Coupon is invalid or expired"}), 404
    return jsonify({"valid": True, "discount_percent": coupon.discount_percent})


@api.post("/orders")
@jwt_required()
def create_order():
    uid = int(get_jwt_identity())
    data = request.get_json() or {}
    cart_items = data.get("items", [])
    if not cart_items:
        return jsonify({"message": "Cart is empty"}), 400

    subtotal = Decimal("0")
    order_items = []

    for item in cart_items:
        product = Product.query.get(item.get("product_id"))
        qty = int(item.get("quantity", 0))
        if not product or qty <= 0:
            return jsonify({"message": "Invalid cart item"}), 400
        if product.stock_quantity < qty:
            return jsonify({"message": f"Insufficient stock: {product.name}"}), 400

        line_total = Decimal(str(product.price)) * qty
        subtotal += line_total
        order_items.append((product, qty, Decimal(str(product.price))))

    discount_percent = 0
    coupon_code = (data.get("coupon_code") or "").upper().strip()
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code, is_active=True).first()
        if coupon and (not coupon.expiry_date or coupon.expiry_date >= date.today()):
            discount_percent = coupon.discount_percent

    total = subtotal * Decimal(100 - discount_percent) / Decimal(100)

    order = Order(
        user_id=uid,
        total_price=total,
        status="pending",
        address=data.get("address"),
        phone=data.get("phone"),
        payment_method=data.get("payment_method", "cod"),
        coupon_code=coupon_code or None,
    )
    db.session.add(order)
    db.session.flush()

    for product, qty, price in order_items:
        product.stock_quantity -= qty
        db.session.add(OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=price))

    db.session.commit()
    return jsonify({"message": "Order created", "order_id": order.id}), 201


@api.get("/me")
@jwt_required()
def me():
    user = User.query.get_or_404(int(get_jwt_identity()))
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
        }
    )


@api.put("/me")
@jwt_required()
def update_profile():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = request.get_json() or {}
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    db.session.commit()
    return jsonify({"message": "Profile updated"})


@api.get("/orders/my")
@jwt_required()
def my_orders():
    uid = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=uid).order_by(Order.created_at.desc()).all()
    payload = []
    for order in orders:
        payload.append(
            {
                "id": order.id,
                "total_price": float(order.total_price),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                "items": [
                    {
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.price),
                    }
                    for item in order.items
                ],
            }
        )
    return jsonify(payload)


@api.get("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    revenue = db.session.query(func.coalesce(func.sum(Order.total_price), 0)).scalar() or 0
    return jsonify(
        {
            "total_revenue": float(revenue),
            "total_orders": Order.query.count(),
            "total_users": User.query.count(),
        }
    )


@api.get("/admin/products")
@role_required("admin")
def admin_products():
    return jsonify([model_to_dict_product(p) for p in Product.query.order_by(Product.id.desc()).all()])


@api.post("/admin/products")
@role_required("admin")
def admin_create_product():
    data = request.get_json() or {}
    product = Product(
        name=data["name"],
        price=data["price"],
        description=data.get("description", ""),
        image_url=data.get("image_url", "https://placehold.co/600x400"),
        stock_quantity=data.get("stock_quantity", 0),
        category_id=data["category_id"],
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product created", "id": product.id}), 201


@api.put("/admin/products/<int:product_id>")
@role_required("admin")
def admin_update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}
    for field in ["name", "price", "description", "image_url", "stock_quantity", "category_id"]:
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return jsonify({"message": "Product updated"})


@api.delete("/admin/products/<int:product_id>")
@role_required("admin")
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})


@api.get("/admin/orders")
@role_required("admin")
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": o.id,
                "username": o.user.username,
                "total_price": float(o.total_price),
                "status": o.status,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders
        ]
    )


@api.put("/admin/orders/<int:order_id>/status")
@role_required("admin")
def admin_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    status = (request.get_json() or {}).get("status")
    if status not in ["approved", "cancelled", "delivering", "delivered", "pending"]:
        return jsonify({"message": "Invalid status"}), 400
    order.status = status
    db.session.commit()
    return jsonify({"message": "Order status updated"})


@api.get("/admin/users")
@role_required("admin")
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "status": u.status,
            }
            for u in users
        ]
    )


@api.put("/admin/users/<int:user_id>/status")
@role_required("admin")
def admin_update_user_status(user_id):
    user = User.query.get_or_404(user_id)
    status = (request.get_json() or {}).get("status")
    if status not in ["active", "inactive"]:
        return jsonify({"message": "Invalid status"}), 400
    user.status = status
    db.session.commit()
    return jsonify({"message": "User status updated"})


@api.get("/admin/coupons")
@role_required("admin")
def admin_list_coupons():
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    return jsonify(
        [
            {
                "id": c.id,
                "code": c.code,
                "discount_percent": c.discount_percent,
                "is_active": c.is_active,
                "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
            }
            for c in coupons
        ]
    )


@api.post("/admin/coupons")
@role_required("admin")
def admin_create_coupon():
    data = request.get_json() or {}
    coupon = Coupon(
        code=data["code"].upper(),
        discount_percent=int(data["discount_percent"]),
        is_active=bool(data.get("is_active", True)),
        expiry_date=data.get("expiry_date"),
    )
    db.session.add(coupon)
    db.session.commit()
    return jsonify({"message": "Coupon created"}), 201
