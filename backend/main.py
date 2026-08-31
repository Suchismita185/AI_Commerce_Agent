from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database.database import get_db
from .database.models import Product

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