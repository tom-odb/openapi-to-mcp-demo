# E-Commerce Dummy API

A FastAPI implementation of the E-Commerce OpenAPI specification for testing purposes.

## Features

- **Products Management**: Create, read, update, delete products
- **Customer Management**: Create and retrieve customer information
- **Order Management**: Create and track orders with automatic stock updates
- **In-memory Storage**: All data stored in memory (resets on restart)
- **Automatic Documentation**: Interactive API docs at `/docs`

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Using uv (recommended)

Install dependencies:
```bash
uv sync
```

### Using pip (alternative)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

### Using uv (recommended)

Start the server:
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Using pip (alternative)

Start the server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Sample data is automatically loaded on startup!** The API comes pre-populated with:
- 6 Products (Laptop, Mouse, Cable, Chair, Desk, Keyboard)
- 3 Customers (Alice, Bob, Carol)
- 3 Orders

The API will be available at:
- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json

## API Endpoints

### Products
- `GET /products` - List products (with pagination and category filter)
- `POST /products` - Create a product
- `GET /products/{productId}` - Get product details
- `PUT /products/{productId}` - Update a product
- `DELETE /products/{productId}` - Delete a product

### Customers
- `GET /customers` - List customers (with pagination and search)
- `POST /customers` - Create a customer
- `GET /customers/{customerId}` - Get customer details
- `GET /customers/{customerId}/orders` - List orders for a customer

### Orders
- `GET /orders` - List orders (with filters for status and customerId)
- `POST /orders` - Create an order
- `GET /orders/{orderId}` - Get order details

## Example Usage

### Create a Product
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "currency": "USD",
    "category": "Electronics",
    "stock": 50
  }'
```

### Create a Customer
```bash
curl -X POST "http://localhost:8000/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }'
```

### Create an Order
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customerId": "customer-uuid-here",
    "items": [
      {
        "productId": "product-uuid-here",
        "quantity": 2
      }
    ]
  }'
```

> **Tip:** Use `GET /customers` and `GET /products` to get valid UUIDs for creating orders.

## Features Implemented

- ✅ All CRUD operations for Products, Customers, and Orders
- ✅ Pagination support (page, limit parameters)
- ✅ Filtering (category, status, customerId, search)
- ✅ Automatic stock management when orders are created
- ✅ Order total calculations (subtotal, shipping, tax)
- ✅ UUID-based identifiers
- ✅ Proper HTTP status codes (200, 201, 204, 404)
- ✅ Input validation with Pydantic
- ✅ CORS enabled for frontend integration
- ✅ Automatic seed data on startup

## Notes

- All data is stored in memory and will be lost when the server restarts
- Sample data (products, customers, orders) automatically loads on startup
- Stock is automatically decremented when orders are created
- Orders automatically calculate totals based on product prices
- Fixed shipping cost of $10.00 and 10% tax rate
