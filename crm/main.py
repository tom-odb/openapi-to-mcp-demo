from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

# Initialize FastAPI app
app = FastAPI(
    title="E-Commerce API",
    version="1.1.0",
    description="A simple e-commerce API for managing products, orders, and customers"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

# Models
class Address(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: str
    country: str = Field(..., example="BE", description="ISO 3166-1 alpha-2 country code")

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    currency: str = "USD"
    category: Optional[str] = None
    stock: Optional[int] = Field(0, ge=0)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)

class Product(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    currency: str = "USD"
    category: Optional[str] = None
    stock: int = Field(..., ge=0)
    createdAt: datetime

class ProductListResponse(BaseModel):
    products: List[Product]
    total: int
    page: int
    limit: int

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    defaultShippingAddress: Optional[Address] = None

class Customer(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str] = None
    defaultShippingAddress: Optional[Address] = None
    createdAt: datetime

class CustomerListResponse(BaseModel):
    customers: List[Customer]
    total: int
    page: int
    limit: int

class OrderItem(BaseModel):
    productId: UUID
    quantity: int = Field(..., ge=1)
    unitPrice: float = Field(..., ge=0)

class OrderItemCreate(BaseModel):
    productId: UUID
    quantity: int = Field(..., ge=1)

class OrderCreate(BaseModel):
    customerId: UUID
    items: List[OrderItemCreate] = Field(..., min_items=1)
    shippingAddress: Optional[Address] = None
    currency: Optional[str] = None

class Order(BaseModel):
    id: UUID
    customerId: UUID
    status: OrderStatus = OrderStatus.pending
    items: List[OrderItem] = Field(..., min_items=1)
    shippingAddress: Optional[Address] = None
    currency: str
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(..., ge=0)
    tax: float = Field(..., ge=0)
    discount: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
    createdAt: datetime
    updatedAt: datetime

class OrderListResponse(BaseModel):
    orders: List[Order]
    total: int
    page: int
    limit: int

# In-memory storage
products_db = {}
customers_db = {}
orders_db = {}

# Seed data
def load_seed_data():
    """Load initial seed data into the database"""
    from datetime import datetime
    from uuid import uuid4
    
    # Create sample products
    sample_products = [
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
    for product_data in sample_products:
        product = Product(
            id=uuid4(),
            **product_data,
            createdAt=datetime.now()
        )
        products_db[product.id] = product
        product_ids.append(product.id)
    
    # Create sample customers
    sample_customers = [
        {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "phone": "+1-555-0101",
            "defaultShippingAddress": Address(
                line1="123 Main St",
                line2="Apt 4B",
                city="New York",
                state="NY",
                postalCode="10001",
                country="US"
            )
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone": "+1-555-0102",
            "defaultShippingAddress": Address(
                line1="456 Oak Avenue",
                city="Los Angeles",
                state="CA",
                postalCode="90001",
                country="US"
            )
        },
        {
            "name": "Carol Williams",
            "email": "carol@example.com",
            "phone": "+1-555-0103",
            "defaultShippingAddress": Address(
                line1="789 Pine Road",
                city="Chicago",
                state="IL",
                postalCode="60601",
                country="US"
            )
        }
    ]
    
    customer_ids = []
    for customer_data in sample_customers:
        customer = Customer(
            id=uuid4(),
            **customer_data,
            createdAt=datetime.now()
        )
        customers_db[customer.id] = customer
        customer_ids.append(customer.id)
    
    # Create sample orders
    sample_orders = [
        {
            "customer_idx": 0,
            "items": [
                {"product_idx": 0, "quantity": 1},  # Laptop
                {"product_idx": 1, "quantity": 2}   # Mouse
            ]
        },
        {
            "customer_idx": 1,
            "items": [
                {"product_idx": 3, "quantity": 1},  # Desk Chair
                {"product_idx": 4, "quantity": 1}   # Standing Desk
            ]
        },
        {
            "customer_idx": 2,
            "items": [
                {"product_idx": 5, "quantity": 1},  # Keyboard
                {"product_idx": 2, "quantity": 3}   # USB-C Cable
            ]
        }
    ]
    
    for order_data in sample_orders:
        customer = customers_db[customer_ids[order_data["customer_idx"]]]
        
        # Create order items
        order_items = []
        for item_data in order_data["items"]:
            product = products_db[product_ids[item_data["product_idx"]]]
            order_items.append(OrderItem(
                productId=product.id,
                quantity=item_data["quantity"],
                unitPrice=product.price
            ))
            # Update stock
            product.stock -= item_data["quantity"]
        
        # Calculate totals
        totals = calculate_order_totals(order_items)
        
        # Create order
        now = datetime.now()
        order = Order(
            id=uuid4(),
            customerId=customer.id,
            status=OrderStatus.pending,
            items=order_items,
            shippingAddress=customer.defaultShippingAddress,
            currency="USD",
            discount=0,
            createdAt=now,
            updatedAt=now,
            **totals
        )
        orders_db[order.id] = order

# Helper functions
def get_product_or_404(product_id: UUID) -> Product:
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

def get_customer_or_404(customer_id: UUID) -> Customer:
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers_db[customer_id]

def get_order_or_404(order_id: UUID) -> Order:
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]

def calculate_order_totals(items: List[OrderItem]) -> dict:
    subtotal = sum(item.unitPrice * item.quantity for item in items)
    shipping = 10.0  # Fixed shipping cost
    tax = subtotal * 0.1  # 10% tax
    total = subtotal + shipping + tax
    return {
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": total
    }

# Product endpoints
@app.get("/products", response_model=ProductListResponse, tags=["Products"])
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    category: Optional[str] = None
):
    """List all products with optional category filter"""
    products = list(products_db.values())
    
    if category:
        products = [p for p in products if p.category == category]
    
    total = len(products)
    start = (page - 1) * limit
    end = start + limit
    paginated_products = products[start:end]
    
    return ProductListResponse(
        products=paginated_products,
        total=total,
        page=page,
        limit=limit
    )

@app.post("/products", response_model=Product, status_code=201, tags=["Products"])
async def create_product(product: ProductCreate):
    """Create a new product"""
    new_product = Product(
        id=uuid4(),
        **product.model_dump(),
        createdAt=datetime.now()
    )
    products_db[new_product.id] = new_product
    return new_product

@app.get("/products/{productId}", response_model=Product, tags=["Products"])
async def get_product(productId: UUID):
    """Get product details by ID"""
    return get_product_or_404(productId)

@app.put("/products/{productId}", response_model=Product, tags=["Products"])
async def update_product(productId: UUID, product_update: ProductUpdate):
    """Update a product"""
    product = get_product_or_404(productId)
    
    update_data = product_update.model_dump(exclude_unset=True)
    updated_product = product.model_copy(update=update_data)
    products_db[productId] = updated_product
    
    return updated_product

@app.delete("/products/{productId}", status_code=204, tags=["Products"])
async def delete_product(productId: UUID):
    """Delete a product"""
    if productId not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del products_db[productId]
    return None

# Customer endpoints
@app.get("/customers", response_model=CustomerListResponse, tags=["Customers"])
async def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    search: Optional[str] = None
):
    """List all customers with optional search"""
    customers = list(customers_db.values())
    
    if search:
        search_lower = search.lower()
        customers = [
            c for c in customers 
            if search_lower in c.name.lower() or search_lower in c.email.lower()
        ]
    
    total = len(customers)
    start = (page - 1) * limit
    end = start + limit
    paginated_customers = customers[start:end]
    
    return CustomerListResponse(
        customers=paginated_customers,
        total=total,
        page=page,
        limit=limit
    )

@app.post("/customers", response_model=Customer, status_code=201, tags=["Customers"])
async def create_customer(customer: CustomerCreate):
    """Create a new customer"""
    new_customer = Customer(
        id=uuid4(),
        **customer.model_dump(),
        createdAt=datetime.now()
    )
    customers_db[new_customer.id] = new_customer
    return new_customer

@app.get("/customers/{customerId}", response_model=Customer, tags=["Customers"])
async def get_customer(customerId: UUID):
    """Get customer details by ID"""
    return get_customer_or_404(customerId)

@app.get("/customers/{customerId}/orders", response_model=OrderListResponse, tags=["Customers", "Orders"])
async def list_customer_orders(
    customerId: UUID,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200)
):
    """List orders for a specific customer"""
    # Verify customer exists
    get_customer_or_404(customerId)
    
    orders = [o for o in orders_db.values() if o.customerId == customerId]
    
    total = len(orders)
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = orders[start:end]
    
    return OrderListResponse(
        orders=paginated_orders,
        total=total,
        page=page,
        limit=limit
    )

# Order endpoints
@app.get("/orders", response_model=OrderListResponse, tags=["Orders"])
async def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    status: Optional[OrderStatus] = None,
    customerId: Optional[UUID] = None
):
    """List all orders with optional filters"""
    orders = list(orders_db.values())
    
    if status:
        orders = [o for o in orders if o.status == status]
    
    if customerId:
        orders = [o for o in orders if o.customerId == customerId]
    
    total = len(orders)
    start = (page - 1) * limit
    end = start + limit
    paginated_orders = orders[start:end]
    
    return OrderListResponse(
        orders=paginated_orders,
        total=total,
        page=page,
        limit=limit
    )

@app.post("/orders", response_model=Order, status_code=201, tags=["Orders"])
async def create_order(order_create: OrderCreate):
    """Create a new order"""
    # Verify customer exists
    customer = get_customer_or_404(order_create.customerId)
    
    # Create order items with current product prices
    order_items = []
    for item_create in order_create.items:
        product = get_product_or_404(item_create.productId)
        
        # Check stock
        if product.stock < item_create.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for product {product.id}"
            )
        
        order_items.append(OrderItem(
            productId=item_create.productId,
            quantity=item_create.quantity,
            unitPrice=product.price
        ))
    
    # Calculate totals
    totals = calculate_order_totals(order_items)
    
    # Determine currency
    currency = order_create.currency or "USD"
    
    # Determine shipping address
    shipping_address = order_create.shippingAddress or customer.defaultShippingAddress
    
    # Create order
    now = datetime.now()
    new_order = Order(
        id=uuid4(),
        customerId=order_create.customerId,
        status=OrderStatus.pending,
        items=order_items,
        shippingAddress=shipping_address,
        currency=currency,
        discount=0,
        createdAt=now,
        updatedAt=now,
        **totals
    )
    
    # Update product stock
    for item_create in order_create.items:
        product = products_db[item_create.productId]
        product.stock -= item_create.quantity
    
    orders_db[new_order.id] = new_order
    return new_order

@app.get("/orders/{orderId}", response_model=Order, tags=["Orders"])
async def get_order(orderId: UUID):
    """Get order details by ID"""
    return get_order_or_404(orderId)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load seed data on startup"""
    load_seed_data()
    print("✅ Seed data loaded successfully")
    print(f"   - {len(products_db)} products")
    print(f"   - {len(customers_db)} customers")
    print(f"   - {len(orders_db)} orders")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": "E-Commerce API",
        "version": "1.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
