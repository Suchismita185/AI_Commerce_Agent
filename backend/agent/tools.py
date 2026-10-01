import requests


BASE_URL = "http://127.0.0.1:8000"


def search_products(query: str):
    """
    Search the merchant product catalog.
    """

    response = requests.get(
        f"{BASE_URL}/products/search",
        params={"q": query}
    )

    response.raise_for_status()

    return response.json()

def get_product(product_id: int):
    """
    Get detailed information about a product.
    """

    response = requests.get(
        f"{BASE_URL}/products/{product_id}"
    )

    response.raise_for_status()

    return response.json()

def add_to_cart(
    customer_id: int,
    product_id: int,
    quantity: int = 1
):
    """
    Add a product to the customer's cart.
    """

    response = requests.post(
        f"{BASE_URL}/cart/{customer_id}/add",
        params={
            "product_id": product_id,
            "quantity": quantity
        }
    )

    response.raise_for_status()

    return response.json()

def get_cart(customer_id: int):
    """
    Get the customer's current cart.
    """

    response = requests.get(
        f"{BASE_URL}/cart/{customer_id}"
    )

    response.raise_for_status()

    return response.json()

