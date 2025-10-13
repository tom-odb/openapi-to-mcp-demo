#!/usr/bin/env python3
"""
Seed script to populate the dummy API with sample data
Run this after starting the API server
"""

import requests
import json
from typing import List, Dict

API_BASE = "http://localhost:8000"

def create_products() -> List[str]:
    """Create sample products and return their IDs"""
    products = [
        {
            "name": "Laptop Pro 15",
            "description": "High-performance laptop with 16GB RAM",
            "price": 1299.99,
            "currency": "USD",
            "category": "Electronics",
            "stock": 25
        },
        {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "price": 29.99,
            "currency": "USD",
            "category": "Electronics",
            "stock": 100
        },
        {
            "name": "USB-C Cable",
            "description": "2m USB-C charging cable",
            "price": 12.99,
            "currency": "USD",
            "category": "Accessories",
            "stock": 200
        },
        {
            "name": "Desk Chair",
            "description": "Ergonomic office chair",
            "price": 249.99,
            "currency": "USD",
            "category": "Furniture",
            "stock": 15
        },
        {
            "name": "Standing Desk",
            "description": "Adjustable height standing desk",
            "price": 599.99,
            "currency": "USD",
            "category": "Furniture",
            "stock": 10
        },
        {
            "name": "Mechanical Keyboard",
            "description": "RGB mechanical keyboard",
            "price": 89.99,
            "currency": "USD",
            "category": "Electronics",
            "stock": 50
        }
    ]
    
    product_ids = []
    print("Creating products...")
    for product in products:
        response = requests.post(f"{API_BASE}/products", json=product)
        if response.status_code == 201:
            product_data = response.json()
            product_ids.append(product_data["id"])
            print(f"  ✓ Created: {product['name']} (ID: {product_data['id']})")
        else:
            print(f"  ✗ Failed to create: {product['name']}")
    
    return product_ids

def create_customers() -> List[str]:
    """Create sample customers and return their IDs"""
    customers = [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1-555-0101",
            "defaultShippingAddress": {
                "line1": "123 Main St",
                "line2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postalCode": "10001",
                "country": "US"
            }
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone": "+1-555-0102",
            "defaultShippingAddress": {
                "line1": "456 Oak Avenue",
                "city": "Los Angeles",
                "state": "CA",
                "postalCode": "90001",
                "country": "US"
            }
        },
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "phone": "+1-555-0103",
            "defaultShippingAddress": {
                "line1": "789 Pine Road",
                "city": "Chicago",
                "state": "IL",
                "postalCode": "60601",
                "country": "US"
            }
        }
    ]
    
    customer_ids = []
    print("\nCreating customers...")
    for customer in customers:
        response = requests.post(f"{API_BASE}/customers", json=customer)
        if response.status_code == 201:
            customer_data = response.json()
            customer_ids.append(customer_data["id"])
            print(f"  ✓ Created: {customer['name']} (ID: {customer_data['id']})")
        else:
            print(f"  ✗ Failed to create: {customer['name']}")
    
    return customer_ids

def create_orders(customer_ids: List[str], product_ids: List[str]):
    """Create sample orders"""
    if not customer_ids or not product_ids:
        print("\nNo customers or products available for creating orders")
        return
    
    orders = [
        {
            "customerId": customer_ids[0],
            "items": [
                {"productId": product_ids[0], "quantity": 1},  # Laptop
                {"productId": product_ids[1], "quantity": 2}   # Mouse
            ]
        },
        {
            "customerId": customer_ids[1],
            "items": [
                {"productId": product_ids[3], "quantity": 1},  # Desk Chair
                {"productId": product_ids[4], "quantity": 1}   # Standing Desk
            ]
        },
        {
            "customerId": customer_ids[2],
            "items": [
                {"productId": product_ids[5], "quantity": 1},  # Keyboard
                {"productId": product_ids[2], "quantity": 3}   # USB-C Cable
            ]
        }
    ]
    
    print("\nCreating orders...")
    for i, order in enumerate(orders, 1):
        response = requests.post(f"{API_BASE}/orders", json=order)
        if response.status_code == 201:
            order_data = response.json()
            print(f"  ✓ Created order {i} (ID: {order_data['id']}, Total: ${order_data['total']:.2f})")
        else:
            print(f"  ✗ Failed to create order {i}: {response.text}")

def main():
    print("=" * 60)
    print("Seeding E-Commerce API with sample data")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            print(f"API returned status code {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to API at {API_BASE}")
        print("Make sure the API server is running (python main.py)")
        return
    
    # Create data
    product_ids = create_products()
    customer_ids = create_customers()
    create_orders(customer_ids, product_ids)
    
    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)
    print(f"\nAPI Documentation: {API_BASE}/docs")
    print(f"View Products: {API_BASE}/products")
    print(f"View Customers: {API_BASE}/customers")
    print(f"View Orders: {API_BASE}/orders")

if __name__ == "__main__":
    main()
