from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel

from .agent.agent import run_agent

from .database.database import get_db
from .database.models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem
)

app = FastAPI(
    title="RazorAgent API",
    description="AI-powered Agentic Commerce Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "RazorAgent API is running"
    }


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    return products

@app.get("/products/search")
def search_products(
    q: str,
    db: Session = Depends(get_db)
):
    products = (
        db.query(Product)
        .filter(
            (Product.name.ilike(f"%{q}%")) |
            (Product.description.ilike(f"%{q}%")) |
            (Product.category.ilike(f"%{q}%")) |
            (Product.tags.ilike(f"%{q}%"))
        )
        .all()
    )

    return products

@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@app.get("/cart/{customer_id}")
def get_cart(
    customer_id: int,
    db: Session = Depends(get_db)
):
    cart = (
        db.query(Cart)
        .filter(Cart.customer_id == customer_id)
        .first()
    )

    if not cart:
        cart = Cart(customer_id=customer_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )

    result = []

    total = 0

    for item in items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if product:
            item_total = product.price * item.quantity
            total += item_total

            result.append({
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "item_total": item_total
            })

    return {
        "cart_id": cart.id,
        "customer_id": customer_id,
        "items": result,
        "total": total
    }

@app.post("/cart/{customer_id}/add")
def add_to_cart(
    customer_id: int,
    product_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product.stock < quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    cart = (
        db.query(Cart)
        .filter(Cart.customer_id == customer_id)
        .first()
    )

    if not cart:
        cart = Cart(customer_id=customer_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
        .first()
    )

    if cart_item:
        new_quantity = cart_item.quantity + quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock available"
            )

        cart_item.quantity = new_quantity

    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )

        db.add(cart_item)

    db.commit()

    return {
        "message": "Product added to cart",
        "product_id": product_id,
        "quantity": quantity
    }

@app.delete("/cart/{customer_id}/remove/{product_id}")
def remove_from_cart(
    customer_id: int,
    product_id: int,
    db: Session = Depends(get_db)
):
    cart = (
        db.query(Cart)
        .filter(Cart.customer_id == customer_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
        .first()
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Product not found in cart"
        )

    db.delete(item)
    db.commit()

    return {
        "message": "Product removed from cart"
    }

@app.post("/checkout/{customer_id}")
def checkout(
    customer_id: int,
    db: Session = Depends(get_db)
):
    # Find customer's cart
    cart = (
        db.query(Cart)
        .filter(Cart.customer_id == customer_id)
        .first()
    )

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    existing_order = (
        db.query(Order)
        .filter(
            Order.cart_id == cart.id,
            Order.status == "PENDING_PAYMENT"
        )
        .first()
    )

    if existing_order:
        return {
            "message": "Existing pending order found",
            "order_id": existing_order.id,
            "total_amount": existing_order.total_amount,
            "status": existing_order.status
        }

    # Get cart items
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart.id)
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total = 0
    order_items = []

    # Validate products and calculate total
    for item in cart_items:

        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product.name}"
            )

        subtotal = product.price * item.quantity
        total += subtotal

        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "quantity": item.quantity,
            "subtotal": subtotal
        })

    # Create order
    order = Order(
        customer_id=customer_id,
        cart_id=cart.id,
        total_amount=total,
        status="PENDING_PAYMENT"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items
    for item in order_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            product_name=item["product_name"],
            price=item["price"],
            quantity=item["quantity"],
            subtotal=item["subtotal"]
        )

        db.add(order_item)

    db.commit()

    return {
        "message": "Order created successfully",
        "order_id": order.id,
        "customer_id": customer_id,
        "total_amount": total,
        "status": order.status,
        "items": order_items
    }

@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order_id)
        .all()
    )

    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "total_amount": order.total_amount,
        "status": order.status,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "price": item.price,
                "quantity": item.quantity,
                "subtotal": item.subtotal
            }
            for item in items
        ]
    }

class ChatRequest(BaseModel):
    customer_id: int
    message: str

@app.post("/chat")
def chat(request: ChatRequest):

    response = run_agent(
        user_message=request.message,
        customer_id=request.customer_id
    )

    return {
        "response": response
    }