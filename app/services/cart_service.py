from sqlmodel import Session, select

from app.models.cart_item import CartItem, CartItemCreate


def get_cart(session: Session, user_id: int) -> list[CartItem]:
    statement = select(CartItem).where(CartItem.user_id == user_id)
    return list(session.exec(statement).all())


def add_to_cart(session: Session, cart_in: CartItemCreate, user_id: int) -> CartItem:
    # Buscar si ya existe el producto en el carrito del usuario
    statement = select(CartItem).where(
        CartItem.user_id == user_id, CartItem.product_id == cart_in.product_id
    )
    existing_item = session.exec(statement).first()

    if existing_item:
        # Si ya existe, acumulamos la cantidad
        existing_item.quantity += cart_in.quantity
        session.add(existing_item)
        session.commit()
        session.refresh(existing_item)
        return existing_item

    # Si no existe, creamos un nuevo registro en el carrito
    db_item = CartItem.model_validate(cart_in)
    db_item.user_id = user_id

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
