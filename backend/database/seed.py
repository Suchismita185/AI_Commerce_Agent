from .database import Base, engine, SessionLocal
from .models import Product


def seed_products():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Avoid inserting duplicate products
    if db.query(Product).count() > 0:
        print("Products already exist.")
        db.close()
        return

    products = [
        Product(
            name="Premium Laptop Backpack",
            description="Water-resistant backpack with a 15.6-inch laptop compartment.",
            category="Bags",
            price=1799,
            stock=20,
            tags="laptop,college,travel,backpack",
            upsell_product_id=2
        ),

        Product(
            name="Rain Cover",
            description="Waterproof rain cover suitable for laptop backpacks.",
            category="Accessories",
            price=199,
            stock=50,
            tags="rain,waterproof,backpack,travel"
        ),

        Product(
            name="Adjustable Laptop Stand",
            description="Adjustable ergonomic stand for laptops.",
            category="Accessories",
            price=799,
            stock=30,
            tags="laptop,stand,office,ergonomic"
        ),

        Product(
            name="Laptop Sleeve",
            description="Protective sleeve for laptops up to 15.6 inches.",
            category="Accessories",
            price=499,
            stock=40,
            tags="laptop,sleeve,protection"
        ),

        Product(
            name="Travel Water Bottle",
            description="Reusable insulated water bottle for travel and college.",
            category="Travel",
            price=299,
            stock=60,
            tags="water,bottle,travel,college"
        )
    ]

    db.add_all(products)
    db.commit()

    print("Products successfully added.")

    db.close()


if __name__ == "__main__":
    seed_products()