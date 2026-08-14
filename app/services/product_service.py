from sqlmodel import Session, select

from app.models.product import Product, ProductCreate, ProductUpdate

# La Capa de Servicios se encarga EXCLUSIVAMENTE de la lógica.
# Jamás sabe qué es una "Request" o "FastAPI". Separación absoluta y agnóstica de la capa web.

def get_products(session: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    statement = select(Product).offset(skip).limit(limit)
    return list(session.exec(statement).all())

def get_product_by_id(session: Session, product_id: int) -> Product | None:
    return session.get(Product, product_id)

def create_product(session: Session, product_in: ProductCreate) -> Product:
    product_db = Product.model_validate(product_in)
    session.add(product_db)
    session.commit()
    session.refresh(product_db)
    return product_db

def update_product(session: Session, product_id: int, product_in: ProductUpdate) -> Product | None:
    product_db = get_product_by_id(session, product_id)
    if not product_db:
        return None
    
    update_data = product_in.model_dump(exclude_unset=True)
    product_db.sqlmodel_update(update_data)
    
    session.add(product_db)
    session.commit()
    session.refresh(product_db)
    return product_db

def delete_product(session: Session, product_id: int) -> bool:
    product_db = get_product_by_id(session, product_id)
    if not product_db:
        return False
        
    session.delete(product_db)
    session.commit()
    return True
