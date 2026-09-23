from fastapi import FastAPI, HTTPException, Depends, Query
from app.schemas import ProductCreate, ProductResponse, ProductUpdate
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product

app = FastAPI(
    title="E-Commerce Product Service",
    version="1.0.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "product-service"
    }
    

@app.post("/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        quantity=product.quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

# @app.get("/products", response_model=list[ProductResponse])
# def get_products():
#     return products

# @app.get("/products", response_model=list[ProductResponse])
# def get_products(db: Session = Depends(get_db)):
#     return db.query(Product).all()

@app.get("/products", response_model=list[ProductResponse])
def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit

    products = (
        db.query(Product)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return products


# @app.get("/products/{product_id}", response_model=ProductResponse)
# def get_product(product_id: int):
#     for product in products:
#         if product["id"] == product_id:
#             return product

#     raise HTTPException(
#         status_code=404,
#         detail="Product not found"
#     )
    
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

# @app.put("/products/{product_id}", response_model=ProductResponse)
# def update_product(product_id: int, product: ProductUpdate):
#     for existing_product in products:
#         if existing_product["id"] == product_id:
#             existing_product["name"] = product.name
#             existing_product["description"] = product.description
#             existing_product["price"] = product.price
#             existing_product["quantity"] = product.quantity

#             return existing_product

#     raise HTTPException(
#         status_code=404,
#         detail="Product not found"
#     )
    
@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    existing_product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.quantity = product.quantity

    db.commit()
    db.refresh(existing_product)

    return existing_product


# @app.delete("/products/{product_id}")
# def delete_product(product_id: int):
#     for index, product in enumerate(products):
#         if product["id"] == product_id:
#             deleted_product = products.pop(index)

#             return {
#                 "message": "Product deleted successfully",
#                 "product": deleted_product
#             }

#     raise HTTPException(
#         status_code=404,
#         detail="Product not found"
#     )

@app.delete("/products/{product_id}")
def delete_product(
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

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }