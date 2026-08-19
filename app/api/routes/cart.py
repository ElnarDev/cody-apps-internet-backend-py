from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models.cart_item import CartItemCreate, CartItemPublic
from app.services import cart_service

router = APIRouter()


@router.get("/", response_model=list[CartItemPublic])
def get_my_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    # Extraemos el user_id del token JWT para mostrar SOLO el carrito del usuario autenticado
    assert current_user.id is not None
    return cart_service.get_cart(session=session, user_id=current_user.id)


@router.post("/", response_model=CartItemPublic)
def add_item_to_cart(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    cart_in: CartItemCreate,
) -> Any:
    # VULNERABILIDAD CRÍTICA EVITADA: Extraemos el ID del usuario directamente de `current_user.id`
    # y no del JSON enviado en el cuerpo de la petición.
    assert current_user.id is not None

    return cart_service.add_to_cart(
        session=session,
        cart_in=cart_in,
        user_id=current_user.id,
    )


@router.patch("/{item_id}", response_model=CartItemPublic)
def update_cart_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int,
    quantity: int,
) -> Any:
    assert current_user.id is not None
    item = cart_service.update_quantity(session, item_id, current_user.id, quantity)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")
    return item


@router.delete("/{item_id}")
def remove_cart_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    item_id: int,
) -> dict:
    assert current_user.id is not None
    deleted = cart_service.remove_item(session, item_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")
    return {"mensaje": f"Item {item_id} eliminado del carrito"}
