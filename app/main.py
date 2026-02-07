from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.core.config import SECRET_KEY, ALGORITHM
from app.core.auth import get_current_user
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import require_role


from app.db.session import get_db, engine
from app.db.base import Base

from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem

from app.schemas.user import UserCreate, UserRead
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.schemas.order import OrderCreate, OrderRead
from app.schemas.auth import Token



app = FastAPI()

# Create tables in DB (if they do not exist)
# Base.metadata.create_all(bind=engine) - replaced with alembic migrations


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok"}

@app.get("/auth/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=get_password_hash(user_in.password),
        role = user_in.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.post("/products", response_model=ProductRead, status_code=201)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        supplier_id=current_user.id,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.get("/products", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.id.desc()).all()
    return products

@app.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.supplier_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this product")

    if product_in.name is not None:
        product.name = product_in.name
    if product_in.description is not None:
        product.description = product_in.description
    if product_in.price is not None:
        product.price = product_in.price

    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.supplier_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this product")

    db.delete(product)
    db.commit()
    return {"deleted": "True"}

@app.get("/orders/my", response_model=list[OrderRead])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("consumer")),
):
    orders = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.consumer_id == current_user.id)
        .order_by(Order.created_aat.desc())
        .all()
    )
    return orders

@app.post("/orders", response_model=OrderRead)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("consumer")),
):
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    order = Order(
        consumer_id=current_user.id,
        status="pending",
    )
    db.add(order)
    db.flush()  # Get order.id before committing

    for item_in in order_in.items:
        if item_in.quantity <= 0:
            raise HTTPException(status_code=400, detail="Item quantity must be greater than zero")
        
        product = db.query(Product).filter(Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item_in.product_id} not found")
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            unit_price=product.price,
        )
        db.add(order_item)

    db.commit()
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.id == order.id).first()
    return order

@app.get("/orders/for-my-products", response_model=list[OrderRead])
def list_orders_for_supplier_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("supplier")),
):
    orders = (
        db.query(Order)
        .options(joinedload(Order.items))
        .join(OrderItem, OrderItem.order_id == Order.id)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(Product.supplier_id == current_user.id)
        .distinct()
        .order_by(Order.id.desc())
        .all()
    )
    return orders

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger sends "username", we will treat it as email
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}





